'use client';

import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Plus,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  Database,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface QualityAudit {
  score: number;
  status: string;
  total_bars: number;
  violations_count: number;
  issues: string[];
  metrics: {
    min_close: number;
    max_close: number;
    mean_volume: number;
    start_timestamp: string;
    end_timestamp: string;
  };
}

interface Dataset {
  id: string;
  symbol: string;
  name: string;
  source: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  total_bars: number;
  quality_score: number;
  quality_audit: QualityAudit;
  created_at: string;
}

interface OHLCVBar {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  vwap?: number;
}

export default function DataBrowserPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [bars, setBars] = useState<OHLCVBar[]>([]);
  const [loading, setLoading] = useState(true);
  const [barsLoading, setBarsLoading] = useState(false);

  // Synthetic Generator Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [symbol, setSymbol] = useState('SPY-SYNTH');
  const [periods, setPeriods] = useState(504);
  const [initialPrice, setInitialPrice] = useState(100.0);
  const [drift, setDrift] = useState(0.08);
  const [volatility, setVolatility] = useState(0.20);
  const [seed, setSeed] = useState(42);
  const [generating, setGenerating] = useState(false);

  const fetchDatasets = async () => {
    try {
      const data = await api.get<Dataset[]>('/datasets');
      setDatasets(data);
      if (data.length > 0 && !selectedDataset) {
        selectDataset(data[0]);
      }
    } catch (err) {
      console.error('Failed to load datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectDataset = async (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setBarsLoading(true);
    try {
      const data = await api.get<OHLCVBar[]>(`/datasets/${dataset.id}/ohlcv?limit=100`);
      setBars(data);
    } catch (err) {
      console.error('Failed to load OHLCV bars:', err);
    } finally {
      setBarsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const newDs = await api.post<Dataset>('/datasets/generate-synthetic', {
        symbol,
        periods: Number(periods),
        initial_price: Number(initialPrice),
        annual_drift: Number(drift),
        annual_volatility: Number(volatility),
        seed: Number(seed),
      });
      setIsModalOpen(false);
      await fetchDatasets();
      selectDataset(newDs);
    } catch (err) {
      console.error('Failed to generate synthetic data:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Shell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5">
              <Database className="w-5 h-5 text-accent" /> Market Data Infrastructure & Ingestion
            </h1>
            <p className="text-xs text-text-secondary mt-1">
              Columnar Parquet storage, automated 5-point data quality audits, and reproducible jump-diffusion generators.
            </p>
          </div>
          <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-1.5">
            <Sparkles className="w-4 h-4" /> Generate Synthetic Dataset
          </Button>
        </div>

        {/* Workstation 2-Column Split */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Datasets Catalog */}
          <div className="space-y-3">
            <div className="text-xs font-semibold uppercase tracking-wider text-text-secondary flex items-center justify-between">
              <span>Catalog ({datasets.length})</span>
              <span className="text-[10px] text-text-muted font-mono">Columnar Parquet</span>
            </div>

            {loading ? (
              <div className="text-xs text-text-muted font-mono py-8 text-center">Loading datasets...</div>
            ) : datasets.length === 0 ? (
              <div className="bg-surface rounded-lg border border-border-subtle p-6 text-center">
                <Database className="w-8 h-8 text-text-muted mx-auto mb-2 opacity-50" />
                <p className="text-xs text-text-secondary mb-3">No datasets imported yet.</p>
                <Button size="sm" onClick={() => setIsModalOpen(true)}>
                  Generate Sample
                </Button>
              </div>
            ) : (
              <div className="space-y-2">
                {datasets.map((d) => (
                  <div
                    key={d.id}
                    onClick={() => selectDataset(d)}
                    className={`p-3.5 rounded-lg border cursor-pointer transition-all duration-150 ${
                      selectedDataset?.id === d.id
                        ? 'bg-surface-elevated border-accent shadow-md'
                        : 'bg-surface border-border-subtle hover:border-border-strong'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-mono font-bold text-text-primary">{d.symbol}</span>
                      <Badge
                        variant={d.quality_score >= 90 ? 'profit' : d.quality_score >= 60 ? 'warning' : 'loss'}
                        size="sm"
                      >
                        QA: {d.quality_score}%
                      </Badge>
                    </div>
                    <div className="text-[11px] text-text-secondary truncate mb-2">{d.name}</div>
                    <div className="flex items-center justify-between text-[10px] font-mono text-text-muted">
                      <span>{d.total_bars} bars</span>
                      <span>{d.source}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Right Column: Selected Dataset Inspector & Quality Report */}
          <div className="lg:col-span-2 space-y-6">
            {selectedDataset ? (
              <>
                {/* Dataset Overview Card */}
                <Card>
                  <CardHeader>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold font-mono text-text-primary">
                          {selectedDataset.symbol}
                        </span>
                        <Badge variant="accent">{selectedDataset.timeframe}</Badge>
                        <Badge variant="neutral">{selectedDataset.source}</Badge>
                      </div>
                      <div className="text-xs text-text-secondary">{selectedDataset.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-[11px] text-text-muted font-mono">Quality Score</div>
                      <div className="text-lg font-bold font-mono text-financial-profit">
                        {selectedDataset.quality_score}%
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                      <div className="bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                        <div className="text-[10px] text-text-muted">Total Bars</div>
                        <div className="font-semibold text-text-primary">{selectedDataset.total_bars}</div>
                      </div>
                      <div className="bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                        <div className="text-[10px] text-text-muted">Start Date</div>
                        <div className="font-semibold text-text-primary">
                          {new Date(selectedDataset.start_date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                        <div className="text-[10px] text-text-muted">End Date</div>
                        <div className="font-semibold text-text-primary">
                          {new Date(selectedDataset.end_date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                        <div className="text-[10px] text-text-muted">QA Status</div>
                        <div className="font-semibold text-financial-profit">
                          {selectedDataset.quality_audit.status}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* 5-Point Quality Audit Report Card */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-accent" />
                      <span className="text-xs font-bold text-text-primary">
                        5-Point Automated Data Quality Audit
                      </span>
                    </div>
                    <Badge variant={selectedDataset.quality_audit.violations_count === 0 ? 'profit' : 'warning'}>
                      {selectedDataset.quality_audit.violations_count} Violations
                    </Badge>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                      <div className="flex items-center gap-2 p-2 rounded bg-surface-elevated/30 border border-border-subtle">
                        <CheckCircle className="w-4 h-4 text-financial-profit shrink-0" />
                        <div>
                          <span className="font-semibold text-text-primary">Price Sanity Invariants:</span>
                          <span className="text-text-muted block text-[11px]">High ≥ max(O,C) & Low ≤ min(O,C)</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-2 rounded bg-surface-elevated/30 border border-border-subtle">
                        <CheckCircle className="w-4 h-4 text-financial-profit shrink-0" />
                        <div>
                          <span className="font-semibold text-text-primary">Volume & Prices Non-Zero:</span>
                          <span className="text-text-muted block text-[11px]">Zero negative prices/volumes</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-2 rounded bg-surface-elevated/30 border border-border-subtle">
                        <CheckCircle className="w-4 h-4 text-financial-profit shrink-0" />
                        <div>
                          <span className="font-semibold text-text-primary">Return Jump Anomaly Check:</span>
                          <span className="text-text-muted block text-[11px]">No single-day jumps &gt; 50%</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 p-2 rounded bg-surface-elevated/30 border border-border-subtle">
                        <CheckCircle className="w-4 h-4 text-financial-profit shrink-0" />
                        <div>
                          <span className="font-semibold text-text-primary">Timestamp Continuity:</span>
                          <span className="text-text-muted block text-[11px]">No duplicate timestamps</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* OHLCV Bars Table */}
                <Card>
                  <CardHeader>
                    <span className="text-xs font-bold text-text-primary">
                      Recent OHLCV Bars ({bars.length} loaded from Parquet)
                    </span>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto max-h-72">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-surface-elevated text-text-secondary sticky top-0 border-b border-border-strong text-[11px]">
                          <tr>
                            <th className="p-2.5">Date</th>
                            <th className="p-2.5 text-right">Open</th>
                            <th className="p-2.5 text-right">High</th>
                            <th className="p-2.5 text-right">Low</th>
                            <th className="p-2.5 text-right">Close</th>
                            <th className="p-2.5 text-right">Volume</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle">
                          {bars.map((bar, idx) => (
                            <tr key={idx} className="hover:bg-surface-elevated/50 transition-colors">
                              <td className="p-2 text-text-secondary">
                                {new Date(bar.timestamp).toLocaleDateString()}
                              </td>
                              <td className="p-2 text-right tabular-nums text-text-primary">{bar.open.toFixed(2)}</td>
                              <td className="p-2 text-right tabular-nums text-text-primary">{bar.high.toFixed(2)}</td>
                              <td className="p-2 text-right tabular-nums text-text-primary">{bar.low.toFixed(2)}</td>
                              <td
                                className={`p-2 text-right tabular-nums font-semibold ${
                                  bar.close >= bar.open ? 'text-financial-profit' : 'text-financial-loss'
                                }`}
                              >
                                {bar.close.toFixed(2)}
                              </td>
                              <td className="p-2 text-right tabular-nums text-text-muted">
                                {bar.volume.toLocaleString()}
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
              <div className="bg-surface rounded-lg border border-border-subtle p-12 text-center text-xs text-text-secondary">
                Select a dataset from the catalog to inspect.
              </div>
            )}
          </div>
        </div>

        {/* Synthetic Generator Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-surface border border-border-strong rounded-lg max-w-md w-full p-6 shadow-2xl">
              <h2 className="text-base font-bold text-text-primary mb-1">
                Deterministic Jump-Diffusion Generator
              </h2>
              <p className="text-xs text-text-secondary mb-4">
                Generates verifiable stochastic price paths with guaranteed seed reproducibility.
              </p>
              <form onSubmit={handleGenerate} className="space-y-3">
                <Input
                  label="Symbol Identifier"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  required
                />
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Trading Bars (Periods)"
                    type="number"
                    value={periods}
                    onChange={(e) => setPeriods(Number(e.target.value))}
                    required
                  />
                  <Input
                    label="Initial Price ($)"
                    type="number"
                    step="0.1"
                    value={initialPrice}
                    onChange={(e) => setInitialPrice(Number(e.target.value))}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    label="Annual Drift (mu)"
                    type="number"
                    step="0.01"
                    value={drift}
                    onChange={(e) => setDrift(Number(e.target.value))}
                    required
                  />
                  <Input
                    label="Annual Vol (sigma)"
                    type="number"
                    step="0.01"
                    value={volatility}
                    onChange={(e) => setVolatility(Number(e.target.value))}
                    required
                  />
                </div>
                <Input
                  label="Deterministic Random Seed"
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(Number(e.target.value))}
                  required
                />
                <div className="flex justify-end gap-2 pt-3">
                  <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" isLoading={generating}>
                    Generate Dataset
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}
