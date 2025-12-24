/**
 * Comparison 2.0 - Advanced Multi-Period Performance Analysis
 * 
 * NEW FEATURES vs V1:
 * - Multi-period comparison (compare Q1, Q2, Q3, Q4 simultaneously)
 * - Statistical significance testing
 * - Seasonality adjustment
 * - Cohort analysis
 * - A/B test analysis
 * - Export comparison reports
 * - Waterfall charts for variance analysis
 * 
 * Usage:
 * Place in: frontend/src/app/comparison-2/page.tsx
 */

"use client";

import { useState, useEffect } from "react";
import {
    Scale, TrendingUp, TrendingDown, Calendar, Filter,
    Download, RefreshCw, AlertCircle, CheckCircle2,
    BarChart3, Activity, Sparkles, Info
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import dynamic from 'next/dynamic';
import { format, subDays, startOfQuarter, endOfQuarter, startOfMonth, endOfMonth } from "date-fns";

// Dynamic chart imports
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const LineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false });
const ComposedChart = dynamic(() => import('recharts').then(mod => mod.ComposedChart), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });
const ReferenceLine = dynamic(() => import('recharts').then(mod => mod.ReferenceLine), { ssr: false });
const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), { ssr: false });

// ============================================================================
// TYPESCRIPT INTERFACES
// ============================================================================

interface PeriodData {
    period: string;
    label: string;
    value: number;
    expected?: number;
    variance?: number;
    variancePercent?: number;
}

interface StatisticalTest {
    metric: string;
    pValue: number;
    isSignificant: boolean;
    confidenceLevel: number;
    interpretation: string;
}

interface CohortData {
    cohort: string;
    retention: number[];
    conversion: number[];
}

// ============================================================================
// MOCK DATA GENERATORS
// ============================================================================

const generateMultiPeriodData = (metric: string, dimension: string): PeriodData[] => {
    const periods = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'];
    const baseValue = metric === 'spend' ? 50000 : metric === 'conversions' ? 800 : 3.5;

    return periods.map((period, idx) => {
        const seasonality = 1 + Math.sin((idx / periods.length) * Math.PI) * 0.2;
        const growth = 1 + (idx * 0.1);
        const value = baseValue * seasonality * growth;
        const expected = baseValue * growth;

        return {
            period,
            label: period,
            value: parseFloat(value.toFixed(2)),
            expected: parseFloat(expected.toFixed(2)),
            variance: parseFloat((value - expected).toFixed(2)),
            variancePercent: parseFloat(((value - expected) / expected * 100).toFixed(1))
        };
    });
};

const generateCohortData = (): CohortData[] => {
    const cohorts = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];

    return cohorts.map((cohort, idx) => ({
        cohort,
        retention: [100, 85, 72, 65, 58, 52, 48, 45].map(v => v - (idx * 2)),
        conversion: [5, 7, 9, 11, 12, 13, 14, 15].map(v => v + (idx * 0.5))
    }));
};

const generateStatisticalTests = (metric: string): StatisticalTest[] => {
    return [
        {
            metric: `${metric} - Q3 vs Q4`,
            pValue: 0.023,
            isSignificant: true,
            confidenceLevel: 95,
            interpretation: 'Statistically significant improvement in Q4 (p < 0.05)'
        },
        {
            metric: `${metric} - Q2 vs Q3`,
            pValue: 0.156,
            isSignificant: false,
            confidenceLevel: 95,
            interpretation: 'No significant difference detected (p > 0.05)'
        }
    ];
};

// ============================================================================
// VARIANCE WATERFALL DATA
// ============================================================================

const generateWaterfallData = (metric: string): any[] => {
    const baseValue = metric === 'spend' ? 50000 : 800;

    return [
        { name: 'Q3 Actual', value: baseValue, type: 'base' },
        { name: 'Platform Change', value: baseValue * 0.15, type: 'increase' },
        { name: 'Creative Refresh', value: baseValue * 0.08, type: 'increase' },
        { name: 'Budget Cut', value: -baseValue * 0.05, type: 'decrease' },
        { name: 'Seasonal Effect', value: baseValue * 0.12, type: 'increase' },
        { name: 'Q4 Actual', value: baseValue * 1.3, type: 'total' }
    ];
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function Comparison2Page() {
    const [comparisonMode, setComparisonMode] = useState<'multi-period' | 'ab-test' | 'cohort'>('multi-period');
    const [dimension, setDimension] = useState<string>('platform');
    const [metric, setMetric] = useState<string>('spend');
    const [selectedPeriods, setSelectedPeriods] = useState<string[]>(['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']);

    const [multiPeriodData, setMultiPeriodData] = useState<PeriodData[]>([]);
    const [waterfallData, setWaterfallData] = useState<any[]>([]);
    const [statisticalTests, setStatisticalTests] = useState<StatisticalTest[]>([]);
    const [cohortData, setCohortData] = useState<CohortData[]>([]);

    useEffect(() => {
        // Load data based on mode
        setMultiPeriodData(generateMultiPeriodData(metric, dimension));
        setWaterfallData(generateWaterfallData(metric));
        setStatisticalTests(generateStatisticalTests(metric));
        setCohortData(generateCohortData());
    }, [metric, dimension, comparisonMode]);

    const formatValue = (value: number) => {
        if (metric === 'spend' || metric === 'cpc' || metric === 'cpa') {
            return `$${value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
        }
        if (metric === 'ctr' || metric === 'roas') {
            return `${value.toFixed(2)}${metric === 'ctr' ? '%' : ''}`;
        }
        return value.toLocaleString();
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
            <div className="container mx-auto space-y-6">

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
                            <Scale className="h-7 w-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold">Advanced Comparison 2.0</h1>
                            <p className="text-muted-foreground">Multi-period analysis with statistical insights</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-2" />
                            Export
                        </Button>
                        <Button variant="outline" size="sm">
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Refresh
                        </Button>
                    </div>
                </div>

                {/* Comparison Mode Tabs */}
                <Tabs value={comparisonMode} onValueChange={(v: any) => setComparisonMode(v)}>
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="multi-period">
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Multi-Period
                        </TabsTrigger>
                        <TabsTrigger value="ab-test">
                            <Activity className="h-4 w-4 mr-2" />
                            A/B Test
                        </TabsTrigger>
                        <TabsTrigger value="cohort">
                            <Sparkles className="h-4 w-4 mr-2" />
                            Cohort Analysis
                        </TabsTrigger>
                    </TabsList>

                    {/* MULTI-PERIOD COMPARISON */}
                    <TabsContent value="multi-period" className="space-y-6">

                        {/* Filters */}
                        <Card>
                            <CardContent className="pt-6">
                                <div className="grid grid-cols-4 gap-4">
                                    <div>
                                        <Label>Dimension</Label>
                                        <Select value={dimension} onValueChange={setDimension}>
                                            <SelectTrigger><SelectValue /></SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="platform">Platform</SelectItem>
                                                <SelectItem value="campaign">Campaign</SelectItem>
                                                <SelectItem value="channel">Channel</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div>
                                        <Label>Metric</Label>
                                        <Select value={metric} onValueChange={setMetric}>
                                            <SelectTrigger><SelectValue /></SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="spend">Spend</SelectItem>
                                                <SelectItem value="conversions">Conversions</SelectItem>
                                                <SelectItem value="cpa">CPA</SelectItem>
                                                <SelectItem value="roas">ROAS</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="col-span-2">
                                        <Label>Compare Periods</Label>
                                        <div className="flex gap-2 mt-2">
                                            {['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'].map(period => (
                                                <Badge
                                                    key={period}
                                                    variant={selectedPeriods.includes(period) ? 'default' : 'outline'}
                                                    className="cursor-pointer"
                                                    onClick={() => {
                                                        setSelectedPeriods(prev =>
                                                            prev.includes(period)
                                                                ? prev.filter(p => p !== period)
                                                                : [...prev, period]
                                                        );
                                                    }}
                                                >
                                                    {period}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Summary Cards */}
                        <div className="grid grid-cols-4 gap-4">
                            {multiPeriodData.map((period, idx) => (
                                <Card key={period.period}>
                                    <CardHeader className="pb-3">
                                        <CardTitle className="text-sm font-medium text-muted-foreground">
                                            {period.period}
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-2">
                                            <div className="flex items-baseline justify-between">
                                                <span className="text-2xl font-bold">{formatValue(period.value)}</span>
                                                {period.variancePercent !== undefined && (
                                                    <Badge variant={period.variancePercent > 0 ? 'default' : 'destructive'} className="text-xs">
                                                        {period.variancePercent > 0 ? '+' : ''}{period.variancePercent}%
                                                    </Badge>
                                                )}
                                            </div>
                                            {period.expected && (
                                                <div className="text-xs text-muted-foreground">
                                                    Expected: {formatValue(period.expected)}
                                                </div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        {/* Trend Chart */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Performance Trend</CardTitle>
                                <CardDescription>Actual vs Expected across periods</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-80">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={multiPeriodData}>
                                            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                            <XAxis dataKey="period" />
                                            <YAxis />
                                            <Tooltip />
                                            <Legend />
                                            <Line
                                                type="monotone"
                                                dataKey="value"
                                                stroke="#6366f1"
                                                strokeWidth={3}
                                                name="Actual"
                                                dot={{ r: 6 }}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="expected"
                                                stroke="#94a3b8"
                                                strokeWidth={2}
                                                strokeDasharray="5 5"
                                                name="Expected"
                                                dot={{ r: 4 }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>

                        <div className="grid grid-cols-2 gap-6">
                            {/* Variance Waterfall */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Variance Analysis</CardTitle>
                                    <CardDescription>Q3 → Q4 breakdown</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="h-64">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={waterfallData}>
                                                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                                <XAxis dataKey="name" angle={-20} textAnchor="end" height={80} tick={{ fontSize: 11 }} />
                                                <YAxis />
                                                <Tooltip />
                                                <Bar
                                                    dataKey="value"
                                                    fill="#6366f1"
                                                    radius={[4, 4, 0, 0]}
                                                >
                                                    {waterfallData.map((entry, index) => (
                                                        <Cell
                                                            key={`cell-${index}`}
                                                            fill={
                                                                entry.type === 'increase' ? '#22c55e' :
                                                                    entry.type === 'decrease' ? '#ef4444' :
                                                                        entry.type === 'total' ? '#6366f1' :
                                                                            '#94a3b8'
                                                            }
                                                        />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Statistical Tests */}
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Activity className="h-5 w-5" />
                                        Statistical Significance
                                    </CardTitle>
                                    <CardDescription>95% confidence level</CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {statisticalTests.map((test, idx) => (
                                        <div key={idx} className="border rounded-lg p-4">
                                            <div className="flex items-start justify-between mb-2">
                                                <p className="font-medium text-sm">{test.metric}</p>
                                                {test.isSignificant ? (
                                                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                                                ) : (
                                                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                                                )}
                                            </div>
                                            <div className="space-y-1">
                                                <div className="flex items-center justify-between text-xs">
                                                    <span className="text-muted-foreground">p-value</span>
                                                    <Badge variant={test.isSignificant ? 'default' : 'outline'} className="text-xs">
                                                        {test.pValue.toFixed(3)}
                                                    </Badge>
                                                </div>
                                                <p className="text-xs text-muted-foreground mt-2">{test.interpretation}</p>
                                            </div>
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>
                        </div>
                    </TabsContent>

                    {/* A/B TEST ANALYSIS */}
                    <TabsContent value="ab-test" className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>A/B Test Results</CardTitle>
                                <CardDescription>Compare test variant performance</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <div className="p-6 border rounded-lg bg-blue-50 dark:bg-blue-950">
                                            <p className="text-sm text-muted-foreground mb-1">Control (A)</p>
                                            <p className="text-3xl font-bold">$45,230</p>
                                            <p className="text-sm text-muted-foreground mt-2">Baseline performance</p>
                                        </div>
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">Conversion Rate</span>
                                                <span className="font-medium">3.2%</span>
                                            </div>
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">CPA</span>
                                                <span className="font-medium">$42.50</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="p-6 border rounded-lg bg-green-50 dark:bg-green-950">
                                            <p className="text-sm text-muted-foreground mb-1">Variant (B)</p>
                                            <p className="text-3xl font-bold text-green-600">$52,890</p>
                                            <Badge className="mt-2 bg-green-600">+16.9% uplift</Badge>
                                        </div>
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">Conversion Rate</span>
                                                <span className="font-medium text-green-600">3.8% (+18.8%)</span>
                                            </div>
                                            <div className="flex justify-between text-sm">
                                                <span className="text-muted-foreground">CPA</span>
                                                <span className="font-medium text-green-600">$38.20 (-10.1%)</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-6 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                                    <div className="flex items-start gap-3">
                                        <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                                        <div>
                                            <p className="font-medium text-green-900 dark:text-green-100">Statistically Significant</p>
                                            <p className="text-sm text-green-800 dark:text-green-200 mt-1">
                                                Variant B shows a significant improvement (p = 0.003, 99% confidence).
                                                Recommend rolling out to 100% of traffic.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* COHORT ANALYSIS */}
                    <TabsContent value="cohort" className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cohort Retention Analysis</CardTitle>
                                <CardDescription>User behavior across cohorts</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-80">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart>
                                            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                                            <XAxis dataKey="week" label={{ value: 'Weeks Since First Touch', position: 'insideBottom', offset: -5 }} />
                                            <YAxis label={{ value: 'Retention %', angle: -90, position: 'insideLeft' }} />
                                            <Tooltip />
                                            <Legend />
                                            {cohortData.map((cohort, idx) => (
                                                <Line
                                                    key={cohort.cohort}
                                                    type="monotone"
                                                    data={cohort.retention.map((r, week) => ({ week: `Week ${week + 1}`, value: r }))}
                                                    dataKey="value"
                                                    stroke={['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'][idx]}
                                                    strokeWidth={2}
                                                    name={cohort.cohort}
                                                />
                                            ))}
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    );
}
