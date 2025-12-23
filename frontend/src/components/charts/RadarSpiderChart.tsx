"use client";

import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const RadarChart = dynamic(() => import('recharts').then(mod => mod.RadarChart), { ssr: false });
const PolarGrid = dynamic(() => import('recharts').then(mod => mod.PolarGrid), { ssr: false });
const PolarAngleAxis = dynamic(() => import('recharts').then(mod => mod.PolarAngleAxis), { ssr: false });
const PolarRadiusAxis = dynamic(() => import('recharts').then(mod => mod.PolarRadiusAxis), { ssr: false });
const Radar = dynamic(() => import('recharts').then(mod => mod.Radar), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });

interface RadarChartProps {
    data: any[];
    metrics?: string[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

// Normalize values to 0-100 scale for radar chart
const normalizeData = (data: any[], metrics: string[]) => {
    const maxValues: { [key: string]: number } = {};

    metrics.forEach(metric => {
        maxValues[metric] = Math.max(...data.map(d => d[metric] || 0));
    });

    return metrics.map(metric => ({
        metric: metric.toUpperCase(),
        fullMark: 100,
        ...data.reduce((acc, item, idx) => {
            const normalized = maxValues[metric] > 0
                ? ((item[metric] || 0) / maxValues[metric]) * 100
                : 0;
            acc[item.name] = Math.round(normalized);
            return acc;
        }, {})
    }));
};

export function RadarSpiderChart({ data, metrics = ['ctr', 'cpc', 'cpa', 'roas', 'cpm'] }: RadarChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data available</div>;
    }

    const normalizedData = normalizeData(data, metrics);
    const platforms = data.map(d => d.name);

    return (
        <motion.div
            className="w-full h-full"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={normalizedData}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis
                        dataKey="metric"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                    />
                    <PolarRadiusAxis
                        angle={30}
                        domain={[0, 100]}
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                    />
                    {platforms.slice(0, 5).map((platform, idx) => (
                        <Radar
                            key={platform}
                            name={platform}
                            dataKey={platform}
                            stroke={COLORS[idx % COLORS.length]}
                            fill={COLORS[idx % COLORS.length]}
                            fillOpacity={0.2}
                            strokeWidth={2}
                        />
                    ))}
                    <Legend
                        wrapperStyle={{ fontSize: '12px' }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                        }}
                        formatter={(value: any) => [`${value}%`, 'Score']}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
