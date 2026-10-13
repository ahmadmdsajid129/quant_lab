'use client';

import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  FlaskConical,
  Play,
  RotateCcw,
  ShieldCheck,
  Hash,
  AlertTriangle,
  Clock,
  DollarSign,
  Percent,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface Project {
  id: string;
  title: string;
}

interface Dataset {
  id: string;
  symbol: string;
  total_bars: number;
}

interface EquityPoint {
  timestamp: string;
  equity: number;
  drawdown: number;
}

interface TradeLog {
  symbol: string;
  entry_time: string;
  exit_time: string;
  side: string;
  quantity: number;
  entry_price: number;
  exit_price: number;
  gross_pnl: number;
  fees: number;
  net_pnl: number;
  return_pct: number;
}

interface BacktestResult {
  experiment_id: string;
  project_id: string;
  dataset_id: string;
  strategy_type: string;
  status: string;
  lineage_hash: string;
  initial_capital: number;
  final_capital: number;
  total_fees_paid: number;
  metrics: {
    total_return: number;
    cagr: number;
    annualized_volatility: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown: number;
    calmar_ratio: number;
    var_95_daily: number;
    cvar_95_daily: number;
    trade_metrics: {
      total_trades: number;
      win_rate: number;
      profit_factor: number;
      avg_win: number;
      avg_loss: number;
      expectancy: number;
    };
  };
  equity_curve: EquityPoint[];
  trade_logs: TradeLog[];
}

export default function BacktestsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [selectedDataset, setSelectedDataset] = useState('');
  const [strategyType, setStrategyType] = useState('MA_CROSSOVER');

  // Strategy parameters
  const [fastPeriod, setFastPeriod] = useState(10);
  const [slowPeriod, setSlowPeriod] = useState(30);
  const [lookbackPeriod, setLookbackPeriod] = useState(60);
  const [mrWindow, setMrWindow] = useState(20);
  const [mrThreshold, setMrThreshold] = useState(2.0);

  // Execution assumptions
  const [capital, setCapital] = useState(100000.0);
  const [commissionBps, setCommissionBps] = useState(5.0);
  const [slippagePct, setSlippagePct] = useState(0.05);

  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);

  useEffect(() => {
    Promise.all([api.get<Project[]>('/projects'), api.get<Dataset[]>('/datasets')])
      .then(([projs, dsets]) => {
        setProjects(projs);
        setDatasets(dsets);
        if (projs.length > 0) setSelectedProject(projs[0].id);
        if (dsets.length > 0) setSelectedDataset(dsets[0].id);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProject || !selectedDataset) return;
    setRunning(true);

    const parameters: Record<string, any> = {};
    if (strategyType === 'MA_CROSSOVER') {
      parameters['fast_period'] = Number(fastPeriod);
      parameters['slow_period'] = Number(slowPeriod);
    } else if (strategyType === 'MOMENTUM') {
      parameters['lookback_period'] = Number(lookbackPeriod);
    } else if (strategyType === 'MEAN_REVERSION') {
      parameters['window'] = Number(mrWindow);
      parameters['entry_threshold'] = Number(mrThreshold);
    }

    try {
      const res = await api.post<BacktestResult>('/backtests/run', {
        project_id: selectedProject,
        dataset_id: selectedDataset,
        strategy_type: strategyType,
        parameters,
        initial_capital: Number(capital),
        commission_bps: Number(commissionBps),
        slippage_pct: Number(slippagePct),
      });
      setResult(res);
    } catch (err) {
      console.error('Failed to run backtest:', err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <Shell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5">
              <TrendingUp className="w-5 h-5 text-accent" /> Strategy Engine & Event-Driven Backtester
            </h1>
            <p className="text-xs text-text-secondary mt-1">
              Discrete time-state simulation, strict t+1 open execution, transaction cost attribution, and cryptographic lineage.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-mono px-2 py-1 rounded bg-financial-profitMuted text-financial-profit border border-financial-profit/30 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" /> No Look-Ahead Leakage
            </span>
          </div>
        </div>

        {/* 2-Column Workstation Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Configuration Console */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <FlaskConical className="w-4 h-4 text-accent" />
                  <span className="text-xs font-bold text-text-primary">Backtest Configuration</span>
                </div>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleRunBacktest} className="space-y-4">
                  {/* Project Selector */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-secondary">Research Project</label>
                    <select
                      className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent"
                      value={selectedProject}
                      onChange={(e) => setSelectedProject(e.target.value)}
                      required
                    >
                      {projects.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.title}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Dataset Selector */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-secondary">Historical Dataset</label>
                    <select
                      className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent"
                      value={selectedDataset}
                      onChange={(e) => setSelectedDataset(e.target.value)}
                      required
                    >
                      {datasets.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.symbol} ({d.total_bars} bars)
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Strategy Template */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-text-secondary">Strategy Model</label>
                    <select
                      className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent"
                      value={strategyType}
                      onChange={(e) => setStrategyType(e.target.value)}
                    >
                      <option value="MA_CROSSOVER">Moving Average Crossover (Trend)</option>
                      <option value="MOMENTUM">Rate-of-Change Momentum</option>
                      <option value="MEAN_REVERSION">Bollinger Z-Score Mean Reversion</option>
                      <option value="BUY_AND_HOLD">Buy & Hold (Passive Baseline)</option>
                    </select>
                  </div>

                  {/* Strategy Specific Parameters */}
                  {strategyType === 'MA_CROSSOVER' && (
                    <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border-subtle">
                      <Input
                        label="Fast SMA"
                        type="number"
                        value={fastPeriod}
                        onChange={(e) => setFastPeriod(Number(e.target.value))}
                        required
                      />
                      <Input
                        label="Slow SMA"
                        type="number"
                        value={slowPeriod}
                        onChange={(e) => setSlowPeriod(Number(e.target.value))}
                        required
                      />
                    </div>
                  )}

                  {strategyType === 'MOMENTUM' && (
                    <div className="pt-2 border-t border-border-subtle">
                      <Input
                        label="Lookback Bars"
                        type="number"
                        value={lookbackPeriod}
                        onChange={(e) => setLookbackPeriod(Number(e.target.value))}
                        required
                      />
                    </div>
                  )}

                  {strategyType === 'MEAN_REVERSION' && (
                    <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border-subtle">
                      <Input
                        label="Window"
                        type="number"
                        value={mrWindow}
                        onChange={(e) => setMrWindow(Number(e.target.value))}
                        required
                      />
                      <Input
                        label="Entry Z-Score"
                        type="number"
                        step="0.1"
                        value={mrThreshold}
                        onChange={(e) => setMrThreshold(Number(e.target.value))}
                        required
                      />
                    </div>
                  )}

                  {/* Capital & Execution Costs */}
                  <div className="space-y-3 pt-2 border-t border-border-subtle">
                    <Input
                      label="Initial Capital ($)"
                      type="number"
                      value={capital}
                      onChange={(e) => setCapital(Number(e.target.value))}
                      required
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        label="Commission (bps)"
                        type="number"
                        step="0.5"
                        value={commissionBps}
                        onChange={(e) => setCommissionBps(Number(e.target.value))}
                        required
                      />
                      <Input
                        label="Slippage (%)"
                        type="number"
                        step="0.01"
                        value={slippagePct}
                        onChange={(e) => setSlippagePct(Number(e.target.value))}
                        required
                      />
                    </div>
                  </div>

                  <Button type="submit" isLoading={running} className="w-full flex items-center justify-center gap-2">
                    <Play className="w-4 h-4" /> Run Event Backtest
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Tearsheet & Execution Results */}
          <div className="lg:col-span-2 space-y-6">
            {!result ? (
              <div className="bg-surface rounded-lg border border-border-subtle p-12 text-center">
                <TrendingUp className="w-10 h-10 text-text-muted mx-auto mb-3 opacity-50" />
                <h3 className="text-sm font-semibold text-text-primary mb-1">No Simulation Results Yet</h3>
                <p className="text-xs text-text-secondary max-w-sm mx-auto">
                  Configure strategy parameters and execute an event-driven backtest.
                </p>
              </div>
            ) : (
              <>
                {/* Result Hero Banner & Lineage */}
                <div className="bg-surface p-5 rounded-lg border border-border-subtle space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border-subtle pb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-text-primary">{result.strategy_type}</span>
                        <Badge variant="profit">COMPLETED</Badge>
                      </div>
                      <div className="text-[11px] font-mono text-text-muted flex items-center gap-1.5">
                        <Hash className="w-3.5 h-3.5 text-accent" />
                        <span>Lineage:</span>
                        <span className="text-accent truncate max-w-xs">{result.lineage_hash}</span>
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-[10px] text-text-muted">Final Equity</div>
                      <div className="text-lg font-bold text-text-primary">
                        ${result.final_capital.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                  </div>

                  {/* Metrics KPI Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted uppercase font-mono">Total Return</div>
                      <div
                        className={`text-base font-bold font-mono ${
                          result.metrics.total_return >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                        }`}
                      >
                        {(result.metrics.total_return * 100).toFixed(2)}%
                      </div>
                      <div className="text-[10px] text-text-muted font-mono">
                        CAGR: {(result.metrics.cagr * 100).toFixed(2)}%
                      </div>
                    </div>

                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted uppercase font-mono">Sharpe Ratio</div>
                      <div className="text-base font-bold font-mono text-accent">
                        {result.metrics.sharpe_ratio.toFixed(2)}
                      </div>
                      <div className="text-[10px] text-text-muted font-mono">
                        Sortino: {result.metrics.sortino_ratio.toFixed(2)}
                      </div>
                    </div>

                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted uppercase font-mono">Max Drawdown</div>
                      <div className="text-base font-bold font-mono text-financial-loss">
                        {(result.metrics.max_drawdown * 100).toFixed(2)}%
                      </div>
                      <div className="text-[10px] text-text-muted font-mono">
                        Calmar: {result.metrics.calmar_ratio.toFixed(2)}
                      </div>
                    </div>

                    <div className="bg-surface-elevated/40 p-3 rounded border border-border-subtle">
                      <div className="text-[10px] text-text-muted uppercase font-mono">Win Rate</div>
                      <div className="text-base font-bold font-mono text-financial-profit">
                        {(result.metrics.trade_metrics.win_rate * 100).toFixed(1)}%
                      </div>
                      <div className="text-[10px] text-text-muted font-mono">
                        Trades: {result.metrics.trade_metrics.total_trades}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Equity Curve SVG Visualization */}
                <Card>
                  <CardHeader>
                    <span className="text-xs font-bold text-text-primary">
                      Equity Curve Progression ({result.equity_curve.length} Timesteps)
                    </span>
                    <span className="text-[10px] font-mono text-text-muted">
                      Total Fees: ${result.total_fees_paid.toFixed(2)}
                    </span>
                  </CardHeader>
                  <CardContent>
                    <div className="h-44 w-full bg-surface-elevated/20 rounded border border-border-subtle p-3 flex flex-col justify-between">
                      {/* Interactive Canvas Bar representation */}
                      <div className="flex items-end gap-0.5 h-32 w-full">
                        {result.equity_curve.map((p, idx) => {
                          const minEq = result.initial_capital * 0.8;
                          const maxEq = Math.max(...result.equity_curve.map((e) => e.equity));
                          const heightPct = Math.max(
                            5,
                            Math.min(100, ((p.equity - minEq) / Math.max(1, maxEq - minEq)) * 100)
                          );
                          const isUnderwater = p.drawdown < -0.05;
                          return (
                            <div key={idx} className="flex-1 flex flex-col justify-end h-full group relative">
                              <div
                                style={{ height: `${heightPct}%` }}
                                className={`w-full rounded-t transition-all ${
                                  isUnderwater ? 'bg-financial-loss/60' : 'bg-accent/80 group-hover:bg-accent'
                                }`}
                              />
                            </div>
                          );
                        })}
                      </div>
                      <div className="flex items-center justify-between text-[10px] font-mono text-text-muted pt-2 border-t border-border-subtle">
                        <span>{result.equity_curve[0]?.timestamp.split('T')[0]}</span>
                        <span className="text-accent">Execution at t+1 Open</span>
                        <span>{result.equity_curve[result.equity_curve.length - 1]?.timestamp.split('T')[0]}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Trade Logs Table */}
                <Card>
                  <CardHeader>
                    <span className="text-xs font-bold text-text-primary">
                      Executed Trades Log ({result.trade_logs.length} trades)
                    </span>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto max-h-64">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-surface-elevated text-text-secondary sticky top-0 border-b border-border-strong text-[11px]">
                          <tr>
                            <th className="p-2.5">Entry</th>
                            <th className="p-2.5">Exit</th>
                            <th className="p-2.5">Side</th>
                            <th className="p-2.5 text-right">Qty</th>
                            <th className="p-2.5 text-right">Entry $</th>
                            <th className="p-2.5 text-right">Exit $</th>
                            <th className="p-2.5 text-right">Fees $</th>
                            <th className="p-2.5 text-right">Net PnL</th>
                            <th className="p-2.5 text-right">Return</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle">
                          {result.trade_logs.map((trade, idx) => (
                            <tr key={idx} className="hover:bg-surface-elevated/40 transition-colors">
                              <td className="p-2 text-text-secondary">{trade.entry_time.split('T')[0]}</td>
                              <td className="p-2 text-text-secondary">{trade.exit_time.split('T')[0]}</td>
                              <td className="p-2">
                                <Badge variant={trade.side === 'LONG' ? 'profit' : 'warning'} size="sm">
                                  {trade.side}
                                </Badge>
                              </td>
                              <td className="p-2 text-right tabular-nums">{trade.quantity.toFixed(2)}</td>
                              <td className="p-2 text-right tabular-nums text-text-muted">
                                ${trade.entry_price.toFixed(2)}
                              </td>
                              <td className="p-2 text-right tabular-nums text-text-muted">
                                ${trade.exit_price.toFixed(2)}
                              </td>
                              <td className="p-2 text-right tabular-nums text-financial-loss">
                                ${trade.fees.toFixed(2)}
                              </td>
                              <td
                                className={`p-2 text-right tabular-nums font-semibold ${
                                  trade.net_pnl >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                                }`}
                              >
                                ${trade.net_pnl.toFixed(2)}
                              </td>
                              <td
                                className={`p-2 text-right tabular-nums ${
                                  trade.return_pct >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                                }`}
                              >
                                {trade.return_pct.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
