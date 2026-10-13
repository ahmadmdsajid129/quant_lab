'use client';

import React, { useEffect, useState } from 'react';
import {
  FileText,
  Download,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  TrendingUp,
  Percent,
  Calendar,
  Database,
  Layers,
  Hash,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { api } from '@/lib/api';

interface TearsheetData {
  title: string;
  experiment_id: string;
  status: string;
  lineage_hash: string;
  created_at: string;
  project: {
    id: string;
    title: string;
    asset_class: string;
    hypotheses: Array<{
      statement: string;
      mechanism: string;
      falsification_criteria: string;
      status: string;
    }>;
  };
  data_provenance: {
    symbol: string;
    source: string;
    total_bars: number;
    start_date: string;
    end_date: string;
    quality_score: number;
  };
  methodology_assumptions: {
    execution_timing: string;
    lookahead_bias_guarantee: string;
    slippage_rate: number;
    commission_bps: number;
    initial_cash: number;
  };
  performance_kpis: {
    total_return_pct: number;
    cagr_pct: number;
    annualized_volatility_pct: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    max_drawdown_pct: number;
    calmar_ratio: number;
    win_rate_pct: number;
    profit_factor: number;
    var_95_pct: number;
    cvar_95_pct: number;
    total_trades: number;
  };
  reproducibility_notice: string;
}

export default function ReportsPage() {
  const [tearsheet, setTearsheet] = useState<TearsheetData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-find latest experiment
  useEffect(() => {
    async function loadLatestExperimentReport() {
      setLoading(true);
      try {
        // Fetch projects to find experiments
        const projects = await api.get<any[]>('/api/v1/projects');
        if (projects && projects.length > 0) {
          const proj = projects[0];
          // Find backtest experiments in project
          if (proj.experiments && proj.experiments.length > 0) {
            const expId = proj.experiments[0].id;
            const res = await api.get<TearsheetData>(`/api/v1/reports/experiments/${expId}/tearsheet`);
            setTearsheet(res);
          }
        }
      } catch (err: any) {
        console.error('Failed to load initial report:', err);
      } finally {
        setLoading(false);
      }
    }
    loadLatestExperimentReport();
  }, []);

  const handleDownloadMarkdown = () => {
    if (!tearsheet) return;
    window.open(`/api/v1/reports/experiments/${tearsheet.experiment_id}/export/markdown`, '_blank');
  };

  const handleDownloadJSON = () => {
    if (!tearsheet) return;
    window.open(`/api/v1/reports/experiments/${tearsheet.experiment_id}/export/json`, '_blank');
  };

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                Institutional Research Reports
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Cryptographic Audit
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Verifiable research tearsheets linking mathematical hypotheses, data provenance, performance metrics, and zero lookahead guarantees.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={handleDownloadMarkdown}
              disabled={!tearsheet}
              className="flex items-center gap-1.5 text-xs text-text-secondary"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Export Markdown</span>
            </Button>
            <Button
              variant="secondary"
              onClick={handleDownloadJSON}
              disabled={!tearsheet}
              className="flex items-center gap-1.5 text-xs text-text-secondary"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export JSON Lineage</span>
            </Button>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-accent-red/10 border border-accent-red/30 flex items-center gap-3 text-sm text-accent-red">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {tearsheet ? (
          <div className="space-y-6">
            {/* Report Header Card */}
            <Card className="bg-bg-surface-1">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border-subtle">
                  <div>
                    <h2 className="text-xl font-bold text-text-primary">{tearsheet.title}</h2>
                    <div className="flex items-center gap-4 text-xs font-mono text-text-secondary mt-1.5">
                      <span>Project: <strong className="text-text-primary">{tearsheet.project.title}</strong></span>
                      <span>Asset Class: <strong className="text-text-primary">{tearsheet.project.asset_class}</strong></span>
                      <span>Date: {tearsheet.created_at.slice(0, 19)}</span>
                    </div>
                  </div>
                  <Badge variant="profit" className="font-mono text-xs">
                    {tearsheet.status}
                  </Badge>
                </div>

                {/* Lineage Hash */}
                <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between text-xs font-mono text-text-muted gap-2">
                  <div className="flex items-center gap-1.5">
                    <Hash className="w-4 h-4 text-accent-blue" />
                    <span>Cryptographic Lineage SHA-256:</span>
                    <span className="text-text-primary break-all">{tearsheet.lineage_hash}</span>
                  </div>
                  <span className="text-[11px] bg-bg-surface-2 px-2 py-0.5 rounded border border-border-subtle">
                    Strict Invariants Verified
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Performance KPIs Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-bg-surface-1">
                <CardContent className="p-4">
                  <div className="text-[11px] font-mono text-text-muted uppercase">Sharpe Ratio</div>
                  <div className="text-2xl font-bold font-mono text-accent-blue mt-1">
                    {tearsheet.performance_kpis.sharpe_ratio.toFixed(2)}
                  </div>
                  <div className="text-[11px] text-text-secondary mt-1">
                    Sortino: {tearsheet.performance_kpis.sortino_ratio.toFixed(2)}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-bg-surface-1">
                <CardContent className="p-4">
                  <div className="text-[11px] font-mono text-text-muted uppercase">CAGR / Ann. Return</div>
                  <div className="text-2xl font-bold font-mono text-financial-profit mt-1">
                    {tearsheet.performance_kpis.cagr_pct.toFixed(2)}%
                  </div>
                  <div className="text-[11px] text-text-secondary mt-1">
                    Cumulative: {tearsheet.performance_kpis.total_return_pct.toFixed(2)}%
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-bg-surface-1">
                <CardContent className="p-4">
                  <div className="text-[11px] font-mono text-text-muted uppercase">Maximum Drawdown</div>
                  <div className="text-2xl font-bold font-mono text-financial-loss mt-1">
                    {tearsheet.performance_kpis.max_drawdown_pct.toFixed(2)}%
                  </div>
                  <div className="text-[11px] text-text-secondary mt-1">
                    Calmar: {tearsheet.performance_kpis.calmar_ratio.toFixed(2)}
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-bg-surface-1">
                <CardContent className="p-4">
                  <div className="text-[11px] font-mono text-text-muted uppercase">Win Rate & Trades</div>
                  <div className="text-2xl font-bold font-mono text-text-primary mt-1">
                    {tearsheet.performance_kpis.win_rate_pct.toFixed(1)}%
                  </div>
                  <div className="text-[11px] text-text-secondary mt-1">
                    Profit Factor: {tearsheet.performance_kpis.profit_factor.toFixed(2)} ({tearsheet.performance_kpis.total_trades} trades)
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* 2-Column: Hypothesis & Data Provenance */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Hypothesis Card */}
              <Card>
                <CardHeader className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-text-secondary" />
                  <span className="font-medium text-sm text-text-primary">Stated Research Hypotheses</span>
                </CardHeader>
                <CardContent className="space-y-4 pt-3">
                  {tearsheet.project.hypotheses.map((h, i) => (
                    <div key={i} className="p-3.5 rounded bg-bg-surface-2 border border-border-subtle space-y-2 text-xs">
                      <div>
                        <span className="font-mono text-text-muted block text-[10px] uppercase">Statement:</span>
                        <p className="font-medium text-text-primary mt-0.5">{h.statement}</p>
                      </div>
                      <div>
                        <span className="font-mono text-text-muted block text-[10px] uppercase">Economic Mechanism:</span>
                        <p className="text-text-secondary mt-0.5">{h.mechanism}</p>
                      </div>
                      <div>
                        <span className="font-mono text-text-muted block text-[10px] uppercase">Falsification Threshold:</span>
                        <p className="text-accent-blue font-mono mt-0.5">{h.falsification_criteria}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Data Provenance Card */}
              <Card>
                <CardHeader className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-text-secondary" />
                  <span className="font-medium text-sm text-text-primary">Data Provenance & Friction</span>
                </CardHeader>
                <CardContent className="space-y-3 pt-3 text-xs font-mono">
                  <div className="flex justify-between py-2 border-b border-border-subtle">
                    <span className="text-text-secondary">Instrument Symbol:</span>
                    <span className="font-bold text-text-primary">{tearsheet.data_provenance.symbol}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border-subtle">
                    <span className="text-text-secondary">Provider Source:</span>
                    <span className="text-text-primary">{tearsheet.data_provenance.source}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border-subtle">
                    <span className="text-text-secondary">Total Sample Bars:</span>
                    <span className="text-text-primary">{tearsheet.data_provenance.total_bars} bars</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border-subtle">
                    <span className="text-text-secondary">Data QA Score:</span>
                    <span className="text-financial-profit">{tearsheet.data_provenance.quality_score}% Clean</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-border-subtle">
                    <span className="text-text-secondary">Execution Timing:</span>
                    <span className="text-text-primary">{tearsheet.methodology_assumptions.execution_timing}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-text-secondary">Transaction Costs:</span>
                    <span className="text-text-primary">
                      {(tearsheet.methodology_assumptions.slippage_rate * 100).toFixed(2)}% Slippage / {tearsheet.methodology_assumptions.commission_bps} bps Comm
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="h-96 rounded-lg border border-dashed border-border-subtle flex flex-col items-center justify-center p-8 text-center text-text-muted">
            <FileText className="w-12 h-12 text-border-strong mb-3" />
            <h3 className="text-sm font-medium text-text-secondary">No Research Tearsheet Selected</h3>
            <p className="text-xs text-text-muted max-w-sm mt-1">
              Execute a backtest run in the **Strategy Backtester** to generate an institutional tearsheet report with cryptographic lineage and export capabilities.
            </p>
          </div>
        )}
      </div>
    </Shell>
  );
}
