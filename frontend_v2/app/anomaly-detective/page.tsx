/**
 * Anomaly Detective - AI-Powered Anomaly Detection
 * 
 * Features:
 * - Real-time anomaly detection
 * - Root cause analysis
 * - Historical anomaly timeline
 * - Impact quantification
 * - Smart alerting
 * 
 * Usage:
 * Place in: frontend/src/app/anomaly-detective/page.tsx
 */

"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle, TrendingUp, TrendingDown, Search, Filter,
  Clock, DollarSign, Activity, Zap, Bell, CheckCircle2,
  XCircle, Info, Calendar, ArrowUpRight, ArrowDownRight
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import dynamic from 'next/dynamic';
import { format, subDays } from "date-fns";
import { anomalyApi } from "@/lib/api";

// Dynamic chart imports
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false });
const Area = dynamic(() => import('recharts').then(mod => mod.Area), { ssr: false });
const AreaChart = dynamic(() => import('recharts').then(mod => mod.AreaChart), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const ReferenceLine = dynamic(() => import('recharts').then(mod => mod.ReferenceLine), { ssr: false });
const ReferenceDot = dynamic(() => import('recharts').then(mod => mod.ReferenceDot), { ssr: false });

// ============================================================================
// TYPESCRIPT INTERFACES
// ============================================================================

interface Anomaly {
  id: string;
  metric: string;
  timestamp: string; // From API as string
  value: number;
  expected_value: number;
  deviation_percent: number;
  severity: 'critical' | 'warning' | 'info'; // Updated to match backend
  status: 'active' | 'investigating' | 'resolved';
  impact_usd: number;
  root_causes: RootCause[];
  recommendations: string[];
  affected_campaigns: string[];
}

interface AnomalyResponse {
  anomalies: Anomaly[];
  total_count: number;
  critical_count: number;
  warning_count: number;
  total_impact_usd: number;
}

interface RootCause {
  factor: string;
  confidence: number; // 0-100
  explanation: string;
  supporting_data?: any;
}

interface TimeSeriesPoint {
  timestamp: string;
  value: number;
  expected?: number;
  anomaly?: boolean;
  upper_bound?: number;
  lower_bound?: number;
}

// ============================================================================
// MOCK DATA (Only for time series visualization)
// ============================================================================

const generateMockTimeSeries = (): TimeSeriesPoint[] => {
  const data: TimeSeriesPoint[] = [];
  const now = new Date();

  for (let i = 30; i >= 0; i--) {
    const date = subDays(now, i);
    const baseValue = 2.5 + Math.sin(i / 3) * 0.3;
    const noise = (Math.random() - 0.5) * 0.2;
    let value = baseValue + noise;

    // Create spike anomaly at day 5
    if (i === 5) value = 4.5;
    // Create drop anomaly at day 15
    if (i === 15) value = 1.2;

    data.push({
      timestamp: format(date, 'MMM dd'),
      value: parseFloat(value.toFixed(2)),
      expected: parseFloat(baseValue.toFixed(2)),
      anomaly: i === 5 || i === 15,
      upper_bound: parseFloat((baseValue + 0.5).toFixed(2)),
      lower_bound: parseFloat((baseValue - 0.5).toFixed(2))
    });
  }

  return data;
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function AnomalyDetectivePage() {
  const [selectedMetric, setSelectedMetric] = useState<string>('all');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesPoint[]>([]);

  // Fetch anomalies from real API
  const { data: apiResponse, isLoading, error } = useQuery({
    queryKey: ['anomalies', selectedMetric, selectedSeverity],
    queryFn: async (): Promise<AnomalyResponse> => {
      return anomalyApi.detect({
        severity: selectedSeverity !== 'all' ? selectedSeverity : undefined,
        days: 7
      });
    }
  });

  const anomalies = apiResponse?.anomalies || [];
  const stats = {
    total: apiResponse?.total_count || 0,
    critical: apiResponse?.critical_count || 0,
    warning: apiResponse?.warning_count || 0,
    impact: apiResponse?.total_impact_usd || 0
  };


  // Generate time series for selected anomaly
  useEffect(() => {
    setTimeSeriesData(generateMockTimeSeries());
  }, [selectedAnomaly]);

  // Get severity color
  const getSeverityColor = (severity: Anomaly['severity']) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-slate-600 bg-slate-50 border-slate-200';
    }
  };

  const getSeverityBadgeVariant = (severity: Anomaly['severity']): "default" | "secondary" | "destructive" | "outline" => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'warning': return 'default';
      case 'info': return 'outline';
      default: return 'secondary';
    }
  };

  const getStatusIcon = (status: Anomaly['status']) => {
    switch (status) {
      case 'active': return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'investigating': return <Search className="h-4 w-4 text-orange-600" />;
      case 'resolved': return <CheckCircle2 className="h-4 w-4 text-green-600" />;
    }
  };

  // Count active anomalies
  const activeCount = anomalies.filter(a => a.status === 'active').length;
  const criticalCount = anomalies.filter(a => a.severity === 'critical').length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
      <div className="container mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-red-500 to-orange-600 rounded-lg">
              <Zap className="h-7 w-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Anomaly Detective</h1>
              <p className="text-muted-foreground">AI-powered anomaly detection and root cause analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={criticalCount > 0 ? "destructive" : "secondary"} className="text-lg px-4 py-2">
              <Bell className="h-4 w-4 mr-2" />
              {activeCount} Active
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Critical Anomalies</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold text-red-600">{stats.critical}</span>
                <AlertTriangle className="h-8 w-8 text-red-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Impact</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold">
                  ${(stats.impact / 1000).toFixed(1)}K
                </span>
                <DollarSign className="h-8 w-8 text-orange-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Avg Detection Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold">2.3m</span>
                <Clock className="h-8 w-8 text-blue-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Resolution Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-3xl font-bold">87%</span>
                <Activity className="h-8 w-8 text-green-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Filters:</span>
              </div>
              <Select value={selectedMetric} onValueChange={setSelectedMetric}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Metric" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Metrics</SelectItem>
                  <SelectItem value="CPC (Cost Per Click)">CPC</SelectItem>
                  <SelectItem value="Conversion Rate">Conversion Rate</SelectItem>
                  <SelectItem value="CTR (Click-Through Rate)">CTR</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severities</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Anomalies List & Detail */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Anomalies List */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Detected Anomalies</CardTitle>
              <CardDescription>{anomalies.length} total anomalies found</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 max-h-[600px] overflow-y-auto">
              {anomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  onClick={() => setSelectedAnomaly(anomaly)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${selectedAnomaly?.id === anomaly.id ? 'ring-2 ring-indigo-500 bg-indigo-50 dark:bg-indigo-950' : ''
                    } ${getSeverityColor(anomaly.severity)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(anomaly.status)}
                      <span className="font-medium text-sm">{anomaly.metric}</span>
                    </div>
                    <Badge variant={getSeverityBadgeVariant(anomaly.severity)} className="text-xs">
                      {anomaly.severity}
                    </Badge>
                  </div>

                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Calendar className="h-3 w-3" />
                      {format(anomaly.timestamp, 'MMM dd, h:mm a')}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold">
                        {anomaly.deviation_percent > 0 ? '+' : ''}{anomaly.deviation_percent.toFixed(1)}%
                      </span>
                      {anomaly.deviation_percent > 0 ? (
                        <ArrowUpRight className="h-5 w-5 text-red-600" />
                      ) : (
                        <ArrowDownRight className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div className="text-xs">
                      Impact: <span className="font-semibold">${anomaly.impact_usd.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Anomaly Detail */}
          <Card className="lg:col-span-2">
            {selectedAnomaly ? (
              <>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-2xl">{selectedAnomaly.metric}</CardTitle>
                      <CardDescription>
                        Detected {format(selectedAnomaly.timestamp, 'MMM dd, yyyy HH:mm')}
                      </CardDescription>
                    </div>
                    <Badge variant={getSeverityBadgeVariant(selectedAnomaly.severity)} className="text-sm px-3 py-1">
                      {selectedAnomaly.severity.toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">

                  {/* Time Series Chart */}
                  <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
                    <h3 className="font-semibold mb-3 text-sm">Metric Timeline (Last 30 Days)</h3>
                    <ResponsiveContainer width="100%" height={250}>
                      <AreaChart data={timeSeriesData}>
                        <defs>
                          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip />
                        <Area
                          type="monotone"
                          dataKey="upper_bound"
                          stroke="none"
                          fill="#e2e8f0"
                          fillOpacity={0.3}
                        />
                        <Area
                          type="monotone"
                          dataKey="lower_bound"
                          stroke="none"
                          fill="#e2e8f0"
                          fillOpacity={0.3}
                        />
                        <Line
                          type="monotone"
                          dataKey="expected"
                          stroke="#94a3b8"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                        />
                        <Area
                          type="monotone"
                          dataKey="value"
                          stroke="#6366f1"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#colorValue)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Impact Summary */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-red-50 dark:bg-red-950 rounded-lg border border-red-200 dark:border-red-800">
                      <p className="text-xs text-muted-foreground mb-1">Actual Value</p>
                      <p className="text-2xl font-bold text-red-600">${selectedAnomaly.value}</p>
                    </div>
                    <div className="text-center p-4 bg-slate-100 dark:bg-slate-800 rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Expected Value</p>
                      <p className="text-2xl font-bold">${selectedAnomaly.expected_value}</p>
                    </div>
                    <div className="text-center p-4 bg-orange-50 dark:bg-orange-950 rounded-lg border border-orange-200 dark:border-orange-800">
                      <p className="text-xs text-muted-foreground mb-1">Financial Impact</p>
                      <p className="text-2xl font-bold text-orange-600">${selectedAnomaly.impact_usd.toLocaleString()}</p>
                    </div>
                  </div>

                  {/* Root Cause Analysis */}
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <Search className="h-5 w-5 text-indigo-600" />
                      Root Cause Analysis
                    </h3>
                    {selectedAnomaly.root_causes.map((cause, idx) => (
                      <div key={idx} className="border rounded-lg p-4 bg-slate-50 dark:bg-slate-900">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium">{cause.factor}</span>
                          <Badge variant="outline" className="text-xs">
                            {cause.confidence}% confidence
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{cause.explanation}</p>
                        {cause.supporting_data && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {Object.entries(cause.supporting_data as Record<string, any>).map(([key, value]) => (
                              <Badge key={key} variant="secondary" className="text-xs">
                                {key}: {String(value)}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Recommendations */}
                  <div className="space-y-3">
                    <h3 className="font-semibold flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      Recommended Actions
                    </h3>
                    <ul className="space-y-2">
                      {selectedAnomaly.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                          <span className="text-green-600 mt-0.5 font-bold">{idx + 1}.</span>
                          <span className="text-sm flex-1">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Affected Campaigns */}
                  <div className="space-y-2">
                    <h3 className="font-semibold text-sm">Affected Campaigns ({selectedAnomaly.affected_campaigns.length})</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedAnomaly.affected_campaigns.map((campaign, idx) => (
                        <Badge key={idx} variant="outline">
                          {campaign}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t">
                    <Button className="flex-1">
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                      Mark as Resolved
                    </Button>
                    <Button variant="outline" className="flex-1">
                      <Bell className="h-4 w-4 mr-2" />
                      Set Alert
                    </Button>
                  </div>

                </CardContent>
              </>
            ) : (
              <CardContent className="flex items-center justify-center h-96">
                <div className="text-center space-y-3">
                  <Info className="h-12 w-12 text-muted-foreground mx-auto opacity-50" />
                  <p className="text-muted-foreground">
                    Select an anomaly to view detailed analysis
                  </p>
                </div>
              </CardContent>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
