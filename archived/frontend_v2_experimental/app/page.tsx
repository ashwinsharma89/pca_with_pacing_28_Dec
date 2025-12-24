"use client";

import Link from "next/link";
import {
  Brain, AlertTriangle, Zap, LayoutDashboard,
  Scale, BarChart3, Upload, ArrowRight
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const pages = [
  {
    name: "Intelligence Studio",
    href: "/intelligence-studio",
    icon: Brain,
    description: "Natural language queries with AI-powered insights and chart generation",
    color: "from-purple-500 to-indigo-600"
  },
  {
    name: "Anomaly Detective",
    href: "/anomaly-detective",
    icon: AlertTriangle,
    description: "Statistical anomaly detection with root cause analysis",
    color: "from-orange-500 to-red-600"
  },
  {
    name: "Real-Time Command",
    href: "/real-time-command",
    icon: Zap,
    description: "Live campaign monitoring with WebSocket streaming",
    color: "from-green-500 to-emerald-600"
  },
  {
    name: "Dashboard Builder 2",
    href: "/dashboard-builder-2",
    icon: LayoutDashboard,
    description: "AI-powered dashboard creation with templates and widgets",
    color: "from-blue-500 to-cyan-600"
  },
  {
    name: "Comparison 2",
    href: "/comparison-2",
    icon: Scale,
    description: "Multi-period analysis with statistical significance testing",
    color: "from-pink-500 to-purple-600"
  },
  {
    name: "Visualizations 2",
    href: "/visualizations-2",
    icon: BarChart3,
    description: "AI chart recommendations with smart visualizations",
    color: "from-indigo-500 to-blue-600"
  },
  {
    name: "Upload Data",
    href: "/upload",
    icon: Upload,
    description: "Upload CSV or Excel files for analysis",
    color: "from-teal-500 to-green-600"
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
      <div className="container mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            PCA Agent V2
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Advanced analytics platform with 7 powerful pages for campaign performance analysis
          </p>
        </div>

        {/* Page Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          {pages.map((page) => {
            const Icon = page.icon;
            return (
              <Link key={page.name} href={page.href}>
                <Card className="h-full hover:shadow-lg transition-all duration-200 hover:scale-105 cursor-pointer">
                  <CardHeader>
                    <div className={`p-3 bg-gradient-to-br ${page.color} rounded-lg w-fit mb-3`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <CardTitle>{page.name}</CardTitle>
                    <CardDescription>{page.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button variant="ghost" className="w-full justify-between">
                      Open Page
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>

        {/* Features */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-6 bg-white dark:bg-slate-900 rounded-lg border">
            <h3 className="font-bold text-lg mb-2">7 Powerful Pages</h3>
            <p className="text-sm text-muted-foreground">
              Comprehensive analytics suite for all your needs
            </p>
          </div>
          <div className="text-center p-6 bg-white dark:bg-slate-900 rounded-lg border">
            <h3 className="font-bold text-lg mb-2">Real-Time Data</h3>
            <p className="text-sm text-muted-foreground">
              WebSocket streaming for live campaign monitoring
            </p>
          </div>
          <div className="text-center p-6 bg-white dark:bg-slate-900 rounded-lg border">
            <h3 className="font-bold text-lg mb-2">AI-Powered</h3>
            <p className="text-sm text-muted-foreground">
              Smart insights and recommendations
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
