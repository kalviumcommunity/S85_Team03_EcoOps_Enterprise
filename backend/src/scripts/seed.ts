import { PrismaClient } from '@prisma/client';
import { randomUUID } from 'node:crypto';
import 'dotenv/config';

const prisma = new PrismaClient();

const categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Beauty', 'Grocery', 'Sports', 'Accessories'];
const regions = ['Delhi', 'Mumbai', 'Bengaluru', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Lucknow', 'Jaipur', 'Ahmedabad'];
const statuses = ['ACTIVE', 'UNDER_REVIEW', 'SUSPENDED'];
const sentiments = ['POSITIVE', 'NEUTRAL', 'NEGATIVE'];
const returnReasons = [
  'Late delivery',
  'Damaged product',
  'Wrong item',
  'Color mismatch',
  'Size issue',
  'Not as described',
  'Quality concerns',
  'Changed mind',
];

const sellerProfiles = [
  { name: 'PrimeCart Retail', region: 'Delhi', category: 'Electronics', status: 'ACTIVE', trust: 92 },
  { name: 'UrbanThread', region: 'Mumbai', category: 'Fashion', status: 'ACTIVE', trust: 86 },
  { name: 'GreenNest Home', region: 'Bengaluru', category: 'Home & Kitchen', status: 'ACTIVE', trust: 81 },
  { name: 'GlowAura', region: 'Hyderabad', category: 'Beauty', status: 'ACTIVE', trust: 77 },
  { name: 'FreshBasket', region: 'Lucknow', category: 'Grocery', status: 'ACTIVE', trust: 72 },
  { name: 'FitForge', region: 'Pune', category: 'Sports', status: 'UNDER_REVIEW', trust: 68 },
  { name: 'StyleLoop', region: 'Jaipur', category: 'Accessories', status: 'ACTIVE', trust: 64 },
  { name: 'MetroMarket', region: 'Chennai', category: 'Electronics', status: 'SUSPENDED', trust: 48 },
];

function randomBetween(min: number, max: number) {
  return Number((Math.random() * (max - min) + min).toFixed(2));
}

function getRiskScore(profileTrust: number) {
  const result = profileTrust + randomBetween(-18, 18);
  return Math.max(35, Math.min(98, result));
}

async function main() {
  await prisma.return.deleteMany();
  await prisma.review.deleteMany();
  await prisma.order.deleteMany();
  await prisma.product.deleteMany();
  await prisma.sellerPerformance.deleteMany();
  await prisma.seller.deleteMany();

  const sellers = await Promise.all(
    Array.from({ length: 120 }, (_, index) => {
      const profile = sellerProfiles[index % sellerProfiles.length];
      return prisma.seller.create({
        data: {
          sellerId: `SELL-${String(index + 1).padStart(4, '0')}`,
          sellerName: `${profile.name.split(' ')[0]}${index + 1}`,
          region: regions[(index + profile.region.length) % regions.length],
          category: categories[(index + 2) % categories.length],
          status: statuses[index % statuses.length],
        },
      });
    }),
  );

  const products = await Promise.all(
    Array.from({ length: 600 }, (_, index) => {
      const seller = sellers[index % sellers.length];
      return prisma.product.create({
        data: {
          productId: `PROD-${String(index + 1).padStart(5, '0')}`,
          sellerId: seller.id,
          productName: `${categories[index % categories.length]} item ${index + 1}`,
          category: categories[index % categories.length],
          price: randomBetween(199, 2499),
          status: 'ACTIVE',
        },
      });
    }),
  );

  const orders = await Promise.all(
    Array.from({ length: 5000 }, (_, index) => {
      const seller = sellers[index % sellers.length];
      const product = products[(index + 2) % products.length];
      const orderDate = new Date(Date.now() - Math.random() * 200 * 24 * 60 * 60 * 1000);
      const deliveryOffset = 2 + Math.random() * 9;
      const expectedDeliveryDate = new Date(orderDate.getTime() + deliveryOffset * 24 * 60 * 60 * 1000);
      const delivered = Math.random() > 0.12;
      const deliveryDate = delivered ? new Date(expectedDeliveryDate.getTime() + (Math.random() > 0.72 ? (Math.random() * 8 - 2) * 24 * 60 * 60 * 1000 : 0)) : null;

      return prisma.order.create({
        data: {
          orderId: `ORD-${String(index + 1).padStart(6, '0')}`,
          sellerId: seller.id,
          productId: product.id,
          orderDate,
          deliveryDate,
          expectedDeliveryDate,
          orderStatus: delivered ? 'DELIVERED' : 'PENDING',
          region: seller.region,
        },
      });
    }),
  );

  for (let i = 0; i < 2500; i += 1) {
    const seller = sellers[i % sellers.length];
    const product = products[(i + 3) % products.length];
    const sentiment = sentiments[i % sentiments.length];
    await prisma.review.create({
      data: {
        sellerId: seller.id,
        productId: product.id,
        rating: randomBetween(2.4, 5),
        reviewText: `Review ${i + 1} from customer about product quality and delivery experience.`,
        sentiment,
        reviewDate: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000),
      },
    });
  }

  for (let i = 0; i < 600; i += 1) {
    const seller = sellers[i % sellers.length];
    const order = orders[i % orders.length];
    const reason = returnReasons[i % returnReasons.length];
    await prisma.return.create({
      data: {
        orderId: `RET-${String(i + 1).padStart(6, '0')}`,
        sellerId: seller.id,
        returnDate: new Date(Date.now() - Math.random() * 150 * 24 * 60 * 60 * 1000),
        returnReason: reason,
        returnStatus: Math.random() > 0.4 ? 'APPROVED' : 'PENDING',
      },
    });
  }

  for (const [sellerIndex, seller] of sellers.entries()) {
    const profile = sellerProfiles[sellerIndex % sellerProfiles.length];
    const pattern = sellerIndex % 5;
    const history = Array.from({ length: 8 }, (_, monthIndex) => {
      const progress = monthIndex / 7;
      const patternOffset = pattern === 1 ? progress * 8 : pattern === 2 ? -progress * 10 : pattern === 3 ? -progress * 18 : 0;
      const baseTrust = getRiskScore(profile.trust + patternOffset);
      const averageRating = clampMetric((baseTrust / 20) + randomBetween(-0.15, 0.15), 2.2, 5);
      const returnRate = clampMetric((100 - baseTrust) / 500 + randomBetween(0, 0.025), 0.02, 0.2);
      const deliveryPerformance = clampMetric(baseTrust + randomBetween(-5, 5), 50, 99);
      const sentimentScore = clampMetric(baseTrust + randomBetween(-8, 8), 35, 99);
      return {
        sellerId: seller.id,
        date: new Date(Date.now() - (7 - monthIndex) * 30 * 24 * 60 * 60 * 1000),
        averageRating,
        returnRate,
        deliveryPerformance,
        sentimentScore,
        trustScore: Number((baseTrust).toFixed(2)),
      };
    });

    await Promise.all(
      history.map((entry) => prisma.sellerPerformance.create({ data: entry })),
    );
  }

  console.log(`Seeded ${sellers.length} sellers, ${products.length} products, ${orders.length} orders, ${2500} reviews, and ${600} returns.`);
}

function clampMetric(value: number, min: number, max: number) {
  return Number(Math.max(min, Math.min(max, value)).toFixed(2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
