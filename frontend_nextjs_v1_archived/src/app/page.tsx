'use client';

import React from 'react';
import Layout from '@/components/Layout';
import { useAuth } from '@/hooks/useAuth';
import { ArrowUpRight, DollarSign, Users, Activity, MousePointer } from 'lucide-react';
import { motion } from 'framer-motion';

const MetricCard = ({ title, value, change, icon: Icon, delay }: { title: string, value: string, change: string, icon: any, delay: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.4 }}
    className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 p-6 rounded-2xl relative overflow-hidden group hover:border-blue-500/30 transition-all duration-300"
  >
    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
      <Icon size={60} />
    </div>

    <div className="flex items-center gap-3 mb-4">
      <div className="p-2.5 bg-blue-500/10 rounded-lg text-blue-400 group-hover:bg-blue-500/20 transition-colors">
        <Icon size={20} />
      </div>
      <span className="text-slate-400 font-medium text-sm">{title}</span>
    </div>

    <div className="flex items-end justify-between">
      <div>
        <h3 className="text-3xl font-bold text-white tracking-tight">{value}</h3>
      </div>
      <div className="flex items-center gap-1 text-emerald-400 text-sm font-semibold bg-emerald-500/10 px-2.5 py-1 rounded-full">
        <ArrowUpRight size={14} />
        {change}
      </div>
    </div>
  </motion.div>
);

export default function Home() {
  const { user } = useAuth(); // We'd check auth here

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-3xl font-bold text-white">Dashboard Overview</h2>
            <p className="text-slate-400 mt-2">Real-time campaign performance analysis</p>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-700 transition-colors border border-slate-700">Last 30 Days</button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500 transition-colors shadow-lg shadow-blue-500/25">Generate Report</button>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard title="Total Spend" value="$124,500" change="+12.5%" icon={DollarSign} delay={0.1} />
          <MetricCard title="Conversions" value="3,842" change="+8.2%" icon={Users} delay={0.2} />
          <MetricCard title="Avg. CPA" value="$32.40" change="-4.1%" icon={Activity} delay={0.3} />
          <MetricCard title="CTR" value="2.85%" change="+0.4%" icon={MousePointer} delay={0.4} />
        </div>

        {/* Chart Section Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <div className="lg:col-span-2 bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6 min-h-[400px]">
            <h3 className="text-lg font-semibold text-white mb-6">Performance Trend</h3>
            <div className="flex items-center justify-center h-[300px] border-2 border-dashed border-slate-700/50 rounded-xl">
              <p className="text-slate-500">Chart Component Here (Recharts)</p>
            </div>
          </div>

          <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Device Breakdown</h3>
            <div className="space-y-4">
              {['Mobile', 'Desktop', 'Tablet'].map((item, i) => (
                <div key={item} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">{item}</span>
                    <span className="text-slate-400 font-mono">{(60 - i * 15)}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-700/50 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${60 - i * 15}%`, opacity: 1 - i * 0.2 }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </Layout>
  );
}
