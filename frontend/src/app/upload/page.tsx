"use client";

import { useState, useEffect } from "react";
import { Upload, FileUp, Database, Loader2, CheckCircle2, FileSpreadsheet } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface UploadMetrics {
    total_spend: number;
    total_clicks: number;
    total_impressions: number;
    total_conversions: number;
    avg_ctr: number;
}

interface SchemaInfo {
    column: string;
    dtype: string;
    null_count: number;
}

interface UploadResult {
    success: boolean;
    imported_count: number;
    message: string;
    summary?: UploadMetrics;
    schema?: SchemaInfo[];
    preview?: any[];
}

interface SheetInfo {
    name: string;
    row_count: number;
    column_count: number;
    error?: string;
}

interface SheetPreview {
    filename: string;
    sheets: SheetInfo[];
    default_sheet: string;
}

// Helper function to format large numbers
const formatNumber = (num: number): string => {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(2) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
};

// Helper function to format cell values (handles dates, numbers, etc.)
const formatCellValue = (value: any): string => {
    if (value === null || value === undefined) return '';

    // Check if it's a date string (ISO format with time component)
    if (typeof value === 'string') {
        const dateMatch = value.match(/^\d{4}-\d{2}-\d{2}(T|\s|$)/);
        if (dateMatch) {
            const date = new Date(value);
            if (!isNaN(date.getTime())) {
                // Check if it's a month-level date (first day of month)
                if (date.getDate() === 1) {
                    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
                }
                return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
            }
        }
    }

    return String(value);
};

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);
    const [result, setResult] = useState<UploadResult | null>(null);

    // Load persisted upload result from localStorage on mount
    useEffect(() => {
        const savedResult = localStorage.getItem('lastUploadResult');
        const savedStatus = localStorage.getItem('lastUploadStatus');
        if (savedResult) {
            try {
                setResult(JSON.parse(savedResult));
            } catch (e) {
                console.error('Failed to parse saved upload result', e);
            }
        }
        if (savedStatus) {
            try {
                setStatus(JSON.parse(savedStatus));
            } catch (e) {
                console.error('Failed to parse saved upload status', e);
            }
        }
    }, []);

    // Persist upload result to localStorage when it changes
    useEffect(() => {
        if (result) {
            localStorage.setItem('lastUploadResult', JSON.stringify(result));
        }
        if (status) {
            localStorage.setItem('lastUploadStatus', JSON.stringify(status));
        }
    }, [result, status]);

    // Excel sheet selection state
    const [showSheetDialog, setShowSheetDialog] = useState(false);
    const [sheetPreview, setSheetPreview] = useState<SheetPreview | null>(null);
    const [selectedSheet, setSelectedSheet] = useState<string>('');
    const [loadingSheets, setLoadingSheets] = useState(false);

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            setStatus(null);
            setResult(null);

            // If it's an Excel file, preview sheets
            if (selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls')) {
                await previewExcelSheets(selectedFile);
            }
        }
    };

    const previewExcelSheets = async (file: File) => {
        setLoadingSheets(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const token = localStorage.getItem('token');
            const headers: HeadersInit = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            headers['X-CSRF-Token'] = 'v2-token-generation-pca';

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/campaigns/upload/preview-sheets`, {
                method: 'POST',
                headers,
                body: formData,
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Sheet preview failed:', response.status, errorText);
                throw new Error(`Failed to preview sheets: ${response.status}`);
            }

            const preview: SheetPreview = await response.json();
            console.log('Sheet preview result:', preview);
            setSheetPreview(preview);
            setSelectedSheet(preview.default_sheet);
            setShowSheetDialog(true);
        } catch (error: any) {
            console.error('Sheet preview error:', error);
            setStatus({
                type: 'error',
                message: `Failed to preview Excel sheets: ${error.message}. Try uploading directly.`
            });
            // Clear loading state but keep file so user can try direct upload
        } finally {
            setLoadingSheets(false);
        }
    };

    const handleUpload = async (sheetName?: string) => {
        if (!file) return;

        setUploading(true);
        setStatus(null);
        setResult(null);
        setShowSheetDialog(false);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Add sheet_name if provided (for Excel files)
            if (sheetName) {
                formData.append('sheet_name', sheetName);
            }

            const token = localStorage.getItem('token');
            const headers: HeadersInit = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            headers['X-CSRF-Token'] = 'v2-token-generation-pca';

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/campaigns/upload`, {
                method: 'POST',
                headers,
                body: formData,
            });

            if (!response.ok) {
                // Handle 401 Unauthorized
                if (response.status === 401 && typeof window !== 'undefined') {
                    window.dispatchEvent(new CustomEvent('unauthorized'));
                }
                const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
                throw new Error(error.detail || 'Upload failed');
            }

            const uploadResult = await response.json();

            if (uploadResult.success) {
                setStatus({
                    type: 'success',
                    message: `Successfully imported ${uploadResult.imported_count} campaigns${sheetName ? ` from sheet "${sheetName}"` : ''}.`
                });
                setResult(uploadResult);
            } else {
                throw new Error(uploadResult.message || "Upload failed");
            }

        } catch (error: any) {
            setStatus({
                type: 'error',
                message: error.message || "Failed to upload file."
            });
        } finally {
            setUploading(false);
        }
    };

    const handleUploadClick = () => {
        // If it's an Excel file and we have sheet preview, show dialog
        if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) && sheetPreview) {
            setShowSheetDialog(true);
        } else {
            // For CSV or if no sheet preview, upload directly
            handleUpload();
        }
    };

    return (
        <div className="container mx-auto py-10 space-y-8">
            <h1 className="text-3xl font-bold tracking-tight">📊 Data Upload</h1>

            {/* Excel Sheet Selection Dialog */}
            <Dialog open={showSheetDialog} onOpenChange={setShowSheetDialog}>
                <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <FileSpreadsheet className="h-5 w-5" />
                            Select Excel Sheet
                        </DialogTitle>
                        <DialogDescription>
                            This Excel file contains multiple sheets. Please select which sheet to upload.
                        </DialogDescription>
                    </DialogHeader>

                    {sheetPreview && (
                        <div className="space-y-4 py-4">
                            <div className="space-y-2">
                                <Label htmlFor="sheet-select">Sheet</Label>
                                <Select value={selectedSheet} onValueChange={setSelectedSheet}>
                                    <SelectTrigger id="sheet-select">
                                        <SelectValue placeholder="Select a sheet" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {sheetPreview.sheets.map((sheet) => (
                                            <SelectItem key={sheet.name} value={sheet.name}>
                                                {sheet.name} - {sheet.error ? '⚠️ Error' : `${sheet.row_count} rows, ${sheet.column_count} cols`}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Sheet Details */}
                            {selectedSheet && (
                                <div className="rounded-md bg-muted p-3 text-sm">
                                    {sheetPreview.sheets.find(s => s.name === selectedSheet)?.error ? (
                                        <p className="text-destructive">
                                            ⚠️ {sheetPreview.sheets.find(s => s.name === selectedSheet)?.error}
                                        </p>
                                    ) : (
                                        <div className="space-y-1">
                                            <p><strong>Sheet:</strong> {selectedSheet}</p>
                                            <p><strong>Rows:</strong> {sheetPreview.sheets.find(s => s.name === selectedSheet)?.row_count.toLocaleString()}</p>
                                            <p><strong>Columns:</strong> {sheetPreview.sheets.find(s => s.name === selectedSheet)?.column_count}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    <DialogFooter className="relative z-[100]">
                        <Button type="button" variant="outline" onClick={() => setShowSheetDialog(false)}>
                            Cancel
                        </Button>
                        <Button
                            type="button"
                            onClick={() => handleUpload(selectedSheet)}
                            disabled={!selectedSheet || uploading}
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <Upload className="mr-2 h-4 w-4" />
                                    Upload Sheet
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            {/* Success Summary View */}
            {result && result.summary ? (
                <div className="space-y-6">
                    <div className="flex items-center justify-between">
                        <Alert className="border-green-500 text-green-700 bg-green-50 dark:bg-green-900/10 flex-1 mr-4">
                            <CheckCircle2 className="h-4 w-4" />
                            <AlertTitle>Upload Complete</AlertTitle>
                            <AlertDescription>
                                {result.message}
                            </AlertDescription>
                        </Alert>
                        <Button
                            type="button"
                            onClick={() => {
                                setFile(null);
                                setSheetPreview(null);
                                setResult(null);
                                setStatus(null);
                                localStorage.removeItem('lastUploadResult');
                                localStorage.removeItem('lastUploadStatus');
                            }}
                        >
                            <Upload className="mr-2 h-4 w-4" />
                            New Upload
                        </Button>
                    </div>

                    {/* Metrics Cards */}
                    <div className="grid gap-4 md:grid-cols-4">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Total Spend</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">${formatNumber(result.summary.total_spend)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Total Clicks</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{formatNumber(result.summary.total_clicks)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Conversions</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{formatNumber(result.summary.total_conversions)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Avg CTR</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{result.summary.avg_ctr.toFixed(2)}%</div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Data Preview - Full Width */}
                    <Card className="overflow-hidden">
                        <CardHeader>
                            <CardTitle>Data Preview</CardTitle>
                            <CardDescription>First 5 rows of imported data.</CardDescription>
                        </CardHeader>
                        <CardContent className="h-[300px] overflow-y-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        {result.schema?.map(col => (
                                            <TableHead key={col.column} className="text-xs max-w-[120px] truncate" title={col.column}>{col.column}</TableHead>
                                        ))}
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {result.preview?.map((row, i) => (
                                        <TableRow key={i}>
                                            {result.schema?.map(col => (
                                                <TableCell key={col.column} className="text-xs max-w-[120px] truncate" title={row[col.column] !== null ? String(row[col.column]) : 'null'}>
                                                    {row[col.column] !== null ? formatCellValue(row[col.column]) : <span className="text-muted-foreground italic">null</span>}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>

                    {/* Schema Info - Below Data Preview */}
                    <Card className="overflow-hidden">
                        <CardHeader>
                            <CardTitle>Data Schema</CardTitle>
                            <CardDescription>Detected columns and data types.</CardDescription>
                        </CardHeader>
                        <CardContent className="max-h-[250px] overflow-y-auto">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Column</TableHead>
                                        <TableHead>Type</TableHead>
                                        <TableHead>Nulls</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {result.schema?.map((col) => (
                                        <TableRow key={col.column}>
                                            <TableCell className="font-medium">{col.column}</TableCell>
                                            <TableCell>{col.dtype}</TableCell>
                                            <TableCell className={col.null_count > 0 ? "text-yellow-600 font-bold" : "text-muted-foreground"}>
                                                {col.null_count}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2">
                    {/* File Upload Section */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileUp className="h-5 w-5" />
                                File Upload
                            </CardTitle>
                            <CardDescription>
                                Upload your campaign data as CSV or Excel files.
                                Required columns: Campaign_Name, Platform, Spend, Impressions, Clicks.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid w-full max-w-sm items-center gap-1.5">
                                <Label htmlFor="campaign-file">Campaign Data File</Label>
                                <Input
                                    id="campaign-file"
                                    type="file"
                                    accept=".csv,.xlsx,.xls"
                                    onChange={handleFileChange}
                                    disabled={loadingSheets}
                                />
                                {loadingSheets && (
                                    <p className="text-sm text-muted-foreground flex items-center gap-2">
                                        <Loader2 className="h-3 w-3 animate-spin" />
                                        Loading sheet information...
                                    </p>
                                )}
                            </div>

                            {file && sheetPreview && (
                                <div className="rounded-md bg-muted p-3 text-sm">
                                    <p className="font-medium mb-1">📄 {sheetPreview.filename}</p>
                                    <p className="text-muted-foreground">
                                        {sheetPreview.sheets.length} sheet{sheetPreview.sheets.length !== 1 ? 's' : ''} detected
                                    </p>
                                </div>
                            )}

                            {status && (
                                <Alert variant={status.type === 'error' ? "destructive" : "default"} className={status.type === 'success' ? "border-green-500 text-green-700 bg-green-50 dark:bg-green-900/10" : ""}>
                                    <AlertTitle>{status.type === 'success' ? "Success" : "Error"}</AlertTitle>
                                    <AlertDescription>
                                        {status.message}
                                    </AlertDescription>
                                </Alert>
                            )}

                            <Button
                                type="button"
                                onClick={handleUploadClick}
                                disabled={!file || uploading || loadingSheets}
                                className="w-full"
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Uploading...
                                    </>
                                ) : (
                                    <>
                                        <Upload className="mr-2 h-4 w-4" />
                                        {file && sheetPreview ? 'Select Sheet & Upload' : 'Upload Data'}
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>

                    {/* Database Connection Placeholder */}
                    <Card className="opacity-75">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Database className="h-5 w-5" />
                                Database Connections
                            </CardTitle>
                            <CardDescription>
                                Connect directly to your ad platforms or data warehouse.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="rounded-md bg-muted p-4 text-sm text-muted-foreground flex flex-col items-center justify-center h-[180px] border border-dashed text-center">
                                <p className="mb-2 font-medium">Coming Soon</p>
                                <p>Direct integration with Google Ads, Meta, Snowflake, and BigQuery.</p>
                            </div>
                            <Button disabled variant="outline" className="w-full">
                                Configure Connection
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            )
            }
        </div >
    );
}
