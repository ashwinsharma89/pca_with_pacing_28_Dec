"use client";

import { motion } from 'framer-motion';

interface SlopeChartProps {
    data: {
        name: string;
        before: number;
        after: number;
    }[];
    beforeLabel?: string;
    afterLabel?: string;
    valuePrefix?: string;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export function SlopeChart({
    data,
    beforeLabel = 'Last Period',
    afterLabel = 'This Period',
    valuePrefix = ''
}: SlopeChartProps) {
    if (!data || data.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data</div>;
    }

    const maxValue = Math.max(...data.flatMap(d => [d.before, d.after]));
    const chartHeight = 200;
    const padding = 40;

    const getY = (value: number) => {
        return chartHeight - padding - ((value / maxValue) * (chartHeight - padding * 2));
    };

    return (
        <motion.div
            className="w-full h-full flex flex-col"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
        >
            <div className="flex justify-between px-8 mb-2">
                <span className="text-sm font-medium text-muted-foreground">{beforeLabel}</span>
                <span className="text-sm font-medium text-muted-foreground">{afterLabel}</span>
            </div>

            <svg width="100%" height={chartHeight} className="overflow-visible">
                {/* Background grid lines */}
                <line
                    x1="15%" y1={padding}
                    x2="15%" y2={chartHeight - padding}
                    stroke="hsl(var(--border))"
                    strokeDasharray="4 4"
                />
                <line
                    x1="85%" y1={padding}
                    x2="85%" y2={chartHeight - padding}
                    stroke="hsl(var(--border))"
                    strokeDasharray="4 4"
                />

                {data.map((item, idx) => {
                    const y1 = getY(item.before);
                    const y2 = getY(item.after);
                    const color = COLORS[idx % COLORS.length];
                    const isIncrease = item.after > item.before;
                    const changePercent = ((item.after - item.before) / item.before * 100).toFixed(1);

                    return (
                        <g key={item.name}>
                            {/* Connecting line */}
                            <motion.line
                                x1="15%"
                                y1={y1}
                                x2="85%"
                                y2={y2}
                                stroke={color}
                                strokeWidth={3}
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ delay: idx * 0.15, duration: 0.6 }}
                            />

                            {/* Before dot */}
                            <motion.circle
                                cx="15%"
                                cy={y1}
                                r={6}
                                fill={color}
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: idx * 0.15 }}
                            />

                            {/* After dot */}
                            <motion.circle
                                cx="85%"
                                cy={y2}
                                r={6}
                                fill={color}
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: idx * 0.15 + 0.4 }}
                            />

                            {/* Before label */}
                            <motion.text
                                x="12%"
                                y={y1}
                                textAnchor="end"
                                dominantBaseline="middle"
                                className="text-xs"
                                style={{ fill: 'hsl(var(--foreground))' }}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: idx * 0.15 + 0.2 }}
                            >
                                {valuePrefix}{item.before.toLocaleString()}
                            </motion.text>

                            {/* After label with change indicator */}
                            <motion.text
                                x="88%"
                                y={y2}
                                textAnchor="start"
                                dominantBaseline="middle"
                                className="text-xs"
                                style={{ fill: 'hsl(var(--foreground))' }}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: idx * 0.15 + 0.5 }}
                            >
                                {valuePrefix}{item.after.toLocaleString()}
                                <tspan
                                    className={isIncrease ? 'fill-green-500' : 'fill-red-500'}
                                    dx="4"
                                    fontSize="10"
                                >
                                    {isIncrease ? '↑' : '↓'}{changePercent}%
                                </tspan>
                            </motion.text>

                            {/* Name label (middle) */}
                            <motion.text
                                x="50%"
                                y={((y1 + y2) / 2) - 8}
                                textAnchor="middle"
                                className="text-xs"
                                style={{ fill: 'hsl(var(--muted-foreground))' }}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: idx * 0.15 + 0.3 }}
                            >
                                {item.name}
                            </motion.text>
                        </g>
                    );
                })}
            </svg>
        </motion.div>
    );
}
