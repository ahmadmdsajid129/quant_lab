'use client';

import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Gauge,
  BarChart2,
  TrendingUp,
  Activity,
  Layers,
  ShieldCheck,
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

interface FeatureDef {
  name: string;
  category: string;
  description: string;
}

interface MLMetrics {
  accuracy_train: number;
  accuracy_test: number;
  roc_auc_test: number;
  brier_score: number;
}

interface DriftFeature {
  ks_statistic: number;
  p_value: number;
  has_drift: boolean;
}

interface MLTrainResult {
  model_type: string;
  n_train_samples: number;
  n_test_samples: number;
  metrics: MLMetrics;
  feature_importances: Record<string, number>;
  concept_drift: {
    drifting_features_count: number;
    total_features: number;
    feature_diagnostics: Record<string, DriftFeature>;
  };
}

export default function MachineLearningPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [availableFeatures, setAvailableFeatures] = useState<FeatureDef[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>('');
  const [modelType, setModelType] = useState<string>('GBDT');
  const [trainRatio, setTrainRatio] = useState<number>(0.75);
  const [selectedFeatures, setSelectedFeatures] = useState<string[]>([
    'ret_1d',
    'ret_5d',
    'ret_20d',
    'vol_10d',
    'vol_30d',
    'rsi_14d',
    'macd',
    'vol_ratio_20d',
  ]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MLTrainResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [dsData, featData] = await Promise.all([
          api.get<Dataset[]>('/api/v1/datasets'),
          api.get<FeatureDef[]>('/api/v1/ml/features'),
        ]);
        setDatasets(dsData || []);
        if (dsData && dsData.length > 0) {
          setSelectedDatasetId(dsData[0].id);
        }
        setAvailableFeatures(featData || []);
      } catch (err: any) {
        console.error('Failed to load initial ML metadata:', err);
      }
    }
    loadData();
  }, []);

  const toggleFeature = (name: string) => {
    if (selectedFeatures.includes(name)) {
      if (selectedFeatures.length > 1) {
        setSelectedFeatures(selectedFeatures.filter((f) => f !== name));
      }
    } else {
      setSelectedFeatures([...selectedFeatures, name]);
    }
  };

  const handleTrain = async () => {
    if (!selectedDatasetId) {
      setError('Please select a dataset to train on.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<MLTrainResult>('/api/v1/ml/train', {
        dataset_id: selectedDatasetId,
        model_type: modelType,
        train_ratio: trainRatio,
        features_selected: selectedFeatures,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Model training failed.');
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
                Machine Learning Laboratory
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Zero-Leakage Pipeline
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Supervised financial directional forecasting with strictly chronological scaling and Kolmogorov-Smirnov covariate shift detection.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <ShieldCheck className="w-4 h-4 text-accent-green" />
              <span>Train-Only Scaling Guarantees Zero Lookahead</span>
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
          {/* Left Column: Parameter Console */}
          <div className="lg:col-span-4 space-y-6">
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Model Configuration</span>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                {/* Dataset selector */}
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                    Dataset
                  </label>
                  <select
                    value={selectedDatasetId}
                    onChange={(e) => setSelectedDatasetId(e.target.value)}
                    className="w-full bg-bg-surface-2 border border-border-subtle rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                  >
                    {datasets.map((ds) => (
                      <option key={ds.id} value={ds.id}>
                        {ds.symbol} ({ds.total_bars} bars)
                      </option>
                    ))}
                    {datasets.length === 0 && <option value="">No datasets available</option>}
                  </select>
                </div>

                {/* Model architecture */}
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1.5">
                    Model Architecture
                  </label>
                  <select
                    value={modelType}
                    onChange={(e) => setModelType(e.target.value)}
                    className="w-full bg-bg-surface-2 border border-border-subtle rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-blue"
                  >
                    <option value="GBDT">Histogram Gradient Boosting (GBDT)</option>
                    <option value="RANDOM_FOREST">Random Forest Classifier (100 Trees)</option>
                    <option value="RIDGE">L2 Ridge Logistic Regression</option>
                  </select>
                </div>

                {/* Train ratio */}
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-xs font-mono text-text-secondary uppercase">
                      Train Partition Ratio
                    </label>
                    <span className="text-xs font-mono text-text-primary">
                      {Math.round(trainRatio * 100)}% Train / {Math.round((1 - trainRatio) * 100)}% Test
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.5"
                    max="0.9"
                    step="0.05"
                    value={trainRatio}
                    onChange={(e) => setTrainRatio(parseFloat(e.target.value))}
                    className="w-full accent-accent-blue cursor-pointer"
                  />
                </div>

                {/* Feature checklist */}
                <div className="pt-2 border-t border-border-subtle">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-mono text-text-secondary uppercase">
                      Features ({selectedFeatures.length}/{availableFeatures.length})
                    </label>
                  </div>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                    {availableFeatures.map((feat) => {
                      const isChecked = selectedFeatures.includes(feat.name);
                      return (
                        <div
                          key={feat.name}
                          onClick={() => toggleFeature(feat.name)}
                          className={`flex items-center justify-between p-2 rounded cursor-pointer border text-xs transition-colors ${
                            isChecked
                              ? 'bg-accent-blue/10 border-accent-blue/40 text-text-primary'
                              : 'bg-bg-surface-2 border-border-subtle text-text-muted hover:border-border-strong'
                          }`}
                        >
                          <div>
                            <span className="font-mono font-medium">{feat.name}</span>
                            <span className="text-[10px] text-text-muted ml-2">[{feat.category}]</span>
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

                {/* Action button */}
                <Button
                  onClick={handleTrain}
                  disabled={loading || !selectedDatasetId}
                  className="w-full mt-4 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Training Model...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Train & Evaluate</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Invariant Note Card */}
            <div className="p-4 rounded bg-bg-surface-1 border border-border-subtle space-y-2 text-xs text-text-secondary">
              <div className="font-medium text-text-primary flex items-center gap-1.5">
                <BrainCircuit className="w-3.5 h-3.5 text-accent-blue" />
                <span>Financial ML Guardrails</span>
              </div>
              <p>
                Standard random K-Fold cross validation leaks future volatility and return distributions into the past.
                QuantLab strictly enforces forward chronological testing with train-only scaling.
              </p>
            </div>
          </div>

          {/* Right Column: Results & Diagnostics */}
          <div className="lg:col-span-8 space-y-6">
            {result ? (
              <>
                {/* KPI Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Train Acc vs Test Acc</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {(result.metrics.accuracy_train * 100).toFixed(1)}% / {(result.metrics.accuracy_test * 100).toFixed(1)}%
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        Overfitting Gap: {Math.abs((result.metrics.accuracy_train - result.metrics.accuracy_test) * 100).toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Out-of-Sample ROC-AUC</div>
                      <div className="text-xl font-semibold text-accent-blue mt-1 font-mono">
                        {result.metrics.roc_auc_test.toFixed(3)}
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        {result.metrics.roc_auc_test >= 0.55 ? 'Informative Signal' : 'Random Guessing Baseline (~0.50)'}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Brier Loss Score</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {result.metrics.brier_score.toFixed(4)}
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        Probability calibration metric
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-4">
                      <div className="text-[11px] font-mono text-text-muted uppercase">Sample Split</div>
                      <div className="text-xl font-semibold text-text-primary mt-1 font-mono">
                        {result.n_train_samples} / {result.n_test_samples}
                      </div>
                      <div className="text-[11px] text-text-secondary mt-1">
                        Train bars / Test bars
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Feature Importance Card */}
                <Card>
                  <CardHeader className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <BarChart2 className="w-4 h-4 text-text-secondary" />
                      <span className="font-medium text-sm text-text-primary">Feature Importance Distribution</span>
                    </div>
                    <Badge variant="neutral" className="font-mono text-xs">
                      {result.model_type}
                    </Badge>
                  </CardHeader>
                  <CardContent className="space-y-3 pt-4">
                    {Object.entries(result.feature_importances).map(([col, imp]) => {
                      const maxVal = Math.max(...Object.values(result.feature_importances), 0.01);
                      const pct = Math.round((imp / maxVal) * 100);
                      return (
                        <div key={col} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="font-mono text-text-primary">{col}</span>
                            <span className="font-mono text-text-secondary">{(imp * 100).toFixed(2)}%</span>
                          </div>
                          <div className="w-full h-2 rounded bg-bg-surface-2 overflow-hidden">
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

                {/* Concept Drift & Covariate Shift Diagnostics */}
                <Card>
                  <CardHeader className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-text-secondary" />
                      <span className="font-medium text-sm text-text-primary">
                        Covariate Shift & Concept Drift (Kolmogorov-Smirnov 2-Sample Test)
                      </span>
                    </div>
                    {result.concept_drift.drifting_features_count === 0 ? (
                      <Badge variant="profit" className="flex items-center gap-1 text-xs">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Stable Distribution</span>
                      </Badge>
                    ) : (
                      <Badge variant="warning" className="flex items-center gap-1 text-xs">
                        <AlertTriangle className="w-3 h-3" />
                        <span>{result.concept_drift.drifting_features_count} Drifting Features</span>
                      </Badge>
                    )}
                  </CardHeader>
                  <CardContent className="pt-2">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead>
                          <tr className="border-b border-border-subtle text-text-muted font-mono uppercase">
                            <th className="py-2.5 px-3">Feature</th>
                            <th className="py-2.5 px-3">KS Statistic</th>
                            <th className="py-2.5 px-3">p-value</th>
                            <th className="py-2.5 px-3 text-right">Drift Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle/50 font-mono">
                          {Object.entries(result.concept_drift.feature_diagnostics).map(
                            ([feat, diag]) => (
                              <tr key={feat} className="hover:bg-bg-surface-2/40">
                                <td className="py-2.5 px-3 text-text-primary font-medium">{feat}</td>
                                <td className="py-2.5 px-3 text-text-secondary">
                                  {diag.ks_statistic.toFixed(4)}
                                </td>
                                <td className="py-2.5 px-3 text-text-secondary">
                                  {diag.p_value.toFixed(4)}
                                </td>
                                <td className="py-2.5 px-3 text-right">
                                  {diag.has_drift ? (
                                    <span className="px-2 py-0.5 rounded text-[11px] bg-accent-amber/10 text-accent-amber border border-accent-amber/30">
                                      Drift (p &lt; 0.05)
                                    </span>
                                  ) : (
                                    <span className="px-2 py-0.5 rounded text-[11px] bg-accent-green/10 text-accent-green border border-accent-green/30">
                                      Stable
                                    </span>
                                  )}
                                </td>
                              </tr>
                            )
                          )}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="h-96 rounded-lg border border-dashed border-border-subtle flex flex-col items-center justify-center p-8 text-center text-text-muted">
                <BrainCircuit className="w-12 h-12 text-border-strong mb-3" />
                <h3 className="text-sm font-medium text-text-secondary">No ML Model Evaluated Yet</h3>
                <p className="text-xs text-text-muted max-w-sm mt-1">
                  Select a dataset, choose a model family, adjust features, and click "Train & Evaluate" to view ROC-AUC metrics and drift diagnostics.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  );
}
