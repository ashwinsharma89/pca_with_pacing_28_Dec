"use client";

import { useMemo } from 'react';
import { motion } from 'framer-motion';

interface HeatmapCalendarProps {
    data: any[];
    valueKey?: string;
    onDayClick?: (date: string, value: number) => void;
}

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

const getColorIntensity = (value: number, max: number): string => {
    if (value === 0) return 'bg-muted/30';
    const ratio = value / max;
    if (ratio < 0.2) return 'bg-emerald-200 dark:bg-emerald-900';
    if (ratio < 0.4) return 'bg-emerald-300 dark:bg-emerald-700';
    if (ratio < 0.6) return 'bg-emerald-400 dark:bg-emerald-600';
    if (ratio < 0.8) return 'bg-emerald-500 dark:bg-emerald-500';
    return 'bg-emerald-600 dark:bg-emerald-400';
};

export function HeatmapCalendar({ data, valueKey = 'spend', onDayClick }: HeatmapCalendarProps) {
    const calendarData = useMemo(() => {
        if (!data || data.length === 0) return { weeks: [], maxValue: 0, monthLabels: [] };

        // Create a map of date -> value
        const dateMap = new Map<string, number>();
        data.forEach(item => {
            const date = item.date?.split('T')[0] || item.date;
            dateMap.set(date, item[valueKey] || 0);
        });

        // Find date range
        const dates = Array.from(dateMap.keys()).sort();
        if (dates.length === 0) return { weeks: [], maxValue: 0, monthLabels: [] };

        const startDate = new Date(dates[0]);
        const endDate = new Date(dates[dates.length - 1]);

        // Adjust to start from Sunday
        const adjustedStart = new Date(startDate);
        adjustedStart.setDate(startDate.getDate() - startDate.getDay());

        const weeks: { date: string; value: number; dayOfWeek: number }[][] = [];
        let currentWeek: { date: string; value: number; dayOfWeek: number }[] = [];
        const monthLabels: { month: string; weekIndex: number }[] = [];
        let lastMonth = -1;

        const current = new Date(adjustedStart);
        let weekIndex = 0;

        while (current <= endDate || currentWeek.length > 0) {
            const dateStr = current.toISOString().split('T')[0];
            const dayOfWeek = current.getDay();
            const value = dateMap.get(dateStr) || 0;

            // Track month labels
            if (current.getMonth() !== lastMonth && dayOfWeek === 0) {
                monthLabels.push({ month: MONTHS[current.getMonth()], weekIndex });
                lastMonth = current.getMonth();
            }

            currentWeek.push({ date: dateStr, value, dayOfWeek });

            if (dayOfWeek === 6) {
                weeks.push(currentWeek);
                currentWeek = [];
                weekIndex++;
            }

            current.setDate(current.getDate() + 1);

            if (current > endDate && currentWeek.length === 0) break;
        }

        if (currentWeek.length > 0) {
            weeks.push(currentWeek);
        }

        const maxValue = Math.max(...Array.from(dateMap.values()), 1);

        return { weeks, maxValue, monthLabels };
    }, [data, valueKey]);

    if (calendarData.weeks.length === 0) {
        return <div className="flex items-center justify-center h-full text-muted-foreground">No data available</div>;
    }

    return (
        <div className="w-full h-full flex flex-col">
            {/* Month labels */}
            <div className="flex mb-1 pl-8">
                {calendarData.monthLabels.map((label, idx) => (
                    <div
                        key={idx}
                        className="text-xs text-muted-foreground"
                        style={{ marginLeft: idx === 0 ? 0 : `${(label.weekIndex - (calendarData.monthLabels[idx - 1]?.weekIndex || 0)) * 14}px` }}
                    >
                        {label.month}
                    </div>
                ))}
            </div>

            <div className="flex">
                {/* Day labels */}
                <div className="flex flex-col mr-2">
                    {DAYS.map((day, idx) => (
                        <div key={day} className="text-xs text-muted-foreground h-3.5 flex items-center">
                            {idx % 2 === 1 ? day : ''}
                        </div>
                    ))}
                </div>

                {/* Calendar grid */}
                <div className="flex gap-0.5 overflow-x-auto">
                    {calendarData.weeks.map((week, weekIdx) => (
                        <div key={weekIdx} className="flex flex-col gap-0.5">
                            {week.map((day, dayIdx) => (
                                <motion.div
                                    key={day.date}
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    transition={{ delay: (weekIdx * 7 + dayIdx) * 0.002 }}
                                    className={`w-3 h-3 rounded-sm cursor-pointer transition-transform hover:scale-125 ${getColorIntensity(day.value, calendarData.maxValue)}`}
                                    title={`${day.date}: $${day.value.toLocaleString()}`}
                                    onClick={() => onDayClick?.(day.date, day.value)}
                                />
                            ))}
                        </div>
                    ))}
                </div>
            </div>

            {/* Legend */}
            <div className="flex items-center justify-end mt-2 gap-1 text-xs text-muted-foreground">
                <span>Less</span>
                <div className="w-3 h-3 rounded-sm bg-muted/30" />
                <div className="w-3 h-3 rounded-sm bg-emerald-200 dark:bg-emerald-900" />
                <div className="w-3 h-3 rounded-sm bg-emerald-300 dark:bg-emerald-700" />
                <div className="w-3 h-3 rounded-sm bg-emerald-400 dark:bg-emerald-600" />
                <div className="w-3 h-3 rounded-sm bg-emerald-500 dark:bg-emerald-500" />
                <div className="w-3 h-3 rounded-sm bg-emerald-600 dark:bg-emerald-400" />
                <span>More</span>
            </div>
        </div>
    );
}
