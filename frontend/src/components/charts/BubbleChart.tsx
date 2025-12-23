"use client";

import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const ScatterChart = dynamic(() => import('recharts').then(mod => mod.ScatterChart), { ssr: false });
const Scatter = dynamic(() => import('recharts').then(mod => mod.Scatter), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const ZAxis = dynamic(() => import('recharts').then(mod => mod.ZAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Legend = dynamic(() => import('recharts').then(mod => mod.Legend), { ssr: false });

interface BubbleChartProps {
    data: any[];
    xKey?: string;
    yKey?: string;
    sizeKey?: string;
    onBubbleClick?: (item: any) => void;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899'];

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        const data = payload[0].payload;
        return (
            <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
                <p className="font-semibold text-foreground">{data.name}</p>
                <p className="text-sm text-muted-foreground">Spend: ${data.spend?.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">Conversions: {data.conversions?.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">ROAS: {data.roas?.toFixed(2)}x</p>
            </div>
        );
    }
    return null;
};

export function BubbleChart({ data, xKey = 'spend', yKey = 'conversions', sizeKey = 'roas', onBubbleClick }: BubbleChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data available</div>;
    }

    // Transform data for scatter chart with bubble sizes
    const bubbleData = data.map((item, index) => ({
        ...item,
        x: item[xKey] || 0,
        y: item[yKey] || 0,
        z: Math.max((item[sizeKey] || 0) * 100, 50), // Scale ROAS for bubble size
        fill: COLORS[index % COLORS.length]
    }));

    // Calculate max ROAS for z-axis domain
    const maxZ = Math.max(...bubbleData.map(d => d.z));

    return (
        <motion.div
            className="w-full h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                        type="number"
                        dataKey="x"
                        name="Spend"
                        unit="$"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <YAxis
                        type="number"
                        dataKey="y"
                        name="Conversions"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                    />
                    <ZAxis
                        type="number"
                        dataKey="z"
                        range={[100, 1000]}
                        name="ROAS"
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    {bubbleData.map((item, index) => (
                        <Scatter
                            key={item.name}
                            name={item.name}
                            data={[item]}
                            fill={item.fill}
                            onClick={() => onBubbleClick?.(item)}
                            cursor="pointer"
                        />
                    ))}
                </ScatterChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
