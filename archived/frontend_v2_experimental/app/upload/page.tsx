"use client";

import { useState } from "react";
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { api } from "@/lib/api";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [progress, setProgress] = useState(0);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setUploadStatus('idle');
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setUploadStatus('idle');
        setProgress(10); // Initial start

        try {
            // Indeterminate progress simulation since fetch doesn't support progress
            const interval = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 95) return 95;
                    return prev + (95 - prev) * 0.1;
                });
            }, 1000);

            await api.uploadData(file);

            clearInterval(interval);
            setProgress(100);
            setUploadStatus('success');
        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus('error');
            setProgress(0);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-6">
            <div className="container mx-auto max-w-4xl space-y-6">
                {/* Header */}
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
                        <Upload className="h-7 w-7 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold">Upload Data</h1>
                        <p className="text-muted-foreground">Upload CSV or Excel files for analysis</p>
                    </div>
                </div>

                {/* Upload Card */}
                <Card>
                    <CardHeader>
                        <CardTitle>File Upload</CardTitle>
                        <CardDescription>
                            Upload your campaign data in CSV or Excel format
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* Drop Zone */}
                        <div className="border-2 border-dashed rounded-lg p-12 text-center hover:border-primary transition-colors">
                            <FileSpreadsheet className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                            <input
                                type="file"
                                accept=".csv,.xlsx,.xls"
                                onChange={handleFileChange}
                                className="hidden"
                                id="file-upload"
                            />
                            <label htmlFor="file-upload" className="cursor-pointer">
                                <Button variant="outline" asChild>
                                    <span>Choose File</span>
                                </Button>
                            </label>
                            <p className="text-sm text-muted-foreground mt-2">
                                or drag and drop your file here
                            </p>
                        </div>

                        {/* Selected File */}
                        {file && (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 bg-accent rounded-lg">
                                    <div className="flex items-center gap-3">
                                        <FileSpreadsheet className="h-5 w-5" />
                                        <div>
                                            <p className="font-medium">{file.name}</p>
                                            <p className="text-sm text-muted-foreground">
                                                {(file.size / (1024 * 1024)).toFixed(2)} MB
                                            </p>
                                        </div>
                                    </div>
                                    <Button
                                        onClick={handleUpload}
                                        disabled={uploading}
                                    >
                                        {uploading ? 'Processing...' : 'Upload'}
                                    </Button>
                                </div>

                                {uploading && (
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-sm">
                                            <span>
                                                {progress < 30 && "Uploading file..."}
                                                {progress >= 30 && progress < 70 && "Parsing data metrics..."}
                                                {progress >= 70 && progress < 90 && "Cleaning and indexing..."}
                                                {progress >= 90 && "Finalizing database insertion..."}
                                            </span>
                                            <span>{Math.round(progress)}%</span>
                                        </div>
                                        <Progress value={progress} className="h-2" />
                                        <p className="text-xs text-muted-foreground text-center">
                                            {progress < 90
                                                ? "Processing large file—this can take 30-60s for files over 100MB."
                                                : "Almost there! Completing the final database transaction."}
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Status Messages */}
                        {uploadStatus === 'success' && (
                            <div className="flex items-center gap-2 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
                                <CheckCircle2 className="h-5 w-5 text-green-600" />
                                <p className="text-green-900 dark:text-green-100">
                                    File uploaded successfully!
                                </p>
                            </div>
                        )}

                        {uploadStatus === 'error' && (
                            <div className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg">
                                <AlertCircle className="h-5 w-5 text-red-600" />
                                <p className="text-red-900 dark:text-red-100">
                                    Upload failed. Please try again.
                                </p>
                            </div>
                        )}

                        {/* Instructions */}
                        <div className="space-y-2">
                            <h3 className="font-medium">File Requirements:</h3>
                            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                                <li>Supported formats: CSV, XLSX, XLS</li>
                                <li>Maximum file size: 200MB</li>
                                <li>Required columns: campaign_name, platform, spend, conversions</li>
                                <li>Optional columns: clicks, impressions, ctr, cpc, cpa</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
