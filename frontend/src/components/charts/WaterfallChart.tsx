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
const ReferenceLine = dynamic(() => import('recharts').then(mod => mod.ReferenceLine), { ssr: false });

interface WaterfallItem {
    name: string;
    value: number;
    start: number;
    end: number;
    isPositive: boolean;
    isTotal: boolean;
}

interface WaterfallChartProps {
    data: Record<string, any>[];
    dataKey?: string;
    nameKey?: string;
}

export function WaterfallChart({ data, dataKey = 'conversions', nameKey = 'name' }: WaterfallChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data available</div>;
    }

    // Transform data for waterfall effect using reduce to avoid reassignment
    const initialWaterfallData: WaterfallItem[] = [];
    const waterfallData = data.reduce((acc, item) => {
        const value = Number(item[dataKey]) || 0;
        const start = acc.length > 0 ? acc[acc.length - 1].end : 0;
        const end = start + value;

        acc.push({
            name: String(item[nameKey]),
            value: value,
            start: start,
            end: end,
            isPositive: value >= 0,
            isTotal: false
        });
        return acc;
    }, initialWaterfallData);

    // Add total bar
    const totalValue = waterfallData.length > 0 ? waterfallData[waterfallData.length - 1].end : 0;
    waterfallData.push({
        name: 'Total',
        value: totalValue,
        start: 0,
        end: totalValue,
        isPositive: true,
        isTotal: true
    });

    const CustomBar = (props: {
        x?: number;
        y?: number;
        width?: number;
        height?: number;
        payload: WaterfallItem;
        index: number;
    }) => {
        const { x, y, width, height, payload, index } = props;
        const fill = payload.isTotal
            ? '#3b82f6'
            : payload.isPositive
                ? '#10b981'
                : '#ef4444';

        return (
            <motion.rect
                x={x || 0}
                y={y || 0}
                width={width || 0}
                height={Math.abs(height || 0)}
                fill={fill}
                rx={4}
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ delay: (index || 0) * 0.1, duration: 0.3 }}
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
                <BarChart data={waterfallData as any[]} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis
                        dataKey="name"
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }}
                        tickFormatter={(v: number) => v.toLocaleString()}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'hsl(var(--card))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                        }}
                        formatter={((value: any, _name: string, props: { payload: WaterfallItem }) => {
                            if (props.payload.isTotal) {
                                return [Number(value).toLocaleString(), 'Total'];
                            }
                            return [Number(value).toLocaleString(), 'Contribution'];
                        }) as any}
                    />
                    <ReferenceLine y={0} stroke="hsl(var(--border))" />
                    <Bar
                        dataKey="value"
                        shape={CustomBar as any}
                    />
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
