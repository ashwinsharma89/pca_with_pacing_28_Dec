"use client";

import { motion } from 'framer-motion';
import { Lightbulb, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface Insight {
    type: 'success' | 'warning' | 'trend-up' | 'trend-down' | 'tip';
    title: string;
    description: string;
    metric?: string;
    change?: number;
}

interface AIInsightCardProps {
    insights?: Insight[];
    autoGenerate?: boolean;
    data?: any;
}

const iconMap = {
    'success': { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10' },
    'warning': { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    'trend-up': { icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    'trend-down': { icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-500/10' },
    'tip': { icon: Lightbulb, color: 'text-blue-500', bg: 'bg-blue-500/10' }
};

// Generate insights from data automatically
const generateInsights = (data: any): Insight[] => {
    const insights: Insight[] = [];

    if (data?.platformData) {
        // Find best performing platform
        const sorted = [...data.platformData].sort((a, b) => (b.roas || 0) - (a.roas || 0));
        if (sorted[0]) {
            insights.push({
                type: 'success',
                title: 'Top Performer',
                description: `${sorted[0].name} has the highest ROAS at ${sorted[0].roas?.toFixed(2)}x`,
                metric: 'ROAS',
                change: sorted[0].roas
            });
        }

        // Find underperforming platform
        if (sorted.length > 1) {
            const worst = sorted[sorted.length - 1];
            if (worst.roas < 1) {
                insights.push({
                    type: 'warning',
                    title: 'Needs Attention',
                    description: `${worst.name} ROAS is below 1.0 - consider optimization`,
                    metric: 'ROAS',
                    change: worst.roas
                });
            }
        }
    }

    if (data?.trend === 'up') {
        insights.push({
            type: 'trend-up',
            title: 'Positive Trend',
            description: 'Overall performance is trending upward this period',
            change: data.changePercent
        });
    }

    if (data?.ctr && data.ctr < 1) {
        insights.push({
            type: 'tip',
            title: 'Optimization Tip',
            description: 'CTR is below 1%. Consider A/B testing ad creatives.',
            metric: 'CTR'
        });
    }

    // Default insight if none generated
    if (insights.length === 0) {
        insights.push({
            type: 'tip',
            title: 'Quick Analysis',
            description: 'Your campaigns are performing within expected ranges.',
        });
    }

    return insights.slice(0, 4);
};

export function AIInsightCard({ insights, autoGenerate = true, data }: AIInsightCardProps) {
    const displayInsights = insights || (autoGenerate && data ? generateInsights(data) : [
        { type: 'tip' as const, title: 'Getting Started', description: 'Add data to generate AI-powered insights' }
    ]);

    return (
        <div className="space-y-3">
            {displayInsights.map((insight, idx) => {
                const { icon: Icon, color, bg } = iconMap[insight.type];

                return (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.15 }}
                    >
                        <Card className="overflow-hidden">
                            <CardContent className="p-3 flex items-start gap-3">
                                <div className={`p-2 rounded-lg ${bg}`}>
                                    <Icon className={`h-4 w-4 ${color}`} />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between">
                                        <span className="font-medium text-sm">{insight.title}</span>
                                        {insight.metric && (
                                            <span className={`text-xs font-mono ${color}`}>
                                                {insight.change !== undefined && (
                                                    insight.change > 0 ? '+' : ''
                                                )}
                                                {insight.change?.toFixed(1)}
                                                {insight.metric === 'ROAS' ? 'x' : '%'}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                                        {insight.description}
                                    </p>
                                </div>

                                {/* Animated accent bar */}
                                <motion.div
                                    className={`absolute left-0 top-0 bottom-0 w-1 ${bg.replace('/10', '')}`}
                                    initial={{ scaleY: 0 }}
                                    animate={{ scaleY: 1 }}
                                    transition={{ delay: idx * 0.15 + 0.2 }}
                                />
                            </CardContent>
                        </Card>
                    </motion.div>
                );
            })}
        </div>
    );
}
