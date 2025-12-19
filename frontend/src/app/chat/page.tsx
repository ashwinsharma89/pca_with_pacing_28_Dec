"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2, Send, Database, User, Bot, Table as TableIcon, Brain, Sparkles, BookOpen, BarChart3, PieChartIcon, TrendingUp, ChevronDown, ChevronRight, Download } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from "recharts";

const CHART_COLORS = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#6366f1', '#14b8a6'];

interface ChartData {
    type: 'bar' | 'pie' | 'line';
    title: string;
    labels: string[];
    values: number[];
    label_key: string;
    value_key: string;
}

interface Message {
    role: "user" | "assistant";
    content: string;
    sql?: string;
    data?: any[];
    columns?: string[];
    knowledge_mode?: boolean;
    sources?: string[];
    rag_enhanced?: boolean;
    summary?: string;
    chart?: ChartData;
}

export default function GlobalChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        { role: "assistant", content: "Hello! I can analyze your campaign data or answer marketing questions.\n\n**Data Mode** (default): Ask SQL-style questions about your data like 'Which platform has highest ROI?'\n\n**Knowledge Mode**: Get marketing insights, benchmarks, and best practices by enabling the toggle above." }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [loadingStage, setLoadingStage] = useState("");
    const [knowledgeMode, setKnowledgeMode] = useState(false);
    const [suggestedQuestions, setSuggestedQuestions] = useState<Array<{ question: string, description: string }>>([]);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Fetch suggested questions on mount
    useEffect(() => {
        const fetchSuggestions = async () => {
            try {
                const response: any = await api.get('/campaigns/suggested-questions');
                if (response?.suggestions) {
                    setSuggestedQuestions(response.suggestions);
                }
            } catch (error) {
                console.error('Failed to fetch suggested questions:', error);
            }
        };
        fetchSuggestions();
    }, []);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Ctrl/Cmd + K to focus input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                inputRef.current?.focus();
            }
            // Escape to clear input
            if (e.key === 'Escape' && document.activeElement === inputRef.current) {
                setInput("");
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMessage = input;
        setInput("");
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setLoading(true);
        setLoadingStage("Analyzing question...");

        try {
            setTimeout(() => setLoadingStage("Generating SQL query..."), 500);
            setTimeout(() => setLoadingStage("Executing query..."), 1500);
            setTimeout(() => setLoadingStage("Generating insights..."), 2500);

            const result = await api.chatGlobal(userMessage, {
                knowledge_mode: knowledgeMode,
                use_rag_context: true
            });

            if (result.success) {
                const data = result.data || [];
                const columns = data.length > 0 ? Object.keys(data[0]) : [];

                setMessages(prev => [...prev, {
                    role: "assistant",
                    content: result.answer,
                    sql: result.sql_query || result.sql,
                    data: data.length > 0 ? data : undefined,
                    columns: columns.length > 0 ? columns : undefined,
                    knowledge_mode: result.knowledge_mode,
                    sources: result.sources,
                    rag_enhanced: result.rag_enhanced,
                    summary: result.summary,
                    chart: result.chart
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: "assistant",
                    content: `Error: ${result.error || "Failed to process query."}`
                }]);
            }
        } catch (error) {
            setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I encountered a network error." }]);
        } finally {
            setLoading(false);
        }
    };

    const formatCellValue = (value: any, columnName?: string): string => {
        if (value === null || value === undefined) return 'N/A';

        const colLower = (columnName || '').toLowerCase();

        // Check if it's a date string (ISO format or similar)
        if (typeof value === 'string') {
            // Match ISO date format or date with time
            const dateMatch = value.match(/^\d{4}-\d{2}-\d{2}(T|\s|$)/);
            if (dateMatch) {
                const date = new Date(value);
                if (!isNaN(date.getTime())) {
                    // Check if it's a month-level date (first day of month, midnight)
                    if (date.getDate() === 1) {
                        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
                    }
                    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
                }
            }
        }

        if (typeof value === 'number') {
            // CTR, Conversion Rate - format with %
            if (colLower.includes('ctr') || colLower.includes('rate') || colLower.includes('conversion_rate')) {
                return `${value.toFixed(2)}%`;
            }

            // CPC, CPM, CPA, Spend - format with $
            if (colLower.includes('cpc') || colLower.includes('cpm') || colLower.includes('cpa') || colLower.includes('spend') || colLower.includes('cost')) {
                if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
                if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
                return `$${value.toFixed(2)}`;
            }

            // ROAS - format with x
            if (colLower.includes('roas')) {
                return `${value.toFixed(2)}x`;
            }

            // Default number formatting
            if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
            if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
            return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
        }
        return String(value);
    };

    const exportToCSV = (data: any[], filename: string) => {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row =>
                headers.map(header => {
                    const value = row[header];
                    const formatted = typeof value === 'string' && value.includes(',')
                        ? `"${value}"`
                        : value;
                    return formatted;
                }).join(',')
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const exportToJSON = (data: any[], filename: string) => {
        if (!data || data.length === 0) return;

        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const renderContent = (content: string) => {
        // Simple markdown-like rendering for bold text and newlines
        return content.split('\n').map((line, lineIdx) => {
            const parts = line.split(/(\*\*[^*]+\*\*)/g);
            return (
                <span key={lineIdx}>
                    {parts.map((part, idx) => {
                        if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={idx}>{part.slice(2, -2)}</strong>;
                        }
                        return part;
                    })}
                    {lineIdx < content.split('\n').length - 1 && <br />}
                </span>
            );
        });
    };

    return (
        <div className="py-10 h-[calc(100vh-4rem)] flex flex-col">
            <div className="mb-6 flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">💬 Q&A</h1>
                    <p className="text-muted-foreground">
                        Ask questions about your campaigns or get marketing insights.
                    </p>
                </div>
                <div className="flex items-center gap-4 p-4 rounded-lg bg-card border">
                    <div className="flex items-center gap-2">
                        <Database className="h-4 w-4 text-muted-foreground" />
                        <span className={`text-sm ${!knowledgeMode ? 'font-medium text-foreground' : 'text-muted-foreground'}`}>Data</span>
                    </div>
                    <Switch
                        checked={knowledgeMode}
                        onCheckedChange={setKnowledgeMode}
                        aria-label="Toggle knowledge mode"
                    />
                    <div className="flex items-center gap-2">
                        <Brain className="h-4 w-4 text-purple-500" />
                        <span className={`text-sm ${knowledgeMode ? 'font-medium text-purple-400' : 'text-muted-foreground'}`}>Knowledge</span>
                    </div>
                </div>
            </div>

            <Card className="flex-1 flex flex-col min-h-0">
                {/* Query Input - At Top */}
                <div className="border-b p-4">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleSend();
                        }}
                        className="flex gap-2"
                    >
                        <Input
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={knowledgeMode
                                ? "Ask about ROAS, benchmarks, best practices, pitfalls..."
                                : "Ask about your campaigns data..."}
                            disabled={loading}
                            className="flex-1"
                        />
                        <Button type="submit" disabled={loading || !input.trim()}>
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                        </Button>
                    </form>

                    {/* Suggested Questions */}
                    {suggestedQuestions.length > 0 && messages.length === 1 && (
                        <div className="mt-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Sparkles className="h-4 w-4 text-purple-500" />
                                <span className="text-sm font-medium text-muted-foreground">Try asking:</span>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {suggestedQuestions.map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => setInput(suggestion.question)}
                                        className="px-3 py-1.5 text-sm rounded-full bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 hover:border-purple-500/40 transition-all duration-200 hover:scale-105"
                                        title={suggestion.description}
                                    >
                                        {suggestion.question}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Messages - Below Input, Newest at Top */}
                <CardContent className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                    {loading && (
                        <div className="flex justify-start">
                            <div className="flex gap-3">
                                <div className={`h-8 w-8 rounded-full flex items-center justify-center ${knowledgeMode ? "bg-purple-500/20" : "bg-muted"}`}>
                                    {knowledgeMode ? <Brain size={16} className="text-purple-400" /> : <Bot size={16} />}
                                </div>
                                <div className={`rounded-lg p-3 ${knowledgeMode ? "bg-purple-500/10" : "bg-muted"}`}>
                                    <div className="flex items-center gap-2 mb-2">
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        <span className="text-sm font-medium">{loadingStage}</span>
                                    </div>
                                    <div className="flex gap-1">
                                        <div className={`h-1 w-12 rounded-full ${loadingStage.includes("Analyzing") ? "bg-purple-500" : "bg-purple-500/30"}`} />
                                        <div className={`h-1 w-12 rounded-full ${loadingStage.includes("Generating SQL") ? "bg-purple-500" : "bg-purple-500/30"}`} />
                                        <div className={`h-1 w-12 rounded-full ${loadingStage.includes("Executing") ? "bg-purple-500" : "bg-purple-500/30"}`} />
                                        <div className={`h-1 w-12 rounded-full ${loadingStage.includes("insights") ? "bg-purple-500" : "bg-purple-500/30"}`} />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {[...messages].reverse().map((msg, index) => (
                        <div
                            key={index}
                            className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div className={`flex max-w-[95%] gap-3 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                                <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-primary text-primary-foreground" : msg.knowledge_mode ? "bg-purple-500/20 text-purple-400" : "bg-muted"}`}>
                                    {msg.role === "user" ? <User size={16} /> : msg.knowledge_mode ? <Brain size={16} /> : <Bot size={16} />}
                                </div>
                                <div className="space-y-2 flex-1">
                                    {/* Knowledge mode badge */}
                                    {msg.knowledge_mode && (
                                        <div className="flex items-center gap-2 text-xs">
                                            <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400 flex items-center gap-1">
                                                <Sparkles size={10} />
                                                Knowledge Mode
                                            </span>
                                        </div>
                                    )}

                                    {/* RAG enhanced badge */}
                                    {msg.rag_enhanced && !msg.knowledge_mode && (
                                        <div className="flex items-center gap-2 text-xs">
                                            <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 flex items-center gap-1">
                                                <BookOpen size={10} />
                                                RAG-Enhanced
                                            </span>
                                        </div>
                                    )}

                                    <div className={`rounded-lg p-3 text-sm ${msg.role === "user"
                                        ? "bg-primary text-primary-foreground"
                                        : msg.knowledge_mode ? "bg-purple-500/10 text-foreground border border-purple-500/20" : "bg-muted text-foreground"
                                        }`}>
                                        {renderContent(msg.content)}
                                    </div>

                                    {/* Knowledge Sources */}
                                    {msg.sources && msg.sources.length > 0 && (
                                        <div className="text-xs text-muted-foreground flex items-center gap-2 flex-wrap">
                                            <BookOpen size={10} />
                                            <span>Sources:</span>
                                            {msg.sources.map((source, i) => (
                                                <span key={i} className="px-1.5 py-0.5 rounded bg-muted">{source}</span>
                                            ))}
                                        </div>
                                    )}

                                    {/* 1. Table Results Display (First) */}
                                    {msg.data && msg.data.length > 0 && msg.columns && (
                                        <Card className="mt-2">
                                            <CardHeader className="pb-3">
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center gap-2">
                                                        <TableIcon size={16} className="text-muted-foreground" />
                                                        <CardTitle className="text-sm">Query Results ({msg.data.length} rows)</CardTitle>
                                                    </div>
                                                    <div className="flex gap-2">
                                                        <Button
                                                            size="sm"
                                                            variant="outline"
                                                            onClick={() => exportToCSV(msg.data!, `query-results-${Date.now()}`)}
                                                            className="h-7 text-xs"
                                                        >
                                                            <Download className="h-3 w-3 mr-1" />
                                                            CSV
                                                        </Button>
                                                        <Button
                                                            size="sm"
                                                            variant="outline"
                                                            onClick={() => exportToJSON(msg.data!, `query-results-${Date.now()}`)}
                                                            className="h-7 text-xs"
                                                        >
                                                            <Download className="h-3 w-3 mr-1" />
                                                            JSON
                                                        </Button>
                                                    </div>
                                                </div>
                                            </CardHeader>
                                            <CardContent className="p-0">
                                                <div className="max-h-[400px] overflow-auto">
                                                    <Table>
                                                        <TableHeader>
                                                            <TableRow className="border-b border-border/50">
                                                                {msg.columns.map((col) => (
                                                                    <TableHead key={col} className="font-semibold whitespace-nowrap">
                                                                        {col}
                                                                    </TableHead>
                                                                ))}
                                                            </TableRow>
                                                        </TableHeader>
                                                        <TableBody>
                                                            {msg.data.slice(0, 100).map((row, rowIndex) => (
                                                                <TableRow key={rowIndex} className="border-0 hover:bg-muted/50">
                                                                    {msg.columns!.map((col) => (
                                                                        <TableCell key={col} className="whitespace-nowrap py-2">
                                                                            {formatCellValue(row[col], col)}
                                                                        </TableCell>
                                                                    ))}
                                                                </TableRow>
                                                            ))}
                                                        </TableBody>
                                                    </Table>
                                                </div>
                                                {msg.data.length > 100 && (
                                                    <div className="text-xs text-muted-foreground text-center py-2 border-t">
                                                        Showing first 100 of {msg.data.length} rows
                                                    </div>
                                                )}
                                            </CardContent>
                                        </Card>
                                    )}

                                    {/* 2. SQL Query Display - Collapsible */}
                                    {msg.sql && msg.sql !== "N/A (Knowledge Mode)" && (
                                        <details className="text-xs group mt-2">
                                            <summary className="flex items-center gap-1.5 cursor-pointer text-muted-foreground hover:text-foreground transition-colors">
                                                <ChevronRight size={12} className="group-open:hidden" />
                                                <ChevronDown size={12} className="hidden group-open:inline" />
                                                <Database size={10} />
                                                <span>View SQL Query</span>
                                            </summary>
                                            <div className="mt-2 bg-slate-950 text-slate-50 p-2 rounded-md font-mono border border-slate-800">
                                                <code className="text-slate-200 whitespace-pre-wrap break-all">{msg.sql}</code>
                                            </div>
                                        </details>
                                    )}

                                    {/* 3. Chart Display */}
                                    {msg.chart && (
                                        <Card className="mt-2">
                                            <CardHeader className="pb-2">
                                                <div className="flex items-center gap-2">
                                                    {msg.chart.type === 'bar' && <BarChart3 size={16} className="text-purple-500" />}
                                                    {msg.chart.type === 'pie' && <PieChartIcon size={16} className="text-cyan-500" />}
                                                    {msg.chart.type === 'line' && <TrendingUp size={16} className="text-green-500" />}
                                                    <CardTitle className="text-sm">{msg.chart.title}</CardTitle>
                                                </div>
                                            </CardHeader>
                                            <CardContent className="pt-0">
                                                <div className="h-[200px]">
                                                    <ResponsiveContainer width="100%" height="100%">
                                                        {msg.chart.type === 'bar' ? (
                                                            <BarChart data={msg.chart.labels.map((label, i) => ({ name: label, value: msg.chart!.values[i] }))}>
                                                                <XAxis dataKey="name" fontSize={10} />
                                                                <YAxis fontSize={10} />
                                                                <Tooltip
                                                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                                                                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                                                                />
                                                                <Bar dataKey="value" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                                            </BarChart>
                                                        ) : msg.chart.type === 'pie' ? (
                                                            <PieChart>
                                                                <Pie
                                                                    data={msg.chart.labels.map((label, i) => ({ name: label, value: msg.chart!.values[i] }))}
                                                                    cx="50%"
                                                                    cy="50%"
                                                                    outerRadius={70}
                                                                    dataKey="value"
                                                                    label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                                                                    labelLine={false}
                                                                >
                                                                    {msg.chart.labels.map((_, index) => (
                                                                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                                                                    ))}
                                                                </Pie>
                                                                <Tooltip />
                                                            </PieChart>
                                                        ) : (
                                                            <LineChart data={msg.chart.labels.map((label, i) => ({ name: label, value: msg.chart!.values[i] }))}>
                                                                <XAxis dataKey="name" fontSize={10} />
                                                                <YAxis fontSize={10} />
                                                                <Tooltip
                                                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                                                                />
                                                                <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} dot={{ fill: '#10b981' }} />
                                                            </LineChart>
                                                        )}
                                                    </ResponsiveContainer>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )}

                                    {/* 3. Summary Display (Last) */}
                                    {msg.summary && (
                                        <Card className="mt-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20">
                                            <CardContent className="p-3">
                                                <div className="text-sm">
                                                    {renderContent(msg.summary)}
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )}

                                </div>
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>
        </div>
    );
}
