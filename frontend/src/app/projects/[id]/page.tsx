'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  BookOpen,
  ArrowLeft,
  Plus,
  Tag,
  CheckCircle2,
  XCircle,
  HelpCircle,
  FileText,
  FlaskConical,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface Hypothesis {
  id: string;
  statement: string;
  mechanism: string;
  predicted_outcome: string;
  falsification_criteria: string;
  status: string;
  created_at: string;
}

interface ResearchNote {
  id: string;
  title: string;
  content: string;
  created_at: string;
}

interface ProjectDetail {
  id: string;
  title: string;
  description: string;
  asset_class: string;
  status: string;
  created_at: string;
  hypotheses: Hypothesis[];
  notes: ResearchNote[];
}

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'hypotheses' | 'notes'>('hypotheses');

  // Hypothesis modal
  const [isHypoModalOpen, setIsHypoModalOpen] = useState(false);
  const [statement, setStatement] = useState('');
  const [mechanism, setMechanism] = useState('');
  const [predictedOutcome, setPredictedOutcome] = useState('');
  const [falsification, setFalsification] = useState('');
  const [submittingHypo, setSubmittingHypo] = useState(false);

  // Note modal
  const [isNoteModalOpen, setIsNoteModalOpen] = useState(false);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);

  const fetchProject = async () => {
    try {
      const data = await api.get<ProjectDetail>(`/projects/${params.id}`);
      setProject(data);
    } catch (err) {
      console.error('Failed to fetch project detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProject();
  }, [params.id]);

  const handleCreateHypo = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingHypo(true);
    try {
      await api.post(`/projects/${params.id}/hypotheses`, {
        statement,
        mechanism,
        predicted_outcome: predictedOutcome,
        falsification_criteria: falsification,
      });
      setStatement('');
      setMechanism('');
      setPredictedOutcome('');
      setFalsification('');
      setIsHypoModalOpen(false);
      await fetchProject();
    } catch (err) {
      console.error('Failed to add hypothesis:', err);
    } finally {
      setSubmittingHypo(false);
    }
  };

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmittingNote(true);
    try {
      await api.post(`/projects/${params.id}/notes`, {
        title: noteTitle,
        content: noteContent,
      });
      setNoteTitle('');
      setNoteContent('');
      setIsNoteModalOpen(false);
      await fetchProject();
    } catch (err) {
      console.error('Failed to add note:', err);
    } finally {
      setSubmittingNote(false);
    }
  };

  if (loading) {
    return (
      <Shell>
        <div className="text-xs text-text-muted font-mono py-12 text-center">Loading project details...</div>
      </Shell>
    );
  }

  if (!project) {
    return (
      <Shell>
        <div className="p-8 text-center">
          <AlertTriangle className="w-8 h-8 text-financial-warning mx-auto mb-2" />
          <h2 className="text-sm font-semibold text-text-primary">Project Not Found</h2>
          <Link href="/projects" className="text-xs text-accent mt-2 inline-block">
            ← Return to Projects
          </Link>
        </div>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className="space-y-6">
        {/* Navigation Breadcrumb & Back */}
        <div className="flex items-center gap-3 text-xs text-text-secondary">
          <Link href="/projects" className="hover:text-accent flex items-center gap-1 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> All Projects
          </Link>
          <span>/</span>
          <span className="text-text-primary font-semibold">{project.title}</span>
        </div>

        {/* Project Header Banner */}
        <div className="bg-surface p-6 rounded-lg border border-border-subtle flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="accent">{project.asset_class}</Badge>
              <Badge variant="neutral">{project.status}</Badge>
            </div>
            <h1 className="text-xl font-bold text-text-primary tracking-tight">{project.title}</h1>
            <p className="text-xs text-text-secondary mt-1.5 max-w-2xl leading-relaxed">
              {project.description || 'No description provided.'}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Link href="/backtests">
              <Button size="sm" variant="outline" className="flex items-center gap-1.5">
                <FlaskConical className="w-4 h-4 text-accent" /> Run Backtest
              </Button>
            </Link>
            <Button
              size="sm"
              onClick={() => (activeTab === 'hypotheses' ? setIsHypoModalOpen(true) : setIsNoteModalOpen(true))}
              className="flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              {activeTab === 'hypotheses' ? 'Add Hypothesis' : 'Add Research Note'}
            </Button>
          </div>
        </div>

        {/* Workstation Tabs */}
        <div className="flex items-center gap-4 border-b border-border-subtle">
          <button
            onClick={() => setActiveTab('hypotheses')}
            className={`pb-2 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
              activeTab === 'hypotheses'
                ? 'border-accent text-accent'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" /> Hypotheses & Falsification ({project.hypotheses.length})
          </button>
          <button
            onClick={() => setActiveTab('notes')}
            className={`pb-2 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
              activeTab === 'notes'
                ? 'border-accent text-accent'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            <FileText className="w-3.5 h-3.5" /> Research Notes ({project.notes.length})
          </button>
        </div>

        {/* Tab 1: Hypotheses */}
        {activeTab === 'hypotheses' && (
          <div className="space-y-4">
            {project.hypotheses.length === 0 ? (
              <div className="bg-surface rounded-lg border border-border-subtle p-8 text-center">
                <HelpCircle className="w-8 h-8 text-text-muted mx-auto mb-2 opacity-50" />
                <h4 className="text-xs font-semibold text-text-primary mb-1">No Hypotheses Defined Yet</h4>
                <p className="text-[11px] text-text-secondary max-w-sm mx-auto mb-3">
                  Specify an explicit hypothesis with market mechanisms and falsification criteria.
                </p>
                <Button size="sm" onClick={() => setIsHypoModalOpen(true)}>
                  Formulate Hypothesis
                </Button>
              </div>
            ) : (
              project.hypotheses.map((h, i) => (
                <Card key={h.id} className="p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-border-subtle pb-3">
                    <span className="text-xs font-mono font-semibold text-accent">HYPOTHESIS #{i + 1}</span>
                    <Badge variant={h.status === 'SUPPORTED' ? 'profit' : h.status === 'FALSIFIED' ? 'loss' : 'neutral'}>
                      {h.status}
                    </Badge>
                  </div>
                  <div className="space-y-3 text-xs">
                    <div>
                      <span className="font-semibold text-text-primary block mb-1">Core Statement:</span>
                      <p className="text-text-secondary leading-relaxed bg-surface-elevated/60 p-2.5 rounded border border-border-strong/50">
                        {h.statement}
                      </p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <span className="font-semibold text-text-primary block mb-1">Underlying Market Mechanism:</span>
                        <p className="text-text-secondary leading-relaxed bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                          {h.mechanism}
                        </p>
                      </div>
                      <div>
                        <span className="font-semibold text-text-primary block mb-1">Predicted Outcome:</span>
                        <p className="text-text-secondary leading-relaxed bg-surface-elevated/40 p-2.5 rounded border border-border-subtle">
                          {h.predicted_outcome}
                        </p>
                      </div>
                    </div>
                    <div>
                      <span className="font-semibold text-financial-warning block mb-1 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-financial-warning" /> Falsification Criteria (When to Reject):
                      </span>
                      <p className="text-text-secondary leading-relaxed bg-surface-elevated/40 p-2.5 rounded border border-financial-warning/20">
                        {h.falsification_criteria}
                      </p>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {/* Tab 2: Research Notes */}
        {activeTab === 'notes' && (
          <div className="space-y-4">
            {project.notes.length === 0 ? (
              <div className="bg-surface rounded-lg border border-border-subtle p-8 text-center">
                <FileText className="w-8 h-8 text-text-muted mx-auto mb-2 opacity-50" />
                <h4 className="text-xs font-semibold text-text-primary mb-1">No Research Notes</h4>
                <p className="text-[11px] text-text-secondary max-w-sm mx-auto mb-3">
                  Document papers, findings, and qualitative observations in Markdown.
                </p>
                <Button size="sm" onClick={() => setIsNoteModalOpen(true)}>
                  Create Research Note
                </Button>
              </div>
            ) : (
              project.notes.map((n) => (
                <Card key={n.id} className="p-5">
                  <div className="flex items-center justify-between border-b border-border-subtle pb-2 mb-3">
                    <h3 className="text-xs font-bold text-text-primary">{n.title}</h3>
                    <span className="text-[10px] font-mono text-text-muted">
                      {new Date(n.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-xs text-text-secondary whitespace-pre-wrap leading-relaxed font-mono bg-surface-elevated/30 p-3 rounded">
                    {n.content}
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {/* Add Hypothesis Modal */}
        {isHypoModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-surface border border-border-strong rounded-lg max-w-lg w-full p-6 shadow-2xl">
              <h2 className="text-base font-bold text-text-primary mb-1">Formulate Scientific Hypothesis</h2>
              <p className="text-xs text-text-secondary mb-4">
                QuantLab mandates formal mechanisms and falsification criteria to prevent p-hacking.
              </p>
              <form onSubmit={handleCreateHypo} className="space-y-3">
                <Input
                  label="Hypothesis Statement"
                  placeholder="e.g. Assets with high 12m momentum outperform low momentum assets"
                  value={statement}
                  onChange={(e) => setStatement(e.target.value)}
                  required
                />
                <div className="space-y-1">
                  <label className="text-xs font-medium text-text-secondary">Market Mechanism (Why?)</label>
                  <textarea
                    className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent h-16"
                    placeholder="e.g. Underreaction to earnings announcements due to institutional latency"
                    value={mechanism}
                    onChange={(e) => setMechanism(e.target.value)}
                    required
                  />
                </div>
                <Input
                  label="Predicted Outcome"
                  placeholder="e.g. Sharpe ratio > 0.8 with CAGR > 8%"
                  value={predictedOutcome}
                  onChange={(e) => setPredictedOutcome(e.target.value)}
                  required
                />
                <div className="space-y-1">
                  <label className="text-xs font-medium text-financial-warning">
                    Falsification Criteria (When to Reject)
                  </label>
                  <textarea
                    className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-financial-warning/30 focus:outline-none focus:ring-1 focus:ring-accent h-16"
                    placeholder="e.g. Net Sharpe <= 0.2 after 10bps transaction costs or DSR p-value > 0.05"
                    value={falsification}
                    onChange={(e) => setFalsification(e.target.value)}
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button type="button" variant="ghost" onClick={() => setIsHypoModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" isLoading={submittingHypo}>
                    Save Hypothesis
                  </Button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Add Note Modal */}
        {isNoteModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-surface border border-border-strong rounded-lg max-w-md w-full p-6 shadow-2xl">
              <h2 className="text-base font-bold text-text-primary mb-1">Add Research Note</h2>
              <form onSubmit={handleCreateNote} className="space-y-3">
                <Input
                  label="Note Title"
                  placeholder="e.g. Literature Notes"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  required
                />
                <div className="space-y-1">
                  <label className="text-xs font-medium text-text-secondary">Content (Markdown)</label>
                  <textarea
                    className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent h-32 font-mono"
                    placeholder="Write research observations..."
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    required
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button type="button" variant="ghost" onClick={() => setIsNoteModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" isLoading={submittingNote}>
                    Save Note
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
