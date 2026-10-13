'use client';

import React, { useEffect, useState } from 'react';
import {
  PieChart,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  TrendingUp,
  ShieldCheck,
  Scale,
  Percent,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface Dataset {
  id: string;
  symbol: string;
  total_bars: number;
}

interface AssetRiskDetail {
  risk_contribution_vol: number;
  relative_risk_pct: number;
}

interface PortfolioMetrics {
  expected_annual_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  turnover: number;
  turnover_cost: number;
}

interface PortfolioOptimizeResult {
  method: string;
  covariance_method: string;
  shrinkage_intensity: number;
  weights: Record<string, number>;
  metrics: PortfolioMetrics;
  risk_contributions: Record<string, AssetRiskDetail>;
}

export default function PortfolioPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetIds, setSelectedDatasetIds] = useState<string[]>([]);
  const [method, setMethod] = useState<string>('MAX_SHARPE');
  const [covMethod, setCovMethod] = useState<string>('LEDOIT_WOLF');
  const [riskFreeRate, setRiskFreeRate] = useState<number>(0.02);
  const [minWeight, setMinWeight] = useState<number>(0.0);
  const [maxWeight, setMaxWeight] = useState<number>(1.0);
  const [turnoverPenaltyBps, setTurnoverPenaltyBps] = useState<number>(10.0);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PortfolioOptimizeResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDatasets() {
      try {
        const data = await api.get<Dataset[]>('/api/v1/datasets');
        setDatasets(data || []);
        if (data && data.length >= 2) {
          // Default select first two datasets
          setSelectedDatasetIds([data[0].id, data[1].id]);
        }
      } catch (err: any) {
        console.error('Failed to load datasets for portfolio:', err);
      }
    }
    loadDatasets();
  }, []);

  const toggleDataset = (id: string) => {
    if (selectedDatasetIds.includes(id)) {
      if (selectedDatasetIds.length > 2) {
        setSelectedDatasetIds(selectedDatasetIds.filter((item) => item !== id));
      }
    } else {
      setSelectedDatasetIds([...selectedDatasetIds, id]);
    }
  };

  const handleOptimize = async () => {
    if (selectedDatasetIds.length < 2) {
      setError('At least 2 distinct assets are required for portfolio optimization.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<PortfolioOptimizeResult>('/api/v1/portfolio/optimize', {
        dataset_ids: selectedDatasetIds,
        method,
        covariance_method: covMethod,
        risk_free_rate: riskFreeRate,
        min_weight: minWeight,
        max_weight: maxWeight,
        turnover_penalty_bps: turnoverPenaltyBps,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Portfolio optimization failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                Portfolio Construction & Risk Attribution
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Ledoit-Wolf Shrinkage
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Markowitz Mean-Variance, Global Minimum Variance, and Equal Risk Parity with exact Euler risk decomposition.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <Scale className="w-4 h-4 text-accent-blue" />
              <span>Euler Invariant: Σ RC_i = σ_p</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-accent-red/10 border border-accent-red/30 flex items-center gap-3 text-sm text-accent-red">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* 2-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Console */}
          <div className="lg:col-span-4 space-y-6">
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Optimization Parameters</span>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {/* Method selector */}
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                    Objective Function
                  </label>
                  <select
                    value={method}
                    onChange={(e) => setMethod(e.target.value)}
                    className="w-full bg-bg-surface-2 border border-border-subtle rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                  >
                    <option value="MAX_SHARPE">Maximum Sharpe Ratio (Tangency)</option>
                    <option value="MIN_VARIANCE">Global Minimum Variance (GMV)</option>
                    <option value="RISK_PARITY">Equal Risk Parity (Risk Budgeting)</option>
                    <option value="INVERSE_VOL">Inverse Volatility Allocation</option>
                    <option value="EQUAL_WEIGHT">Equal Weight Benchmark (1/N)</option>
                  </select>
                </div>

                {/* Covariance Estimator */}
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                    Covariance Estimator
                  </label>
                  <select
                    value={covMethod}
                    onChange={(e) => setCovMethod(e.target.value)}
                    className="w-full bg-bg-surface-2 border border-border-subtle rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                  >
                    <option value="LEDOIT_WOLF">Ledoit-Wolf Optimal Shrinkage</option>
                    <option value="SAMPLE">Empirical Sample Covariance</option>
                  </select>
                </div>

                {/* Risk-free Rate */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                      Risk-Free Rate
                    </label>
                    <Input
                      type="number"
                      step="0.005"
                      value={riskFreeRate}
                      onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                      Turnover Cost (bps)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={turnoverPenaltyBps}
                      onChange={(e) => setTurnoverPenaltyBps(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                {/* Weight bounds */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                      Min Weight
                    </label>
                    <Input
                      type="number"
                      step="0.05"
                      min="0.0"
                      max="0.5"
                      value={minWeight}
                      onChange={(e) => setMinWeight(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                      Max Weight
                    </label>
                    <Input
                      type="number"
                      step="0.05"
                      min="0.1"
                      max="1.0"
                      value={maxWeight}
                      onChange={(e) => setMaxWeight(parseFloat(e.target.value) || 1.0)}
                    />
                  </div>
                </div>

                {/* Multi-asset selector */}
                <div className="pt-2 border-t border-border-subtle">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-mono text-text-secondary uppercase">
                      Holdings Pool ({selectedDatasetIds.length} Selected)
                    </label>
                  </div>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                    {datasets.map((ds) => {
                      const isChecked = selectedDatasetIds.includes(ds.id);
                      return (
                        <div
                          key={ds.id}
                          onClick={() => toggleDataset(ds.id)}
                          className={`flex items-center justify-between p-2 rounded cursor-pointer border text-xs transition-colors ${
                            isChecked
                              ? 'bg-accent-blue/10 border-accent-blue/40 text-text-primary'
                              : 'bg-bg-surface-2 border-border-subtle text-text-muted hover:border-border-strong'
                          }`}
                        >
                          <div>
                            <span className="font-mono font-medium">{ds.symbol}</span>
                            <span className="text-[10px] text-text-muted ml-2">({ds.total_bars} bars)</span>
                          </div>
                          <span
                            className={`w-3.5 h-3.5 rounded flex items-center justify-center border text-[9px] ${
                              isChecked
                                ? 'bg-accent-blue text-white border-accent-blue'
                                : 'border-border-strong'
                            }`}
                          >
                            {isChecked ? '✓' : ''}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Submit button */}
                <Button
                  onClick={handleOptimize}
                  disabled={loading || selectedDatasetIds.length < 2}
                  className="w-full mt-4 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Optimizing Portfolio...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Solve Allocation</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Invariant Explanation Card */}
            <div className="p-4 rounded bg-bg-surface-1 border border-border-subtle space-y-2 text-xs text-text-secondary">
              <div className="font-medium text-text-primary flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-accent-green" />
                <span>Ledoit-Wolf Shrinkage Invariant</span>
              </div>
              <p>
                Empirical sample covariance is notoriously noisy and prone to inversion error.
                Ledoit-Wolf computes an analytically optimal shrinkage intensity δ towards a structured target, guaranteeing well-conditioned numerical optimization.
              </p>
            </div>
          </div>

          {/* Right Column: Output */}
          <div className="lg:col-span-8 space-y-6">
            {result ? (
              <>
                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Expected Return</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {(result.metrics.expected_annual_return * 100).toFixed(2)}%
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">Annualized μ_p</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Portfolio Volatility</div>
                      <div className="text-xl font-semibold text-accent-blue mt-1 font-mono">
                        {(result.metrics.annualized_volatility * 100).toFixed(2)}%
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">Annualized σ_p</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Sharpe Ratio</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {result.metrics.sharpe_ratio.toFixed(2)}
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        (μ_p - r_f) / σ_p
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Shrinkage Intensity (δ)</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {result.shrinkage_intensity.toFixed(3)}
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        {result.covariance_method}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Allocation Weights Table & Progress Bars */}
                <Card>
                  <CardHeader className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <PieChart className="w-4 h-4 text-text-secondary" />
                      <span className="font-medium text-sm text-text-primary">Optimized Asset Weights</span>
                    </div>
                    <Badge variant="neutral" className="font-mono text-xs">
                      {result.method}
                    </Badge>
                  </CardHeader>
                  <CardContent className="space-y-4 pt-4">
                    {Object.entries(result.weights).map(([symbol, weight]) => {
                      const pct = Math.round(weight * 100);
                      return (
                        <div key={symbol} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="font-mono text-text-primary font-medium">{symbol}</span>
                            <span className="font-mono text-text-secondary">{(weight * 100).toFixed(2)}%</span>
                          </div>
                          <div className="w-full h-2.5 rounded bg-bg-surface-2 overflow-hidden">
                            <div
                              className="h-full bg-accent-blue rounded transition-all duration-300"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </CardContent>
                </Card>

                {/* Risk Decomposition Table */}
                <Card>
                  <CardHeader className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Scale className="w-4 h-4 text-text-secondary" />
                      <span className="font-medium text-sm text-text-primary">
                        Euler Risk Decomposition (Marginal & Relative Risk Contributions)
                      </span>
                    </div>
                    <Badge variant="profit" className="text-xs font-mono">
                      Exact Invariant
                    </Badge>
                  </CardHeader>
                  <CardContent className="pt-2">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="border-b border-border-subtle text-text-muted font-mono uppercase">
                            <th className="py-2.5 px-3">Asset Symbol</th>
                            <th className="py-2.5 px-3">Allocated Weight</th>
                            <th className="py-2.5 px-3">Marginal Vol Contrib (RC_i)</th>
                            <th className="py-2.5 px-3 text-right">Relative Risk Contrib (%)</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle/50 font-mono">
                          {Object.entries(result.risk_contributions).map(([symbol, risk]) => (
                            <tr key={symbol} className="hover:bg-bg-surface-2/40">
                              <td className="py-2.5 px-3 text-text-primary font-medium">{symbol}</td>
                              <td className="py-2.5 px-3 text-text-secondary">
                                {((result.weights[symbol] || 0) * 100).toFixed(2)}%
                              </td>
                              <td className="py-2.5 px-3 text-text-secondary">
                                {(risk.risk_contribution_vol * 100).toFixed(2)}%
                              </td>
                              <td className="py-2.5 px-3 text-right text-text-primary font-medium">
                                {risk.relative_risk_pct.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="h-96 rounded-lg border border-dashed border-border-subtle flex flex-col items-center justify-center p-8 text-center text-text-muted">
                <PieChart className="w-12 h-12 text-border-strong mb-3" />
                <h3 className="text-sm font-medium text-text-secondary">No Portfolio Optimized Yet</h3>
                <p className="text-xs text-text-muted max-w-sm mt-1">
                  Select at least two assets from your workspace, choose an objective function (e.g. Max Sharpe or Risk Parity), and click "Solve Allocation".
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
