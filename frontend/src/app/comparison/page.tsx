"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
    ArrowLeft, Calendar, Loader2, TrendingUp, TrendingDown,
    BarChart3, RefreshCw, Info, ChevronLeft, ChevronRight,
    ArrowUpRight, ArrowDownRight, Scale
} from "lucide-react";
import { format, subDays, startOfDay, endOfDay, differenceInDays, isSameDay } from "date-fns";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DateRangePicker } from "@/components/ui/date-range-picker";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import dynamic from 'next/dynamic';
import { DateRange } from "react-day-picker";

// Recharts imports
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const RechartsBarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const RechartsLineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });

const CHART_COLORS = {
    current: '#6366f1', // Indigo
    previous: '#94a3b8', // Slate
};

interface ComparisonData {
    dimension: string;
    current: number;
    previous: number;
    delta: number;
    deltaPercent: number;
}

export default function ComparisonPage() {
    const { token, isLoading: authLoading } = useAuth();
    const router = useRouter();

    const [loading, setLoading] = useState(false);
    const [dateRange, setDateRange] = useState<DateRange | undefined>({
        from: subDays(new Date(), 7),
        to: new Date(),
    });
    const [comparisonMode, setComparisonMode] = useState<'auto' | 'preset' | 'custom'>('auto');
    const [preset, setPreset] = useState<string>('last_7_vs_prev_7');
    const [comparisonDateRange, setComparisonDateRange] = useState<DateRange | undefined>();

    const [dimension, setDimension] = useState<string>("platform");
    const [metric, setMetric] = useState<string>("spend");
    const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
    const [summaryMetrics, setSummaryMetrics] = useState<any>(null);

    // Auth Guard
    useEffect(() => {
        if (!authLoading && !token) router.push("/login");
    }, [authLoading, token, router]);

    // Calculate date ranges based on preset
    const calculatePresetRanges = useCallback((presetValue: string): { current: DateRange, comparison: DateRange } => {
        const today = new Date();
        const ranges: Record<string, { current: DateRange, comparison: DateRange }> = {
            'last_7_vs_prev_7': {
                current: { from: subDays(today, 6), to: today },
                comparison: { from: subDays(today, 13), to: subDays(today, 7) }
            },
            'last_30_vs_prev_30': {
                current: { from: subDays(today, 29), to: today },
                comparison: { from: subDays(today, 59), to: subDays(today, 30) }
            },
            'last_2_months_vs_prev_2_months': {
                current: { from: subDays(today, 60), to: today },
                comparison: { from: subDays(today, 120), to: subDays(today, 61) }
            },
            'last_3_months_vs_prev_3_months': {
                current: { from: subDays(today, 90), to: today },
                comparison: { from: subDays(today, 180), to: subDays(today, 91) }
            },
        };
        return ranges[presetValue] || ranges['last_7_vs_prev_7'];
    }, []);

    // Update date ranges when preset changes
    useEffect(() => {
        if (comparisonMode === 'preset') {
            const ranges = calculatePresetRanges(preset);
            setDateRange(ranges.current);
            setComparisonDateRange(ranges.comparison);
        }
    }, [comparisonMode, preset, calculatePresetRanges]);

    const fetchData = useCallback(async () => {
        if (!dateRange?.from || !dateRange?.to) return;

        setLoading(true);
        try {
            const start = format(dateRange.from, 'yyyy-MM-dd');
            const end = format(dateRange.to, 'yyyy-MM-dd');

            let prevStart: string;
            let prevEnd: string;

            // Calculate comparison period based on mode
            if (comparisonMode === 'custom' && comparisonDateRange?.from && comparisonDateRange?.to) {
                // Custom mode: use user-selected comparison range
                prevStart = format(comparisonDateRange.from, 'yyyy-MM-dd');
                prevEnd = format(comparisonDateRange.to, 'yyyy-MM-dd');
            } else {
                // Auto mode or Preset mode: calculate previous period of same length
                const daysDiff = differenceInDays(dateRange.to, dateRange.from) + 1;
                prevStart = format(subDays(dateRange.from, daysDiff), 'yyyy-MM-dd');
                prevEnd = format(subDays(dateRange.from, 1), 'yyyy-MM-dd');
            }

            // Fetch Current Period
            const currentParams = new URLSearchParams({
                x_axis: dimension,
                y_axis: metric,
                start_date: start,
                end_date: end,
            });
            const currentRes: any = await api.get(`/campaigns/chart-data?${currentParams}`);
            const currentItems = currentRes.data || [];

            // Fetch Previous Period
            const prevParams = new URLSearchParams({
                x_axis: dimension,
                y_axis: metric,
                start_date: prevStart,
                end_date: prevEnd,
            });
            const prevRes: any = await api.get(`/campaigns/chart-data?${prevParams}`);
            const prevItems = prevRes.data || [];

            // Merge Data
            const merged: Record<string, ComparisonData> = {};

            currentItems.forEach((item: any) => {
                const dim = item[dimension] || 'Unknown';
                const val = item[metric] || 0;
                merged[dim] = {
                    dimension: dim,
                    current: val,
                    previous: 0,
                    delta: 0,
                    deltaPercent: 0
                };
            });

            prevItems.forEach((item: any) => {
                const dim = item[dimension] || 'Unknown';
                const val = item[metric] || 0;
                if (!merged[dim]) {
                    merged[dim] = {
                        dimension: dim,
                        current: 0,
                        previous: val,
                        delta: 0,
                        deltaPercent: 0
                    };
                } else {
                    merged[dim].previous = val;
                }
            });

            // Calculate Deltas
            const finalData = Object.values(merged).map(item => {
                const delta = item.current - item.previous;
                const deltaPercent = item.previous !== 0 ? (delta / item.previous) * 100 : (item.current !== 0 ? 100 : 0);
                return { ...item, delta, deltaPercent };
            }).sort((a, b) => b.current - a.current);

            setComparisonData(finalData);

            // Summary Totals
            const totalCurrent = finalData.reduce((sum, item) => sum + item.current, 0);
            const totalPrevious = finalData.reduce((sum, item) => sum + item.previous, 0);
            const totalDelta = totalCurrent - totalPrevious;
            const totalDeltaPercent = totalPrevious !== 0 ? (totalDelta / totalPrevious) * 100 : (totalCurrent !== 0 ? 100 : 0);

            setSummaryMetrics({
                current: totalCurrent,
                previous: totalPrevious,
                delta: totalDelta,
                deltaPercent: totalDeltaPercent,
                prevStart,
                prevEnd
            });

        } catch (error) {
            console.error("Failed to fetch comparison data", error);
        } finally {
            setLoading(false);
        }
    }, [dateRange, comparisonDateRange, comparisonMode, dimension, metric]);

    useEffect(() => {
        if (token && dateRange?.from && dateRange?.to) {
            fetchData();
        }
    }, [token, dateRange, comparisonDateRange, comparisonMode, dimension, metric, fetchData]);

    const formatValue = (val: number) => {
        if (metric === 'spend' || metric === 'cpc' || metric === 'cpa') {
            return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
        if (metric === 'ctr' || metric === 'roas') {
            return `${val.toFixed(2)}${metric === 'ctr' ? '%' : ''}`;
        }
        return val.toLocaleString();
    };

    if (authLoading) return <div className="flex h-screen items-center justify-center bg-background"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    if (!token) return null;

    return (
        <div className="container mx-auto py-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
                        <Scale className="inline-block mr-2 h-8 w-8 text-indigo-500" />
                        Performance Comparison
                    </h1>
                    <p className="text-muted-foreground text-sm">Compare campaign performance between two time periods</p>
                </div>
                <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                </Button>
            </div>

            {/* Controls */}
            <Card>
                <CardContent className="py-4">
                    <div className="space-y-4">
                        {/* Comparison Mode Selector */}
                        <div className="space-y-1">
                            <Label className="text-xs font-semibold">Comparison Mode</Label>
                            <div className="flex gap-2">
                                <Button
                                    variant={comparisonMode === 'auto' ? 'default' : 'outline'}
                                    size="sm"
                                    onClick={() => setComparisonMode('auto')}
                                    className="flex-1"
                                >
                                    Auto
                                </Button>
                                <Button
                                    variant={comparisonMode === 'preset' ? 'default' : 'outline'}
                                    size="sm"
                                    onClick={() => setComparisonMode('preset')}
                                    className="flex-1"
                                >
                                    Presets
                                </Button>
                                <Button
                                    variant={comparisonMode === 'custom' ? 'default' : 'outline'}
                                    size="sm"
                                    onClick={() => setComparisonMode('custom')}
                                    className="flex-1"
                                >
                                    Custom
                                </Button>
                            </div>
                        </div>

                        {/* Preset Selector (shown when preset mode) */}
                        {comparisonMode === 'preset' && (
                            <div className="space-y-1">
                                <Label className="text-xs">Quick Compare</Label>
                                <Select value={preset} onValueChange={setPreset}>
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="last_7_vs_prev_7">Last 7 days vs Previous 7 days</SelectItem>
                                        <SelectItem value="last_30_vs_prev_30">Last 30 days vs Previous 30 days</SelectItem>
                                        <SelectItem value="last_2_months_vs_prev_2_months">Last 2 months vs Previous 2 months</SelectItem>
                                        <SelectItem value="last_3_months_vs_prev_3_months">Last 3 months vs Previous 3 months</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        )}

                        {/* Date Range Pickers */}
                        <div className="flex flex-wrap gap-4 items-end">
                            {comparisonMode === 'custom' ? (
                                <>
                                    <div className="space-y-1 min-w-[250px]">
                                        <Label className="text-xs">Period A (Current)</Label>
                                        <DateRangePicker
                                            date={dateRange}
                                            onDateChange={setDateRange}
                                        />
                                    </div>
                                    <div className="space-y-1 min-w-[250px]">
                                        <Label className="text-xs">Period B (Comparison)</Label>
                                        <DateRangePicker
                                            date={comparisonDateRange}
                                            onDateChange={setComparisonDateRange}
                                        />
                                    </div>
                                </>
                            ) : (
                                <div className="space-y-1 min-w-[250px]">
                                    <Label className="text-xs">
                                        {comparisonMode === 'preset' ? 'Date Ranges (Auto-calculated)' : 'Analysis Period'}
                                    </Label>
                                    <DateRangePicker
                                        date={dateRange}
                                        onDateChange={setDateRange}
                                    />
                                </div>
                            )}
                            <div className="space-y-1 min-w-[150px]">
                                <Label className="text-xs">Compare By (X-Axis)</Label>
                                <Select value={dimension} onValueChange={setDimension}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="platform">Platform</SelectItem>
                                        <SelectItem value="channel">Channel</SelectItem>
                                        <SelectItem value="funnel_stage">Funnel Stage</SelectItem>
                                        <SelectItem value="objective">Objective</SelectItem>
                                        <SelectItem value="status">Status</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-1 min-w-[150px]">
                                <Label className="text-xs">Metric (Y-Axis)</Label>
                                <Select value={metric} onValueChange={setMetric}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="spend">Spend ($)</SelectItem>
                                        <SelectItem value="impressions">Impressions</SelectItem>
                                        <SelectItem value="clicks">Clicks</SelectItem>
                                        <SelectItem value="conversions">Conversions</SelectItem>
                                        <SelectItem value="ctr">CTR (%)</SelectItem>
                                        <SelectItem value="cpc">CPC ($)</SelectItem>
                                        <SelectItem value="cpa">CPA ($)</SelectItem>
                                        <SelectItem value="roas">ROAS</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Summary KPI */}
            {summaryMetrics && (
                <div className="grid gap-4 md:grid-cols-3">
                    <Card className="bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border-indigo-500/20">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">Current Period Total</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{formatValue(summaryMetrics.current)}</div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {dateRange?.from && format(dateRange.from, 'MMM d')} - {dateRange?.to && format(dateRange.to, 'MMM d, yyyy')}
                            </p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">Previous Period Total</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-muted-foreground">{formatValue(summaryMetrics.previous)}</div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {summaryMetrics.prevStart && format(new Date(summaryMetrics.prevStart), 'MMM d')} - {summaryMetrics.prevEnd && format(new Date(summaryMetrics.prevEnd), 'MMM d, yyyy')}
                            </p>
                        </CardContent>
                    </Card>
                    <Card className={`border-l-4 ${summaryMetrics.deltaPercent >= 0 ? 'border-l-green-500' : 'border-l-red-500'}`}>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-muted-foreground">Total Change</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold flex items-center gap-2 ${summaryMetrics.deltaPercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                {summaryMetrics.deltaPercent >= 0 ? <ArrowUpRight /> : <ArrowDownRight />}
                                {Math.abs(summaryMetrics.deltaPercent).toFixed(1)}%
                            </div>
                            <p className="text-xs text-muted-foreground mt-1">
                                {summaryMetrics.delta >= 0 ? '+' : ''}{formatValue(summaryMetrics.delta)} in total
                            </p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Main Comparison Chart */}
            <div className="grid gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            Comparison Chart
                            <div className="flex items-center gap-4 text-xs font-normal">
                                <div className="flex items-center gap-1">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS.current }}></div>
                                    Current Period
                                </div>
                                <div className="flex items-center gap-1">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: CHART_COLORS.previous }}></div>
                                    Previous Period
                                </div>
                            </div>
                        </CardTitle>
                        <CardDescription>Side-by-side view of {metric} across {dimension}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="flex items-center justify-center h-[400px]">
                                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            </div>
                        ) : (
                            <div className="h-[400px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <RechartsBarChart data={comparisonData}>
                                        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                        <XAxis dataKey="dimension" className="text-xs" />
                                        <YAxis className="text-xs" />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)', borderRadius: '8px' }}
                                            formatter={(value: any) => [formatValue(value), '']}
                                        />
                                        <Legend />
                                        <Bar dataKey="current" name="Current" fill={CHART_COLORS.current} radius={[4, 4, 0, 0]} />
                                        <Bar dataKey="previous" name="Previous" fill={CHART_COLORS.previous} radius={[4, 4, 0, 0]} />
                                    </RechartsBarChart>
                                </ResponsiveContainer>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Detailed Data Table */}
                <Card>
                    <CardHeader>
                        <CardTitle>Detailed Comparison Breakdown</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="rounded-md border">
                            <table className="w-full text-sm">
                                <thead className="bg-muted/50">
                                    <tr className="border-b">
                                        <th className="px-4 py-3 text-left font-medium">{dimension.charAt(0).toUpperCase() + dimension.slice(1).replace('_', ' ')}</th>
                                        <th className="px-4 py-3 text-right font-medium">Previous Period</th>
                                        <th className="px-4 py-3 text-right font-medium">Current Period</th>
                                        <th className="px-4 py-3 text-right font-medium">Change (%)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {comparisonData.map((item, idx) => (
                                        <tr key={idx} className="border-b hover:bg-muted/30 transition-colors">
                                            <td className="px-4 py-3 font-medium">{item.dimension}</td>
                                            <td className="px-4 py-3 text-right text-muted-foreground">{formatValue(item.previous)}</td>
                                            <td className="px-4 py-3 text-right font-bold">{formatValue(item.current)}</td>
                                            <td className={`px-4 py-3 text-right font-medium ${item.deltaPercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                <div className="flex items-center justify-end gap-1">
                                                    {item.deltaPercent >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                                                    {Math.abs(item.deltaPercent).toFixed(1)}%
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                    {comparisonData.length === 0 && !loading && (
                                        <tr>
                                            <td colSpan={4} className="px-4 py-8 text-center text-muted-foreground">
                                                No comparison data available for the selected range.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
