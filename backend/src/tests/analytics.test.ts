import { describe, expect, it } from 'vitest';
import { calculateTrustScore, calculateMarketplaceHealth, classifyRisk, DEFAULT_RISK_THRESHOLDS } from '../lib/analytics.js';

describe('Trust score engine', () => {
  it('calculates a healthy trust score as expected', () => {
    const score = calculateTrustScore({
      rating: 4.7,
      returnRate: 0.04,
      sentiment: 88,
      deliveryPerformance: 95,
      consistency: 90,
    });

    expect(score).toBeGreaterThan(85);
    expect(classifyRisk(score, DEFAULT_RISK_THRESHOLDS)).toBe('Healthy');
  });

  it('classifies risky sellers below the threshold', () => {
    const score = calculateTrustScore({
      rating: 2.8,
      returnRate: 0.19,
      sentiment: 38,
      deliveryPerformance: 56,
      consistency: 42,
    });

    expect(score).toBeLessThan(70);
    expect(classifyRisk(score, DEFAULT_RISK_THRESHOLDS)).toBe('High Risk');
  });

  it('computes marketplace health from aggregated metrics', () => {
    const score = calculateMarketplaceHealth({
      avgTrustScore: 82,
      healthyPct: 58,
      highRiskPct: 18,
      avgRating: 4.2,
      avgReturnRate: 0.12,
      avgDelivery: 88,
      avgSentiment: 76,
    });

    expect(score).toBeGreaterThan(0);
    expect(score).toBeLessThanOrEqual(100);
  });
});
