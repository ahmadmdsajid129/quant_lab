'use client';

import React, { useEffect, useState } from 'react';
import {
  Layers,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  TrendingUp,
  Activity,
  ArrowDownUp,
  Clock,
  ShieldCheck,
  Send,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface PriceLevel {
  price: number;
  quantity: number;
  order_count: number;
}

interface Trade {
  trade_id: string;
  price: number;
  quantity: number;
  taker_side: string;
  timestamp: number;
}

interface LOBSnapshot {
  symbol: string;
  best_bid: number | null;
  best_ask: number | null;
  spread: number | null;
  mid_price: number | null;
  microprice: number | null;
  order_flow_imbalance: number;
  total_open_orders: number;
  bids: PriceLevel[];
  asks: PriceLevel[];
  recent_trades: Trade[];
}

export default function MicrostructurePage() {
  const [symbol, setSymbol] = useState<string>('BTC/USD');
  const [initialMid, setInitialMid] = useState<number>(65000.0);
  const [tickSize, setTickSize] = useState<number>(1.0);
  const [numEvents, setNumEvents] = useState<number>(150);
  const [seed, setSeed] = useState<number>(42);

  // Manual order submission
  const [orderSide, setOrderSide] = useState<'BID' | 'ASK'>('BID');
  const [orderPrice, setOrderPrice] = useState<number>(65000.0);
  const [orderQty, setOrderQty] = useState<number>(0.5);

  const [loading, setLoading] = useState(false);
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [snapshot, setSnapshot] = useState<LOBSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post<LOBSnapshot>('/api/v1/microstructure/simulate', {
        symbol,
        initial_mid: initialMid,
        tick_size: tickSize,
        num_events: numEvents,
        seed,
      });
      setSnapshot(res);
      if (res.best_bid) {
        setOrderPrice(res.best_bid);
      }
    } catch (err: any) {
      setError(err.message || 'Simulation failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitOrder = async () => {
    setSubmittingOrder(true);
    setError(null);
    try {
      const res = await api.post<LOBSnapshot>('/api/v1/microstructure/order', {
        symbol,
        side: orderSide,
        price: orderPrice,
        quantity: orderQty,
      });
      setSnapshot(res);
    } catch (err: any) {
      setError(err.message || 'Order submission failed.');
    } finally {
      setSubmittingOrder(false);
    }
  };

  useEffect(() => {
    handleSimulate();
  }, []);

  const maxBidQty = snapshot ? Math.max(...snapshot.bids.map((b) => b.quantity), 1.0) : 1.0;
  const maxAskQty = snapshot ? Math.max(...snapshot.asks.map((a) => a.quantity), 1.0) : 1.0;

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                Market Microstructure & Limit Order Book
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Price-Time Priority
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Continuous double-auction L2 matching engine with microprice dynamics and order-flow imbalance (OFI).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <ShieldCheck className="w-4 h-4 text-accent-green" />
              <span>Matching Engine: Strict FIFO Queue Execution</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-accent-red/10 border border-accent-red/30 flex items-center gap-3 text-sm text-accent-red">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Microstructure Metrics Banner */}
        {snapshot && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Best Bid</div>
                <div className="text-lg font-semibold text-financial-profit mt-0.5 font-mono">
                  {snapshot.best_bid ? snapshot.best_bid.toFixed(2) : '—'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Best Ask</div>
                <div className="text-lg font-semibold text-financial-loss mt-0.5 font-mono">
                  {snapshot.best_ask ? snapshot.best_ask.toFixed(2) : '—'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Spread</div>
                <div className="text-lg font-semibold text-text-primary mt-0.5 font-mono">
                  {snapshot.spread ? snapshot.spread.toFixed(2) : '—'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Mid Price</div>
                <div className="text-lg font-semibold text-text-primary mt-0.5 font-mono">
                  {snapshot.mid_price ? snapshot.mid_price.toFixed(2) : '—'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Microprice</div>
                <div className="text-lg font-semibold text-accent-blue mt-0.5 font-mono">
                  {snapshot.microprice ? snapshot.microprice.toFixed(2) : '—'}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-3">
                <div className="text-[10px] font-mono text-text-muted uppercase">Order Flow Imbalance</div>
                <div className={`text-lg font-semibold mt-0.5 font-mono ${
                  snapshot.order_flow_imbalance >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                }`}>
                  {(snapshot.order_flow_imbalance * 100).toFixed(1)}%
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 2-Column: Order Book Ladder & Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Order Book Ladder (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            <Card>
              <CardHeader className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-text-secondary" />
                  <span className="font-medium text-sm text-text-primary">
                    L2 Order Book Depth Ladder ({snapshot ? snapshot.symbol : symbol})
                  </span>
                </div>
                <Badge variant="neutral" className="font-mono text-xs">
                  {snapshot ? `${snapshot.total_open_orders} Resting Orders` : '0 Orders'}
                </Badge>
              </CardHeader>
              <CardContent className="p-0">
                <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-border-subtle">
                  {/* Bids Ladder (Buy side) */}
                  <div className="p-4 space-y-2">
                    <div className="flex justify-between text-[11px] font-mono text-text-muted uppercase pb-2 border-b border-border-subtle">
                      <span>Bid Price</span>
                      <span>Quantity</span>
                      <span>Orders</span>
                    </div>
                    {snapshot?.bids.map((b) => {
                      const fillPct = Math.round((b.quantity / maxBidQty) * 100);
                      return (
                        <div
                          key={b.price}
                          className="relative flex justify-between items-center text-xs font-mono py-1 px-1.5 rounded hover:bg-bg-surface-2 cursor-pointer"
                          onClick={() => {
                            setOrderSide('ASK');
                            setOrderPrice(b.price);
                          }}
                        >
                          <div
                            className="absolute right-0 top-0 bottom-0 bg-financial-profitMuted/30 rounded -z-0 transition-all"
                            style={{ width: `${fillPct}%` }}
                          />
                          <span className="text-financial-profit font-medium z-10">{b.price.toFixed(2)}</span>
                          <span className="text-text-primary z-10">{b.quantity.toFixed(3)}</span>
                          <span className="text-text-muted text-[10px] z-10">[{b.order_count}]</span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Asks Ladder (Sell side) */}
                  <div className="p-4 space-y-2">
                    <div className="flex justify-between text-[11px] font-mono text-text-muted uppercase pb-2 border-b border-border-subtle">
                      <span>Ask Price</span>
                      <span>Quantity</span>
                      <span>Orders</span>
                    </div>
                    {snapshot?.asks.map((a) => {
                      const fillPct = Math.round((a.quantity / maxAskQty) * 100);
                      return (
                        <div
                          key={a.price}
                          className="relative flex justify-between items-center text-xs font-mono py-1 px-1.5 rounded hover:bg-bg-surface-2 cursor-pointer"
                          onClick={() => {
                            setOrderSide('BID');
                            setOrderPrice(a.price);
                          }}
                        >
                          <div
                            className="absolute left-0 top-0 bottom-0 bg-financial-lossMuted/30 rounded -z-0 transition-all"
                            style={{ width: `${fillPct}%` }}
                          />
                          <span className="text-financial-loss font-medium z-10">{a.price.toFixed(2)}</span>
                          <span className="text-text-primary z-10">{a.quantity.toFixed(3)}</span>
                          <span className="text-text-muted text-[10px] z-10">[{a.order_count}]</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Executed Trade Tape */}
            <Card>
              <CardHeader className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-text-secondary" />
                  <span className="font-medium text-sm text-text-primary">Recent Trades (Execution Tape)</span>
                </div>
                <Badge variant="neutral" className="text-xs font-mono">
                  {snapshot?.recent_trades.length || 0} Fills
                </Badge>
              </CardHeader>
              <CardContent className="pt-2">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead>
                      <tr className="border-b border-border-subtle text-text-muted uppercase text-[11px]">
                        <th className="py-2 px-3">Trade ID</th>
                        <th className="py-2 px-3">Side</th>
                        <th className="py-2 px-3">Execution Price</th>
                        <th className="py-2 px-3">Quantity</th>
                        <th className="py-2 px-3 text-right">Time (s)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border-subtle/50">
                      {snapshot?.recent_trades.map((t) => (
                        <tr key={t.trade_id} className="hover:bg-bg-surface-2/40">
                          <td className="py-2 px-3 text-text-muted">{t.trade_id}</td>
                          <td className="py-2 px-3">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              t.taker_side === 'BID'
                                ? 'bg-financial-profitMuted text-financial-profit'
                                : 'bg-financial-lossMuted text-financial-loss'
                            }`}>
                              {t.taker_side === 'BID' ? 'BUY' : 'SELL'}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-text-primary font-medium">{t.price.toFixed(2)}</td>
                          <td className="py-2 px-3 text-text-secondary">{t.quantity.toFixed(3)}</td>
                          <td className="py-2 px-3 text-right text-text-muted">{t.timestamp.toFixed(2)}s</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Interactive Order Entry & Simulation Controls (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            {/* Live Order Placement */}
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Send className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Order Placement Console</span>
              </CardHeader>
              <CardContent className="space-y-4 pt-4">
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setOrderSide('BID')}
                    className={`py-2 rounded text-xs font-mono font-semibold border transition-colors ${
                      orderSide === 'BID'
                        ? 'bg-financial-profit text-white border-financial-profit'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    BUY / BID
                  </button>
                  <button
                    type="button"
                    onClick={() => setOrderSide('ASK')}
                    className={`py-2 rounded text-xs font-mono font-semibold border transition-colors ${
                      orderSide === 'ASK'
                        ? 'bg-financial-loss text-white border-financial-loss'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    SELL / ASK
                  </button>
                </div>

                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                    Limit Price
                  </label>
                  <Input
                    type="number"
                    step="0.5"
                    value={orderPrice}
                    onChange={(e) => setOrderPrice(parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                    Order Quantity
                  </label>
                  <Input
                    type="number"
                    step="0.1"
                    min="0.01"
                    value={orderQty}
                    onChange={(e) => setOrderQty(parseFloat(e.target.value) || 0)}
                  />
                </div>

                <Button
                  onClick={handleSubmitOrder}
                  disabled={submittingOrder}
                  className="w-full mt-2 flex items-center justify-center gap-2"
                >
                  {submittingOrder ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Posting Order...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Submit {orderSide} Limit Order</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Poisson Event Stream Simulator */}
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Stochastic LOB Simulator</span>
              </CardHeader>
              <CardContent className="space-y-3 pt-3">
                <div>
                  <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                    Symbol
                  </label>
                  <Input
                    type="text"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Initial Mid
                    </label>
                    <Input
                      type="number"
                      value={initialMid}
                      onChange={(e) => setInitialMid(parseFloat(e.target.value) || 100)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Tick Size
                    </label>
                    <Input
                      type="number"
                      step="0.01"
                      value={tickSize}
                      onChange={(e) => setTickSize(parseFloat(e.target.value) || 0.05)}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Event Count
                    </label>
                    <Input
                      type="number"
                      value={numEvents}
                      onChange={(e) => setNumEvents(parseInt(e.target.value) || 100)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Seed
                    </label>
                    <Input
                      type="number"
                      value={seed}
                      onChange={(e) => setSeed(parseInt(e.target.value) || 42)}
                    />
                  </div>
                </div>

                <Button
                  onClick={handleSimulate}
                  disabled={loading}
                  variant="secondary"
                  className="w-full mt-2 flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Simulating...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Re-seed Simulation</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Shell>
  );
}
