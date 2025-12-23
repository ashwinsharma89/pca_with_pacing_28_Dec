"use client";

import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { motion } from 'framer-motion';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';
import { ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown } from 'lucide-react';

interface KpiSparkGroupsProps {
    data: {
        current: any;
        previous: any;
        sparkline: any[];
    };
}

export function KpiSparkGroups({ data }: KpiSparkGroupsProps) {
    if (!data || !data.current) return null;

    const { current, previous, sparkline } = data;

    // Format large numbers as M or K
    const formatNumber = (num: number) => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return num.toLocaleString();
    };

    const calculateChange = (curr: number, prev: number) => {
        if (prev === 0) return 0;
        return ((curr - prev) / prev) * 100;
    };

    const formatPercent = (val: number) => {
        const absVal = Math.abs(val).toFixed(0);
        return `${val >= 0 ? '' : '-'}${absVal}%`;
    };

    const MetricItem = ({ label, value, color }: { label: string; value: string | number; color?: string }) => (
        <div className="flex flex-col items-center flex-1">
            <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium mb-1">{label}</span>
            <span className={`text-xl font-bold ${color || 'text-foreground'}`}>{value}</span>
        </div>
    );

    const ChangeIndicator = ({ val }: { val: number }) => (
        <div className={`flex items-center gap-0.5 text-xs font-bold ${val >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
            {val >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            {formatPercent(val)}
        </div>
    );

    const kpiGroups = [
        {
            title: "Spend & Impressions",
            color: "bg-emerald-500",
            metrics: [
                { label: "Cost", value: `$${formatNumber(current.spend)}` },
                { label: "CPM", value: `$${current.cpm.toFixed(2)}` },
                { label: "Impressions", value: formatNumber(current.impressions) },
                { label: "Reach", value: formatNumber(Math.round(current.impressions * 0.65)) }
            ],
            sparkKey: "spend",
            changes: [
                calculateChange(current.spend, previous.spend),
                calculateChange(current.cpm, previous.cpm),
                calculateChange(current.impressions, previous.impressions),
                calculateChange(current.impressions * 0.65, previous.impressions * 0.65)
            ]
        },
        {
            title: "Clicks",
            color: "bg-amber-500",
            metrics: [
                { label: "Clicks", value: formatNumber(current.clicks) },
                { label: "CTR", value: `${current.ctr.toFixed(2)}%` },
                { label: "CPC", value: `$${current.cpc.toFixed(2)}` }
            ],
            sparkKey: "clicks",
            changes: [
                calculateChange(current.clicks, previous.clicks),
                calculateChange(current.ctr, previous.ctr),
                calculateChange(current.cpc, previous.cpc)
            ]
        },
        {
            title: "Conversions",
            color: "bg-blue-500",
            metrics: [
                { label: "Conversions", value: formatNumber(current.conversions) },
                { label: "Conv Rate", value: `${((current.conversions / Math.max(1, current.clicks)) * 100).toFixed(2)}%` },
                { label: "CPA", value: `$${current.cpa.toFixed(2)}` },
                { label: "ROAS", value: `${current.roas.toFixed(2)}x` }
            ],
            sparkKey: "conversions",
            changes: [
                calculateChange(current.conversions, previous.conversions),
                calculateChange(current.conversions / Math.max(1, current.clicks), previous.conversions / Math.max(1, previous.clicks)),
                calculateChange(current.cpa, previous.cpa),
                calculateChange(current.roas, previous.roas)
            ]
        }
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {kpiGroups.map((group, idx) => (
                <Card key={idx} className="overflow-hidden border-none bg-background/50 backdrop-blur-sm shadow-lg ring-1 ring-white/10">
                    <div className={`${group.color} py-2 px-4`}>
                        <span className="text-white text-xs font-bold uppercase tracking-widest">{group.title}</span>
                    </div>
                    <CardContent className="p-6 space-y-4">
                        <div className="flex justify-between items-end">
                            {group.metrics.map((m, i) => (
                                <MetricItem key={i} label={m.label} value={m.value} />
                            ))}
                        </div>


                        <div className="flex justify-between px-2 pt-2">
                            {group.changes.map((c, i) => (
                                <ChangeIndicator key={i} val={c} />
                            ))}
                        </div>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
