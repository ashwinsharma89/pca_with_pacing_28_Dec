"""
Anomaly Detection API Endpoints
REST API for anomaly detection using IsolationForest
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
from src.ml.anomaly_detection import anomaly_detector

router = APIRouter(prefix="/api/anomaly", tags=["anomaly-detection"])

class TrainRequest(BaseModel):
    """Request to train anomaly detector."""
    metric_name: str
    historical_data: List[Dict[str, Any]]
    contamination: float = 0.1

class DetectRequest(BaseModel):
    """Request to detect anomalies."""
    metric_name: str
    current_data: List[Dict[str, Any]]

class TimeSeriesRequest(BaseModel):
    """Request for time series anomaly detection."""
    metric_name: str
    time_series: List[Dict[str, Any]]
    window_size: int = 10

class PatternRequest(BaseModel):
    """Request for pattern anomaly detection."""
    data: List[Dict[str, Any]]
    pattern_type: str = "sudden_spike"

class MultivariateRequest(BaseModel):
    """Request for multivariate anomaly detection."""
    data: List[Dict[str, Any]]
    feature_columns: List[str]

@router.post("/train")
async def train_detector(request: TrainRequest) -> Dict[str, Any]:
    """
    Train anomaly detector for a specific metric.
    
    Args:
        request: Training request with historical data
    
    Returns:
        Training result
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.historical_data)
        
        # Ensure required columns
        if 'value' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Historical data must contain 'value' column"
            )
        
        # Train detector
        anomaly_detector.train_metric_detector(
            metric_name=request.metric_name,
            historical_data=df,
            contamination=request.contamination
        )
        
        return {
            "success": True,
            "message": f"Detector trained for {request.metric_name}",
            "metric_name": request.metric_name,
            "samples": len(df),
            "contamination": request.contamination
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect")
async def detect_anomaly(request: DetectRequest) -> Dict[str, Any]:
    """
    Detect anomalies in current data.
    
    Args:
        request: Detection request with current data
    
    Returns:
        Anomaly detection result
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.current_data)
        
        # Ensure required columns
        if 'value' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Current data must contain 'value' column"
            )
        
        # Detect anomalies
        result = anomaly_detector.detect_anomaly(
            metric_name=request.metric_name,
            current_data=df
        )
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/timeseries")
async def detect_timeseries_anomalies(request: TimeSeriesRequest) -> Dict[str, Any]:
    """
    Detect anomalies in time series data.
    
    Args:
        request: Time series request
    
    Returns:
        List of detected anomalies
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.time_series)
        
        # Ensure required columns
        if 'value' not in df.columns or 'timestamp' not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="Time series must contain 'value' and 'timestamp' columns"
            )
        
        # Detect anomalies
        anomalies = anomaly_detector.detect_time_series_anomalies(
            metric_name=request.metric_name,
            time_series=df,
            window_size=request.window_size
        )
        
        return {
            "success": True,
            "metric_name": request.metric_name,
            "total_points": len(df),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/pattern")
async def detect_pattern_anomalies(request: PatternRequest) -> Dict[str, Any]:
    """
    Detect specific pattern anomalies.
    
    Args:
        request: Pattern detection request
    
    Returns:
        List of detected pattern anomalies
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Detect pattern anomalies
        anomalies = anomaly_detector.detect_pattern_anomalies(
            data=df,
            pattern_type=request.pattern_type
        )
        
        return {
            "success": True,
            "pattern_type": request.pattern_type,
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/multivariate")
async def detect_multivariate_anomalies(request: MultivariateRequest) -> Dict[str, Any]:
    """
    Detect anomalies across multiple correlated metrics.
    
    Args:
        request: Multivariate detection request
    
    Returns:
        Multivariate anomaly detection result
    """
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        
        # Ensure all feature columns exist
        missing_cols = set(request.feature_columns) - set(df.columns)
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing_cols}"
            )
        
        # Detect multivariate anomalies
        result = anomaly_detector.detect_multivariate_anomalies(
            data=df,
            feature_columns=request.feature_columns
        )
        
        return {
            "success": True,
            **result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_trained_models() -> Dict[str, Any]:
    """
    List all trained anomaly detection models.
    
    Returns:
        List of trained models
    """
    models = list(anomaly_detector.models.keys())
    
    model_info = []
    for model_name in models:
        baseline = anomaly_detector.baselines.get(model_name, {})
        model_info.append({
            "metric_name": model_name,
            "baseline_mean": baseline.get("mean"),
            "baseline_std": baseline.get("std"),
            "baseline_p95": baseline.get("p95"),
            "baseline_p99": baseline.get("p99")
        })
    
    return {
        "success": True,
        "total_models": len(models),
        "models": model_info
    }

@router.delete("/models/{metric_name}")
async def delete_model(metric_name: str) -> Dict[str, Any]:
    """
    Delete a trained model.
    
    Args:
        metric_name: Name of the metric model to delete
    
    Returns:
        Deletion result
    """
    if metric_name not in anomaly_detector.models:
        raise HTTPException(
            status_code=404,
            detail=f"Model for {metric_name} not found"
        )
    
    del anomaly_detector.models[metric_name]
    del anomaly_detector.scalers[metric_name]
    del anomaly_detector.baselines[metric_name]
    
    return {
        "success": True,
        "message": f"Model for {metric_name} deleted"
    }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check for anomaly detection service.
    
    Returns:
        Service health status
    """
    return {
        "success": True,
        "service": "anomaly_detection",
        "status": "healthy",
        "trained_models": len(anomaly_detector.models),
        "algorithms": ["IsolationForest", "Z-Score", "Pattern Matching"]
    }
