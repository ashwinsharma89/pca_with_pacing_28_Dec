"use client";

import { useState, useEffect, useRef, Fragment } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
    FileText, Download, Share2, Link2, Copy, Check, Calendar,
    BarChart3, Loader2, RefreshCw, Mail, Clock, Settings2,
    Plus, Trash2, MessageSquare, Send, TrendingUp, Activity, Sparkles, Table, ChevronRight, ChevronDown, Filter, LayoutGrid, ArrowLeft, ArrowRight
} from "lucide-react";
import { format } from "date-fns";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import dynamic from 'next/dynamic';

// Dynamically import charts
const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const RechartsBarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const RechartsPieChart = dynamic(() => import('recharts').then(mod => mod.PieChart), { ssr: false });
const Pie = dynamic(() => import('recharts').then(mod => mod.Pie), { ssr: false });
const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e', '#f97316', '#22c55e', '#14b8a6'];

interface ReportConfig {
    title: string;
    description: string;
    includeKPIs: boolean;
    includeCharts: boolean;
    includeTables: boolean;
    dateRange: string;
    format: 'pdf' | 'csv';
}

interface Annotation {
    id: string;
    chartId: string;
    text: string;
    x: number;
    y: number;
    createdAt: string;
}

interface SharedReport {
    id: string;
    name: string;
    config: any;
    createdAt: string;
    expiresAt: string;
    views: number;
}

interface PivotConfig {
    rows: string[];
    column: string;
    values: string[];
    aggregation: 'sum' | 'avg' | 'count';
    layout: 'compact' | 'tabular';
    design: {
        density: 'compact' | 'normal' | 'spacious';
        striped: boolean;
        gridLines: boolean;
    };
}

const PIVOT_DIMENSIONS = [
    { value: 'platform', label: 'Platform' },
    { value: 'name', label: 'Campaign' },
    { value: 'channel', label: 'Channel' },
    { value: 'objective', label: 'Objective' },
    { value: 'region', label: 'Region' },
    { value: 'device_type', label: 'Device' },
    { value: 'placement', label: 'Placement' },
    { value: 'ad_type', label: 'Ad Type' },
    { value: 'date', label: 'Date' }
];

const PIVOT_METRICS = [
    { value: 'spend', label: 'Spend' },
    { value: 'impressions', label: 'Impressions' },
    { value: 'clicks', label: 'Clicks' },
    { value: 'conversions', label: 'Conversions' },
    { value: 'ctr', label: 'CTR' },
    { value: 'cpa', label: 'CPA' },
    { value: 'roas', label: 'ROAS' }
];

export default function ReportsPage() {
    const { token, isLoading } = useAuth();
    const router = useRouter();
    const searchParams = useSearchParams();

    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [metrics, setMetrics] = useState<any>(null);
    const [chartData, setChartData] = useState<any[]>([]);
    const [sharedReports, setSharedReports] = useState<SharedReport[]>([]);
    const [annotations, setAnnotations] = useState<Annotation[]>([]);

    // Report configuration
    const [reportConfig, setReportConfig] = useState<ReportConfig>({
        title: 'Campaign Performance Report',
        description: 'Overview of campaign performance metrics and insights',
        includeKPIs: true,
        includeCharts: true,
        includeTables: true,
        dateRange: 'last30days',
        format: 'pdf'
    });

    // Share dialog state
    const [shareUrl, setShareUrl] = useState('');
    const [showShareDialog, setShowShareDialog] = useState(false);

    // Annotation state
    const [newAnnotation, setNewAnnotation] = useState('');
    const [showAnnotationDialog, setShowAnnotationDialog] = useState(false);

    // Pivot Table State
    const [pivotConfig, setPivotConfig] = useState<PivotConfig>({
        rows: ['platform'],
        column: '',
        values: ['spend'],
        aggregation: 'sum',
        layout: 'compact',
        design: {
            density: 'compact',
            striped: false,
            gridLines: true
        }
    });
    const [pivotData, setPivotData] = useState<any[]>([]);
    const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

    // Auth Guard
    useEffect(() => {
        if (!isLoading && !token) router.push("/login");
    }, [isLoading, token, router]);

    useEffect(() => {
        if (token) {
            loadData();
            loadSharedReports();
        }
    }, [token]);

    const loadData = async () => {
        setLoading(true);
        try {
            const response: any = await api.get('/campaigns?limit=5000');
            const campaigns = response.campaigns || [];

            if (campaigns.length > 0) {
                // Calculate metrics
                const totalSpend = campaigns.reduce((sum: number, c: any) => sum + (c.spend || 0), 0);
                const totalClicks = campaigns.reduce((sum: number, c: any) => sum + (c.clicks || 0), 0);
                const totalImpressions = campaigns.reduce((sum: number, c: any) => sum + (c.impressions || 0), 0);
                const totalConversions = campaigns.reduce((sum: number, c: any) => sum + (c.conversions || 0), 0);
                const avgCTR = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
                const avgCPA = totalConversions > 0 ? totalSpend / totalConversions : 0;

                setMetrics({
                    spend: totalSpend,
                    impressions: totalImpressions,
                    clicks: totalClicks,
                    conversions: totalConversions,
                    ctr: avgCTR,
                    cpa: avgCPA,
                    campaigns: campaigns.length
                });

                // Aggregate by platform for charts
                const platformData: Record<string, any> = {};
                campaigns.forEach((c: any) => {
                    const platform = c.platform || 'Unknown';
                    if (!platformData[platform]) {
                        platformData[platform] = { platform, spend: 0, clicks: 0, conversions: 0 };
                    }
                    platformData[platform].spend += c.spend || 0;
                    platformData[platform].clicks += c.clicks || 0;
                    platformData[platform].conversions += c.conversions || 0;
                });
                setChartData(Object.values(platformData));

                // Process data for Pivot Table (Flatten JSON fields)
                const flattenedData = campaigns.map((c: any) => ({
                    ...c,
                    name: c.campaign_name || c.name || 'Unknown',
                    region: (c.additional_data || {}).region || 'Unknown',
                    device_type: (c.additional_data || {}).device_type || 'Unknown',
                    bid_strategy: (c.additional_data || {}).bid_strategy || 'Unknown',
                    date: c.date ? format(new Date(c.date), 'yyyy-MM-dd') : 'Unknown'
                }));
                setPivotData(flattenedData);
            }
        } catch (error) {
            console.error("Failed to load data", error);
        } finally {
            setLoading(false);
        }
    };

    const loadSharedReports = () => {
        const saved = localStorage.getItem('sharedReports');
        if (saved) {
            setSharedReports(JSON.parse(saved));
        }
    };

    const generatePDFReport = async () => {
        setGenerating(true);
        try {
            const jsPDF = (await import('jspdf')).default;
            const autoTable = (await import('jspdf-autotable')).default;
            const html2canvas = (await import('html2canvas')).default;

            const doc = new jsPDF();
            const pageWidth = doc.internal.pageSize.getWidth();

            // Title
            doc.setFontSize(24);
            doc.setTextColor(99, 102, 241); // Indigo
            doc.text(reportConfig.title, pageWidth / 2, 25, { align: 'center' });

            // Description
            doc.setFontSize(12);
            doc.setTextColor(100);
            doc.text(reportConfig.description, pageWidth / 2, 35, { align: 'center' });

            // Date
            doc.setFontSize(10);
            doc.text(`Generated: ${format(new Date(), 'MMMM d, yyyy h:mm a')}`, pageWidth / 2, 45, { align: 'center' });

            let yPos = 60;

            // KPIs Section
            if (reportConfig.includeKPIs && metrics) {
                doc.setFontSize(16);
                doc.setTextColor(0);
                doc.text('Key Performance Indicators', 14, yPos);
                yPos += 10;

                const kpiData = [
                    ['Metric', 'Value'],
                    ['Total Spend', `$${metrics.spend.toLocaleString(undefined, { maximumFractionDigits: 2 })}`],
                    ['Impressions', metrics.impressions.toLocaleString()],
                    ['Clicks', metrics.clicks.toLocaleString()],
                    ['Conversions', metrics.conversions.toLocaleString()],
                    ['CTR', `${metrics.ctr.toFixed(2)}%`],
                    ['CPA', `$${metrics.cpa.toFixed(2)}`],
                    ['Campaigns', metrics.campaigns.toString()],
                ];

                autoTable(doc, {
                    startY: yPos,
                    head: [kpiData[0]],
                    body: kpiData.slice(1),
                    theme: 'striped',
                    headStyles: { fillColor: [99, 102, 241] },
                    margin: { left: 14, right: 14 },
                });

                yPos = (doc as any).lastAutoTable.finalY + 20;
            }

            // Platform Performance Table
            if (reportConfig.includeTables && chartData.length > 0) {
                if (yPos > 200) {
                    doc.addPage();
                    yPos = 20;
                }

                doc.setFontSize(16);
                doc.setTextColor(0);
                doc.text('Platform Performance', 14, yPos);
                yPos += 10;

                const tableData = chartData.map(row => [
                    row.platform,
                    `$${row.spend.toLocaleString(undefined, { maximumFractionDigits: 2 })}`,
                    row.clicks.toLocaleString(),
                    row.conversions.toLocaleString()
                ]);

                autoTable(doc, {
                    startY: yPos,
                    head: [['Platform', 'Spend', 'Clicks', 'Conversions']],
                    body: tableData,
                    theme: 'striped',
                    headStyles: { fillColor: [99, 102, 241] },
                    margin: { left: 14, right: 14 },
                });
            }

            // Annotations Section
            if (annotations.length > 0) {
                doc.addPage();
                doc.setFontSize(16);
                doc.setTextColor(0);
                doc.text('Annotations & Notes', 14, 20);

                let annotationY = 35;
                annotations.forEach((annotation, index) => {
                    doc.setFontSize(10);
                    doc.setTextColor(100);
                    doc.text(`${index + 1}. ${annotation.text}`, 14, annotationY);
                    annotationY += 10;
                });
            }

            // Save PDF
            doc.save(`${reportConfig.title.replace(/\s+/g, '_')}_${format(new Date(), 'yyyy-MM-dd')}.pdf`);

        } catch (error) {
            console.error("Failed to generate PDF", error);
        } finally {
            setGenerating(false);
        }
    };

    const generateCSVReport = () => {
        if (!chartData.length) return;

        const headers = ['Platform', 'Spend', 'Clicks', 'Conversions'];
        const rows = chartData.map(row => [
            row.platform,
            row.spend.toFixed(2),
            row.clicks,
            row.conversions
        ]);

        const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `campaign_report_${format(new Date(), 'yyyy-MM-dd')}.csv`;
        link.click();
        URL.revokeObjectURL(url);
    };

    const generateReport = () => {
        if (reportConfig.format === 'pdf') {
            generatePDFReport();
        } else {
            generateCSVReport();
        }
    };

    const createShareableLink = () => {
        const reportId = Date.now().toString(36);
        const report: SharedReport = {
            id: reportId,
            name: reportConfig.title,
            config: { ...reportConfig, metrics, chartData },
            createdAt: new Date().toISOString(),
            expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
            views: 0
        };

        const updated = [...sharedReports, report];
        setSharedReports(updated);
        localStorage.setItem('sharedReports', JSON.stringify(updated));

        const url = `${window.location.origin}/reports?shared=${reportId}`;
        setShareUrl(url);
        setShowShareDialog(true);
    };

    const copyToClipboard = async () => {
        await navigator.clipboard.writeText(shareUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const addAnnotation = () => {
        if (!newAnnotation.trim()) return;

        const annotation: Annotation = {
            id: Date.now().toString(),
            chartId: 'main',
            text: newAnnotation,
            x: 0,
            y: 0,
            createdAt: new Date().toISOString()
        };

        setAnnotations([...annotations, annotation]);
        setNewAnnotation('');
        setShowAnnotationDialog(false);
    };

    const removeAnnotation = (id: string) => {
        setAnnotations(annotations.filter(a => a.id !== id));
    };

    const deleteSharedReport = (id: string) => {
        const updated = sharedReports.filter(r => r.id !== id);
        setSharedReports(updated);
        localStorage.setItem('sharedReports', JSON.stringify(updated));
    };

    const formatCurrency = (val: number) =>
        val >= 1000000 ? `$${(val / 1000000).toFixed(2)}M` :
            val >= 1000 ? `$${(val / 1000).toFixed(1)}K` : `$${val.toFixed(0)}`;

    // Pivot Table Logic
    const getPivotData = () => {
        if (!pivotData.length) return {};

        const { rows, column, values, aggregation } = pivotConfig;

        // 1. Group by Rows
        const grouped: any = {};

        pivotData.forEach(item => {
            // Create nested key for rows
            let currentLevel = grouped;
            const rowKeyParts = rows.map(r => item[r] || 'Unknown');

            // Handle Columns (if selected)
            const colKey = column ? (item[column] || 'Unknown') : 'Total';

            // Navigate/Create nested structure
            rowKeyParts.forEach((part, idx) => {
                if (!currentLevel[part]) {
                    currentLevel[part] = { _data: [], _sub: {} };
                }
                currentLevel[part]._data.push(item);
                if (idx < rowKeyParts.length - 1) {
                    currentLevel = currentLevel[part]._sub;
                }
            });
        });

        return grouped;
    };

    const getRowStyle = (index: number) => {
        const { density, striped } = pivotConfig.design;
        let className = "border-b transition-colors ";

        // Density (Padding handled in Cells, but row height can differ)

        // Striped
        if (striped && index % 2 !== 0) {
            className += "bg-muted/30 ";
        } else {
            className += "hover:bg-muted/50 ";
        }

        return className;
    };

    const getCellStyle = (isHeader: boolean = false, isLast: boolean = false) => {
        const { density, gridLines } = pivotConfig.design;
        let className = isHeader ? "font-semibold text-muted-foreground " : "";

        // Density
        if (density === 'compact') className += "p-1 ";
        else if (density === 'spacious') className += "p-4 ";
        else className += "p-2 "; // normal

        // Grid Lines
        if (gridLines && !isLast) className += "border-r ";

        return className;
    };

    const calculateLimit = (items: any[], metric: string) => {
        if (!items.length) return 0;
        const sum = items.reduce((acc, item) => acc + (Number(item[metric]) || 0), 0);
        return pivotConfig.aggregation === 'avg' ? sum / items.length :
            pivotConfig.aggregation === 'count' ? items.length : sum;
    };

    const renderPivotRowsTabular = (data: any, parentKeys: string[] = []): React.ReactNode[] => {
        if (!data || typeof data !== 'object') return [];

        let rows: React.ReactNode[] = [];

        Object.entries(data).forEach(([key, value]: [string, any], index) => {
            const currentKeys = [...parentKeys, key];

            // If leaf node (has _data but no _sub children or at end of hierarchy)
            const isLeaf = !value._sub || Object.keys(value._sub).length === 0;

            if (isLeaf) {
                // Render a row
                rows.push(
                    <tr key={currentKeys.join('-')} className={getRowStyle(rows.length + index)}>
                        {/* Render all dimension columns */}
                        {pivotConfig.rows.map((d, i) => (
                            <td key={d} className={`text-sm truncate max-w-[150px] border-r ${getCellStyle(false, false)}`}>
                                {currentKeys[i] || '-'}
                            </td>
                        ))}

                        {/* Render all metric columns */}
                        {pivotConfig.values.map((metric, idx) => {
                            const val = calculateLimit(value._data || [], metric);
                            const isLast = idx === pivotConfig.values.length - 1;
                            return (
                                <td key={metric} className={`text-right font-mono ${getCellStyle(false, isLast)}`}>
                                    {metric.includes('spend') || metric.includes('cpa') ? formatCurrency(val) :
                                        metric.includes('ctr') ? `${val.toFixed(2)}%` :
                                            val.toLocaleString(undefined, { maximumFractionDigits: 1 })}
                                </td>
                            );
                        })}
                    </tr>
                );
            } else {
                // Recurse
                rows = [...rows, ...renderPivotRowsTabular(value._sub, currentKeys)];
            }
        });

        return rows;
    };

    const renderPivotRows = (data: any, depth = 0, parentKey = '', index = 0): React.ReactNode[] => {
        if (!data || typeof data !== 'object') return [];

        return Object.entries(data).map(([key, value]: [string, any], i) => {
            if (!value || typeof value !== 'object') return null;

            const rowId = `${parentKey}-${key}`;
            const isExpanded = expandedRows[rowId] !== false; // Default expanded
            const hasChildren = value._sub && Object.keys(value._sub).length > 0;

            // Adjust index for recursive striped effect roughly
            const globalIndex = index + i;

            return (
                <Fragment key={rowId}>
                    <tr className={getRowStyle(globalIndex)}>
                        <td className={`border-r ${getCellStyle(false, false)}`} style={{ paddingLeft: `${depth * 20 + 8}px` }}>
                            <div className="flex items-center gap-1">
                                {hasChildren && (
                                    <button onClick={() => setExpandedRows({ ...expandedRows, [rowId]: !isExpanded })}>
                                        {isExpanded ? <ChevronDown className="h-4 w-4 text-muted-foreground" /> : <ChevronRight className="h-4 w-4 text-muted-foreground" />}
                                    </button>
                                )}
                                <span className="font-medium">{key}</span>
                                <span className="text-xs text-muted-foreground ml-2">({value._data.length})</span>
                            </div>
                        </td>
                        {pivotConfig.values.map((metric, idx) => {
                            const val = calculateLimit(value._data || [], metric);
                            const isLast = idx === pivotConfig.values.length - 1;
                            return (
                                <td key={metric} className={`text-right font-mono ${getCellStyle(false, isLast)}`}>
                                    {metric.includes('spend') || metric.includes('cpa') ? formatCurrency(val) :
                                        metric.includes('ctr') ? `${val.toFixed(2)}%` :
                                            val.toLocaleString(undefined, { maximumFractionDigits: 1 })}
                                </td>
                            );
                        })}
                    </tr>
                    {isExpanded && hasChildren && renderPivotRows(value._sub, depth + 1, rowId, globalIndex + 1)}
                </Fragment>
            );
        });
    };

    const handleExportPivot = () => {
        // Simple CSV export for current view
        const headerRow = ['Dimension', ...pivotConfig.values.map(v => `${v} (${pivotConfig.aggregation})`)];
        const rows = [headerRow];

        const traverse = (data: any, prefix = '') => {
            Object.entries(data).forEach(([key, value]: [string, any]) => {
                const metrics = pivotConfig.values.map(metric => calculateLimit(value._data, metric));
                rows.push([`${prefix}${key}`, ...metrics.map(m => m.toString())]);
                if (Object.keys(value._sub).length > 0) {
                    traverse(value._sub, `${prefix}${key} > `);
                }
            });
        };

        traverse(getPivotData());

        const csvContent = rows.map(r => r.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pivot_export_${Date.now()}.csv`;
        a.click();
    };

    if (isLoading) return <div className="flex h-screen items-center justify-center"><Loader2 className="h-8 w-8 animate-spin" /></div>;
    if (!token) return null;

    return (
        <div className="container mx-auto py-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-indigo-500 to-purple-600 bg-clip-text text-transparent">
                        📄 Reports & Export
                    </h1>
                    <p className="text-muted-foreground text-sm">Generate reports, share dashboards, and add annotations</p>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={loadData}>
                    <RefreshCw className="mr-2 h-4 w-4" />Refresh
                </Button>
            </div>

            <Tabs defaultValue="generate" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="generate"><FileText className="mr-2 h-4 w-4" />Generate Report</TabsTrigger>
                    <TabsTrigger value="pivot"><LayoutGrid className="mr-2 h-4 w-4" />Pivot Table</TabsTrigger>
                    <TabsTrigger value="share"><Share2 className="mr-2 h-4 w-4" />Shared Reports</TabsTrigger>
                    <TabsTrigger value="annotations"><MessageSquare className="mr-2 h-4 w-4" />Annotations</TabsTrigger>
                </TabsList>

                {/* Generate Report Tab */}
                <TabsContent value="generate" className="space-y-4">
                    <div className="grid gap-4 lg:grid-cols-3">
                        {/* Report Configuration */}
                        <Card className="lg:col-span-1">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2"><Settings2 className="h-5 w-5" />Report Settings</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label>Report Title</Label>
                                    <Input
                                        value={reportConfig.title}
                                        onChange={(e) => setReportConfig({ ...reportConfig, title: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Textarea
                                        value={reportConfig.description}
                                        onChange={(e) => setReportConfig({ ...reportConfig, description: e.target.value })}
                                        rows={2}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Format</Label>
                                    <Select value={reportConfig.format} onValueChange={(v: 'pdf' | 'csv') => setReportConfig({ ...reportConfig, format: v })}>
                                        <SelectTrigger><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="pdf">PDF Report</SelectItem>
                                            <SelectItem value="csv">CSV Data</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-3">
                                    <Label>Include Sections</Label>
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-sm">
                                            <input
                                                type="checkbox"
                                                checked={reportConfig.includeKPIs}
                                                onChange={(e) => setReportConfig({ ...reportConfig, includeKPIs: e.target.checked })}
                                                className="rounded"
                                            />
                                            Key Metrics
                                        </label>
                                        <label className="flex items-center gap-2 text-sm">
                                            <input
                                                type="checkbox"
                                                checked={reportConfig.includeCharts}
                                                onChange={(e) => setReportConfig({ ...reportConfig, includeCharts: e.target.checked })}
                                                className="rounded"
                                            />
                                            Charts
                                        </label>
                                        <label className="flex items-center gap-2 text-sm">
                                            <input
                                                type="checkbox"
                                                checked={reportConfig.includeTables}
                                                onChange={(e) => setReportConfig({ ...reportConfig, includeTables: e.target.checked })}
                                                className="rounded"
                                            />
                                            Data Tables
                                        </label>
                                    </div>
                                </div>
                                <div className="flex gap-2 pt-2">
                                    <Button type="button" onClick={generateReport} disabled={generating} className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600">
                                        {generating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
                                        {generating ? 'Generating...' : 'Generate'}
                                    </Button>
                                    <Button type="button" variant="outline" onClick={createShareableLink}>
                                        <Share2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Preview */}
                        <Card className="lg:col-span-2">
                            <CardHeader>
                                <CardTitle>Report Preview</CardTitle>
                                <CardDescription>Preview of your report content</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {loading ? (
                                    <div className="flex items-center justify-center h-[300px]">
                                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                                    </div>
                                ) : (
                                    <>
                                        {/* KPIs Preview */}
                                        {reportConfig.includeKPIs && metrics && (
                                            <div>
                                                <h3 className="font-semibold mb-3">Key Metrics</h3>
                                                <div className="grid grid-cols-4 gap-3">
                                                    <div className="p-3 bg-indigo-500/10 rounded-lg text-center">
                                                        <p className="text-xs text-muted-foreground">Spend</p>
                                                        <p className="text-lg font-bold text-indigo-500">{formatCurrency(metrics.spend)}</p>
                                                    </div>
                                                    <div className="p-3 bg-green-500/10 rounded-lg text-center">
                                                        <p className="text-xs text-muted-foreground">Clicks</p>
                                                        <p className="text-lg font-bold text-green-500">{metrics.clicks.toLocaleString()}</p>
                                                    </div>
                                                    <div className="p-3 bg-orange-500/10 rounded-lg text-center">
                                                        <p className="text-xs text-muted-foreground">Conversions</p>
                                                        <p className="text-lg font-bold text-orange-500">{metrics.conversions.toLocaleString()}</p>
                                                    </div>
                                                    <div className="p-3 bg-pink-500/10 rounded-lg text-center">
                                                        <p className="text-xs text-muted-foreground">CTR</p>
                                                        <p className="text-lg font-bold text-pink-500">{metrics.ctr.toFixed(2)}%</p>
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* Chart Preview */}
                                        {reportConfig.includeCharts && chartData.length > 0 && (
                                            <div>
                                                <h3 className="font-semibold mb-3">Platform Performance</h3>
                                                <div className="h-[200px]">
                                                    <ResponsiveContainer width="100%" height="100%">
                                                        <RechartsBarChart data={chartData}>
                                                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                                            <XAxis dataKey="platform" className="text-xs" />
                                                            <YAxis className="text-xs" />
                                                            <Tooltip contentStyle={{ backgroundColor: 'var(--background)', borderColor: 'var(--border)' }} />
                                                            <Bar dataKey="spend" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                                        </RechartsBarChart>
                                                    </ResponsiveContainer>
                                                </div>
                                            </div>
                                        )}

                                        {/* Table Preview */}
                                        {reportConfig.includeTables && chartData.length > 0 && (
                                            <div>
                                                <h3 className="font-semibold mb-3">Data Table</h3>
                                                <div className="border rounded-lg overflow-hidden">
                                                    <table className="w-full text-sm">
                                                        <thead className="bg-muted">
                                                            <tr>
                                                                <th className="px-4 py-2 text-left">Platform</th>
                                                                <th className="px-4 py-2 text-right">Spend</th>
                                                                <th className="px-4 py-2 text-right">Clicks</th>
                                                                <th className="px-4 py-2 text-right">Conversions</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {chartData.slice(0, 5).map((row, i) => (
                                                                <tr key={i} className="border-t">
                                                                    <td className="px-4 py-2">{row.platform}</td>
                                                                    <td className="px-4 py-2 text-right">{formatCurrency(row.spend)}</td>
                                                                    <td className="px-4 py-2 text-right">{row.clicks.toLocaleString()}</td>
                                                                    <td className="px-4 py-2 text-right">{row.conversions.toLocaleString()}</td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Pivot Table Tab */}
                <TabsContent value="pivot" className="space-y-4">
                    <div className="grid gap-4 lg:grid-cols-4">
                        {/* Pivot Controls */}
                        <Card className="lg:col-span-1 border-t-4 border-t-purple-500 shadow-sm">
                            <CardHeader className="pb-3 bg-muted/20">
                                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                                    <Filter className="h-4 w-4 text-purple-600" /> Configuration
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4 pt-4">
                                {/* Rows Selector */}
                                <div className="space-y-2">
                                    <Label className="text-xs font-semibold text-muted-foreground">Row Grouping (Order Matters)</Label>
                                    <div className="flex flex-wrap gap-2">
                                        {pivotConfig.rows.map((r, i) => (
                                            <span key={r} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-purple-100 text-purple-700 text-xs font-medium border border-purple-200">
                                                {/* Move Left */}
                                                {i > 0 && (
                                                    <button onClick={() => {
                                                        const newRows = [...pivotConfig.rows];
                                                        [newRows[i], newRows[i - 1]] = [newRows[i - 1], newRows[i]];
                                                        setPivotConfig({ ...pivotConfig, rows: newRows });
                                                    }} className="hover:text-purple-900"><ArrowLeft className="h-3 w-3" /></button>
                                                )}

                                                {PIVOT_DIMENSIONS.find(d => d.value === r)?.label}

                                                {/* Move Right */}
                                                {i < pivotConfig.rows.length - 1 && (
                                                    <button onClick={() => {
                                                        const newRows = [...pivotConfig.rows];
                                                        [newRows[i], newRows[i + 1]] = [newRows[i + 1], newRows[i]];
                                                        setPivotConfig({ ...pivotConfig, rows: newRows });
                                                    }} className="hover:text-purple-900"><ArrowRight className="h-3 w-3" /></button>
                                                )}

                                                <div className="h-3 w-px bg-purple-300 mx-1"></div>
                                                <button onClick={() => setPivotConfig({ ...pivotConfig, rows: pivotConfig.rows.filter(row => row !== r) })}><Trash2 className="h-3 w-3" /></button>
                                            </span>
                                        ))}
                                    </div>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <button className="flex h-8 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-xs ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                                                <span>+ Add/Remove Dimensions</span>
                                                <ChevronDown className="h-4 w-4 opacity-50" />
                                            </button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-[200px] p-0" align="start">
                                            <div className="p-2 space-y-1 max-h-[300px] overflow-auto">
                                                {PIVOT_DIMENSIONS.map(d => {
                                                    const isSelected = pivotConfig.rows.includes(d.value);
                                                    return (
                                                        <div key={d.value} className="flex items-center space-x-2 p-1 hover:bg-muted rounded">
                                                            <Checkbox
                                                                id={`row-${d.value}`}
                                                                checked={isSelected}
                                                                onCheckedChange={(checked) => {
                                                                    if (checked) {
                                                                        setPivotConfig({ ...pivotConfig, rows: [...pivotConfig.rows, d.value] });
                                                                    } else {
                                                                        setPivotConfig({ ...pivotConfig, rows: pivotConfig.rows.filter(r => r !== d.value) });
                                                                    }
                                                                }}
                                                            />
                                                            <label htmlFor={`row-${d.value}`} className="text-xs cursor-pointer w-full font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                                {d.label}
                                                            </label>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </PopoverContent>
                                    </Popover>
                                </div>

                                <div className="border-t my-2"></div>

                                {/* Values Selector (Multi-Select) */}
                                <div className="space-y-2">
                                    <Label className="text-xs font-semibold text-muted-foreground">Metrics (Values)</Label>
                                    <div className="flex flex-wrap gap-2">
                                        {pivotConfig.values.map((v, i) => (
                                            <span key={v} className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-green-100 text-green-700 text-xs font-medium border border-green-200">
                                                {/* Move Left */}
                                                {i > 0 && (
                                                    <button onClick={() => {
                                                        const newValues = [...pivotConfig.values];
                                                        [newValues[i], newValues[i - 1]] = [newValues[i - 1], newValues[i]];
                                                        setPivotConfig({ ...pivotConfig, values: newValues });
                                                    }} className="hover:text-green-900"><ArrowLeft className="h-3 w-3" /></button>
                                                )}

                                                {PIVOT_METRICS.find(m => m.value === v)?.label}

                                                {/* Move Right */}
                                                {i < pivotConfig.values.length - 1 && (
                                                    <button onClick={() => {
                                                        const newValues = [...pivotConfig.values];
                                                        [newValues[i], newValues[i + 1]] = [newValues[i + 1], newValues[i]];
                                                        setPivotConfig({ ...pivotConfig, values: newValues });
                                                    }} className="hover:text-green-900"><ArrowRight className="h-3 w-3" /></button>
                                                )}

                                                <div className="h-3 w-px bg-green-300 mx-1"></div>
                                                <button onClick={() => setPivotConfig({ ...pivotConfig, values: pivotConfig.values.filter(val => val !== v) })}><Trash2 className="h-3 w-3" /></button>
                                            </span>
                                        ))}
                                    </div>
                                    <Popover>
                                        <PopoverTrigger asChild>
                                            <button className="flex h-8 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-xs ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                                                <span>+ Add/Remove Metrics</span>
                                                <ChevronDown className="h-4 w-4 opacity-50" />
                                            </button>
                                        </PopoverTrigger>
                                        <PopoverContent className="w-[200px] p-0" align="start">
                                            <div className="p-2 space-y-1 max-h-[300px] overflow-auto">
                                                {PIVOT_METRICS.map(m => {
                                                    const isSelected = pivotConfig.values.includes(m.value);
                                                    return (
                                                        <div key={m.value} className="flex items-center space-x-2 p-1 hover:bg-muted rounded">
                                                            <Checkbox
                                                                id={`val-${m.value}`}
                                                                checked={isSelected}
                                                                onCheckedChange={(checked) => {
                                                                    if (checked) {
                                                                        setPivotConfig({ ...pivotConfig, values: [...pivotConfig.values, m.value] });
                                                                    } else {
                                                                        setPivotConfig({ ...pivotConfig, values: pivotConfig.values.filter(val => val !== m.value) });
                                                                    }
                                                                }}
                                                            />
                                                            <label htmlFor={`val-${m.value}`} className="text-xs cursor-pointer w-full font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                                                                {m.label}
                                                            </label>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </PopoverContent>
                                    </Popover>
                                </div>

                                {/* Layout & Aggregation */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label className="text-xs font-semibold text-muted-foreground">Aggregation</Label>
                                        <div className="grid grid-cols-3 gap-1">
                                            {['sum', 'avg', 'count'].map(agg => (
                                                <button
                                                    key={agg}
                                                    onClick={() => setPivotConfig({ ...pivotConfig, aggregation: agg as any })}
                                                    className={`text-xs py-1 rounded border ${pivotConfig.aggregation === agg ? 'bg-purple-600 text-white border-purple-600' : 'bg-background hover:bg-muted'}`}
                                                >
                                                    {agg.toUpperCase()}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <Label className="text-xs font-semibold text-muted-foreground">Layout</Label>
                                        <div className="flex items-center gap-2">
                                            <div className="grid grid-cols-2 gap-1 flex-1">
                                                {['compact', 'tabular'].map(l => (
                                                    <button
                                                        key={l}
                                                        onClick={() => setPivotConfig({ ...pivotConfig, layout: l as any })}
                                                        className={`text-xs py-1 rounded border capitalize ${pivotConfig.layout === l ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-background hover:bg-muted'}`}
                                                    >
                                                        {l}
                                                    </button>
                                                ))}
                                            </div>

                                            {/* Style Settings Popover */}
                                            <Popover>
                                                <PopoverTrigger asChild>
                                                    <Button variant="outline" size="sm" className="h-full px-3"><Settings2 className="h-4 w-4" /></Button>
                                                </PopoverTrigger>
                                                <PopoverContent className="w-[280px] p-4" align="end">
                                                    <h4 className="font-medium text-sm mb-3">Table Appearance</h4>
                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <Label className="text-xs">Density</Label>
                                                            <div className="grid grid-cols-3 gap-1">
                                                                {['compact', 'normal', 'spacious'].map(d => (
                                                                    <button
                                                                        key={d}
                                                                        onClick={() => setPivotConfig({ ...pivotConfig, design: { ...pivotConfig.design, density: d as any } })}
                                                                        className={`text-xs py-1 rounded border capitalize ${pivotConfig.design.density === d ? 'bg-primary text-primary-foreground border-primary' : 'bg-background hover:bg-muted'}`}
                                                                    >
                                                                        {d}
                                                                    </button>
                                                                ))}
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center justify-between">
                                                            <Label className="text-xs">Striped Rows</Label>
                                                            <Switch
                                                                checked={pivotConfig.design.striped}
                                                                onCheckedChange={(c) => setPivotConfig({ ...pivotConfig, design: { ...pivotConfig.design, striped: c } })}
                                                            />
                                                        </div>

                                                        <div className="flex items-center justify-between">
                                                            <Label className="text-xs">Grid Lines</Label>
                                                            <Switch
                                                                checked={pivotConfig.design.gridLines}
                                                                onCheckedChange={(c) => setPivotConfig({ ...pivotConfig, design: { ...pivotConfig.design, gridLines: c } })}
                                                            />
                                                        </div>
                                                    </div>
                                                </PopoverContent>
                                            </Popover>
                                        </div>
                                    </div>
                                </div>

                                <Button className="w-full mt-4 bg-gradient-to-r from-purple-600 to-indigo-600" size="sm" onClick={handleExportPivot}>
                                    <Download className="mr-2 h-4 w-4" /> Export CSV
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Pivot Grid */}
                        <Card className="lg:col-span-3 min-h-[500px]">
                            <CardHeader className="py-3 border-b flex flex-row items-center justify-between">
                                <CardTitle className="text-base font-medium">Analysis Grid</CardTitle>
                                <div className="text-xs text-muted-foreground">{pivotData.length} records analyzed</div>
                            </CardHeader>
                            <CardContent className="p-0 overflow-auto max-h-[600px]">
                                {loading ? (
                                    <div className="flex items-center justify-center p-12"><Loader2 className="h-8 w-8 animate-spin text-purple-600" /></div>
                                ) : (
                                    <table className="w-full text-sm">
                                        <thead className="bg-muted/50 sticky top-0 z-10 backdrop-blur-sm">
                                            <tr>
                                                {pivotConfig.layout === 'tabular' ? (
                                                    // Tabular Header: All Dimension Columns
                                                    pivotConfig.rows.map(r => (
                                                        <th key={r} className={`text-left border-b border-r max-w-[150px] ${getCellStyle(true, false)}`}>
                                                            {PIVOT_DIMENSIONS.find(d => d.value === r)?.label}
                                                        </th>
                                                    ))
                                                ) : (
                                                    // Compact Header: Single Group Column
                                                    <th className={`text-left border-b border-r w-1/3 ${getCellStyle(true, false)}`}>Group</th>
                                                )}

                                                {/* Metric Columns */}
                                                {pivotConfig.values.map((v, i) => {
                                                    const isLast = i === pivotConfig.values.length - 1;
                                                    return (
                                                        <th key={v} className={`text-right border-b border-r min-w-[100px] ${getCellStyle(true, isLast)}`}>
                                                            {pivotConfig.aggregation.toUpperCase()} of {PIVOT_METRICS.find(m => m.value === v)?.label}
                                                        </th>
                                                    );
                                                })}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {pivotConfig.layout === 'tabular'
                                                ? renderPivotRowsTabular(getPivotData())
                                                : renderPivotRows(getPivotData())
                                            }
                                        </tbody>
                                        <tfoot className="bg-muted/20 font-semibold sticky bottom-0">
                                            <tr>
                                                {pivotConfig.layout === 'tabular' ? (
                                                    <td colSpan={pivotConfig.rows.length} className={`border-t border-r ${getCellStyle(false, false)}`}>Grand Total</td>
                                                ) : (
                                                    <td className={`border-t border-r ${getCellStyle(false, false)}`}>Grand Total</td>
                                                )}

                                                {pivotConfig.values.map((v, i) => {
                                                    const isLast = i === pivotConfig.values.length - 1;
                                                    return (
                                                        <td key={v} className={`border-t text-right border-r ${getCellStyle(false, isLast)}`}>
                                                            {(() => {
                                                                const val = calculateLimit(pivotData, v);
                                                                return v.includes('spend') ? formatCurrency(val) :
                                                                    v.includes('ctr') ? `${val.toFixed(2)}%` : val.toLocaleString(undefined, { maximumFractionDigits: 1 });
                                                            })()}
                                                        </td>
                                                    );
                                                })}
                                            </tr>
                                        </tfoot>
                                    </table>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                {/* Shared Reports Tab */}
                <TabsContent value="share" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Shared Reports</CardTitle>
                            <CardDescription>Manage your shareable report links</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {sharedReports.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                                    <Share2 className="h-12 w-12 mb-4 opacity-20" />
                                    <p>No shared reports yet</p>
                                    <p className="text-sm">Generate a report and click the share button</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {sharedReports.map(report => (
                                        <div key={report.id} className="flex items-center justify-between p-4 border rounded-lg">
                                            <div>
                                                <p className="font-medium">{report.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    Created: {format(new Date(report.createdAt), 'MMM d, yyyy')} •
                                                    Expires: {format(new Date(report.expiresAt), 'MMM d, yyyy')} •
                                                    {report.views} views
                                                </p>
                                            </div>
                                            <div className="flex gap-2">
                                                <Button type="button" variant="outline" size="sm" onClick={() => {
                                                    setShareUrl(`${window.location.origin}/reports?shared=${report.id}`);
                                                    setShowShareDialog(true);
                                                }}>
                                                    <Link2 className="mr-2 h-4 w-4" />Copy Link
                                                </Button>
                                                <Button type="button" variant="ghost" size="sm" className="text-destructive" onClick={() => deleteSharedReport(report.id)}>
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Annotations Tab */}
                <TabsContent value="annotations" className="space-y-4">
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between">
                            <div>
                                <CardTitle>Annotations & Notes</CardTitle>
                                <CardDescription>Add notes and callouts to your reports</CardDescription>
                            </div>
                            <Dialog open={showAnnotationDialog} onOpenChange={setShowAnnotationDialog}>
                                <DialogTrigger asChild>
                                    <Button type="button" size="sm">
                                        <Plus className="mr-2 h-4 w-4" />Add Note
                                    </Button>
                                </DialogTrigger>
                                <DialogContent>
                                    <DialogHeader>
                                        <DialogTitle>Add Annotation</DialogTitle>
                                    </DialogHeader>
                                    <div className="py-4">
                                        <Textarea
                                            placeholder="Enter your note or insight..."
                                            value={newAnnotation}
                                            onChange={(e) => setNewAnnotation(e.target.value)}
                                            rows={4}
                                        />
                                    </div>
                                    <DialogFooter>
                                        <Button type="button" variant="outline" onClick={() => setShowAnnotationDialog(false)}>Cancel</Button>
                                        <Button type="button" onClick={addAnnotation}>Add Note</Button>
                                    </DialogFooter>
                                </DialogContent>
                            </Dialog>
                        </CardHeader>
                        <CardContent>
                            {annotations.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                                    <MessageSquare className="h-12 w-12 mb-4 opacity-20" />
                                    <p>No annotations yet</p>
                                    <p className="text-sm">Add notes to document insights</p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {annotations.map((annotation, index) => (
                                        <div key={annotation.id} className="flex items-start gap-3 p-4 border rounded-lg bg-muted/30">
                                            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold">
                                                {index + 1}
                                            </div>
                                            <div className="flex-1">
                                                <p className="text-sm">{annotation.text}</p>
                                                <p className="text-xs text-muted-foreground mt-1">
                                                    Added: {format(new Date(annotation.createdAt), 'MMM d, yyyy h:mm a')}
                                                </p>
                                            </div>
                                            <Button type="button" variant="ghost" size="sm" className="text-destructive" onClick={() => removeAnnotation(annotation.id)}>
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Share Dialog */}
            <Dialog open={showShareDialog} onOpenChange={setShowShareDialog}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Share Report</DialogTitle>
                    </DialogHeader>
                    <div className="py-4 space-y-4">
                        <p className="text-sm text-muted-foreground">
                            Copy this link to share your report. The link expires in 7 days.
                        </p>
                        <div className="flex gap-2">
                            <Input value={shareUrl} readOnly className="font-mono text-xs" />
                            <Button type="button" onClick={copyToClipboard} variant="outline">
                                {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                            </Button>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </div>
    );
}
