'use client';

import React, { useEffect, useState } from 'react';
import {
  Terminal,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Play,
  Send,
  Power,
  RefreshCw,
} from 'lucide-react';
import { Shell } from '@/components/layout/Shell';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { api } from '@/lib/api';

interface PositionDetail {
  id: string;
  symbol: string;
  side: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  pnl_pct: number;
}

interface PaperOrderDetail {
  id: string;
  symbol: string;
  order_type: string;
  side: string;
  quantity: number;
  limit_price: number | null;
  status: string;
  filled_quantity: number;
  filled_price: number | null;
  created_at: string;
}

interface PaperAccountSummary {
  account_id: string;
  name: string;
  currency: string;
  initial_cash: number;
  current_cash: number;
  positions_market_value: number;
  total_equity: number;
  unrealized_pnl: number;
  total_return_pct: number;
  positions: PositionDetail[];
  recent_orders: PaperOrderDetail[];
}

export default function PaperTradingPage() {
  const [account, setAccount] = useState<PaperAccountSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [orderSubmitting, setOrderSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  // Order ticket state
  const [symbol, setSymbol] = useState<string>('BTC/USD');
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState<number>(0.5);
  const [price, setPrice] = useState<number>(65000.0);
  const [orderType, setOrderType] = useState<string>('MARKET');

  const loadAccount = async () => {
    setLoading(true);
    try {
      const res = await api.get<PaperAccountSummary>('/api/v1/paper-trading/account');
      setAccount(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load paper trading account.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccount();
  }, []);

  const handleOrderSubmit = async () => {
    setOrderSubmitting(true);
    setError(null);
    setStatusMessage(null);
    try {
      await api.post('/api/v1/paper-trading/orders', {
        symbol,
        side,
        quantity,
        price,
        order_type: orderType,
      });
      setStatusMessage(`Order executed: ${side} ${quantity} ${symbol} @ ~$${price.toFixed(2)}`);
      await loadAccount();
    } catch (err: any) {
      setError(err.message || 'Order failed risk checks.');
    } finally {
      setOrderSubmitting(false);
    }
  };

  const handleKillSwitch = async () => {
    if (!confirm('Engage Emergency Kill Switch? This will cancel all active orders immediately.')) return;
    try {
      const res = await api.post<{ message: string }>('/api/v1/paper-trading/kill-switch');
      setStatusMessage(res.message);
      await loadAccount();
    } catch (err: any) {
      setError(err.message || 'Kill switch engagement failed.');
    }
  };

  const handleReset = async () => {
    if (!confirm('Reset paper account? This will clear all virtual positions and reset cash to $100,000.')) return;
    try {
      const res = await api.post<PaperAccountSummary>('/api/v1/paper-trading/reset');
      setAccount(res);
      setStatusMessage('Paper trading account successfully reset to $100,000.00 cash.');
    } catch (err: any) {
      setError(err.message || 'Account reset failed.');
    }
  };

  const estimatedNotional = quantity * price;

  return (
    <Shell>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-subtle pb-6">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold text-text-primary">
                Simulated Paper Trading
              </h1>
              <Badge variant="neutral" className="font-mono text-xs">
                Zero-Risk Sandbox
              </Badge>
            </div>
            <p className="text-sm text-text-secondary mt-1">
              Virtual order execution with pre-trade risk controls, cash & position conservation, and an emergency kill switch.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              onClick={handleReset}
              className="flex items-center gap-1.5 text-xs text-text-secondary"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Reset Account</span>
            </Button>
            <Button
              variant="secondary"
              onClick={handleKillSwitch}
              className="flex items-center gap-1.5 text-xs text-accent-red border-accent-red/30 hover:bg-accent-red/10"
            >
              <Power className="w-3.5 h-3.5" />
              <span>Kill Switch</span>
            </Button>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded bg-accent-red/10 border border-accent-red/30 flex items-center gap-3 text-sm text-accent-red">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {statusMessage && (
          <div className="p-4 rounded bg-accent-green/10 border border-accent-green/30 flex items-center gap-3 text-sm text-accent-green">
            <ShieldCheck className="w-5 h-5 flex-shrink-0" />
            <span>{statusMessage}</span>
          </div>
        )}

        {/* Account KPI Banner */}
        {account && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[11px] font-mono text-text-muted uppercase">Portfolio Equity</div>
                <div className="text-2xl font-bold font-mono text-text-primary mt-1">
                  ${account.total_equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="text-[11px] text-text-secondary mt-1">
                  Cash + Position Market Value
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[11px] font-mono text-text-muted uppercase">Available Cash</div>
                <div className="text-2xl font-bold font-mono text-accent-blue mt-1">
                  ${account.current_cash.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="text-[11px] text-text-secondary mt-1">
                  Unallocated Buying Power
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[11px] font-mono text-text-muted uppercase">Holdings Value</div>
                <div className="text-2xl font-bold font-mono text-text-primary mt-1">
                  ${account.positions_market_value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="text-[11px] text-text-secondary mt-1">
                  {account.positions.length} Active Positions
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[11px] font-mono text-text-muted uppercase">Unrealized PnL</div>
                <div className={`text-2xl font-bold font-mono mt-1 ${
                  account.unrealized_pnl >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                }`}>
                  {account.unrealized_pnl >= 0 ? '+' : ''}${account.unrealized_pnl.toFixed(2)}
                </div>
                <div className="text-[11px] text-text-secondary mt-1">
                  Open position profit / loss
                </div>
              </CardContent>
            </Card>

            <Card className="bg-bg-surface-1">
              <CardContent className="p-4">
                <div className="text-[11px] font-mono text-text-muted uppercase">Total Return</div>
                <div className={`text-2xl font-bold font-mono mt-1 ${
                  account.total_return_pct >= 0 ? 'text-financial-profit' : 'text-financial-loss'
                }`}>
                  {account.total_return_pct >= 0 ? '+' : ''}{account.total_return_pct.toFixed(2)}%
                </div>
                <div className="text-[11px] text-text-secondary mt-1">
                  Baseline: ${account.initial_cash.toLocaleString()}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 2-Column: Order Blotter & Positions */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Order Ticket Console (4 cols) */}
          <div className="lg:col-span-4 space-y-6">
            <Card>
              <CardHeader className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-text-secondary" />
                <span className="font-medium text-sm text-text-primary">Order Execution Ticket</span>
              </CardHeader>
              <CardContent className="space-y-4 pt-3">
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setSide('BUY')}
                    className={`py-2 rounded text-xs font-mono font-semibold border transition-colors ${
                      side === 'BUY'
                        ? 'bg-financial-profit text-white border-financial-profit'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    BUY / LONG
                  </button>
                  <button
                    type="button"
                    onClick={() => setSide('SELL')}
                    className={`py-2 rounded text-xs font-mono font-semibold border transition-colors ${
                      side === 'SELL'
                        ? 'bg-financial-loss text-white border-financial-loss'
                        : 'bg-bg-surface-2 border-border-subtle text-text-muted'
                    }`}
                  >
                    SELL / CLOSE
                  </button>
                </div>

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
                      Quantity
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      min="0.01"
                      value={quantity}
                      onChange={(e) => setQuantity(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-mono text-text-secondary uppercase block mb-1">
                      Simulated Price ($)
                    </label>
                    <Input
                      type="number"
                      step="1"
                      value={price}
                      onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                {/* Pre-trade cost breakdown */}
                <div className="p-3 rounded bg-bg-surface-2 border border-border-subtle space-y-1.5 text-xs font-mono">
                  <div className="flex justify-between text-text-secondary">
                    <span>Gross Notional:</span>
                    <span className="text-text-primary font-medium">${estimatedNotional.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-text-secondary">
                    <span>Est. Slippage (5 bps):</span>
                    <span className="text-text-primary">${(estimatedNotional * 0.0005).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-text-secondary">
                    <span>Est. Commission (2 bps):</span>
                    <span className="text-text-primary">${(estimatedNotional * 0.0002).toFixed(2)}</span>
                  </div>
                  <div className="pt-1 border-t border-border-subtle flex justify-between text-text-primary font-semibold">
                    <span>Max Order Limit:</span>
                    <span className="text-accent-blue">$50,000.00</span>
                  </div>
                </div>

                <Button
                  onClick={handleOrderSubmit}
                  disabled={orderSubmitting || estimatedNotional <= 0 || estimatedNotional > 50_000}
                  className="w-full flex items-center justify-center gap-2"
                >
                  {orderSubmitting ? (
                    <>
                      <RotateCcw className="w-4 h-4 animate-spin" />
                      <span>Transacting...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Execute {side} Order</span>
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Active Positions & Order Blotter (8 cols) */}
          <div className="lg:col-span-8 space-y-6">
            {/* Open Positions */}
            <Card>
              <CardHeader className="flex items-center justify-between">
                <span className="font-medium text-sm text-text-primary">Open Positions Blotter</span>
                <Badge variant="neutral" className="text-xs font-mono">
                  {account?.positions.length || 0} Holdings
                </Badge>
              </CardHeader>
              <CardContent className="pt-2">
                {account && account.positions.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-border-subtle text-text-muted uppercase text-[11px]">
                          <th className="py-2.5 px-3">Symbol</th>
                          <th className="py-2.5 px-3">Side</th>
                          <th className="py-2.5 px-3">Quantity</th>
                          <th className="py-2.5 px-3">Avg Entry</th>
                          <th className="py-2.5 px-3">Current Px</th>
                          <th className="py-2.5 px-3 text-right">Unrealized PnL</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border-subtle/50">
                        {account.positions.map((pos) => (
                          <tr key={pos.id} className="hover:bg-bg-surface-2/40">
                            <td className="py-2.5 px-3 font-semibold text-text-primary">{pos.symbol}</td>
                            <td className="py-2.5 px-3">
                              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-financial-profitMuted text-financial-profit">
                                {pos.side}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-text-primary">{pos.quantity.toFixed(3)}</td>
                            <td className="py-2.5 px-3 text-text-secondary">${pos.entry_price.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-text-secondary">${pos.current_price.toFixed(2)}</td>
                            <td className="py-2.5 px-3 text-right font-semibold">
                              <span className={pos.unrealized_pnl >= 0 ? 'text-financial-profit' : 'text-financial-loss'}>
                                {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)} ({pos.pnl_pct.toFixed(2)}%)
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-text-muted">
                    No open positions in simulated portfolio. Place an order to establish holdings.
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Execution History */}
            <Card>
              <CardHeader className="flex items-center justify-between">
                <span className="font-medium text-sm text-text-primary">Execution Audit Blotter</span>
                <Badge variant="neutral" className="text-xs font-mono">
                  {account?.recent_orders.length || 0} Records
                </Badge>
              </CardHeader>
              <CardContent className="pt-2">
                {account && account.recent_orders.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-border-subtle text-text-muted uppercase text-[11px]">
                          <th className="py-2 px-3">Time</th>
                          <th className="py-2 px-3">Symbol</th>
                          <th className="py-2 px-3">Side</th>
                          <th className="py-2 px-3">Qty</th>
                          <th className="py-2 px-3">Fill Price</th>
                          <th className="py-2 px-3 text-right">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border-subtle/50">
                        {account.recent_orders.map((ord) => (
                          <tr key={ord.id} className="hover:bg-bg-surface-2/40">
                            <td className="py-2 px-3 text-text-muted">{ord.created_at.slice(0, 19)}</td>
                            <td className="py-2 px-3 font-medium text-text-primary">{ord.symbol}</td>
                            <td className="py-2 px-3">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                ord.side === 'BUY'
                                  ? 'bg-financial-profitMuted text-financial-profit'
                                  : 'bg-financial-lossMuted text-financial-loss'
                              }`}>
                                {ord.side}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-text-secondary">{ord.quantity.toFixed(3)}</td>
                            <td className="py-2 px-3 text-text-primary">
                              {ord.filled_price ? `$${ord.filled_price.toFixed(2)}` : '—'}
                            </td>
                            <td className="py-2 px-3 text-right">
                              <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                                ord.status === 'FILLED'
                                  ? 'bg-accent-green/10 text-accent-green border border-accent-green/30'
                                  : 'bg-accent-red/10 text-accent-red border border-accent-red/30'
                              }`}>
                                {ord.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="py-8 text-center text-xs text-text-muted">
                    No execution records in current session.
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Shell>
  );
}
