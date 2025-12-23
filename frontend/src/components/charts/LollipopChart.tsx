"use client";

import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';

const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), { ssr: false });
const LabelList = dynamic(() => import('recharts').then(mod => mod.LabelList), { ssr: false });

interface LollipopChartProps {
    data: any[];
    dataKey: string;
    nameKey?: string;
    color?: string;
    horizontal?: boolean;
}

const COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e'];

export function LollipopChart({
    data,
    dataKey,
    nameKey = 'name',
    color,
    horizontal = true
}: LollipopChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data</div>;
    }

    // For lollipop effect, we use thin bars with circle dots at the end
    const CustomBar = (props: any) => {
        const { x, y, width, height, fill, index } = props;
        const dotRadius = 8;

        return (
            <g>
                {/* Stem */}
                <motion.rect
                    x={x}
                    y={y + height / 2 - 2}
                    width={width}
                    height={4}
                    fill={fill}
                    rx={2}
                    initial={{ width: 0 }}
                    animate={{ width: width }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
                />
                {/* Dot/Circle at end */}
                <motion.circle
                    cx={x + width}
                    cy={y + height / 2}
                    r={dotRadius}
                    fill={fill}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: index * 0.1 + 0.3, duration: 0.3 }}
                />
            </g>
        );
    };

    return (
        <motion.div
            className="w-full h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ top: 10, right: 40, left: 80, bottom: 10 }}
                >
                    <XAxis
                        type="number"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        axisLine={{ stroke: 'hsl(var(--border))' }}
                        tickLine={{ stroke: 'hsl(var(--border))' }}
                    />
                    <YAxis
                        type="category"
                        dataKey={nameKey}
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        axisLine={{ stroke: 'hsl(var(--border))' }}
                        tickLine={false}
                        width={70}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                        }}
                        formatter={(value: any) => [value.toLocaleString(), dataKey]}
                    />
                    <Bar
                        dataKey={dataKey}
                        shape={<CustomBar />}
                        barSize={30}
                    >
                        {data.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={color || COLORS[index % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
