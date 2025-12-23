"use client";

import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

const ResponsiveContainer = dynamic(() => import('recharts').then(mod => mod.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import('recharts').then(mod => mod.BarChart), { ssr: false });
const Bar = dynamic(() => import('recharts').then(mod => mod.Bar), { ssr: false });
const XAxis = dynamic(() => import('recharts').then(mod => mod.XAxis), { ssr: false });
const YAxis = dynamic(() => import('recharts').then(mod => mod.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import('recharts').then(mod => mod.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import('recharts').then(mod => mod.Tooltip), { ssr: false });
const Cell = dynamic(() => import('recharts').then(mod => mod.Cell), { ssr: false });
const ReferenceLine = dynamic(() => import('recharts').then(mod => mod.ReferenceLine), { ssr: false });

interface WaterfallChartProps {
    data: any[];
    dataKey?: string;
    nameKey?: string;
}

export function WaterfallChart({ data, dataKey = 'conversions', nameKey = 'name' }: WaterfallChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data available</div>;
    }

    // Transform data for waterfall effect
    let cumulative = 0;
    const waterfallData = data.map((item, index) => {
        const value = item[dataKey] || 0;
        const start = cumulative;
        cumulative += value;

        return {
            name: item[nameKey],
            value: value,
            start: start,
            end: cumulative,
            isPositive: value >= 0,
            isTotal: false
        };
    });

    // Add total bar
    waterfallData.push({
        name: 'Total',
        value: cumulative,
        start: 0,
        end: cumulative,
        isPositive: true,
        isTotal: true
    });

    const CustomBar = (props: any) => {
        const { x, y, width, height, payload } = props;
        const fill = payload.isTotal
            ? '#3b82f6'
            : payload.isPositive
                ? '#10b981'
                : '#ef4444';

        return (
            <motion.rect
                x={x}
                y={payload.isTotal ? y : y}
                width={width}
                height={Math.abs(height)}
                fill={fill}
                rx={4}
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: props.index * 0.1, duration: 0.3 }}
                style={{ originY: 1 }}
            />
        );
    };

    return (
        <motion.div
            className="w-full h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={waterfallData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                        dataKey="name"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        tickFormatter={(value) => value.toLocaleString()}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                        }}
                        formatter={(value: any, name: any, props: any) => {
                            if (props.payload.isTotal) {
                                return [`${Number(value).toLocaleString()}`, 'Total'];
                            }
                            return [`+${Number(value).toLocaleString()}`, 'Contribution'];
                        }}
                    />
                    <ReferenceLine y={0} stroke="hsl(var(--border))" />
                    <Bar
                        dataKey="value"
                        shape={<CustomBar />}
                    >
                        {waterfallData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.isTotal ? '#3b82f6' : '#10b981'}
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
