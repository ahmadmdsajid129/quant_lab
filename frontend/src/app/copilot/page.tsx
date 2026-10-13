'use client';

import React, { useState } from 'react';
import {
  Zap,
  Send,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  Sparkles,
  BookOpen,
  LineChart,
  Bot,
  User as UserIcon,
  HelpCircle,
  FileText,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface GroundedArtifacts {
  verified_results: string[];
  statistical_inferences: string[];
  hypotheses: string[];
}

interface ChatMessage {
  sender: 'user' | 'assistant';
  content: string;
  artifacts?: GroundedArtifacts;
}

interface FindingDetail {
  category: string;
  severity: string;
  title: string;
  description: string;
}

interface AuditResult {
  is_methodologically_sound: boolean;
  methodology_health_score: number;
  severity_summary: Record<string, number>;
  findings: FindingDetail[];
  recommended_next_experiments: string[];
}

export default function CopilotPage() {
  // Chat state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      content:
        'Welcome to the **QuantLab AI Research Copilot**.\n\nI am grounded in your workspace\'s active hypotheses, datasets, and backtest logs. How can I assist your quantitative workflow today?',
    },
  ]);
  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [loadingChat, setLoadingChat] = useState<boolean>(false);

  // Methodology Auditor state
  const [strategyDesc, setStrategyDesc] = useState<string>('Dual Moving Average Crossover (20d / 50d)');
  const [slippagePct, setSlippagePct] = useState<number>(0.0005);
  const [commissionBps, setCommissionBps] = useState<number>(2.5);
  const [numTrials, setNumTrials] = useState<number>(5);
  const [reportedSharpe, setReportedSharpe] = useState<number>(1.45);
  const [isNextBarOpen, setIsNextBarOpen] = useState<boolean>(true);
  const [isChronological, setIsChronological] = useState<boolean>(true);

  const [loadingAudit, setLoadingAudit] = useState<boolean>(false);
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);

  const handleSendMessage = async (textToSend?: string) => {
    const prompt = textToSend || inputPrompt;
    if (!prompt.trim()) return;

    const newMessages: ChatMessage[] = [...messages, { sender: 'user', content: prompt }];
    setMessages(newMessages);
    setInputPrompt('');
    setLoadingChat(true);

    try {
      const res = await api.post<{
        response: string;
        grounded_artifacts: GroundedArtifacts;
      }>('/api/v1/copilot/chat', { prompt });

      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          content: res.response,
          artifacts: res.grounded_artifacts,
        },
      ]);
    } catch (err: any) {
      setMessages([
        ...newMessages,
        {
          sender: 'assistant',
          content: `⚠️ Failed to retrieve grounded response: ${err.message || 'Unknown error'}`,
        },
      ]);
    } finally {
      setLoadingChat(false);
    }
  };

  const handleAudit = async () => {
    setLoadingAudit(true);
    try {
      const res = await api.post<AuditResult>('/api/v1/copilot/audit-methodology', {
        strategy_description: strategyDesc,
        slippage_pct: slippagePct,
        commission_bps: commissionBps,
        num_trials_tested: numTrials,
        reported_sharpe: reportedSharpe,
        uses_chronological_split: isChronological,
        execution_at_next_bar_open: isNextBarOpen,
      });
      setAuditResult(res);
    } catch (err: any) {
      console.error('Audit failed:', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  const suggestedPrompts = [
    'Audit my methodology for lookahead bias and cost realism',
    'Review active hypotheses and falsification criteria',
    'Suggest a feature engineering pipeline for time series',
    'Interpret my latest backtest Sharpe and Drawdown',
  ];

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                AI Research Copilot
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Artifact-Grounded
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Evidence-based quantitative assistant grounded in real workspace hypotheses, execution logs, and automated methodology auditing.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <ShieldCheck className="w-4 h-4 text-accent-green" />
              <span>Grounded in Workspace Lineage</span>
            </div>
          </div>
        </div>

        {/* 2-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Interactive Chat (7 cols) */}
          <div className="lg:col-span-7 space-y-4 flex flex-col h-[750px]">
            {/* Messages Scroll Area */}
            <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-lg bg-bg-surface-1 border border-border-subtle">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex gap-3 text-sm ${
                    msg.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {msg.sender === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center shrink-0 text-accent">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-lg p-4 space-y-3 ${
                      msg.sender === 'user'
                        ? 'bg-accent-blue text-white'
                        : 'bg-bg-surface-2 border border-border-subtle text-text-primary'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-xs leading-relaxed font-sans">
                      {msg.content}
                    </div>

                    {/* Cited Artifacts Badge Drawer */}
                    {msg.artifacts && (
                      <div className="pt-2 border-t border-border-subtle/60 space-y-1.5">
                        <div className="text-[10px] font-mono text-text-muted uppercase">
                          Citing Verified Artifacts:
                        </div>
                        {msg.artifacts.verified_results.map((res, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-[11px] text-financial-profit font-mono">
                            <CheckCircle2 className="w-3 h-3 shrink-0" />
                            <span>{res}</span>
                          </div>
                        ))}
                        {msg.artifacts.hypotheses.map((h, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-[11px] text-accent-blue font-mono">
                            <FileText className="w-3 h-3 shrink-0" />
                            <span>{h}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {msg.sender === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-bg-surface-2 border border-border-subtle flex items-center justify-center shrink-0 text-text-secondary">
                      <UserIcon className="w-4 h-4" />
                    </div>
                  )}
                </div>
              ))}
              {loadingChat && (
                <div className="flex gap-3 text-sm">
                  <div className="w-8 h-8 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center text-accent animate-spin">
                    <RotateCcw className="w-4 h-4" />
                  </div>
                  <div className="bg-bg-surface-2 border border-border-subtle rounded-lg p-3 text-xs text-text-muted">
                    Retrieving workspace artifacts and synthesizing grounded response...
                  </div>
                </div>
              )}
            </div>

            {/* Suggested Prompt Chips */}
            <div className="flex flex-wrap gap-1.5">
              {suggestedPrompts.map((p, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSendMessage(p)}
                  className="px-2.5 py-1 rounded-full bg-bg-surface-2 hover:bg-bg-surface-1 border border-border-subtle text-[11px] text-text-secondary transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <div className="flex gap-2">
              <Input
                placeholder="Ask about hypotheses, backtests, or feature pipelines..."
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <Button onClick={() => handleSendMessage()} disabled={loadingChat || !inputPrompt.trim()}>
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Right Column: Research Methodology Auditor (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            <Card>
              <CardHeader className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Methodology Health Auditor</span>
              </CardHeader>
              <CardContent className="space-y-4 pt-3">
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                    Strategy Description
                  </label>
                  <Input
                    type="text"
                    value={strategyDesc}
                    onChange={(e) => setStrategyDesc(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Slippage (%)
                    </label>
                    <Input
                      type="number"
                      step="0.0001"
                      value={slippagePct}
                      onChange={(e) => setSlippagePct(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Commission (bps)
                    </label>
                    <Input
                      type="number"
                      step="0.5"
                      value={commissionBps}
                      onChange={(e) => setCommissionBps(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Trials Tested (K)
                    </label>
                    <Input
                      type="number"
                      value={numTrials}
                      onChange={(e) => setNumTrials(parseInt(e.target.value) || 1)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Reported Sharpe
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      value={reportedSharpe}
                      onChange={(e) => setReportedSharpe(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                {/* Invariant Switches */}
                <div className="space-y-2 pt-2 border-t border-border-subtle text-xs">
                  <label className="flex items-center justify-between cursor-pointer">
                    <span className="text-text-secondary">Execution Timing:</span>
                    <button
                      type="button"
                      onClick={() => setIsNextBarOpen(!isNextBarOpen)}
                      className={`px-2 py-0.5 rounded font-mono text-[10px] font-medium border ${
                        isNextBarOpen
                          ? 'bg-financial-profitMuted text-financial-profit border-financial-profit/30'
                          : 'bg-financial-lossMuted text-financial-loss border-financial-loss/30'
                      }`}
                    >
                      {isNextBarOpen ? 'Next-Bar Open (Valid)' : 'Same-Bar Close (Lookahead)'}
                    </button>
                  </label>

                  <label className="flex items-center justify-between cursor-pointer">
                    <span className="text-text-secondary">Data Split Partition:</span>
                    <button
                      type="button"
                      onClick={() => setIsChronological(!isChronological)}
                      className={`px-2 py-0.5 rounded font-mono text-[10px] font-medium border ${
                        isChronological
                          ? 'bg-financial-profitMuted text-financial-profit border-financial-profit/30'
                          : 'bg-financial-lossMuted text-financial-loss border-financial-loss/30'
                      }`}
                    >
                      {isChronological ? 'Chronological (Valid)' : 'Random K-Fold (Leakage)'}
                    </button>
                  </label>
                </div>

                <Button
                  onClick={handleAudit}
                  disabled={loadingAudit}
                  className="w-full mt-2 flex items-center justify-center gap-2"
                >
                  {loadingAudit ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Auditing Methodology...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Audit Methodology Health</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Audit Results Panel */}
            {auditResult && (
              <Card>
                <CardHeader className="flex items-center justify-between">
                  <span className="font-medium text-sm text-text-primary">Audit Diagnostic Report</span>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-text-muted">Health Score:</span>
                    <Badge
                      variant={
                        auditResult.methodology_health_score >= 80
                          ? 'profit'
                          : auditResult.methodology_health_score >= 50
                          ? 'warning'
                          : 'loss'
                      }
                      className="font-mono text-xs"
                    >
                      {auditResult.methodology_health_score} / 100
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3 pt-3">
                  {auditResult.findings.length === 0 ? (
                    <div className="p-3 rounded bg-accent-green/10 border border-accent-green/30 text-xs text-accent-green flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>Zero methodological biases detected. Research setup adheres to institutional rigor.</span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {auditResult.findings.map((f, i) => (
                        <div
                          key={i}
                          className={`p-3 rounded border text-xs space-y-1 ${
                            f.severity === 'HIGH'
                              ? 'bg-accent-red/10 border-accent-red/30'
                              : 'bg-accent-amber/10 border-accent-amber/30'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-text-primary">{f.title}</span>
                            <span
                              className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold ${
                                f.severity === 'HIGH' ? 'text-accent-red' : 'text-accent-amber'
                              }`}
                            >
                              {f.severity}
                            </span>
                          </div>
                          <p className="text-text-secondary text-[11px]">{f.description}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Recommended Next Experiments */}
                  <div className="pt-2 border-t border-border-subtle">
                    <div className="text-[11px] font-mono text-text-muted uppercase mb-1.5">
                      Recommended Next Actions:
                    </div>
                    <ul className="space-y-1 text-xs text-text-secondary list-disc pl-4">
                      {auditResult.recommended_next_experiments.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
