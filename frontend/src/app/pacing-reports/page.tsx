"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Upload, FileSpreadsheet, Download, Trash2, Calendar, TrendingUp, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';

interface Template {
    filename: string;
    uploaded_at: string;
    size_bytes: number;
    valid: boolean;
}

interface Report {
    filename: string;
    generated_at: string;
    size_bytes: number;
}

interface GenerateReportParams {
    template_filename: string;
    start_date?: string;
    end_date?: string;
    aggregation: 'daily' | 'weekly' | 'monthly';
    filters?: Record<string, any>;
}

export default function PacingReportsPage() {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [reports, setReports] = useState<Report[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [selectedTemplateDetails, setSelectedTemplateDetails] = useState<any>(null);
    const [validating, setValidating] = useState(false);
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [aggregation, setAggregation] = useState<'daily' | 'weekly' | 'monthly'>('daily');
    const [uploading, setUploading] = useState(false);
    const [generating, setGenerating] = useState(false);
    const [loading, setLoading] = useState(false);

    const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
    const [activeJobId, setActiveJobId] = useState<string | null>(null);
    const [jobProgress, setJobProgress] = useState<number>(0);
    const [jobStatus, setJobStatus] = useState<string>('');


    // Disabled initial auto-load on page load per user request
    // useEffect(() => {
    //     loadData();
    // }, []);


    const loadData = async () => {
        try {
            setLoading(true);
            await Promise.all([loadTemplates(), loadReports()]);
        } catch (error) {
            console.error('Failed to load data:', error);
            showAlert('error', 'Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    const loadTemplates = async () => {
        try {
            const response = await api.request<{ success: boolean; data: { templates: Template[] } }>(
                '/pacing-reports/templates',
                { method: 'GET' }
            );
            if (response.success && response.data) {
                setTemplates(response.data.templates);
            }
        } catch (error) {
            console.error('Failed to load templates:', error);
        }
    };

    const loadReports = async () => {
        try {
            const response = await api.request<{ success: boolean; data: { reports: Report[] } }>(
                '/pacing-reports/reports',
                { method: 'GET' }
            );
            if (response.success && response.data) {
                setReports(response.data.reports);
            }
        } catch (error) {
            console.error('Failed to load reports:', error);
        }
    };

    const fetchTemplateDetails = async (filename: string) => {
        if (!filename) {
            setSelectedTemplateDetails(null);
            return;
        }

        try {
            setValidating(true);
            const response = await api.request<{ success: boolean; data: any }>(
                `/pacing-reports/templates/${filename}/validate`,
                { method: 'GET' }
            );

            if (response.success && response.data) {
                setSelectedTemplateDetails(response.data);
            }
        } catch (error) {
            console.error('Failed to fetch template details:', error);
            setSelectedTemplateDetails(null);
        } finally {
            setValidating(false);
        }
    };

    useEffect(() => {
        if (selectedTemplate) {
            fetchTemplateDetails(selectedTemplate);
        } else {
            setSelectedTemplateDetails(null);
        }
    }, [selectedTemplate]);

    const handleTemplateUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file extension
        if (!file.name.endsWith('.xlsx')) {
            showAlert('error', 'Please upload an Excel file (.xlsx)');
            event.target.value = '';
            return;
        }

        // Validate file size
        if (file.size === 0) {
            showAlert('error', 'File is empty (0 bytes). Please select a valid Excel template.');
            event.target.value = '';
            return;
        }

        if (file.size > 200 * 1024 * 1024) { // 200 MB limit
            showAlert('error', 'File is too large. Maximum size is 200 MB.');
            event.target.value = '';
            return;
        }

        try {
            setUploading(true);
            const formData = new FormData();
            formData.append('file', file);

            console.log('Uploading template:', file.name, 'Size:', file.size, 'bytes');

            // Use the backend URL from environment variable or default to localhost:8000
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
            const uploadUrl = `${API_URL}/pacing-reports/upload-template`;

            console.log('Upload URL:', uploadUrl);

            // Create AbortController for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout for large files

            try {
                const response = await fetch(uploadUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'X-CSRF-Token': 'v2-token-generation-pca',
                    },
                    body: formData,
                    signal: controller.signal,
                });

                clearTimeout(timeoutId);

                console.log('Upload response status:', response.status);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Upload failed:', response.status, errorText);
                    throw new Error(`Upload failed with status ${response.status}: ${errorText.substring(0, 100)}`);
                }

                const result = await response.json();
                console.log('Upload result:', result);

                if (result.success) {
                    // Build success message with validation details
                    let successMsg = result.data?.message || `Template "${file.name}" uploaded successfully`;

                    // Add detected sheets info
                    if (result.data?.detected_sheets) {
                        const detected = result.data.detected_sheets;
                        const detectedInfo = [];
                        if (detected.daily) detectedInfo.push(`Daily: "${detected.daily}"`);
                        if (detected.weekly) detectedInfo.push(`Weekly: "${detected.weekly}"`);
                        if (detectedInfo.length > 0) {
                            successMsg += ` | Detected: ${detectedInfo.join(', ')}`;
                        }
                    }

                    showAlert('success', successMsg);

                    // Log warnings and suggestions to console for user reference
                    if (result.data?.warnings && result.data.warnings.length > 0) {
                        console.warn('Template warnings:', result.data.warnings);
                    }
                    if (result.data?.suggestions && result.data.suggestions.length > 0) {
                        console.info('Template suggestions:', result.data.suggestions);
                    }

                    await loadTemplates();
                    // Auto-select the newly uploaded template
                    if (result.data?.filename) {
                        setSelectedTemplate(result.data.filename);
                    }
                } else {
                    const errorMsg = result.error || result.message || 'Upload failed';
                    console.error('Upload result error:', errorMsg);
                    showAlert('error', errorMsg);
                }
            } catch (fetchError) {
                clearTimeout(timeoutId);

                if (fetchError instanceof Error && fetchError.name === 'AbortError') {
                    throw new Error('Upload timed out after 30 seconds. Please try a smaller file or check your connection.');
                }
                throw fetchError;
            }
        } catch (error) {
            console.error('Upload exception:', error);
            const errorMessage = error instanceof Error ? error.message : 'Failed to upload template';
            showAlert('error', errorMessage);
        } finally {
            setUploading(false);
            // Reset file input
            event.target.value = '';
        }
    };

    const handleGenerateReport = async () => {
        if (!selectedTemplate) {
            showAlert('error', 'Please select a template');
            return;
        }

        try {
            setGenerating(true);
            setJobProgress(0);
            setJobStatus('Initiating request...');

            const params: GenerateReportParams = {
                template_filename: selectedTemplate,
                aggregation,
            };

            if (startDate) params.start_date = startDate;
            if (endDate) params.end_date = endDate;

            const response = await api.request<{ success: boolean; data: any }>(
                '/pacing-reports/generate',
                {
                    method: 'POST',
                    body: JSON.stringify(params),
                }
            );

            if (response.success && response.data?.job_id) {
                const jobId = response.data.job_id;
                setActiveJobId(jobId);
                startPolling(jobId);
            } else {
                setGenerating(false);
                showAlert('error', response.data?.error || 'Report generation failed to start');
            }
        } catch (error) {
            console.error('Report generation failed:', error);
            setGenerating(false);
            showAlert('error', 'Failed to generate report');
        }
    };

    const startPolling = (jobId: string) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await api.request<{ success: boolean; data: any }>(
                    `/pacing-reports/status/${jobId}`,
                    { method: 'GET' }
                );

                if (response.success && response.data) {
                    const { status, progress, message } = response.data;

                    setJobProgress(progress || 0);
                    setJobStatus(message || '');

                    if (status === 'completed') {
                        clearInterval(pollInterval);
                        setGenerating(false);
                        setActiveJobId(null);
                        showAlert('success', 'Report generated successfully!');
                        await loadReports();
                    } else if (status === 'failed') {
                        clearInterval(pollInterval);
                        setGenerating(false);
                        setActiveJobId(null);
                        showAlert('error', `Generation failed: ${message}`);
                    }
                }
            } catch (error) {
                console.error('Status polling failed:', error);
                // We keep polling in case it's a transient network issue
            }
        }, 2000);
    };

    const handleDownloadReport = async (filename: string) => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
            const token = localStorage.getItem('token');
            const url = `${API_URL}/pacing-reports/download/${filename}`;

            console.log('Downloading report:', filename, 'from:', url);

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            console.log('Download response status:', response.status);

            if (!response.ok) {
                throw new Error(`Download failed with status ${response.status}`);
            }

            const blob = await response.blob();
            console.log('Downloaded blob size:', blob.size, 'bytes');

            // Create download link
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            a.style.display = 'none';

            // Add to DOM, click, and remove
            document.body.appendChild(a);

            // Try to trigger download
            try {
                a.click();
                console.log('Download triggered successfully');
                showAlert('success', `Downloading ${filename}`);
            } catch (clickError) {
                console.error('Click failed, trying alternative method:', clickError);
                // Fallback: open in new tab
                window.open(downloadUrl, '_blank');
                showAlert('success', `Opening ${filename} in new tab`);
            }

            // Cleanup
            setTimeout(() => {
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
            }, 100);

        } catch (error) {
            console.error('Download failed:', error);
            const errorMsg = error instanceof Error ? error.message : 'Failed to download report';
            showAlert('error', errorMsg);
        }
    };

    const handleDeleteTemplate = async (filename: string) => {
        if (!confirm(`Delete template "${filename}"?`)) return;

        try {
            const response = await api.request<{ success: boolean }>(
                `/pacing-reports/templates/${filename}`,
                { method: 'DELETE' }
            );

            if (response.success) {
                showAlert('success', 'Template deleted');
                await loadTemplates();
                if (selectedTemplate === filename) {
                    setSelectedTemplate('');
                }
            }
        } catch (error) {
            console.error('Delete failed:', error);
            showAlert('error', 'Failed to delete template');
        }
    };

    const handleDeleteReport = async (filename: string) => {
        if (!confirm(`Delete report "${filename}"?`)) return;

        try {
            const response = await api.request<{ success: boolean }>(
                `/pacing-reports/reports/${filename}`,
                { method: 'DELETE' }
            );

            if (response.success) {
                showAlert('success', 'Report deleted');
                await loadReports();
            }
        } catch (error) {
            console.error('Delete failed:', error);
            showAlert('error', 'Failed to delete report');
        }
    };

    const showAlert = (type: 'success' | 'error', message: string) => {
        setAlert({ type, message });
        setTimeout(() => setAlert(null), 5000);
    };

    const formatFileSize = (bytes: number): string => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const formatDate = (dateString: string): string => {
        return new Date(dateString).toLocaleString();
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Pacing Reports</h1>
                    <p className="text-muted-foreground mt-1">
                        Generate Excel-based pacing reports with daily, weekly, or monthly aggregations
                    </p>
                </div>
                <TrendingUp className="h-12 w-12 text-primary opacity-20" />
            </div>

            {/* Alert */}
            {alert && (
                <Alert variant={alert.type === 'error' ? 'destructive' : 'default'}>
                    {alert.type === 'success' ? (
                        <CheckCircle2 className="h-4 w-4" />
                    ) : (
                        <AlertCircle className="h-4 w-4" />
                    )}
                    <AlertDescription>{alert.message}</AlertDescription>
                </Alert>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Template Upload & Selection */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Upload className="h-5 w-5" />
                            Template Management
                        </CardTitle>
                        <CardDescription>
                            Upload and manage Excel templates for pacing reports
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Upload Button */}
                        <div>
                            <Label htmlFor="template-upload" className="cursor-pointer">
                                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6 hover:border-primary/50 transition-colors text-center">
                                    {uploading ? (
                                        <Loader2 className="h-8 w-8 mx-auto animate-spin text-primary" />
                                    ) : (
                                        <>
                                            <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                                            <p className="text-sm font-medium">Click to upload template</p>
                                            <p className="text-xs text-muted-foreground mt-1">Excel files (.xlsx) only</p>
                                        </>
                                    )}
                                </div>
                            </Label>
                            <Input
                                id="template-upload"
                                type="file"
                                accept=".xlsx"
                                className="hidden"
                                onChange={handleTemplateUpload}
                                disabled={uploading}
                            />
                        </div>

                        {/* Template List */}
                        <div className="space-y-2">
                            <Label>Available Templates</Label>
                            {loading ? (
                                <div className="flex items-center justify-center p-4">
                                    <Loader2 className="h-6 w-6 animate-spin" />
                                </div>
                            ) : templates.length === 0 ? (
                                <div className="text-center py-4 space-y-3">
                                    <p className="text-sm text-muted-foreground">
                                        No templates loaded in this session
                                    </p>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => loadTemplates()}
                                    >
                                        <TrendingUp className="mr-2 h-4 w-4" />
                                        Load Existing Templates
                                    </Button>
                                </div>
                            ) : (
                                <div className="space-y-2 max-h-64 overflow-y-auto">
                                    {templates.map((template) => (
                                        <div
                                            key={template.filename}
                                            className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors ${selectedTemplate === template.filename
                                                ? 'border-primary bg-primary/5'
                                                : 'border-border hover:border-primary/50'
                                                }`}
                                            onClick={() => setSelectedTemplate(template.filename)}
                                        >
                                            <div className="flex items-center gap-3 flex-1 min-w-0">
                                                <FileSpreadsheet className="h-5 w-5 text-green-600 flex-shrink-0" />
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-medium truncate">{template.filename}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {formatFileSize(template.size_bytes)} • {formatDate(template.uploaded_at)}
                                                    </p>
                                                </div>
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleDeleteTemplate(template.filename);
                                                }}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Selected Template Details */}
                        {(selectedTemplateDetails || validating) && (
                            <div className="bg-muted/30 rounded-lg p-4 space-y-3 border border-dashed border-primary/20">
                                <div className="flex items-center justify-between">
                                    <h4 className="text-sm font-semibold flex items-center gap-2">
                                        {validating ? (
                                            <>
                                                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                                Validating...
                                            </>
                                        ) : (
                                            <>
                                                <CheckCircle2 className={`h-4 w-4 ${selectedTemplateDetails?.valid ? 'text-green-500' : 'text-amber-500'}`} />
                                                Template Ready
                                            </>
                                        )}
                                    </h4>
                                </div>

                                {!validating && selectedTemplateDetails && (
                                    <div className="grid grid-cols-2 gap-2">
                                        <div className={`p-2 rounded border text-xs ${selectedTemplateDetails.detected_sheets?.daily ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
                                            <div className="text-[10px] text-muted-foreground uppercase font-semibold">Daily</div>
                                            <div className="font-medium truncate">{selectedTemplateDetails.detected_sheets?.daily || 'Not Found'}</div>
                                        </div>
                                        <div className={`p-2 rounded border text-xs ${selectedTemplateDetails.detected_sheets?.weekly ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
                                            <div className="text-[10px] text-muted-foreground uppercase font-semibold">Weekly</div>
                                            <div className="font-medium truncate">{selectedTemplateDetails.detected_sheets?.weekly || 'Not Found'}</div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Report Generation */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="h-5 w-5" />
                            Generate Report
                        </CardTitle>
                        <CardDescription>
                            Configure and generate pacing reports
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Aggregation Level */}
                        <div className="space-y-2">
                            <Label>Aggregation Level</Label>
                            <Select value={aggregation} onValueChange={(value: any) => setAggregation(value)}>
                                <SelectTrigger>
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="daily">Daily</SelectItem>
                                    <SelectItem value="weekly">Weekly</SelectItem>
                                    <SelectItem value="monthly">Monthly</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        {/* Date Range */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="start-date">Start Date (Optional)</Label>
                                <Input
                                    id="start-date"
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="end-date">End Date (Optional)</Label>
                                <Input
                                    id="end-date"
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                />
                            </div>
                        </div>

                        {/* Generate Button */}
                        <Button
                            className="w-full"
                            size="lg"
                            onClick={handleGenerateReport}
                            disabled={!selectedTemplate || generating}
                        >
                            {generating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <TrendingUp className="mr-2 h-4 w-4" />
                                    Generate Report
                                </>
                            )}
                        </Button>

                        {/* Progress Indicator */}
                        {generating && (
                            <div className="space-y-2 pt-2">
                                <div className="flex justify-between text-xs font-medium text-muted-foreground">
                                    <span className="animate-pulse">{jobStatus || 'Processing...'}</span>
                                    <span>{jobProgress}%</span>
                                </div>
                                <div className="w-full bg-secondary/50 rounded-full h-1.5 overflow-hidden">
                                    <div
                                        className="bg-primary h-full transition-all duration-500 ease-out shadow-[0_0_10px_rgba(var(--primary),0.5)]"
                                        style={{ width: `${jobProgress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        {!selectedTemplate && !generating && (
                            <p className="text-xs text-muted-foreground text-center">
                                Please select a template to generate a report
                            </p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Generated Reports */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileSpreadsheet className="h-5 w-5" />
                        Generated Reports
                    </CardTitle>
                    <CardDescription>
                        Download or delete previously generated reports
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex items-center justify-center p-8">
                            <Loader2 className="h-8 w-8 animate-spin" />
                        </div>
                    ) : reports.length === 0 ? (
                        <div className="text-center py-12">
                            <FileSpreadsheet className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
                            <p className="text-muted-foreground">No reports loaded yet</p>
                            <div className="mt-4 flex flex-col items-center gap-2">
                                <Button
                                    variant="outline"
                                    onClick={() => loadReports()}
                                >
                                    <Download className="mr-2 h-4 w-4" />
                                    Load Generated Reports
                                </Button>
                                <p className="text-xs text-muted-foreground">
                                    Generate your first report using a template above
                                </p>
                            </div>
                        </div>

                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {reports.map((report) => (
                                <div
                                    key={report.filename}
                                    className="border rounded-lg p-4 hover:border-primary/50 transition-colors"
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <FileSpreadsheet className="h-8 w-8 text-green-600" />
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDeleteReport(report.filename)}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    <h3 className="font-medium text-sm mb-2 truncate" title={report.filename}>
                                        {report.filename}
                                    </h3>
                                    <p className="text-xs text-muted-foreground mb-3">
                                        {formatFileSize(report.size_bytes)} • {formatDate(report.generated_at)}
                                    </p>
                                    <div className="flex gap-2">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            className="flex-1"
                                            onClick={() => handleDownloadReport(report.filename)}
                                        >
                                            <Download className="mr-2 h-4 w-4" />
                                            Download
                                        </Button>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            className="flex-1"
                                            asChild
                                        >
                                            <a
                                                href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/pacing-reports/download/${report.filename}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                <FileSpreadsheet className="mr-2 h-4 w-4" />
                                                Open
                                            </a>
                                        </Button>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="w-full text-xs mt-2"
                                        onClick={() => {
                                            const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/pacing-reports/download/${report.filename}`;
                                            navigator.clipboard.writeText(url);
                                            showAlert('success', 'Link copied! Paste in browser to download');
                                        }}
                                    >
                                        Copy Download Link
                                    </Button>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
