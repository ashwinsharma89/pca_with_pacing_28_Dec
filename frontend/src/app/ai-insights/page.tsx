"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
    Bot, Send, Loader2, Sparkles, TrendingUp, TrendingDown,
    AlertTriangle, Lightbulb, BarChart3, RefreshCw, Copy, Check,
    ArrowUpRight, ArrowDownRight, Zap, Target, Activity
} from "lucide-react";
import { format } from "date-fns";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import dynamic from 'next/dynamic';

// Dynamically import charts
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const RechartsBarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const RechartsLineChart = dynamic(() => import('recharts').then(mod => mod.LineChart), { ssr: false });
const Line = dynamic(() => import('recharts').then(mod => mod.Line), { ssr: false });
const RechartsAreaChart = dynamic(() => import('recharts').then(mod => mod.AreaChart), { ssr: false });
const Area = dynamic(() => import('recharts').then(mod => mod.Area), { ssr: false });
const RechartsPieChart = dynamic(() => import('recharts').then(mod => mod.PieChart), { ssr: false });
const Pie = dynamic(() => import('recharts').then(mod => mod.Pie), { ssr: false });
const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });
const ReferenceLine = dynamic(() => import('recharts').then(mod => mod.ReferenceLine), { ssr: false });

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e', '#f97316', '#22c55e', '#14b8a6'];

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    chart?: {
        type: string;
        data: any[];
        xAxis: string;
        yAxis: string;
    };
    insights?: string[];
    timestamp: Date;
}

interface Anomaly {
    id: string;
    type: 'spike' | 'drop' | 'trend' | 'outlier';
    severity: 'low' | 'medium' | 'high';
    metric: string;
    dimension: string;
    value: number;
    expected: number;
    deviation: number;
    description: string;
}

interface Recommendation {
    id: string;
    type: 'optimization' | 'alert' | 'opportunity';
    title: string;
    description: string;
    impact: string;
    priority: 'low' | 'medium' | 'high';
}

// Natural Language Query Parser
const parseNLQuery = (query: string): { chartType: string; xAxis: string; yAxis: string; aggregation: string; filters?: any } => {
    const q = query.toLowerCase();

    // Detect chart type
    let chartType = 'bar';
    if (q.includes('pie') || q.includes('distribution') || q.includes('breakdown')) chartType = 'pie';
    else if (q.includes('line') || q.includes('trend') || q.includes('over time')) chartType = 'line';
    else if (q.includes('area')) chartType = 'area';

    // Detect dimension (x-axis)
    let xAxis = 'platform';
    if (q.includes('channel')) xAxis = 'channel';
    else if (q.includes('funnel') || q.includes('stage')) xAxis = 'funnel_stage';
    else if (q.includes('objective')) xAxis = 'objective';
    else if (q.includes('status')) xAxis = 'status';
    else if (q.includes('campaign')) xAxis = 'name';

    // Detect metric (y-axis)
    let yAxis = 'spend';
    if (q.includes('click')) yAxis = 'clicks';
    else if (q.includes('impression')) yAxis = 'impressions';
    else if (q.includes('conversion')) yAxis = 'conversions';
    else if (q.includes('ctr') || q.includes('click-through') || q.includes('click through')) yAxis = 'ctr';
    else if (q.includes('cpc') || q.includes('cost per click')) yAxis = 'cpc';
    else if (q.includes('cpa') || q.includes('cost per acquisition') || q.includes('cost per conversion')) yAxis = 'cpa';
    else if (q.includes('roas') || q.includes('return')) yAxis = 'roas';

    // Detect aggregation
    let aggregation = 'sum';
    if (q.includes('average') || q.includes('avg') || q.includes('mean')) aggregation = 'avg';
    else if (q.includes('count') || q.includes('number of')) aggregation = 'count';

    return { chartType, xAxis, yAxis, aggregation };
};

// Anomaly Detection
const detectAnomalies = (data: any[], campaigns: any[]): Anomaly[] => {
    const anomalies: Anomaly[] = [];

    if (!campaigns.length) return anomalies;

    // Group by platform and find anomalies
    const platformData: Record<string, { spend: number; clicks: number; conversions: number; count: number }> = {};
    campaigns.forEach((c: any) => {
        const p = c.platform || 'Unknown';
        if (!platformData[p]) platformData[p] = { spend: 0, clicks: 0, conversions: 0, count: 0 };
        platformData[p].spend += c.spend || 0;
        platformData[p].clicks += c.clicks || 0;
        platformData[p].conversions += c.conversions || 0;
        platformData[p].count++;
    });

    // Calculate averages
    const platforms = Object.entries(platformData);
    const avgSpend = platforms.reduce((sum, [_, d]) => sum + d.spend, 0) / platforms.length;
    const avgClicks = platforms.reduce((sum, [_, d]) => sum + d.clicks, 0) / platforms.length;
    const avgConversions = platforms.reduce((sum, [_, d]) => sum + d.conversions, 0) / platforms.length;

    // Find spend anomalies
    platforms.forEach(([platform, data]) => {
        const spendDeviation = ((data.spend - avgSpend) / avgSpend) * 100;
        if (Math.abs(spendDeviation) > 50) {
            anomalies.push({
                id: `spend-${platform}`,
                type: spendDeviation > 0 ? 'spike' : 'drop',
                severity: Math.abs(spendDeviation) > 100 ? 'high' : 'medium',
                metric: 'spend',
                dimension: platform,
                value: data.spend,
                expected: avgSpend,
                deviation: spendDeviation,
                description: `${platform} spend is ${Math.abs(spendDeviation).toFixed(0)}% ${spendDeviation > 0 ? 'above' : 'below'} average`
            });
        }

        // CPA anomaly check
        const cpa = data.conversions > 0 ? data.spend / data.conversions : 0;
        const avgCPA = avgConversions > 0 ? avgSpend / avgConversions : 0;
        if (avgCPA > 0) {
            const cpaDeviation = ((cpa - avgCPA) / avgCPA) * 100;
            if (cpaDeviation > 50) {
                anomalies.push({
                    id: `cpa-${platform}`,
                    type: 'outlier',
                    severity: cpaDeviation > 100 ? 'high' : 'medium',
                    metric: 'CPA',
                    dimension: platform,
                    value: cpa,
                    expected: avgCPA,
                    deviation: cpaDeviation,
                    description: `${platform} CPA ($${cpa.toFixed(2)}) is ${cpaDeviation.toFixed(0)}% higher than average`
                });
            }
        }
    });

    return anomalies.slice(0, 5); // Return top 5
};

// Generate Smart Recommendations
const generateRecommendations = (campaigns: any[], anomalies: Anomaly[]): Recommendation[] => {
    const recommendations: Recommendation[] = [];

    if (!campaigns.length) return recommendations;

    // Analyze platform performance
    const platformPerf: Record<string, { spend: number; conversions: number }> = {};
    campaigns.forEach((c: any) => {
        const p = c.platform || 'Unknown';
        if (!platformPerf[p]) platformPerf[p] = { spend: 0, conversions: 0 };
        platformPerf[p].spend += c.spend || 0;
        platformPerf[p].conversions += c.conversions || 0;
    });

    // Find best performing platform
    let bestPlatform = '';
    let bestCPA = Infinity;
    Object.entries(platformPerf).forEach(([platform, data]) => {
        if (data.conversions > 0) {
            const cpa = data.spend / data.conversions;
            if (cpa < bestCPA) {
                bestCPA = cpa;
                bestPlatform = platform;
            }
        }
    });

    if (bestPlatform) {
        recommendations.push({
            id: 'best-platform',
            type: 'optimization',
            title: `Scale ${bestPlatform} campaigns`,
            description: `${bestPlatform} has the lowest CPA at $${bestCPA.toFixed(2)}. Consider increasing budget allocation.`,
            impact: 'Could reduce overall CPA by 15-20%',
            priority: 'high'
        });
    }

    // Find worst performing platform
    let worstPlatform = '';
    let worstCPA = 0;
    Object.entries(platformPerf).forEach(([platform, data]) => {
        if (data.conversions > 0) {
            const cpa = data.spend / data.conversions;
            if (cpa > worstCPA && data.spend > 1000) {
                worstCPA = cpa;
                worstPlatform = platform;
            }
        }
    });

    if (worstPlatform && worstCPA > bestCPA * 2) {
        recommendations.push({
            id: 'worst-platform',
            type: 'alert',
            title: `Review ${worstPlatform} performance`,
            description: `${worstPlatform} CPA ($${worstCPA.toFixed(2)}) is ${((worstCPA / bestCPA - 1) * 100).toFixed(0)}% higher than best performer.`,
            impact: 'Could save significant budget',
            priority: 'high'
        });
    }

    // Add anomaly-based recommendations
    anomalies.forEach(anomaly => {
        if (anomaly.severity === 'high') {
            recommendations.push({
                id: `anomaly-${anomaly.id}`,
                type: 'alert',
                title: `Investigate ${anomaly.dimension} ${anomaly.metric}`,
                description: anomaly.description,
                impact: 'Requires immediate attention',
                priority: 'high'
            });
        }
    });

    // Generic optimization suggestion
    recommendations.push({
        id: 'funnel-opt',
        type: 'opportunity',
        title: 'Optimize funnel stage allocation',
        description: 'Analyze spend distribution across awareness, consideration, and conversion stages.',
        impact: 'Could improve overall funnel efficiency',
        priority: 'medium'
    });

    return recommendations.slice(0, 5);
};

// Example queries for suggestions
const EXAMPLE_QUERIES = [
    "Show me spend by platform",
    "What's the conversion breakdown by channel?",
    "Show CTR trend by funnel stage",
    "Which platform has the best CPA?",
    "Give me a pie chart of impressions by platform"
];

export default function AIInsightsPage() {
    const { token, isLoading } = useAuth();
    const router = useRouter();
    const chatEndRef = useRef<HTMLDivElement>(null);

    const [loading, setLoading] = useState(false);
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [campaigns, setCampaigns] = useState<any[]>([]);
    const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [copied, setCopied] = useState<string | null>(null);

    // Auth Guard
    useEffect(() => {
        if (!isLoading && !token) router.push("/login");
    }, [isLoading, token, router]);

    useEffect(() => {
        if (token) loadData();
    }, [token]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadData = async () => {
        setLoading(true);
        try {
            const response: any = await api.get('/campaigns?limit=5000');
            const data = response.campaigns || [];
            setCampaigns(data);

            // Detect anomalies
            const detectedAnomalies = detectAnomalies([], data);
            setAnomalies(detectedAnomalies);

            // Generate recommendations
            const recs = generateRecommendations(data, detectedAnomalies);
            setRecommendations(recs);

            // Add welcome message
            if (messages.length === 0) {
                setMessages([{
                    id: '1',
                    role: 'assistant',
                    content: `👋 Hi! I'm your AI Analytics Assistant. I've analyzed ${data.length.toLocaleString()} campaigns and found ${detectedAnomalies.length} anomalies. Ask me anything about your data!`,
                    timestamp: new Date()
                }]);
            }
        } catch (error) {
            console.error("Failed to load data", error);
        } finally {
            setLoading(false);
        }
    };

    const handleQuery = async () => {
        if (!query.trim()) return;

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: query,
            timestamp: new Date()
        };
        setMessages(prev => [...prev, userMessage]);
        setQuery('');
        setLoading(true);

        try {
            // Parse the natural language query
            const parsed = parseNLQuery(query);

            // Fetch chart data
            const params = new URLSearchParams({
                x_axis: parsed.xAxis,
                y_axis: parsed.yAxis,
                aggregation: parsed.aggregation
            });
            const response: any = await api.get(`/campaigns/chart-data?${params.toString()}`);
            const chartData = response.data || [];

            // Generate insights
            const insights: string[] = [];
            if (chartData.length > 0) {
                const total = chartData.reduce((sum: number, d: any) => sum + (d[parsed.yAxis] || 0), 0);
                const max = chartData.reduce((max: any, d: any) => (d[parsed.yAxis] || 0) > (max[parsed.yAxis] || 0) ? d : max, chartData[0]);
                const min = chartData.reduce((min: any, d: any) => (d[parsed.yAxis] || 0) < (min[parsed.yAxis] || 0) ? d : min, chartData[0]);

                insights.push(`📊 Total ${parsed.yAxis}: ${total.toLocaleString()}`);
                insights.push(`🔝 Highest: ${max[parsed.xAxis]} with ${(max[parsed.yAxis] || 0).toLocaleString()}`);
                insights.push(`🔻 Lowest: ${min[parsed.xAxis]} with ${(min[parsed.yAxis] || 0).toLocaleString()}`);
            }

            const assistantMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `Here's your ${parsed.chartType} chart showing ${parsed.yAxis} by ${parsed.xAxis}:`,
                chart: {
                    type: parsed.chartType,
                    data: chartData,
                    xAxis: parsed.xAxis,
                    yAxis: parsed.yAxis
                },
                insights,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, assistantMessage]);

        } catch (error) {
            console.error("Failed to process query", error);
            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Sorry, I couldn't process that query. Please try again with a different question.",
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const copyInsight = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopied(id);
        setTimeout(() => setCopied(null), 2000);
    };

    const renderChart = (chart: ChatMessage['chart']) => {
        if (!chart || !chart.data.length) return null;

        switch (chart.type) {
            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <RechartsPieChart>
                            <Pie data={chart.data} dataKey={chart.yAxis} nameKey={chart.xAxis} cx="50%" cy="50%" outerRadius={80} innerRadius={50} paddingAngle={2} label={({ percent }) => percent != null ? `${(percent * 100).toFixed(0)}%` : ''}>
                                {chart.data.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </RechartsPieChart>
                    </ResponsiveContainer>
                );
            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <RechartsLineChart data={chart.data}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey={chart.xAxis} className="text-xs" />
                            <YAxis className="text-xs" />
                            <Tooltip contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }} />
                            <Line type="monotone" dataKey={chart.yAxis} stroke="#6366f1" strokeWidth={2} dot={{ r: 4 }} />
                        </RechartsLineChart>
                    </ResponsiveContainer>
                );
            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <RechartsAreaChart data={chart.data}>
                            <defs>
                                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey={chart.xAxis} className="text-xs" />
                            <YAxis className="text-xs" />
                            <Tooltip contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }} />
                            <Area type="monotone" dataKey={chart.yAxis} stroke="#6366f1" fill="url(#areaGrad)" />
                        </RechartsAreaChart>
                    </ResponsiveContainer>
                );
            default:
                return (
                    <ResponsiveContainer width="100%" height={250}>
                        <RechartsBarChart data={chart.data}>
                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                            <XAxis dataKey={chart.xAxis} className="text-xs" angle={-30} textAnchor="end" height={60} interval={0} />
                            <YAxis className="text-xs" />
                            <Tooltip contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }} />
                            <Bar dataKey={chart.yAxis} fill="#6366f1" radius={[4, 4, 0, 0]} />
                        </RechartsBarChart>
                    </ResponsiveContainer>
                );
        }
    };

    if (isLoading) return <div className="flex h-screen items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    if (!token) return null;

    return (
        <div className="container mx-auto py-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
                        🤖 AI Insights
                    </h1>
                    <p className="text-muted-foreground text-sm">Natural language analytics, anomaly detection & smart recommendations</p>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={loadData}>
                    <RefreshCw className="mr-2 h-4 w-4" />Refresh
                </Button>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                {/* Main Chat Interface */}
                <div className="lg:col-span-2 space-y-4">
                    <Card className="h-[600px] flex flex-col">
                        <CardHeader className="pb-2 border-b">
                            <CardTitle className="flex items-center gap-2">
                                <Bot className="h-5 w-5 text-primary" />
                                AI Analytics Assistant
                            </CardTitle>
                            <CardDescription>Ask questions in natural language</CardDescription>
                        </CardHeader>

                        {/* Chat Messages */}
                        <CardContent className="flex-1 overflow-auto p-4 space-y-4">
                            {messages.map((msg) => (
                                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[85%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                                        <p className="text-sm">{msg.content}</p>

                                        {msg.chart && (
                                            <div className="mt-3 p-2 bg-background rounded-lg">
                                                {renderChart(msg.chart)}
                                            </div>
                                        )}

                                        {msg.insights && msg.insights.length > 0 && (
                                            <div className="mt-3 space-y-1">
                                                {msg.insights.map((insight, i) => (
                                                    <div key={i} className="flex items-center justify-between text-xs p-2 bg-background/50 rounded">
                                                        <span>{insight}</span>
                                                        <Button
                                                            type="button"
                                                            variant="ghost"
                                                            size="icon"
                                                            className="h-5 w-5"
                                                            onClick={() => copyInsight(insight, `${msg.id}-${i}`)}
                                                        >
                                                            {copied === `${msg.id}-${i}` ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
                                                        </Button>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        <p className="text-xs opacity-60 mt-2">{format(msg.timestamp, 'h:mm a')}</p>
                                    </div>
                                </div>
                            ))}

                            {loading && (
                                <div className="flex justify-start">
                                    <div className="p-3 rounded-lg bg-muted">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                    </div>
                                </div>
                            )}
                            <div ref={chatEndRef} />
                        </CardContent>

                        {/* Example Queries */}
                        <div className="px-4 pb-2">
                            <div className="flex gap-2 overflow-x-auto pb-2">
                                {EXAMPLE_QUERIES.slice(0, 3).map((eq, i) => (
                                    <Button
                                        key={i}
                                        type="button"
                                        variant="outline"
                                        size="sm"
                                        className="text-xs whitespace-nowrap shrink-0"
                                        onClick={() => setQuery(eq)}
                                    >
                                        {eq}
                                    </Button>
                                ))}
                            </div>
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t">
                            <form onSubmit={(e) => { e.preventDefault(); handleQuery(); }} className="flex gap-2">
                                <Input
                                    placeholder="Ask about your campaign data..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    disabled={loading}
                                    className="flex-1"
                                />
                                <Button type="submit" disabled={loading || !query.trim()} className="bg-gradient-to-r from-indigo-500 to-purple-600">
                                    <Send className="h-4 w-4" />
                                </Button>
                            </form>
                        </div>
                    </Card>
                </div>

                {/* Sidebar: Anomalies & Recommendations */}
                <div className="space-y-4">
                    {/* Anomalies */}
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-lg">
                                <AlertTriangle className="h-5 w-5 text-orange-500" />
                                Anomalies Detected
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {anomalies.length === 0 ? (
                                <p className="text-sm text-muted-foreground text-center py-4">No anomalies detected</p>
                            ) : (
                                anomalies.map(anomaly => (
                                    <div key={anomaly.id} className={`p-3 rounded-lg border-l-4 ${anomaly.severity === 'high' ? 'border-l-red-500 bg-red-500/10' :
                                            anomaly.severity === 'medium' ? 'border-l-orange-500 bg-orange-500/10' :
                                                'border-l-yellow-500 bg-yellow-500/10'
                                        }`}>
                                        <div className="flex items-start gap-2">
                                            {anomaly.type === 'spike' ? <ArrowUpRight className="h-4 w-4 text-red-500 shrink-0 mt-0.5" /> :
                                                anomaly.type === 'drop' ? <ArrowDownRight className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" /> :
                                                    <Activity className="h-4 w-4 text-orange-500 shrink-0 mt-0.5" />}
                                            <div>
                                                <p className="text-sm font-medium">{anomaly.dimension}</p>
                                                <p className="text-xs text-muted-foreground">{anomaly.description}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </CardContent>
                    </Card>

                    {/* Smart Recommendations */}
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-lg">
                                <Lightbulb className="h-5 w-5 text-yellow-500" />
                                Smart Recommendations
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            {recommendations.map(rec => (
                                <div key={rec.id} className={`p-3 rounded-lg ${rec.type === 'optimization' ? 'bg-green-500/10 border border-green-500/20' :
                                        rec.type === 'alert' ? 'bg-red-500/10 border border-red-500/20' :
                                            'bg-blue-500/10 border border-blue-500/20'
                                    }`}>
                                    <div className="flex items-start gap-2">
                                        {rec.type === 'optimization' ? <Target className="h-4 w-4 text-green-500 shrink-0 mt-0.5" /> :
                                            rec.type === 'alert' ? <AlertTriangle className="h-4 w-4 text-red-500 shrink-0 mt-0.5" /> :
                                                <Zap className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" />}
                                        <div>
                                            <p className="text-sm font-medium">{rec.title}</p>
                                            <p className="text-xs text-muted-foreground mt-1">{rec.description}</p>
                                            <p className="text-xs text-primary mt-1">💡 {rec.impact}</p>
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
