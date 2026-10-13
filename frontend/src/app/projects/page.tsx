'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { BookOpen, Plus, Tag, Calendar, Activity, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface Project {
  id: string;
  title: string;
  description: string;
  asset_class: string;
  status: string;
  created_at: string;
  hypotheses_count: number;
  experiments_count: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [assetClass, setAssetClass] = useState('EQUITIES');
  const [submitting, setSubmitting] = useState(false);

  const fetchProjects = async () => {
    try {
      const data = await api.get<Project[]>('/projects');
      setProjects(data);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      await api.post('/projects', {
        title,
        description,
        asset_class: assetClass,
      });
      setTitle('');
      setDescription('');
      setIsModalOpen(false);
      await fetchProjects();
    } catch (err) {
      console.error('Failed to create project:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'VALIDATED':
        return <Badge variant="profit">VALIDATED</Badge>;
      case 'REJECTED':
        return <Badge variant="loss">REJECTED</Badge>;
      case 'IN_PROGRESS':
        return <Badge variant="accent">IN PROGRESS</Badge>;
      default:
        return <Badge variant="neutral">DRAFT</Badge>;
    }
  };

  return (
    <Shell>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-5">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-text-primary flex items-center gap-2.5">
              <BookOpen className="w-5 h-5 text-accent" /> Research Projects & Hypotheses
            </h1>
            <p className="text-xs text-text-secondary mt-1">
              Scientific hypothesis management, economic mechanisms, falsification rules, and auditable research lineage.
            </p>
          </div>
          <Button onClick={() => setIsModalOpen(true)} className="flex items-center gap-1.5">
            <Plus className="w-4 h-4" /> New Research Project
          </Button>
        </div>

        {/* Project Grid */}
        {loading ? (
          <div className="text-xs text-text-muted font-mono py-12 text-center">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="bg-surface rounded-lg border border-border-subtle p-12 text-center">
            <BookOpen className="w-10 h-10 text-text-muted mx-auto mb-3 opacity-50" />
            <h3 className="text-sm font-semibold text-text-primary mb-1">No Research Projects Found</h3>
            <p className="text-xs text-text-secondary max-w-sm mx-auto mb-4">
              Formulate a structured hypothesis to test financial market mechanisms and run backtests.
            </p>
            <Button onClick={() => setIsModalOpen(true)} size="sm">
              Create First Project
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p) => (
              <Link key={p.id} href={`/projects/${p.id}`} className="group block">
                <Card className="h-full hover:border-accent transition-all duration-150 flex flex-col justify-between">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      <Tag className="w-3.5 h-3.5 text-accent" />
                      <span className="text-[11px] font-mono text-text-secondary uppercase">{p.asset_class}</span>
                    </div>
                    {getStatusBadge(p.status)}
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <h3 className="text-sm font-semibold text-text-primary group-hover:text-accent transition-colors line-clamp-1">
                      {p.title}
                    </h3>
                    <p className="text-xs text-text-secondary line-clamp-2 leading-relaxed">
                      {p.description || 'No description provided.'}
                    </p>
                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-border-subtle text-[11px] font-mono text-text-muted">
                      <div>
                        Hypotheses: <span className="text-text-primary font-semibold">{p.hypotheses_count}</span>
                      </div>
                      <div>
                        Experiments: <span className="text-text-primary font-semibold">{p.experiments_count}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}

        {/* Create Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-surface border border-border-strong rounded-lg max-w-md w-full p-6 shadow-2xl">
              <h2 className="text-base font-bold text-text-primary mb-1">New Research Project</h2>
              <p className="text-xs text-text-secondary mb-4">
                Define the asset class, hypothesis scope, and research objectives.
              </p>
              <form onSubmit={handleCreate} className="space-y-4">
                <Input
                  label="Project Title"
                  placeholder="e.g. Cross-Sectional Momentum in S&P 500"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-secondary">Asset Class</label>
                  <select
                    className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent"
                    value={assetClass}
                    onChange={(e) => setAssetClass(e.target.value)}
                  >
                    <option value="EQUITIES">Equities & ETFs</option>
                    <option value="CRYPTO">Cryptocurrency</option>
                    <option value="FX">Foreign Exchange</option>
                    <option value="DERIVATIVES">Options & Derivatives</option>
                    <option value="MULTI_ASSET">Multi-Asset</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-secondary">Research Description</label>
                  <textarea
                    className="w-full px-3 py-2 text-xs bg-surface-elevated text-text-primary rounded-md border border-border-strong focus:outline-none focus:ring-1 focus:ring-accent h-24"
                    placeholder="Describe the research objective, market anomaly, or expected behavior..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>
                <div className="flex justify-end gap-2 pt-2">
                  <Button type="button" variant="ghost" onClick={() => setIsModalOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" isLoading={submitting}>
                    Create Project
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
