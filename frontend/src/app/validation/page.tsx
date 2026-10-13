'use client';

import React, { useEffect, useState } from 'react';
import {
  Activity,
  ShieldAlert,
  Sliders,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Zap,
  Play,
  RotateCcw,
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

interface DSRResult {
  observed_sharpe: number;
  expected_max_sharpe_hurdle: number;
  num_trials_tested: number;
  track_length: number;
  deflated_sharpe_ratio: number;
  p_value: number;
  is_statistically_significant: boolean;
}

interface WalkForwardWindow {
  window_index: number;
  train_start: string;
  train_end: string;
  test_start: string;
  test_end: string;
  sharpe_is: number;
  sharpe_oos: number;
  walk_forward_efficiency: number;
  oos_total_return: number;
}

interface WalkForwardResult {
  total_windows: number;
  mean_in_sample_sharpe: number;
  mean_out_of_sample_sharpe: number;
  overall_walk_forward_efficiency: number;
  is_robust: boolean;
  windows: WalkForwardWindow[];
}

export default function ValidationPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState('');

  // DSR State
  const [observedSharpe, setObservedSharpe] = useState(1.8);
  const [trackLength, setTrackLength] = useState(252);
  const [numTrials, setNumTrials] = useState(25);
  const [skewness, setSkewness] = useState(-0.5);
  const [kurtosis, setKurtosis] = useState(1.2);
  const [dsrResult, setDsrResult] = useState<DSRResult | null>(null);

  // Walk Forward State
  const [wfTrainBars, setWfTrainBars] = useState(252);
  const [wfTestBars, setWfTestBars] = useState(63);
  const [wfResult, setWfResult] = useState<WalkForwardResult | null>(null);
  const [wfRunning, setWfRunning] = useState(false);

  useEffect(() => {
    api.get<Dataset[]>('/datasets')
      .then((data) => {
        setDatasets(data);
        if (data.length > 0) setSelectedDataset(data[0].id);
      })
      .catch((err) => console.error(err));
  }, []);

  // Compute DSR on parameter change
  const computeDSR = async () => {
    try {
      const res = await api.post<DSRResult>('/validation/deflated-sharpe', {
        observed_sharpe: Number(observedSharpe),
        track_length: Number(trackLength),
        skewness: Number(skewness),
        excess_kurtosis: Number(kurtosis),
        num_trials: Number(numTrials),
      });
      setDsrResult(res);
    } catch (err) {
      console.error('Failed to compute DSR:', err);
    }
  };

  useEffect(() => {
    computeDSR();
  }, [observedSharpe, trackLength, numTrials, skewness, kurtosis]);

  const handleRunWalkForward = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDataset) return;
    setWfRunning(true);
    try {
      const res = await api.post<WalkForwardResult>('/validation/walk-forward', {
        dataset_id: selectedDataset,
        strategy_type: 'MA_CROSSOVER',
        parameters: { fast_period: 10, slow_period: 30 },
        train_bars: Number(wfTrainBars),
        test_bars: Number(wfTestBars),
      });
      setWfResult(res);
    } catch (err) {
      console.error('Failed to run walk-forward:', err);
    } finally {
      setWfRunning(false);
    }
  };

  return (
    <Shell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5">
              <Activity className="w-5 h-5 text-accent" /> Statistical Validation & Bias Elimination Lab
            </h1>
            <p className="text-xs text-text-secondary mt-1">
              Deflated Sharpe Ratio (DSR), multiple-testing corrections, purged K-Fold cross-validation, and walk-forward efficiency.
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-1 rounded bg-financial-profitMuted text-financial-profit border border-financial-profit/30 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" /> P-Hacking Guard Active
          </span>
        </div>

        {/* Section 1: Deflated Sharpe Ratio Laboratory */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Controls */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-accent" />
                <span className="text-xs font-bold text-text-primary">DSR Parameters</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                label="Observed Sharpe Ratio"
                type="number"
                step="0.05"
                value={observedSharpe}
                onChange={(e) => setObservedSharpe(Number(e.target.value))}
              />
              <Input
                label="Track Length (Number of Bars)"
                type="number"
                value={trackLength}
                onChange={(e) => setTrackLength(Number(e.target.value))}
              />
              <Input
                label="Total Trials Tested (K Strategies / Params)"
                type="number"
                value={numTrials}
                onChange={(e) => setNumTrials(Number(e.target.value))}
              />
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Skewness"
                  type="number"
                  step="0.1"
                  value={skewness}
                  onChange={(e) => setSkewness(Number(e.target.value))}
                />
                <Input
                  label="Excess Kurtosis"
                  type="number"
                  step="0.1"
                  value={kurtosis}
                  onChange={(e) => setKurtosis(Number(e.target.value))}
                />
              </div>
            </CardContent>
          </Card>

          {/* DSR Results & Explanation */}
          <div className="lg:col-span-2 space-y-4">
            {dsrResult && (
              <Card>
                <CardHeader>
                  <span className="text-xs font-bold text-text-primary">
                    Deflated Sharpe Ratio Diagnostic (Bailey & López de Prado, 2014)
                  </span>
                  <Badge variant={dsrResult.is_statistically_significant ? 'profit' : 'loss'}>
                    {dsrResult.is_statistically_significant
                      ? 'GENUINE DISCOVERY (p < 0.05)'
                      : 'LIKELY FALSE DISCOVERY (p ≥ 0.05)'}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted">Observed SR</div>
                      <div className="text-base font-bold text-text-primary">{dsrResult.observed_sharpe}</div>
                    </div>
                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted">Required Hurdle SR*</div>
                      <div className="text-base font-bold text-financial-warning">
                        {dsrResult.expected_max_sharpe_hurdle}
                      </div>
                    </div>
                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted">Deflated SR Metric</div>
                      <div className="text-base font-bold text-accent">{dsrResult.deflated_sharpe_ratio}</div>
                    </div>
                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted">p-value</div>
                      <div
                        className={`text-base font-bold ${
                          dsrResult.is_statistically_significant ? 'text-financial-profit' : 'text-financial-loss'
                        }`}
                      >
                        {dsrResult.p_value}
                      </div>
                    </div>
                  </div>

                  <div className="bg-surface-elevated/30 p-3 rounded border border-border-subtle text-xs text-text-secondary leading-relaxed">
                    <p>
                      <strong>Statistical Interpretation:</strong> Because you tested{' '}
                      <span className="font-mono text-accent font-semibold">{dsrResult.num_trials_tested}</span> candidate
                      configurations, random chance alone produces an expected maximum Sharpe of{' '}
                      <span className="font-mono text-financial-warning font-semibold">
                        {dsrResult.expected_max_sharpe_hurdle}
                      </span>
                      . Your observed Sharpe of {dsrResult.observed_sharpe} has a p-value of {dsrResult.p_value}.
                      {!dsrResult.is_statistically_significant &&
                        ' This strategy fails the multiple-testing significance hurdle and should not be deployed.'}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Section 2: Walk-Forward Analysis Engine */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-accent" />
              <span className="text-xs font-bold text-text-primary">
                Out-of-Sample Walk-Forward Validation Engine
              </span>
            </div>
            <form onSubmit={handleRunWalkForward} className="flex items-center gap-3">
              <select
                className="px-2.5 py-1 text-xs bg-surface-elevated text-text-primary rounded border border-border-strong focus:outline-none"
                value={selectedDataset}
                onChange={(e) => setSelectedDataset(e.target.value)}
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.symbol} ({d.total_bars} bars)
                  </option>
                ))}
              </select>
              <Button size="sm" type="submit" isLoading={wfRunning} className="flex items-center gap-1.5">
                <Play className="w-3.5 h-3.5" /> Run Walk-Forward
              </Button>
            </form>
          </CardHeader>
          <CardContent>
            {!wfResult ? (
              <div className="py-8 text-center text-xs text-text-muted">
                Execute walk-forward analysis to compute in-sample vs out-of-sample efficiency.
              </div>
            ) : (
              <div className="space-y-4">
                {/* WFE Hero Banner */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div className="text-[10px] text-text-muted">Total Windows</div>
                    <div className="text-base font-bold text-text-primary">{wfResult.total_windows}</div>
                  </div>
                  <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div className="text-[10px] text-text-muted">Mean IS Sharpe</div>
                    <div className="text-base font-bold text-text-primary">{wfResult.mean_in_sample_sharpe}</div>
                  </div>
                  <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div className="text-[10px] text-text-muted">Mean OOS Sharpe</div>
                    <div className="text-base font-bold text-accent">{wfResult.mean_out_of_sample_sharpe}</div>
                  </div>
                  <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                    <div className="text-[10px] text-text-muted">Walk-Forward Efficiency</div>
                    <div
                      className={`text-base font-bold ${
                        wfResult.is_robust ? 'text-financial-profit' : 'text-financial-loss'
                      }`}
                    >
                      {(wfResult.overall_walk_forward_efficiency * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Windows Table */}
                <div className="overflow-x-auto max-h-56">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-surface-elevated text-text-secondary sticky top-0 border-b border-border-strong text-[11px]">
                      <tr>
                        <th className="p-2.5">Window</th>
                        <th className="p-2.5">In-Sample Period</th>
                        <th className="p-2.5">Out-of-Sample Period</th>
                        <th className="p-2.5 text-right">IS Sharpe</th>
                        <th className="p-2.5 text-right">OOS Sharpe</th>
                        <th className="p-2.5 text-right">WFE Ratio</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-subtle">
                      {wfResult.windows.map((w) => (
                        <tr key={w.window_index} className="hover:bg-surface-elevated/40 transition-colors">
                          <td className="p-2 text-text-primary">Window #{w.window_index}</td>
                          <td className="p-2 text-text-secondary text-[11px]">
                            {w.train_start.split('T')[0]} → {w.train_end.split('T')[0]}
                          </td>
                          <td className="p-2 text-text-secondary text-[11px]">
                            {w.test_start.split('T')[0]} → {w.test_end.split('T')[0]}
                          </td>
                          <td className="p-2 text-right tabular-nums">{w.sharpe_is.toFixed(2)}</td>
                          <td className="p-2 text-right tabular-nums text-accent">{w.sharpe_oos.toFixed(2)}</td>
                          <td
                            className={`p-2 text-right tabular-nums font-semibold ${
                              w.walk_forward_efficiency >= 0.5 ? 'text-financial-profit' : 'text-financial-loss'
                            }`}
                          >
                            {(w.walk_forward_efficiency * 100).toFixed(0)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Shell>
  );
}
