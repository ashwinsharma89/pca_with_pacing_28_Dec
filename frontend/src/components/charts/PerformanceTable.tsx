"use client";

import React, { useState } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface PerformanceTableProps {
    title: string;
    description: string;
    data: any[];
    type: 'month' | 'platform' | 'channel' | 'funnel';
    onMonthClick?: (month: string) => void;
    selectedMonth?: string | null;
    onPlatformClick?: (platform: string) => void;
    selectedPlatform?: string | null;
    onFunnelStageClick?: (funnelStage: string) => void;
    selectedFunnelStage?: string | null;
}

export function PerformanceTable({ title, description, data, type, onMonthClick, selectedMonth, onPlatformClick, selectedPlatform, onFunnelStageClick, selectedFunnelStage }: PerformanceTableProps) {
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

    if (!data || data.length === 0) return null;

    const formatMonth = (monthStr: string) => {
        const [year, month] = monthStr.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1);
        const monthName = date.toLocaleDateString('en-US', { month: 'short' });
        const yearShort = year.slice(-2);
        return `${monthName} ${yearShort}`;
    };

    const formatValue = (key: string, val: any) => {
        if (key === 'month') return formatMonth(val);
        if (key === 'spend') return `$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
        if (key === 'cpm' || key === 'cpc' || key === 'cpa') return `$${Number(val).toFixed(2)}`;
        if (key === 'ctr' || key === 'roas') return `${Number(val).toFixed(2)}${key === 'ctr' ? '%' : 'x'}`;
        if (key === 'impressions' || key === 'clicks' || key === 'conversions' || key === 'reach') return Number(val).toLocaleString();
        return val;
    };

    const getHeatmapColor = (key: string, val: number, allData: any[]) => {
        const values = allData.map(d => Number(d[key]));
        const min = Math.min(...values);
        const max = Math.max(...values);
        const range = max - min;
        if (range === 0) return 'rgba(16, 185, 129, 0.1)';

        const percentage = (val - min) / range;

        // Green scale for good metrics (spend, impressions, clicks, conversions, roas, ctr)
        // Red scale for cost metrics (cpm, cpc, cpa) - but let's stick to one consistent green for now as in snip
        const opacity = 0.1 + (percentage * 0.4);
        return `rgba(16, 185, 129, ${opacity})`;
    };

    const columns = type === 'funnel' ? [
        { key: 'platform', label: 'Funnel Stage' },
        { key: 'spend', label: 'Spend' },
        { key: 'impressions', label: 'Impressions' },
        { key: 'reach', label: 'Reach' },
        { key: 'cpm', label: 'CPM' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'ctr', label: 'CTR' },
        { key: 'cpc', label: 'CPC' },
        { key: 'conversions', label: 'Conversions' },
        { key: 'cpa', label: 'CPA' },
        { key: 'roas', label: 'ROAS' }
    ] : [
        { key: type === 'month' ? 'month' : (type === 'platform' ? 'platform' : 'channel'), label: type === 'month' ? 'Month' : (type === 'platform' ? 'Platform' : 'Channel') },
        { key: 'spend', label: 'Spend' },
        { key: 'clicks', label: 'Clicks' },
        { key: 'ctr', label: 'CTR' },
        { key: 'conversions', label: 'Conversions' },
        { key: 'cpa', label: 'CPA' },
        { key: 'roas', label: 'ROAS' }
    ];

    // Sort data
    const sortedData = React.useMemo(() => {
        if (!sortKey) return data;

        return [...data].sort((a, b) => {
            const aVal = a[sortKey];
            const bVal = b[sortKey];

            // Handle string sorting (month, platform)
            if (typeof aVal === 'string' && typeof bVal === 'string') {
                const comparison = aVal.localeCompare(bVal);
                return sortDirection === 'asc' ? comparison : -comparison;
            }

            // Handle number sorting
            const aNum = Number(aVal) || 0;
            const bNum = Number(bVal) || 0;
            return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
        });
    }, [data, sortKey, sortDirection]);

    const handleSort = (key: string) => {
        if (sortKey === key) {
            // Toggle direction if same column
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            // New column, default to descending for numbers, ascending for text
            setSortKey(key);
            setSortDirection(key === 'month' || key === 'platform' ? 'asc' : 'desc');
        }
    };

    const getSortIcon = (key: string) => {
        if (sortKey !== key) {
            return <ArrowUpDown className="h-3 w-3 opacity-50" />;
        }
        return sortDirection === 'asc'
            ? <ArrowUp className="h-3 w-3" />
            : <ArrowDown className="h-3 w-3" />;
    };

    return (
        <Card className="border-none bg-background/50 backdrop-blur-sm shadow-lg ring-1 ring-white/10">
            <CardHeader>
                <CardTitle className="text-sm font-bold uppercase tracking-wider">{title}</CardTitle>
                <CardDescription>{description}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border border-white/5 overflow-hidden">
                    <Table>
                        <TableHeader className="bg-white/5">
                            <TableRow>
                                {columns.map(col => (
                                    <TableHead
                                        key={col.key}
                                        className="text-[10px] font-bold uppercase tracking-tight h-8 py-0 cursor-pointer hover:bg-white/10 transition-colors"
                                        onClick={() => handleSort(col.key)}
                                    >
                                        <div className="flex items-center gap-1">
                                            {col.label}
                                            {getSortIcon(col.key)}
                                        </div>
                                    </TableHead>
                                ))}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {sortedData.map((row, i) => {
                                const isMonthRow = type === 'month';
                                const isPlatformRow = type === 'platform';
                                const isFunnelRow = type === 'funnel';
                                const isSelected = (isMonthRow && selectedMonth === row.month)
                                    || (isPlatformRow && selectedPlatform === row.platform)
                                    || (isFunnelRow && selectedFunnelStage === row.platform);
                                const isClickable = (isMonthRow && onMonthClick)
                                    || (isPlatformRow && onPlatformClick)
                                    || (isFunnelRow && onFunnelStageClick);

                                return (
                                    <TableRow
                                        key={i}
                                        className={`
                                            border-white/5 transition-all
                                            ${isClickable ? 'cursor-pointer hover:bg-blue-500/20' : 'hover:bg-white/5'}
                                            ${isSelected ? 'bg-blue-500/30 ring-1 ring-blue-400/50' : ''}
                                        `}
                                        onClick={() => {
                                            if (isMonthRow && onMonthClick) {
                                                onMonthClick(row.month);
                                            } else if (isPlatformRow && onPlatformClick) {
                                                onPlatformClick(row.platform);
                                            } else if (isFunnelRow && onFunnelStageClick) {
                                                onFunnelStageClick(row.platform);
                                            }
                                        }}
                                    >
                                        {columns.map(col => {
                                            const isNumeric = typeof row[col.key] === 'number';
                                            const bgColor = isNumeric && col.key !== 'month' && col.key !== 'platform'
                                                ? getHeatmapColor(col.key, row[col.key], data)
                                                : 'transparent';

                                            return (
                                                <TableCell
                                                    key={col.key}
                                                    className={`py-2 text-xs font-medium ${isSelected && (col.key === 'month' || col.key === 'platform') ? 'font-bold text-blue-400' : ''}`}
                                                    style={{ backgroundColor: bgColor }}
                                                >
                                                    {formatValue(col.key, row[col.key])}
                                                </TableCell>
                                            );
                                        })}
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                </div>
            </CardContent>
        </Card>
    );
}
