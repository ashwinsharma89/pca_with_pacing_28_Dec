/**
 * Real-Time Command Center - Live Campaign Monitoring
 * 
 * Features:
 * - Real-time data streaming (WebSocket)
 * - Live campaign monitoring
 * - Auto-refresh metrics
 * - Live alerts
 * - Budget pacing tracker
 * 
 * Usage:
 * Place in: frontend/src/app/real-time-command/page.tsx
 */

"use client";

import { useState, useEffect, useRef } from "react";
import {
  Activity, Zap, TrendingUp, TrendingDown, Play, Pause,
  AlertCircle, DollarSign, Target, Users, MousePointer,
  Bell, Settings, Download, RefreshCw, Maximize2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import dynamic from 'next/dynamic';

// Dynamic chart imports
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false });
const AreaChart = dynamic(() => import('recharts').then(mod => mod.AreaChart), { ssr: false });
const Area = dynamic(() => import('recharts').then(mod => mod.Area), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });

// ============================================================================
// TYPESCRIPT INTERFACES
// ============================================================================

interface LiveMetric {
  current: number;
  previous: number;
  change_percent: number;
  trend: 'up' | 'down' | 'stable';
  sparkline: number[];
}

interface CampaignStatus {
  id: string;
  name: string;
  platform: 'Google Ads' | 'Meta Ads' | 'LinkedIn' | 'TikTok';
  status: 'active' | 'paused' | 'warning' | 'critical';
  spend_today: number;
  daily_budget: number;
  pacing_percent: number;
  cpa: number;
  conversions: number;
  last_update: Date;
}

interface LiveAlert {
  id: string;
  timestamp: Date;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  campaign?: string;
  metric?: string;
}

interface StreamingDataPoint {
  time: string;
  value: number;
}

// ============================================================================
// MOCK DATA & STREAMING SIMULATION
// ============================================================================

const generateSparkline = (length: number = 20): number[] => {
  return Array.from({ length }, () => Math.random() * 100 + 50);
};

const INITIAL_CAMPAIGNS: CampaignStatus[] = [
  {
    id: 'camp-001',
    name: 'Black Friday - Google Shopping',
    platform: 'Google Ads',
    status: 'active',
    spend_today: 1245.50,
    daily_budget: 1500,
    pacing_percent: 83,
    cpa: 12.40,
    conversions: 98,
    last_update: new Date()
  },
  {
    id: 'camp-002',
    name: 'Holiday Sale - Meta Carousel',
    platform: 'Meta Ads',
    status: 'warning',
    spend_today: 890.20,
    daily_budget: 1000,
    pacing_percent: 89,
    cpa: 8.90,
    conversions: 142,
    last_update: new Date()
  },
  {
    id: 'camp-003',
    name: 'B2B Lead Gen - LinkedIn',
    platform: 'LinkedIn',
    status: 'active',
    spend_today: 340.00,
    daily_budget: 500,
    pacing_percent: 68,
    cpa: 45.20,
    conversions: 12,
    last_update: new Date()
  },
  {
    id: 'camp-004',
    name: 'Gen Z Awareness - TikTok',
    platform: 'TikTok',
    status: 'critical',
    spend_today: 520.80,
    daily_budget: 400,
    pacing_percent: 130,
    cpa: 3.20,
    conversions: 234,
    last_update: new Date()
  }
];

// ============================================================================
// LIVE METRICS HOOK
// ============================================================================

const useLiveMetrics = (isStreaming: boolean) => {
  const [metrics, setMetrics] = useState({
    spend: { current: 0, previous: 0, change_percent: 0, trend: 'up' as const, sparkline: generateSparkline() },
    conversions: { current: 0, previous: 0, change_percent: 0, trend: 'up' as const, sparkline: generateSparkline() },
    cpa: { current: 0, previous: 0, change_percent: 0, trend: 'down' as const, sparkline: generateSparkline() },
    ctr: { current: 0, previous: 0, change_percent: 0, trend: 'up' as const, sparkline: generateSparkline() }
  });

  const [campaigns, setCampaigns] = useState<CampaignStatus[]>([]);
  const [alerts, setAlerts] = useState<LiveAlert[]>([]);
  const [streamData, setStreamData] = useState<StreamingDataPoint[]>([]);
  const ws = useRef<WebSocket | null>(null);

  // Fetch initial snapshot on mount
  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/v1/realtime/snapshot', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          console.error('Failed to fetch snapshot');
          return;
        }

        const data = await response.json();

        // Update metrics
        if (data.metrics) {
          setMetrics({
            spend: { ...data.metrics.spend, sparkline: generateSparkline() },
            conversions: { ...data.metrics.conversions, sparkline: generateSparkline() },
            cpa: { ...data.metrics.cpa, sparkline: generateSparkline() },
            ctr: { ...data.metrics.ctr, sparkline: generateSparkline() }
          });
        }

        // Update campaigns
        if (data.campaigns) {
          setCampaigns(data.campaigns.map((c: any) => ({
            ...c,
            last_update: new Date(c.last_update)
          })));
        }

        // Update alerts
        if (data.alerts) {
          setAlerts(data.alerts.map((a: any) => ({
            ...a,
            timestamp: new Date(a.timestamp)
          })));
        }
      } catch (error) {
        console.error('Error fetching snapshot:', error);
      }
    };

    fetchSnapshot();
  }, []);

  // WebSocket connection for live updates
  useEffect(() => {
    if (!isStreaming) {
      ws.current?.close();
      return;
    }

    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/realtime/stream`;

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'metrics_update') {
          // Update metrics with sparkline preservation
          if (data.metrics) {
            setMetrics(prev => ({
              spend: {
                ...data.metrics.spend,
                sparkline: [...prev.spend.sparkline.slice(1), data.metrics.spend.current]
              },
              conversions: {
                ...data.metrics.conversions,
                sparkline: [...prev.conversions.sparkline.slice(1), data.metrics.conversions.current]
              },
              cpa: {
                ...data.metrics.cpa,
                sparkline: [...prev.cpa.sparkline.slice(1), data.metrics.cpa.current]
              },
              ctr: {
                ...data.metrics.ctr,
                sparkline: [...prev.ctr.sparkline.slice(1), data.metrics.ctr.current]
              }
            }));
          }

          // Update campaigns
          if (data.campaigns) {
            setCampaigns(data.campaigns.map((c: any) => ({
              ...c,
              last_update: new Date(c.last_update)
            })));
          }

          // Update alerts (prepend new alerts)
          if (data.alerts && data.alerts.length > 0) {
            setAlerts(prev => [
              ...data.alerts.map((a: any) => ({
                ...a,
                timestamp: new Date(a.timestamp)
              })),
              ...prev
            ].slice(0, 10)); // Keep last 10
          }

          // Update streaming chart
          const now = new Date();
          const timeStr = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          });

          setStreamData(prev => {
            const newData = [...prev, {
              time: timeStr,
              value: data.metrics?.spend?.current || 0
            }];
            return newData.slice(-30); // Keep last 30 points
          });
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.current?.close();
    };
  }, [isStreaming]);

  return { metrics, campaigns, alerts, streamData };
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function RealTimeCommandPage() {
  const [isStreaming, setIsStreaming] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const { metrics, campaigns, alerts, streamData } = useLiveMetrics(isStreaming);

  const getPacingColor = (percent: number) => {
    if (percent > 110) return 'text-red-600';
    if (percent > 90) return 'text-orange-600';
    if (percent < 70) return 'text-blue-600';
    return 'text-green-600';
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'Google Ads': return 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300';
      case 'Meta Ads': return 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300';
      case 'LinkedIn': return 'bg-cyan-100 text-cyan-700 dark:bg-cyan-950 dark:text-cyan-300';
      case 'TikTok': return 'bg-pink-100 text-pink-700 dark:bg-pink-950 dark:text-pink-300';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusBadge = (status: CampaignStatus['status']) => {
    switch (status) {
      case 'active': return <Badge className="bg-green-500">Active</Badge>;
      case 'paused': return <Badge variant="secondary">Paused</Badge>;
      case 'warning': return <Badge className="bg-orange-500">Warning</Badge>;
      case 'critical': return <Badge variant="destructive">Critical</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white p-4">
      <div className="container mx-auto space-y-4">

        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg">
                <Zap className="h-7 w-7 text-white" />
              </div>
              {isStreaming && (
                <div className="absolute -top-1 -right-1 h-4 w-4 bg-green-500 rounded-full animate-pulse border-2 border-slate-950" />
              )}
            </div>
            <div>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                Real-Time Command Center
                {isStreaming && <Badge className="bg-green-500 animate-pulse">LIVE</Badge>}
              </h1>
              <p className="text-sm text-slate-400">
                {new Date().toLocaleString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Switch
                checked={isStreaming}
                onCheckedChange={setIsStreaming}
                id="streaming"
              />
              <Label htmlFor="streaming" className="text-sm">
                {isStreaming ? 'Streaming' : 'Paused'}
              </Label>
            </div>

            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4 text-slate-400" />
              <Switch
                checked={soundEnabled}
                onCheckedChange={setSoundEnabled}
                id="sound"
              />
              <Label htmlFor="sound" className="text-sm">Sound</Label>
            </div>

            <Button variant="outline" size="sm" className="border-slate-700">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Live Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {Object.entries(metrics).map(([key, data]) => (
            <Card key={key} className="bg-slate-900 border-slate-800">
              <CardContent className="pt-6">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-400 uppercase tracking-wide">
                      {key === 'cpa' ? 'CPA' : key === 'ctr' ? 'CTR' : key.charAt(0).toUpperCase() + key.slice(1)}
                    </span>
                    {data.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4 text-green-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-red-500" />
                    )}
                  </div>

                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-bold">
                      {key === 'spend' || key === 'cpa' ? '$' : ''}
                      {data.current.toFixed(key === 'spend' ? 0 : key === 'conversions' ? 0 : 2)}
                      {key === 'ctr' ? '%' : ''}
                    </span>
                    <span className={`text-sm ${data.change_percent > 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {data.change_percent > 0 ? '+' : ''}{data.change_percent.toFixed(1)}%
                    </span>
                  </div>

                  <div className="h-12">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={data.sparkline.map((v, i) => ({ value: v }))}>
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke={data.trend === 'up' ? '#22c55e' : '#ef4444'}
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Live Stream Chart */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              Live Spend Stream (Last 60 seconds)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={streamData}>
                  <defs>
                    <linearGradient id="streamGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                    labelStyle={{ color: '#94a3b8' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#22c55e"
                    strokeWidth={2}
                    fill="url(#streamGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Campaigns & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

          {/* Campaign Monitor */}
          <Card className="lg:col-span-2 bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Active Campaigns ({campaigns.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {campaigns.map((campaign) => (
                  <div key={campaign.id} className="p-4 bg-slate-800 rounded-lg border border-slate-700">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">{campaign.name}</span>
                          {getStatusBadge(campaign.status)}
                        </div>
                        <Badge className={`text-xs ${getPlatformColor(campaign.platform)}`}>
                          {campaign.platform}
                        </Badge>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-slate-400">Updated</p>
                        <p className="text-xs">{campaign.last_update.toLocaleTimeString()}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-3">
                      <div>
                        <p className="text-xs text-slate-400">Spend</p>
                        <p className="text-lg font-semibold">${campaign.spend_today.toFixed(0)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Budget</p>
                        <p className="text-lg font-semibold">${campaign.daily_budget}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">CPA</p>
                        <p className="text-lg font-semibold">${campaign.cpa.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-400">Conv.</p>
                        <p className="text-lg font-semibold">{campaign.conversions}</p>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">Pacing</span>
                        <span className={`font-semibold ${getPacingColor(campaign.pacing_percent)}`}>
                          {campaign.pacing_percent.toFixed(0)}%
                        </span>
                      </div>
                      <Progress
                        value={campaign.pacing_percent}
                        className="h-2"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Live Alerts */}
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-orange-500" />
                Live Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 max-h-[500px] overflow-y-auto">
              {alerts.length === 0 && (
                <p className="text-sm text-slate-400 text-center py-8">
                  No alerts yet. Monitoring live...
                </p>
              )}
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`p-3 rounded-lg border ${alert.severity === 'critical'
                      ? 'bg-red-950 border-red-800'
                      : alert.severity === 'warning'
                        ? 'bg-orange-950 border-orange-800'
                        : 'bg-blue-950 border-blue-800'
                    }`}
                >
                  <div className="flex items-start gap-2">
                    <AlertCircle className={`h-4 w-4 mt-0.5 ${alert.severity === 'critical'
                        ? 'text-red-500'
                        : alert.severity === 'warning'
                          ? 'text-orange-500'
                          : 'text-blue-500'
                      }`} />
                    <div className="flex-1">
                      <p className="text-sm font-medium">{alert.message}</p>
                      {alert.campaign && (
                        <p className="text-xs text-slate-400 mt-1">{alert.campaign}</p>
                      )}
                      <p className="text-xs text-slate-500 mt-1">
                        {alert.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
