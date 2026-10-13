'use client';

import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  TrendingUp,
  Percent,
  Layers,
  Scale,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface OptionGreeks {
  price: number;
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
}

interface OptionPriceResult {
  model_used: string;
  exercise_style: string;
  price: number;
  greeks: OptionGreeks;
  put_call_parity_diff: number | null;
}

interface PayoffLeg {
  type: string;
  strike: number;
  position: string;
  premium: number;
}

interface PayoffPoint {
  underlying_price: number;
  pnl: number;
}

interface StrategyPayoffResult {
  strategy: string;
  spot: number;
  net_debit_credit: number;
  max_profit: number | string;
  max_loss: number | string;
  legs: PayoffLeg[];
  curve: PayoffPoint[];
}

export default function OptionsPage() {
  // Pricing tab state
  const [spot, setSpot] = useState<number>(100.0);
  const [strike, setStrike] = useState<number>(100.0);
  const [expiryDays, setExpiryDays] = useState<number>(30.0);
  const [rate, setRate] = useState<number>(0.02);
  const [volatility, setVolatility] = useState<number>(0.25);
  const [optionType, setOptionType] = useState<'CALL' | 'PUT'>('CALL');
  const [pricingModel, setPricingModel] = useState<string>('BLACK_SCHOLES');
  const [exerciseStyle, setExerciseStyle] = useState<string>('EUROPEAN');

  // Strategy payoff state
  const [strategy, setStrategy] = useState<string>('BULL_CALL_SPREAD');

  // Implied Volatility inversion state
  const [marketPrice, setMarketPrice] = useState<number>(3.50);
  const [solvedIV, setSolvedIV] = useState<number | null>(null);

  const [loadingPrice, setLoadingPrice] = useState(false);
  const [loadingPayoff, setLoadingPayoff] = useState(false);
  const [priceResult, setPriceResult] = useState<OptionPriceResult | null>(null);
  const [payoffResult, setPayoffResult] = useState<StrategyPayoffResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCalculatePrice = async () => {
    setLoadingPrice(true);
    setError(null);
    try {
      const res = await api.post<OptionPriceResult>('/api/v1/options/price', {
        spot,
        strike,
        expiry_days: expiryDays,
        rate,
        volatility,
        option_type: optionType,
        pricing_model: pricingModel,
        exercise_style: exerciseStyle,
      });
      setPriceResult(res);
      setMarketPrice(res.price);
    } catch (err: any) {
      setError(err.message || 'Pricing calculation failed.');
    } finally {
      setLoadingPrice(false);
    }
  };

  const handleSolveIV = async () => {
    setError(null);
    try {
      const res = await api.post<{ implied_volatility: number | null }>('/api/v1/options/implied-vol', {
        market_price: marketPrice,
        spot,
        strike,
        expiry_days: expiryDays,
        rate,
        option_type: optionType,
      });
      setSolvedIV(res.implied_volatility);
    } catch (err: any) {
      setError(err.message || 'IV inversion failed.');
    }
  };

  const handleCalculatePayoff = async () => {
    setLoadingPayoff(true);
    setError(null);
    try {
      const res = await api.post<StrategyPayoffResult>('/api/v1/options/payoff', {
        strategy,
        spot,
        volatility,
        expiry_days: expiryDays,
        rate,
      });
      setPayoffResult(res);
    } catch (err: any) {
      setError(err.message || 'Payoff computation failed.');
    } finally {
      setLoadingPayoff(false);
    }
  };

  useEffect(() => {
    handleCalculatePrice();
    handleCalculatePayoff();
  }, []);

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                Options & Derivatives Laboratory
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Black-Scholes & CRR Trees
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Analytical Greeks (Delta, Gamma, Vega, Theta, Rho), Put-Call Parity validation, Brent IV inversion, and multi-leg strategy payoff profiles.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <ShieldCheck className="w-4 h-4 text-accent-green" />
              <span>Put-Call Parity Invariant Enforced</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-accent-red/10 border border-accent-red/30 flex items-center gap-3 text-sm text-accent-red">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Section 1: Pricing & Greeks */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls (4 cols) */}
          <div className="lg:col-span-4 space-y-4">
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Contract Parameters</span>
              </CardHeader>
              <CardContent className="space-y-3 pt-3">
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setOptionType('CALL')}
                    className={`py-1.5 rounded text-xs font-mono font-semibold border transition-colors ${
                      optionType === 'CALL'
                        ? 'bg-accent-blue text-white border-accent-blue'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    CALL OPTION
                  </button>
                  <button
                    type="button"
                    onClick={() => setOptionType('PUT')}
                    className={`py-1.5 rounded text-xs font-mono font-semibold border transition-colors ${
                      optionType === 'PUT'
                        ? 'bg-accent-blue text-white border-accent-blue'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    PUT OPTION
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Spot Price (S)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={spot}
                      onChange={(e) => setSpot(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Strike Price (K)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={strike}
                      onChange={(e) => setStrike(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Days to Expiry (T)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={expiryDays}
                      onChange={(e) => setExpiryDays(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Volatility (σ)
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      value={volatility}
                      onChange={(e) => setVolatility(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Pricing Model
                    </label>
                    <select
                      value={pricingModel}
                      onChange={(e) => setPricingModel(e.target.value)}
                      className="w-full bg-bg-surface-2 border border-border-subtle rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none"
                    >
                      <option value="BLACK_SCHOLES">Black-Scholes-Merton</option>
                      <option value="BINOMIAL_TREE">CRR Binomial Tree (100 steps)</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Exercise Style
                    </label>
                    <select
                      value={exerciseStyle}
                      onChange={(e) => setExerciseStyle(e.target.value)}
                      className="w-full bg-bg-surface-2 border border-border-subtle rounded px-2 py-1.5 text-xs text-text-primary focus:outline-none"
                    >
                      <option value="EUROPEAN">European</option>
                      <option value="AMERICAN">American</option>
                    </select>
                  </div>
                </div>

                <Button
                  onClick={handleCalculatePrice}
                  disabled={loadingPrice}
                  className="w-full mt-2 flex items-center justify-center gap-2"
                >
                  {loadingPrice ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Pricing...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Calculate Option Value</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Implied Volatility Solver Card */}
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Percent className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Implied Volatility Inversion</span>
              </CardHeader>
              <CardContent className="space-y-3 pt-3">
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                    Observed Market Price ($)
                  </label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      step="0.05"
                      value={marketPrice}
                      onChange={(e) => setMarketPrice(parseFloat(e.target.value) || 0)}
                    />
                    <Button variant="secondary" onClick={handleSolveIV} className="text-xs whitespace-nowrap">
                      Invert IV
                    </Button>
                  </div>
                </div>
                {solvedIV !== null && (
                  <div className="p-2.5 rounded bg-bg-surface-2 border border-border-subtle flex justify-between items-center text-xs">
                    <span className="text-text-secondary">Implied Volatility (σ_IV):</span>
                    <span className="font-mono font-semibold text-accent-blue text-sm">
                      {(solvedIV * 100).toFixed(2)}%
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Pricing Results & Greeks (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {priceResult && (
              <>
                {/* Fair Value Banner */}
                <div className="p-5 rounded-lg bg-bg-surface-1 border border-border-subtle flex items-center justify-between">
                  <div>
                    <div className="text-xs font-mono text-text-muted uppercase">
                      Theoretical Fair Value ({priceResult.exercise_style} {optionType})
                    </div>
                    <div className="text-3xl font-bold font-mono text-text-primary mt-1">
                      ${priceResult.price.toFixed(4)}
                    </div>
                    <div className="text-xs text-text-secondary mt-1">
                      Model: {priceResult.model_used} | Parity Residual: {priceResult.put_call_parity_diff?.toFixed(6) || '0.000000'}
                    </div>
                  </div>
                  <Badge variant="profit" className="text-xs font-mono">
                    Arbitrage-Free
                  </Badge>
                </div>

                {/* Greeks Grid */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-3">
                      <div className="text-[10px] font-mono text-text-muted uppercase">Delta (Δ)</div>
                      <div className="text-lg font-semibold text-text-primary mt-0.5 font-mono">
                        {priceResult.greeks.delta.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-text-secondary mt-0.5">Hedge Ratio (∂V/∂S)</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-3">
                      <div className="text-[10px] font-mono text-text-muted uppercase">Gamma (Γ)</div>
                      <div className="text-lg font-semibold text-text-primary mt-0.5 font-mono">
                        {priceResult.greeks.gamma.toFixed(5)}
                      </div>
                      <div className="text-[10px] text-text-secondary mt-0.5">Curvature (∂²V/∂S²)</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-3">
                      <div className="text-[10px] font-mono text-text-muted uppercase">Vega (𝒱)</div>
                      <div className="text-lg font-semibold text-accent-blue mt-0.5 font-mono">
                        {priceResult.greeks.vega.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-text-secondary mt-0.5">Per 1% Vol (∂V/∂σ)</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-3">
                      <div className="text-[10px] font-mono text-text-muted uppercase">Theta (Θ)</div>
                      <div className="text-lg font-semibold text-financial-loss mt-0.5 font-mono">
                        {priceResult.greeks.theta.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-text-secondary mt-0.5">1-Day Decay (∂V/∂t)</div>
                    </CardContent>
                  </Card>

                  <Card className="bg-bg-surface-1">
                    <CardContent className="p-3">
                      <div className="text-[10px] font-mono text-text-muted uppercase">Rho (ρ)</div>
                      <div className="text-lg font-semibold text-text-primary mt-0.5 font-mono">
                        {priceResult.greeks.rho.toFixed(4)}
                      </div>
                      <div className="text-[10px] text-text-secondary mt-0.5">Per 1% Rate (∂V/∂r)</div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}

            {/* Section 2: Strategy Payoff Diagram */}
            <Card>
              <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-text-secondary" />
                  <span className="font-medium text-sm text-text-primary">Multi-Leg Strategy Payoff Profile</span>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={strategy}
                    onChange={(e) => setStrategy(e.target.value)}
                    className="bg-bg-surface-2 border border-border-subtle rounded px-2.5 py-1 text-xs text-text-primary focus:outline-none"
                  >
                    <option value="BULL_CALL_SPREAD">Bull Call Spread</option>
                    <option value="BEAR_PUT_SPREAD">Bear Put Spread</option>
                    <option value="LONG_STRADDLE">Long Straddle</option>
                    <option value="LONG_STRANGLE">Long Strangle</option>
                    <option value="IRON_CONDOR">Iron Condor</option>
                    <option value="LONG_CALL">Long Call</option>
                    <option value="LONG_PUT">Long Put</option>
                  </select>
                  <Button variant="secondary" onClick={handleCalculatePayoff} className="text-xs py-1 px-2.5">
                    Update Payoff
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4 pt-3">
                {payoffResult && (
                  <>
                    {/* Key characteristics */}
                    <div className="grid grid-cols-3 gap-3 text-xs font-mono">
                      <div className="p-3 rounded bg-bg-surface-2 border border-border-subtle">
                        <span className="text-text-muted block text-[10px]">Net Debit / Credit:</span>
                        <span className="font-semibold text-text-primary text-sm">
                          ${payoffResult.net_debit_credit.toFixed(2)}
                        </span>
                      </div>
                      <div className="p-3 rounded bg-bg-surface-2 border border-border-subtle">
                        <span className="text-text-muted block text-[10px]">Max Profit:</span>
                        <span className="font-semibold text-financial-profit text-sm">
                          {typeof payoffResult.max_profit === 'number'
                            ? `$${payoffResult.max_profit.toFixed(2)}`
                            : payoffResult.max_profit}
                        </span>
                      </div>
                      <div className="p-3 rounded bg-bg-surface-2 border border-border-subtle">
                        <span className="text-text-muted block text-[10px]">Max Risk / Loss:</span>
                        <span className="font-semibold text-financial-loss text-sm">
                          {typeof payoffResult.max_loss === 'number'
                            ? `$${payoffResult.max_loss.toFixed(2)}`
                            : payoffResult.max_loss}
                        </span>
                      </div>
                    </div>

                    {/* Legs table */}
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead>
                          <tr className="border-b border-border-subtle text-text-muted text-[10px] uppercase">
                            <th className="py-1.5 px-2">Position</th>
                            <th className="py-1.5 px-2">Option Type</th>
                            <th className="py-1.5 px-2">Strike Price</th>
                            <th className="py-1.5 px-2 text-right">Premium Paid</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-border-subtle/40">
                          {payoffResult.legs.map((leg, idx) => (
                            <tr key={idx}>
                              <td className="py-1.5 px-2">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                  leg.position === 'LONG'
                                    ? 'bg-financial-profitMuted text-financial-profit'
                                    : 'bg-financial-lossMuted text-financial-loss'
                                }`}>
                                  {leg.position}
                                </span>
                              </td>
                              <td className="py-1.5 px-2 text-text-primary">{leg.type}</td>
                              <td className="py-1.5 px-2 text-text-primary">${leg.strike.toFixed(2)}</td>
                              <td className="py-1.5 px-2 text-right text-text-secondary">${leg.premium.toFixed(4)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Payoff Curve Preview (First/Last Points) */}
                    <div className="p-3 rounded bg-bg-surface-2 border border-border-subtle">
                      <div className="text-[11px] font-mono text-text-muted mb-2 flex justify-between">
                        <span>Terminal PnL Profile Across Expiration Spot</span>
                        <span>Zero PnL Break-Even Level</span>
                      </div>
                      <div className="h-28 flex items-end gap-1">
                        {payoffResult.curve.map((pt, i) => {
                          const maxAbs = Math.max(
                            ...payoffResult.curve.map((p) => Math.abs(p.pnl)),
                            1.0
                          );
                          const heightPct = Math.round((Math.abs(pt.pnl) / maxAbs) * 100);
                          const isProfit = pt.pnl >= 0;
                          return (
                            <div
                              key={i}
                              title={`S: $${pt.underlying_price} | PnL: $${pt.pnl}`}
                              className="flex-1 flex flex-col justify-end items-center h-full group relative cursor-pointer"
                            >
                              <div
                                className={`w-full rounded-t transition-all ${
                                  isProfit ? 'bg-financial-profit' : 'bg-financial-loss'
                                }`}
                                style={{ height: `${Math.max(heightPct, 4)}%` }}
                              />
                            </div>
                          );
                        })}
                      </div>
                      <div className="flex justify-between text-[10px] font-mono text-text-muted mt-2">
                        <span>${payoffResult.curve[0]?.underlying_price.toFixed(0)}</span>
                        <span>Current Spot: ${payoffResult.spot.toFixed(0)}</span>
                        <span>${payoffResult.curve[payoffResult.curve.length - 1]?.underlying_price.toFixed(0)}</span>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Shell>
  );
}
