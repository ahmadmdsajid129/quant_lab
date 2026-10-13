'use client';

import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Activity,
  Cpu,
  Database,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Ban,
  Layers,
  HardDrive,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { api } from '@/lib/api';

interface JobItem {
  id: string;
  job_type: string;
  status: string;
  progress: number;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

interface TelemetryData {
  system_status: string;
  database_status: string;
  active_worker_threads: number;
  queue_backlog: number;
  total_completed_jobs: number;
  uptime_seconds: number;
  memory_usage_mb: number;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
  const [loading, setLoading] = useState(false);
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [jobsData, telemData] = await Promise.all([
        api.get<JobItem[]>('/api/v1/jobs'),
        api.get<TelemetryData>('/api/v1/jobs/telemetry'),
      ]);
      setJobs(jobsData || []);
      setTelemetry(telemData || null);
    } catch (err: any) {
      console.error('Failed to load telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // 10s auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleCancelJob = async (jobId: string) => {
    setCancellingId(jobId);
    try {
      await api.post(`/api/v1/jobs/${jobId}/cancel`);
      await loadData();
    } catch (err: any) {
      alert(`Failed to cancel job: ${err.message || 'Unknown error'}`);
    } finally {
      setCancellingId(null);
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
                Operational Telemetry & Job Monitoring
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Process Observability
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Real-time monitoring of asynchronous worker threads, queue backlogs, memory footprint, and compute job lifecycles.
            </p>
          </div>

          <Button
            variant="secondary"
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-1.5 text-xs text-text-secondary"
          >
            <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Telemetry</span>
          </Button>
        </div>

        {/* Telemetry KPI Grid */}
        {telemetry && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">System Status</div>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className={`w-2 h-2 rounded-full ${
                    telemetry.system_status === 'HEALTHY' ? 'bg-accent-green' : 'bg-accent-red'
                  }`} />
                  <span className="text-base font-bold font-mono text-text-primary">
                    {telemetry.system_status}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">Database Connection</div>
                <div className="text-base font-bold font-mono text-accent-blue mt-1">
                  {telemetry.database_status}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">Memory (RSS)</div>
                <div className="text-base font-bold font-mono text-text-primary mt-1">
                  {telemetry.memory_usage_mb.toFixed(1)} MB
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">Worker Pool</div>
                <div className="text-base font-bold font-mono text-text-primary mt-1">
                  {telemetry.active_worker_threads} Threads
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">Queue Backlog</div>
                <div className="text-base font-bold font-mono text-text-primary mt-1">
                  {telemetry.queue_backlog} Pending
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[10px] font-mono text-text-muted uppercase">System Uptime</div>
                <div className="text-base font-bold font-mono text-text-primary mt-1">
                  {(telemetry.uptime_seconds / 60).toFixed(1)} mins
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Jobs Blotter Table */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-text-secondary" />
              <span className="font-medium text-sm text-text-primary">Background Execution Task Queue</span>
            </div>
            <Badge variant="neutral" className="text-xs font-mono">
              {jobs.length} Active Records
            </Badge>
          </CardHeader>
          <CardContent className="pt-2">
            {jobs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-border-subtle text-text-muted uppercase text-[11px]">
                      <th className="py-2.5 px-3">Job ID</th>
                      <th className="py-2.5 px-3">Task Type</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Progress</th>
                      <th className="py-2.5 px-3">Queued At</th>
                      <th className="py-2.5 px-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle/50">
                    {jobs.map((j) => (
                      <tr key={j.id} className="hover:bg-bg-surface-2/40">
                        <td className="py-2.5 px-3 text-text-muted font-mono">{j.id.slice(0, 8)}...</td>
                        <td className="py-2.5 px-3 font-semibold text-text-primary">{j.job_type}</td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            j.status === 'COMPLETED'
                              ? 'bg-accent-green/10 text-accent-green border border-accent-green/30'
                              : j.status === 'RUNNING'
                              ? 'bg-accent-blue/10 text-accent-blue border border-accent-blue/30'
                              : j.status === 'CANCELLED'
                              ? 'bg-bg-surface-2 text-text-muted border border-border-subtle'
                              : 'bg-accent-amber/10 text-accent-amber border border-accent-amber/30'
                          }`}>
                            {j.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <div className="w-28 space-y-1">
                            <div className="flex justify-between text-[10px] text-text-secondary">
                              <span>{j.progress.toFixed(0)}%</span>
                            </div>
                            <div className="w-full h-1.5 rounded bg-bg-surface-2 overflow-hidden">
                              <div
                                className="h-full bg-accent-blue rounded transition-all duration-300"
                                style={{ width: `${Math.min(100, j.progress)}%` }}
                              />
                            </div>
                          </div>
                        </td>
                        <td className="py-2.5 px-3 text-text-secondary">{j.created_at.slice(0, 19)}</td>
                        <td className="py-2.5 px-3 text-right">
                          {['QUEUED', 'RUNNING'].includes(j.status) && (
                            <button
                              type="button"
                              onClick={() => handleCancelJob(j.id)}
                              disabled={cancellingId === j.id}
                              className="px-2 py-1 rounded text-[10px] text-accent-red hover:bg-accent-red/10 border border-accent-red/30 transition-colors"
                            >
                              {cancellingId === j.id ? 'Cancelling...' : 'Cancel'}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-text-muted">
                No background execution jobs currently active or queued.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Shell>
  );
}
