'use client';

import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Activity,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Sparkles,
  TrendingDown,
  Percent,
  Sliders,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { api } from '@/lib/api';

interface Dataset {
  id: string;
  symbol: string;
  name: string;
  total_bars: number;
}

interface AnalyticsSummary {
  dataset_id: string;
  symbol: string;
  total_bars: number;
  distribution: {
    count: number;
    mean_daily: number;
    mean_annualized: number;
    std_daily: number;
    std_annualized: number;
    skewness: number;
    excess_kurtosis: number;
    jarque_bera: {
      statistic: number;
      p_value: number;
      is_normal: boolean;
    };
    augmented_dickey_fuller: {
      test_statistic: number;
      p_value: number;
      is_stationary: boolean;
      critical_values: Record<string, number>;
    };
  };
  acf_lags: number[];
  max_drawdown: number;
  current_annualized_volatility: number;
}

export default function AnalyticsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [windowSize, setWindowSize] = useState<number>(21);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);

  useEffect(() => {
    api.get<Dataset[]>('/datasets')
      .then((data) => {
        setDatasets(data);
        if (data.length > 0) {
          setSelectedDatasetId(data[0].id);
          fetchAnalytics(data[0].id, 21);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const fetchAnalytics = async (datasetId: string, window: number) => {
    if (!datasetId) return;
    setComputing(true);
    try {
      const res = await api.post<AnalyticsSummary>('/analytics/summary', {
        dataset_id: datasetId,
        rolling_window: window,
      });
      setAnalytics(res);
    } catch (err) {
      console.error('Failed to compute analytics:', err);
    } finally {
      setComputing(false);
    }
  };

  const handleDatasetChange = (id: string) => {
    setSelectedDatasetId(id);
    fetchAnalytics(id, windowSize);
  };

  const handleWindowChange = (w: number) => {
    setWindowSize(w);
    fetchAnalytics(selectedDatasetId, w);
  };

  return (
    <Shell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5">
              <BarChart3 className="w-5 h-5 text-accent" /> Exploratory Time-Series Analytics & Diagnostics
            </h1>
            <p className="text-xs text-text-secondary mt-1">
              Statistical moments, excess kurtosis, Jarque-Bera normality tests, and Augmented Dickey-Fuller stationarity.
            </p>
          </div>

          {/* Controls Bar */}
          <div className="flex items-center gap-3">
            <select
              className="px-3 py-1.5 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent"
              value={selectedDatasetId}
              onChange={(e) => handleDatasetChange(e.target.value)}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.symbol} ({d.total_bars} bars)
                </option>
              ))}
            </select>

            <div className="flex items-center gap-2 bg-surface-elevated px-3 py-1 rounded border border-border-strong text-xs font-mono">
              <span className="text-text-muted">Window:</span>
              <span className="text-accent font-semibold">{windowSize}d</span>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-xs text-text-muted font-mono py-12 text-center">Loading datasets...</div>
        ) : !analytics ? (
          <div className="bg-surface rounded-lg border border-border-subtle p-8 text-center text-xs text-text-muted">
            No dataset available. Please generate or import a dataset in the Market Data module.
          </div>
        ) : (
          <div className="space-y-6">
            {/* Core Moments Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-surface p-4 rounded-lg border border-border-subtle">
                <div className="text-[11px] text-text-secondary uppercase tracking-wider mb-1">
                  Ann. Mean Return
                </div>
                <div
                  className={`text-xl font-bold font-mono ${
                    analytics.distribution.mean_annualized >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                  }`}
                >
                  {(analytics.distribution.mean_annualized * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-text-muted mt-1 font-mono">
                  Daily: {(analytics.distribution.mean_daily * 100).toFixed(3)}%
                </div>
              </div>

              <div className="bg-surface p-4 rounded-lg border border-border-subtle">
                <div className="text-[11px] text-text-secondary uppercase tracking-wider mb-1">
                  Ann. Volatility
                </div>
                <div className="text-xl font-bold font-mono text-text-primary">
                  {(analytics.distribution.std_annualized * 100).toFixed(2)}%
                </div>
                <div className="text-[10px] text-text-muted mt-1 font-mono">
                  Current ({windowSize}d): {(analytics.current_annualized_volatility * 100).toFixed(2)}%
                </div>
              </div>

              <div className="bg-surface p-4 rounded-lg border border-border-subtle">
                <div className="text-[11px] text-text-secondary uppercase tracking-wider mb-1">
                  Skewness
                </div>
                <div
                  className={`text-xl font-bold font-mono ${
                    analytics.distribution.skewness < 0 ? 'text-financial-warning' : 'text-text-primary'
                  }`}
                >
                  {analytics.distribution.skewness.toFixed(3)}
                </div>
                <div className="text-[10px] text-text-muted mt-1">
                  {analytics.distribution.skewness < 0 ? 'Left-tail risk' : 'Right-skewed'}
                </div>
              </div>

              <div className="bg-surface p-4 rounded-lg border border-border-subtle">
                <div className="text-[11px] text-text-secondary uppercase tracking-wider mb-1">
                  Excess Kurtosis
                </div>
                <div
                  className={`text-xl font-bold font-mono ${
                    analytics.distribution.excess_kurtosis > 0 ? 'text-financial-loss' : 'text-text-primary'
                  }`}
                >
                  {analytics.distribution.excess_kurtosis.toFixed(3)}
                </div>
                <div className="text-[10px] text-text-muted mt-1">
                  {analytics.distribution.excess_kurtosis > 0 ? 'Leptokurtic (Fat tails)' : 'Platykurtic'}
                </div>
              </div>
            </div>

            {/* Formal Hypothesis Testing Diagnostic Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Card 1: Jarque-Bera Normality Test */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-accent" />
                    <span className="text-xs font-bold text-text-primary">Jarque-Bera Normality Test</span>
                  </div>
                  <Badge variant={analytics.distribution.jarque_bera.is_normal ? 'profit' : 'warning'}>
                    {analytics.distribution.jarque_bera.is_normal ? 'NORMAL (p > 0.05)' : 'FAT-TAILED (p ≤ 0.05)'}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-3 text-xs">
                  <div className="grid grid-cols-2 gap-3 font-mono bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div>
                      <span className="text-[10px] text-text-muted block">Test Statistic (JB):</span>
                      <span className="font-semibold text-text-primary">
                        {analytics.distribution.jarque_bera.statistic}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-text-muted block">p-value:</span>
                      <span className="font-semibold text-text-primary">
                        {analytics.distribution.jarque_bera.p_value}
                      </span>
                    </div>
                  </div>
                  <p className="text-[11px] text-text-secondary leading-relaxed">
                    {analytics.distribution.jarque_bera.is_normal
                      ? 'The null hypothesis of normal distribution cannot be rejected. Standard parametric Gaussian risk models are valid.'
                      : 'The null hypothesis of normality is strongly rejected. Financial returns exhibit significant tail risk. Non-parametric or Extreme Value Theory (EVT) VaR recommended.'}
                  </p>
                </CardContent>
              </Card>

              {/* Card 2: Augmented Dickey-Fuller Stationarity Test */}
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-accent" />
                    <span className="text-xs font-bold text-text-primary">Augmented Dickey-Fuller (ADF) Test</span>
                  </div>
                  <Badge variant={analytics.distribution.augmented_dickey_fuller.is_stationary ? 'profit' : 'loss'}>
                    {analytics.distribution.augmented_dickey_fuller.is_stationary
                      ? 'STATIONARY (p < 0.05)'
                      : 'UNIT ROOT (NON-STATIONARY)'}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-3 text-xs">
                  <div className="grid grid-cols-2 gap-3 font-mono bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div>
                      <span className="text-[10px] text-text-muted block">ADF Statistic:</span>
                      <span className="font-semibold text-text-primary">
                        {analytics.distribution.augmented_dickey_fuller.test_statistic}
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-text-muted block">p-value:</span>
                      <span className="font-semibold text-text-primary">
                        {analytics.distribution.augmented_dickey_fuller.p_value}
                      </span>
                    </div>
                  </div>
                  <p className="text-[11px] text-text-secondary leading-relaxed">
                    {analytics.distribution.augmented_dickey_fuller.is_stationary
                      ? 'The return series is stationary (no stochastic unit root). Suitable for linear regressions, ARIMA, GARCH, and mean-reverting features.'
                      : 'The series is non-stationary. Raw prices must be differenced or fractional-differenced before modeling to avoid spurious correlation.'}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Autocorrelation Function (ACF) Visual Bar Chart */}
            <Card>
              <CardHeader>
                <span className="text-xs font-bold text-text-primary">
                  Autocorrelation Function (ACF) up to 20 Lags
                </span>
                <span className="text-[10px] text-text-muted font-mono">Lags 1 - 20 (Return Memory)</span>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-1.5 h-32 pt-4 px-2 border-b border-border-subtle">
                  {analytics.acf_lags.slice(1).map((acf, i) => {
                    const heightPercent = Math.min(100, Math.max(5, Math.abs(acf) * 200));
                    const isPositive = acf >= 0;
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                        <div
                          style={{ height: `${heightPercent}%` }}
                          className={`w-full rounded-t transition-all ${
                            isPositive ? 'bg-accent/70 group-hover:bg-accent' : 'bg-financial-loss/70 group-hover:bg-financial-loss'
                          }`}
                        />
                        <div className="text-[9px] text-text-muted font-mono mt-1">{i + 1}</div>
                        {/* Hover Tooltip */}
                        <div className="absolute -top-8 bg-surface-elevated text-text-primary text-[10px] font-mono px-1.5 py-0.5 rounded border border-border-strong opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 whitespace-nowrap">
                          Lag {i + 1}: {acf.toFixed(4)}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="flex items-center justify-between text-[11px] text-text-muted pt-2 font-mono">
                  <span>Lag 1 (Short-term bounce / momentum)</span>
                  <span>Lag 20 (~1 Month persistence)</span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </Shell>
  );
}
