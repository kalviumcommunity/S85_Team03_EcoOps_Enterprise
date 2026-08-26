import cors from 'cors';
import express, { type NextFunction, type Request, type Response } from 'express';
import { z } from 'zod';
import { env } from './config/env.js';
import { prisma } from './lib/prisma.js';
import { calculateMarketplaceHealth, calculateTrustContributions, calculateTrustScore, classifyRisk, DEFAULT_RISK_THRESHOLDS } from './lib/analytics.js';
import { createCsvReport, createExcelReport, createPdfReport, getReportMimeType } from './lib/reporting.js';

const app = express();

const allowedOrigins = Array.from(new Set([
  env.frontendUrl,
  'http://localhost:5173',
  'http://127.0.0.1:5173',
  'http://localhost:4173',
  'http://127.0.0.1:4173',
])).filter(Boolean);

app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
      return;
    }

    callback(new Error(`CORS policy blocked origin: ${origin}`));
  },
  credentials: true,
}));
app.use(express.json({ limit: '2mb' }));

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

const reportQuerySchema = z.object({
  type: z.enum(['csv', 'xlsx', 'pdf']).default('csv'),
  category: z.string().optional(),
  region: z.string().optional(),
  risk: z.string().optional(),
});

const listQuerySchema = z.object({
  search: z.string().optional(),
  category: z.string().optional(),
  region: z.string().optional(),
  risk: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sort: z.enum(['sellerName', 'trustScore', 'rating', 'returnRate', 'deliveryPerformance', 'updatedAt']).default('trustScore'),
});

const trendQuerySchema = z.object({
  startDate: z.string().optional(),
  endDate: z.string().optional(),
});

const parseRisk = (value?: string) => {
  if (!value) return undefined;
  const normalized = value.toLowerCase();
  if (normalized === 'healthy') return 'Healthy';
  if (normalized === 'under monitoring' || normalized === 'under_monitoring') return 'Under Monitoring';
  if (normalized === 'high risk' || normalized === 'high_risk') return 'High Risk';
  return value;
};

const getSellerMetrics = (seller: any) => {
  const metrics = {
    rating: Number((seller.reviews.reduce((sum: number, review: any) => sum + Number(review.rating), 0) / Math.max(seller.reviews.length, 1)).toFixed(2)),
    returnRate: Number((seller.returns.length / Math.max(seller.orders.length, 1)).toFixed(4)),
    deliveryPerformance: Number((seller.orders.filter((order: any) => order.deliveryDate && order.orderStatus !== 'CANCELLED').length
      ? (seller.orders.filter((order: any) => order.deliveryDate && order.orderStatus !== 'CANCELLED').reduce((sum: number, order: any) => {
          const expected = order.expectedDeliveryDate ? new Date(order.expectedDeliveryDate).getTime() : null;
          const delivered = order.deliveryDate ? new Date(order.deliveryDate).getTime() : null;
          if (!expected || !delivered) return sum + 100;
          const delay = Math.max((delivered - expected) / (1000 * 60 * 60 * 24), 0);
          return sum + Math.max(0, 100 - delay * 5);
        }, 0) / seller.orders.filter((order: any) => order.deliveryDate && order.orderStatus !== 'CANCELLED').length) : 100).toFixed(2)),
    sentiment: Number((seller.reviews.reduce((sum: number, review: any) => sum + (review.sentiment === 'POSITIVE' ? 100 : review.sentiment === 'NEGATIVE' ? 30 : 70), 0) / Math.max(seller.reviews.length, 1)).toFixed(2)),
    consistency: Number((seller.performance.length ? seller.performance.reduce((sum: number, item: any) => sum + Number(item.trustScore), 0) / seller.performance.length : 82).toFixed(2)),
  };

  const trustScore = calculateTrustScore({
    rating: metrics.rating,
    returnRate: metrics.returnRate,
    sentiment: metrics.sentiment,
    deliveryPerformance: metrics.deliveryPerformance,
    consistency: metrics.consistency,
  });

  return {
    ...metrics,
    trustScore,
    riskClassification: classifyRisk(trustScore),
  };
};

const withSellerData = async (seller: any) => {
  const reviews = await prisma.review.findMany({ where: { sellerId: seller.id }, orderBy: { reviewDate: 'desc' }, take: 20 });
  const returns = await prisma.return.findMany({ where: { sellerId: seller.id }, orderBy: { returnDate: 'desc' }, take: 20 });
  const orders = await prisma.order.findMany({ where: { sellerId: seller.id }, orderBy: { orderDate: 'desc' }, take: 200 });
  const performance = await prisma.sellerPerformance.findMany({ where: { sellerId: seller.id }, orderBy: { date: 'asc' } });
  const products = await prisma.product.findMany({ where: { sellerId: seller.id } });
  const sellerWithExtras = { ...seller, reviews, returns, orders, performance, products };
  return getSellerMetrics(sellerWithExtras);
};

app.get('/api/dashboard/overview', async (_req, res, next) => {
  try {
    const sellers = await prisma.seller.findMany({
      include: { reviews: true, orders: true, returns: true, performance: true },
    });

    const normalized = sellers.map((seller) => getSellerMetrics(seller));
    const healthy = normalized.filter((item) => item.riskClassification === 'Healthy').length;
    const underMonitoring = normalized.filter((item) => item.riskClassification === 'Under Monitoring').length;
    const highRisk = normalized.filter((item) => item.riskClassification === 'High Risk').length;
    const avgTrust = normalized.reduce((sum, item) => sum + item.trustScore, 0) / Math.max(normalized.length, 1);
    const avgRating = normalized.reduce((sum, item) => sum + item.rating, 0) / Math.max(normalized.length, 1);
    const avgReturnRate = normalized.reduce((sum, item) => sum + item.returnRate, 0) / Math.max(normalized.length, 1);
    const avgDelivery = normalized.reduce((sum, item) => sum + item.deliveryPerformance, 0) / Math.max(normalized.length, 1);
    const avgSentiment = normalized.reduce((sum, item) => sum + item.sentiment, 0) / Math.max(normalized.length, 1);
    const sellerRows = sellers.map((seller, index) => ({
      id: seller.id,
      sellerId: seller.sellerId,
      sellerName: seller.sellerName,
      trustScore: normalized[index].trustScore,
      risk: normalized[index].riskClassification,
    }));

    res.json({
      totalSellers: sellers.length,
      healthySellers: healthy,
      underMonitoringSellers: underMonitoring,
      highRiskSellers: highRisk,
      marketplaceHealthScore: Number(calculateMarketplaceHealth({
        avgTrustScore: avgTrust,
        healthyPct: (healthy / Math.max(sellers.length, 1)) * 100,
        highRiskPct: (highRisk / Math.max(sellers.length, 1)) * 100,
        avgRating,
        avgReturnRate,
        avgDelivery,
        avgSentiment,
      }).toFixed(2)),
      averageRating: Number(avgRating.toFixed(2)),
      averageReturnRate: Number((avgReturnRate * 100).toFixed(2)),
      deliveryPerformance: Number(avgDelivery.toFixed(2)),
      averageSentiment: Number(avgSentiment.toFixed(2)),
      riskDistribution: {
        Healthy: healthy,
        'Under Monitoring': underMonitoring,
        'High Risk': highRisk,
      },
      topRiskySellers: sellerRows.filter((seller) => seller.risk === 'High Risk').sort((left, right) => left.trustScore - right.trustScore).slice(0, 5),
      topPerformingSellers: sellerRows.filter((seller) => seller.risk === 'Healthy').sort((left, right) => right.trustScore - left.trustScore).slice(0, 5),
    });
  } catch (error) {
    next(error);
  }
});

app.get('/api/dashboard/trends', async (req, res, next) => {
  try {
    const parsed = trendQuerySchema.parse(req.query);
    const startDate = parsed.startDate ? new Date(parsed.startDate) : new Date(Date.now() - 180 * 24 * 60 * 60 * 1000);
    const endDate = parsed.endDate ? new Date(parsed.endDate) : new Date();
    if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime()) || startDate > endDate) {
      return res.status(400).json({ message: 'Invalid trend date range' });
    }

    const performance = await prisma.sellerPerformance.findMany({
      where: { date: { gte: startDate, lte: endDate } },
      orderBy: { date: 'asc' },
    });

    const grouped = performance.reduce<Record<string, { trustScore: number; averageRating: number; returnRate: number; deliveryPerformance: number; sentimentScore: number; count: number }>>((acc, item) => {
      const key = item.date.toISOString().slice(0, 10);
      const current = acc[key] ?? { trustScore: 0, averageRating: 0, returnRate: 0, deliveryPerformance: 0, sentimentScore: 0, count: 0 };
      current.trustScore += item.trustScore;
      current.averageRating += item.averageRating;
      current.returnRate += item.returnRate;
      current.deliveryPerformance += item.deliveryPerformance;
      current.sentimentScore += item.sentimentScore;
      current.count += 1;
      acc[key] = current;
      return acc;
    }, {});

    const trends = Object.entries(grouped).map(([date, value]) => ({
      date,
      trustScore: Number((value.trustScore / value.count).toFixed(2)),
      rating: Number((value.averageRating / value.count).toFixed(2)),
      returnRate: Number((value.returnRate / value.count * 100).toFixed(2)),
      delivery: Number((value.deliveryPerformance / value.count).toFixed(2)),
      sentiment: Number((value.sentimentScore / value.count).toFixed(2)),
    }));

    res.json(trends.slice(-12));
  } catch (error) {
    next(error);
  }
});

app.get('/api/categories', async (_req, res, next) => {
  try {
    const categories = await prisma.seller.groupBy({
      by: ['category'],
      _count: { category: true },
    });
    res.json(categories.map((item) => ({ name: item.category, count: item._count.category })));
  } catch (error) {
    next(error);
  }
});

app.get('/api/regions', async (_req, res, next) => {
  try {
    const regions = await prisma.seller.groupBy({
      by: ['region'],
      _count: { region: true },
    });
    res.json(regions.map((item) => ({ name: item.region, count: item._count.region })));
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers', async (req, res, next) => {
  try {
    const parsed = listQuerySchema.parse(req.query);
    const filter: any = {};

    if (parsed.search) {
      filter.OR = [
        { sellerName: { contains: parsed.search, mode: 'insensitive' } },
        { sellerId: { contains: parsed.search, mode: 'insensitive' } },
      ];
    }

    if (parsed.category) filter.category = parsed.category;
    if (parsed.region) filter.region = parsed.region;
    // Risk is derived from calculated metrics, not the seller lifecycle status.

    const sellers = await prisma.seller.findMany({
      where: filter,
      include: {
        reviews: true,
        orders: true,
        returns: true,
        performance: true,
      },
    });

    let rows = sellers.map((seller) => {
      const metrics = getSellerMetrics(seller);
      return {
        id: seller.id,
        sellerId: seller.sellerId,
        sellerName: seller.sellerName,
        category: seller.category,
        region: seller.region,
        trustScore: metrics.trustScore,
        rating: metrics.rating,
        returnRate: Number((metrics.returnRate * 100).toFixed(2)),
        deliveryPerformance: metrics.deliveryPerformance,
        sentiment: metrics.sentiment,
        risk: metrics.riskClassification,
        updatedAt: seller.updatedAt,
      };
    });

    if (parsed.risk) rows = rows.filter((row) => row.risk === parseRisk(parsed.risk));
    rows.sort((left, right) => {
      const leftValue = left[parsed.sort as keyof typeof left];
      const rightValue = right[parsed.sort as keyof typeof right];
      if (leftValue === rightValue) return 0;
      return leftValue > rightValue ? -1 : 1;
    });

    const total = rows.length;
    const start = (parsed.page - 1) * parsed.limit;
    res.json({ rows: rows.slice(start, start + parsed.limit), total, page: parsed.page, limit: parsed.limit, totalPages: Math.ceil(total / parsed.limit) });
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/risk', async (_req, res, next) => {
  try {
    const sellers = await prisma.seller.findMany({ include: { reviews: true, returns: true, orders: true, performance: true } });
    const rows = sellers.map((seller) => {
      const metrics = getSellerMetrics(seller);
      return {
        id: seller.id,
        sellerId: seller.sellerId,
        sellerName: seller.sellerName,
        category: seller.category,
        region: seller.region,
        trustScore: metrics.trustScore,
        risk: metrics.riskClassification,
        rating: metrics.rating,
        returnRate: Number((metrics.returnRate * 100).toFixed(2)),
        deliveryPerformance: metrics.deliveryPerformance,
        sentiment: metrics.sentiment,
        trend: Number(((metrics.consistency ?? 75) - 70).toFixed(2)),
        mainRiskDriver: metrics.returnRate > 0.12 ? 'High return rate' : metrics.rating < 3.5 ? 'Poor rating' : metrics.sentiment < 60 ? 'Negative sentiment' : metrics.deliveryPerformance < 75 ? 'Poor delivery' : 'Declining consistency',
      };
    }).filter((row) => row.risk === 'High Risk');

    res.json(rows);
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/:id', async (req, res, next) => {
  try {
    const seller = await prisma.seller.findUnique({
      where: { id: req.params.id },
      include: { reviews: true, orders: true, returns: true, performance: true, products: true },
    });
    if (!seller) return res.status(404).json({ message: 'Seller not found' });
    const metrics = getSellerMetrics(seller);
    const contribution = calculateTrustContributions(metrics);
    res.json({
      ...seller,
      ...metrics,
      contribution: Object.fromEntries(Object.entries(contribution).map(([key, value]) => [key, Number(value.toFixed(2))])),
    });
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/:id/performance', async (req, res, next) => {
  try {
    const performance = await prisma.sellerPerformance.findMany({
      where: { sellerId: req.params.id },
      orderBy: { date: 'asc' },
    });
    res.json(performance);
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/:id/trends', async (req, res, next) => {
  try {
    const performance = await prisma.sellerPerformance.findMany({
      where: { sellerId: req.params.id },
      orderBy: { date: 'asc' },
    });
    res.json(performance.map((entry) => ({
      date: entry.date.toISOString().slice(0, 10),
      trustScore: entry.trustScore,
      rating: entry.averageRating,
      returnRate: entry.returnRate * 100,
      delivery: entry.deliveryPerformance,
      sentiment: entry.sentimentScore,
    })));
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/:id/reviews', async (req, res, next) => {
  try {
    const reviews = await prisma.review.findMany({
      where: { sellerId: req.params.id },
      orderBy: { reviewDate: 'desc' },
      take: 20,
    });
    res.json(reviews);
  } catch (error) {
    next(error);
  }
});

app.get('/api/sellers/:id/returns', async (req, res, next) => {
  try {
    const returns = await prisma.return.findMany({
      where: { sellerId: req.params.id },
      orderBy: { returnDate: 'desc' },
      take: 20,
    });
    res.json(returns);
  } catch (error) {
    next(error);
  }
});

app.get('/api/reports', async (_req, res) => {
  const sellers = await prisma.seller.findMany({ include: { reviews: true, orders: true, returns: true, performance: true } });
  const rows = sellers.map((seller) => {
    const metrics = getSellerMetrics(seller);
    return {
      sellerId: seller.sellerId,
      sellerName: seller.sellerName,
      category: seller.category,
      region: seller.region,
      trustScore: metrics.trustScore,
      risk: metrics.riskClassification,
      rating: metrics.rating,
      returnRate: Number((metrics.returnRate * 100).toFixed(2)),
      deliveryPerformance: metrics.deliveryPerformance,
      sentiment: metrics.sentiment,
    };
  });
  res.json(rows.slice(0, 20));
});

app.post('/api/reports/export', async (req, res, next) => {
  try {
    const parsed = reportQuerySchema.parse(req.body);
    const sellers = await prisma.seller.findMany({ include: { reviews: true, orders: true, returns: true, performance: true } });
    const rows = sellers.map((seller) => {
      const metrics = getSellerMetrics(seller);
      return {
        sellerId: seller.sellerId,
        sellerName: seller.sellerName,
        category: seller.category,
        region: seller.region,
        risk: metrics.riskClassification,
        trustScore: metrics.trustScore,
        rating: metrics.rating,
        returnRate: Number((metrics.returnRate * 100).toFixed(2)),
        deliveryPerformance: metrics.deliveryPerformance,
        sentiment: metrics.sentiment,
      };
    });

    const title = parsed.category || parsed.region ? 'Filtered Seller Report' : 'Marketplace Seller Report';
    const data = parsed.category ? rows.filter((row) => row.category === parsed.category) : parsed.region ? rows.filter((row) => row.region === parsed.region) : rows;

    let output: Buffer | string;
    let fileName = `stap-report.${parsed.type}`;

    if (parsed.type === 'csv') {
      output = await createCsvReport(data);
      res.type('text/csv');
    } else if (parsed.type === 'xlsx') {
      output = await createExcelReport(data);
      res.type('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    } else {
      output = await createPdfReport(title, data);
      res.type('application/pdf');
    }

    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    res.send(output);
  } catch (error) {
    next(error);
  }
});

app.use((err: Error, req: Request, res: Response, _next: NextFunction) => {
  console.error(`[${req.method} ${req.originalUrl}]`, err);
  const databaseUnavailable = err.message.includes('Can\'t reach database server') || err.message.includes('P1001');
  res.status(databaseUnavailable ? 503 : 500).json({
    message: databaseUnavailable ? 'Database unavailable. Start PostgreSQL and run the Prisma migration and seed.' : err.message || 'Internal server error',
  });
});

export default app;
