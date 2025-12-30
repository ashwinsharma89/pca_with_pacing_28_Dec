"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

// Simple layout without auth
function SimpleLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-[#0a0e1a] text-[#f1f5f9]">
            <header className="border-b border-[#334155] bg-[#0f172a]/80 backdrop-blur-xl sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <Link href="/ad-explorer" className="flex items-center gap-2 font-bold text-lg">
                        <span className="text-2xl">📊</span>
                        Ad Platform Data Explorer
                    </Link>
                    <div className="flex items-center gap-4 text-sm text-[#94a3b8]">
                        <span>Google Ads • Meta Ads</span>
                    </div>
                </div>
            </header>
            <main>{children}</main>
        </div>
    );
}

// Platform options
const PLATFORMS = [
    { id: "google_ads", name: "Google Ads", icon: "🔵" },
    { id: "meta_ads", name: "Meta Ads", icon: "🔷" },
];

// Lookback presets
const LOOKBACK_OPTIONS = [
    { days: 7, label: "Last 7 days" },
    { days: 14, label: "Last 14 days" },
    { days: 30, label: "Last 30 days" },
    { days: 90, label: "Last 90 days" },
];

// Column definitions by platform
const COLUMN_DEFS = {
    google_ads: [
        { key: "campaign_name", label: "Campaign", group: "Campaign" },
        { key: "campaign_status", label: "Campaign Status", group: "Campaign" },
        { key: "campaign_objective", label: "Objective", group: "Campaign" },
        { key: "campaign_budget", label: "Budget", group: "Campaign", format: "currency" },
        { key: "ad_group_name", label: "Ad Group", group: "Ad Group" },
        { key: "ad_group_status", label: "AG Status", group: "Ad Group" },
        { key: "ad_group_type", label: "AG Type", group: "Ad Group" },
        { key: "ad_name", label: "Ad", group: "Ad" },
        { key: "ad_status", label: "Ad Status", group: "Ad" },
        { key: "ad_type", label: "Ad Type", group: "Ad" },
        { key: "ad_spend", label: "Spend", group: "Metrics", format: "currency" },
        { key: "ad_impressions", label: "Impressions", group: "Metrics", format: "number" },
        { key: "ad_clicks", label: "Clicks", group: "Metrics", format: "number" },
        { key: "ad_conversions", label: "Conversions", group: "Metrics", format: "number" },
        { key: "ad_ctr", label: "CTR", group: "Metrics", format: "percent" },
        { key: "ad_cpc", label: "CPC", group: "Metrics", format: "currency" },
        { key: "ad_cpa", label: "CPA", group: "Metrics", format: "currency" },
    ],
    meta_ads: [
        { key: "campaign_name", label: "Campaign", group: "Campaign" },
        { key: "campaign_status", label: "Campaign Status", group: "Campaign" },
        { key: "campaign_objective", label: "Objective", group: "Campaign" },
        { key: "campaign_budget", label: "Budget", group: "Campaign", format: "currency" },
        { key: "ad_set_name", label: "Ad Set", group: "Ad Set" },
        { key: "ad_set_status", label: "AS Status", group: "Ad Set" },
        { key: "ad_set_optimization", label: "Optimization", group: "Ad Set" },
        { key: "ad_name", label: "Ad", group: "Ad" },
        { key: "ad_status", label: "Ad Status", group: "Ad" },
        { key: "ad_format", label: "Format", group: "Ad" },
        { key: "ad_spend", label: "Spend", group: "Metrics", format: "currency" },
        { key: "ad_impressions", label: "Impressions", group: "Metrics", format: "number" },
        { key: "ad_clicks", label: "Clicks", group: "Metrics", format: "number" },
        { key: "ad_conversions", label: "Conversions", group: "Metrics", format: "number" },
        { key: "ad_ctr", label: "CTR", group: "Metrics", format: "percent" },
        { key: "ad_cpc", label: "CPC", group: "Metrics", format: "currency" },
        { key: "ad_cpa", label: "CPA", group: "Metrics", format: "currency" },
    ],
};

// Format value based on type
function formatValue(value: any, format?: string): string {
    if (value === null || value === undefined) return "-";
    switch (format) {
        case "currency":
            return `$${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        case "number":
            return Number(value).toLocaleString();
        case "percent":
            return `${Number(value).toFixed(2)}%`;
        default:
            return String(value);
    }
}

export default function AdExplorerPage() {
    const [platform, setPlatform] = useState("google_ads");
    const [lookbackDays, setLookbackDays] = useState(30);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<any[]>([]);
    const [columns, setColumns] = useState<string[]>([]);
    const [visibleColumns, setVisibleColumns] = useState<Set<string>>(new Set());
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
    const [showColumnPicker, setShowColumnPicker] = useState(false);

    // Fetch data when platform or lookback changes
    useEffect(() => {
        fetchData();
    }, [platform, lookbackDays]);

    // Initialize visible columns when platform changes
    useEffect(() => {
        const cols = COLUMN_DEFS[platform as keyof typeof COLUMN_DEFS] || [];
        const defaultVisible = new Set(cols.slice(0, 10).map((c) => c.key));
        setVisibleColumns(defaultVisible);
    }, [platform]);

    async function fetchData() {
        setLoading(true);
        try {
            const res = await fetch(
                `http://localhost:8000/api/v1/connectors/${platform}/hierarchy?mock_mode=true&lookback_days=${lookbackDays}`
            );
            const json = await res.json();
            setData(json.data || []);
            setColumns(json.columns || []);
        } catch (err) {
            console.error("Failed to fetch:", err);
        }
        setLoading(false);
    }

    // Sort data
    const sortedData = [...data].sort((a, b) => {
        if (!sortKey) return 0;
        const aVal = a[sortKey];
        const bVal = b[sortKey];
        if (aVal === bVal) return 0;
        const cmp = aVal < bVal ? -1 : 1;
        return sortDir === "asc" ? cmp : -cmp;
    });

    // Toggle column visibility
    function toggleColumn(key: string) {
        const next = new Set(visibleColumns);
        if (next.has(key)) next.delete(key);
        else next.add(key);
        setVisibleColumns(next);
    }

    // Export to CSV
    function exportCSV() {
        const colDefs = COLUMN_DEFS[platform as keyof typeof COLUMN_DEFS] || [];
        const visibleCols = colDefs.filter((c) => visibleColumns.has(c.key));
        const headers = visibleCols.map((c) => c.label).join(",");
        const rows = sortedData.map((row) =>
            visibleCols.map((c) => formatValue(row[c.key], c.format)).join(",")
        );
        const csv = [headers, ...rows].join("\n");
        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${platform}_hierarchy_${new Date().toISOString().split("T")[0]}.csv`;
        a.click();
    }

    const colDefs = COLUMN_DEFS[platform as keyof typeof COLUMN_DEFS] || [];
    const visibleCols = colDefs.filter((c) => visibleColumns.has(c.key));

    return (
        <SimpleLayout>
            <div className="p-6 space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-foreground">Ad Platform Data Explorer</h1>
                        <p className="text-muted-foreground">View full hierarchy: Campaign → Ad Group/Set → Ad</p>
                    </div>
                    <button
                        onClick={exportCSV}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition"
                    >
                        Export CSV
                    </button>
                </div>

                {/* Filters */}
                <div className="flex flex-wrap gap-4 p-4 bg-card rounded-xl border border-border">
                    {/* Platform */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm text-muted-foreground">Platform</label>
                        <select
                            value={platform}
                            onChange={(e) => setPlatform(e.target.value)}
                            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground"
                        >
                            {PLATFORMS.map((p) => (
                                <option key={p.id} value={p.id}>
                                    {p.icon} {p.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Lookback */}
                    <div className="flex flex-col gap-1">
                        <label className="text-sm text-muted-foreground">Lookback Window</label>
                        <select
                            value={lookbackDays}
                            onChange={(e) => setLookbackDays(Number(e.target.value))}
                            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground"
                        >
                            {LOOKBACK_OPTIONS.map((o) => (
                                <option key={o.days} value={o.days}>
                                    {o.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Column Picker */}
                    <div className="flex flex-col gap-1 relative">
                        <label className="text-sm text-muted-foreground">Columns</label>
                        <button
                            onClick={() => setShowColumnPicker(!showColumnPicker)}
                            className="px-3 py-2 bg-input border border-border rounded-lg text-foreground text-left"
                        >
                            {visibleColumns.size} of {colDefs.length} columns
                        </button>
                        {showColumnPicker && (
                            <div className="absolute top-full mt-1 z-50 w-64 max-h-80 overflow-y-auto bg-card border border-border rounded-lg shadow-xl p-3">
                                {["Campaign", "Ad Group", "Ad Set", "Ad", "Metrics"].map((group) => {
                                    const groupCols = colDefs.filter((c) => c.group === group);
                                    if (groupCols.length === 0) return null;
                                    return (
                                        <div key={group} className="mb-3">
                                            <div className="text-xs font-semibold text-muted-foreground mb-1">{group}</div>
                                            {groupCols.map((col) => (
                                                <label key={col.key} className="flex items-center gap-2 py-1 cursor-pointer hover:bg-muted/50 rounded px-1">
                                                    <input
                                                        type="checkbox"
                                                        checked={visibleColumns.has(col.key)}
                                                        onChange={() => toggleColumn(col.key)}
                                                        className="rounded"
                                                    />
                                                    <span className="text-sm text-foreground">{col.label}</span>
                                                </label>
                                            ))}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Refresh */}
                    <div className="flex flex-col gap-1 justify-end">
                        <button
                            onClick={fetchData}
                            disabled={loading}
                            className="px-4 py-2 bg-accent text-accent-foreground rounded-lg hover:bg-accent/90 transition disabled:opacity-50"
                        >
                            {loading ? "Loading..." : "Refresh"}
                        </button>
                    </div>
                </div>

                {/* Data Table */}
                <div className="bg-card rounded-xl border border-border overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-muted/50">
                                <tr>
                                    {visibleCols.map((col) => (
                                        <th
                                            key={col.key}
                                            onClick={() => {
                                                if (sortKey === col.key) {
                                                    setSortDir(sortDir === "asc" ? "desc" : "asc");
                                                } else {
                                                    setSortKey(col.key);
                                                    setSortDir("desc");
                                                }
                                            }}
                                            className="px-4 py-3 text-left font-medium text-muted-foreground cursor-pointer hover:text-foreground whitespace-nowrap"
                                        >
                                            {col.label}
                                            {sortKey === col.key && (
                                                <span className="ml-1">{sortDir === "asc" ? "↑" : "↓"}</span>
                                            )}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border">
                                {loading ? (
                                    <tr>
                                        <td colSpan={visibleCols.length} className="px-4 py-8 text-center text-muted-foreground">
                                            Loading data...
                                        </td>
                                    </tr>
                                ) : sortedData.length === 0 ? (
                                    <tr>
                                        <td colSpan={visibleCols.length} className="px-4 py-8 text-center text-muted-foreground">
                                            No data available
                                        </td>
                                    </tr>
                                ) : (
                                    sortedData.map((row, i) => (
                                        <tr key={i} className="hover:bg-muted/30 transition">
                                            {visibleCols.map((col) => (
                                                <td key={col.key} className="px-4 py-3 text-foreground whitespace-nowrap">
                                                    {formatValue(row[col.key], col.format)}
                                                </td>
                                            ))}
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                    {/* Footer */}
                    <div className="px-4 py-3 bg-muted/30 border-t border-border flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                            {sortedData.length} rows • {visibleCols.length} columns
                        </span>
                        <span className="text-xs text-muted-foreground">
                            Mock Mode • Data from {platform.replace("_", " ")}
                        </span>
                    </div>
                </div>
            </div>
        </SimpleLayout>
    );
}
