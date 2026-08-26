export type RiskThresholds = {
  healthyMin: number;
  monitoringMin: number;
};

export const DEFAULT_RISK_THRESHOLDS: RiskThresholds = {
  healthyMin: 85,
  monitoringMin: 70,
};

export function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

export function classifyRisk(score: number, thresholds: RiskThresholds = DEFAULT_RISK_THRESHOLDS): string {
  if (score >= thresholds.healthyMin) return 'Healthy';
  if (score >= thresholds.monitoringMin) return 'Under Monitoring';
  return 'High Risk';
}

export function calculateTrustScore(metrics: {
  rating: number;
  returnRate: number;
  sentiment: number;
  deliveryPerformance: number;
  consistency: number;
}): number {
  const contributions = calculateTrustContributions(metrics);

  const trustScore =
    contributions.rating +
    contributions.returns +
    contributions.sentiment +
    contributions.delivery +
    contributions.consistency;

  return Number(trustScore.toFixed(2));
}

export function calculateTrustContributions(metrics: {
  rating: number;
  returnRate: number;
  sentiment: number;
  deliveryPerformance: number;
  consistency: number;
}) {
  return {
    rating: clamp((metrics.rating / 5) * 100, 0, 100) * 0.25,
    returns: clamp(100 - (metrics.returnRate * 100), 0, 100) * 0.2,
    sentiment: clamp(metrics.sentiment, 0, 100) * 0.2,
    delivery: clamp(metrics.deliveryPerformance, 0, 100) * 0.2,
    consistency: clamp(metrics.consistency, 0, 100) * 0.15,
  };
}

export function calculateMarketplaceHealth(metrics: {
  avgTrustScore: number;
  healthyPct: number;
  highRiskPct: number;
  avgRating: number;
  avgReturnRate: number;
  avgDelivery: number;
  avgSentiment: number;
}): number {
  const healthyWeight = (metrics.healthyPct / 100) * 30;
  const riskPenalty = (metrics.highRiskPct / 100) * 25;
  const trustWeight = (metrics.avgTrustScore / 100) * 25;
  const ratingWeight = (metrics.avgRating / 5) * 10;
  const returnPenalty = (metrics.avgReturnRate / 1) * 10;
  const deliveryWeight = (metrics.avgDelivery / 100) * 10;
  const sentimentWeight = (metrics.avgSentiment / 100) * 10;

  const score =
    healthyWeight +
    trustWeight +
    ratingWeight +
    deliveryWeight +
    sentimentWeight -
    riskPenalty -
    returnPenalty;

  return Number(clamp(score, 0, 100).toFixed(2));
}
