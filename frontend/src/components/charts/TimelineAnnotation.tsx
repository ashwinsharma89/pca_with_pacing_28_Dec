"use client";

import { motion } from 'framer-motion';
import { Flag, Star, AlertTriangle, Zap, Calendar } from 'lucide-react';

interface Annotation {
    date: string;
    label: string;
    type: 'milestone' | 'alert' | 'campaign' | 'event';
}

interface TimelineAnnotationProps {
    annotations: Annotation[];
}

const typeConfig = {
    milestone: { icon: Flag, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    alert: { icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    campaign: { icon: Zap, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    event: { icon: Calendar, color: 'text-purple-500', bg: 'bg-purple-500/10' }
};

export function TimelineAnnotation({ annotations }: TimelineAnnotationProps) {
    if (!annotations || annotations.length === 0) {
        return <div className="text-xs text-muted-foreground">No annotations</div>;
    }

    return (
        <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-px bg-border" />

            <div className="space-y-3">
                {annotations.map((annotation, idx) => {
                    const config = typeConfig[annotation.type];
                    const Icon = config.icon;

                    return (
                        <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="flex items-start gap-3 relative"
                        >
                            {/* Icon dot */}
                            <div className={`relative z-10 p-1.5 rounded-full ${config.bg}`}>
                                <Icon className={`h-4 w-4 ${config.color}`} />
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0 pb-2">
                                <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">{annotation.label}</span>
                                    <span className="text-xs text-muted-foreground">
                                        {new Date(annotation.date).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
