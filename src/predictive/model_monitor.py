"""
ML Model Monitoring
Tracks model performance, data drift, and prediction quality
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import deque
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class PredictionLog:
    """Log of a single prediction"""
    model_id: str
    model_version: str
    input_features: Dict[str, Any]
    prediction: Any
    actual: Optional[Any] = None
    latency_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ModelMonitor:
    """
    Monitor ML model performance and health
    
    Features:
    - Prediction latency tracking
    - Accuracy/error monitoring
    - Data drift detection
    - Alerting on degradation
    """
    
    WINDOW_SIZE = 1000  # Keep last N predictions
    
    def __init__(self, model_id: str, model_version: str):
        self.model_id = model_id
        self.model_version = model_version
        self.predictions: deque = deque(maxlen=self.WINDOW_SIZE)
        self.latencies: deque = deque(maxlen=self.WINDOW_SIZE)
        self.errors: deque = deque(maxlen=self.WINDOW_SIZE)
        self.feature_stats: Dict[str, Dict] = {}
        self._baseline_stats: Dict[str, Dict] = {}
    
    def log_prediction(
        self,
        input_features: Dict[str, Any],
        prediction: Any,
        latency_ms: float,
        actual: Any = None
    ) -> PredictionLog:
        """Log a prediction for monitoring"""
        log = PredictionLog(
            model_id=self.model_id,
            model_version=self.model_version,
            input_features=input_features,
            prediction=prediction,
            actual=actual,
            latency_ms=latency_ms
        )
        
        self.predictions.append(log)
        self.latencies.append(latency_ms)
        
        if actual is not None:
            error = abs(prediction - actual) if isinstance(prediction, (int, float)) else (prediction != actual)
            self.errors.append(error)
        
        # Update feature stats
        self._update_feature_stats(input_features)
        
        return log
    
    def _update_feature_stats(self, features: Dict[str, Any]):
        """Update running statistics for features"""
        for name, value in features.items():
            if not isinstance(value, (int, float)):
                continue
            
            if name not in self.feature_stats:
                self.feature_stats[name] = {"values": deque(maxlen=self.WINDOW_SIZE)}
            
            self.feature_stats[name]["values"].append(value)
    
    def set_baseline(self):
        """Set current statistics as baseline for drift detection"""
        for name, stats in self.feature_stats.items():
            values = list(stats["values"])
            if values:
                self._baseline_stats[name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values)
                }
        logger.info(f"Baseline set for model {self.model_id}")
    
    def get_latency_stats(self) -> Dict:
        """Get latency statistics"""
        if not self.latencies:
            return {"error": "No data"}
        
        latencies = list(self.latencies)
        return {
            "count": len(latencies),
            "mean_ms": np.mean(latencies),
            "p50_ms": np.percentile(latencies, 50),
            "p95_ms": np.percentile(latencies, 95),
            "p99_ms": np.percentile(latencies, 99),
            "max_ms": np.max(latencies)
        }
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        if not self.errors:
            return {"error": "No labeled data"}
        
        errors = list(self.errors)
        return {
            "count": len(errors),
            "mean_error": np.mean(errors),
            "std_error": np.std(errors),
            "max_error": np.max(errors)
        }
    
    def detect_drift(self, threshold: float = 2.0) -> Dict[str, Dict]:
        """
        Detect data drift using statistical comparison to baseline
        
        Args:
            threshold: Number of standard deviations for drift alert
            
        Returns:
            Dict of features with drift detected
        """
        drift_report = {}
        
        for name, stats in self.feature_stats.items():
            if name not in self._baseline_stats:
                continue
            
            baseline = self._baseline_stats[name]
            current_values = list(stats["values"])
            
            if not current_values or baseline["std"] == 0:
                continue
            
            current_mean = np.mean(current_values)
            z_score = abs(current_mean - baseline["mean"]) / baseline["std"]
            
            if z_score > threshold:
                drift_report[name] = {
                    "baseline_mean": baseline["mean"],
                    "current_mean": current_mean,
                    "z_score": z_score,
                    "drift_detected": True
                }
        
        if drift_report:
            logger.warning(f"Data drift detected in {len(drift_report)} features")
        
        return drift_report
    
    def get_health_report(self) -> Dict:
        """Get overall model health report"""
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "predictions_logged": len(self.predictions),
            "latency": self.get_latency_stats(),
            "errors": self.get_error_stats() if self.errors else None,
            "drift": self.detect_drift(),
            "timestamp": datetime.utcnow().isoformat()
        }


class ModelMonitorRegistry:
    """Registry of model monitors"""
    
    def __init__(self):
        self.monitors: Dict[str, ModelMonitor] = {}
    
    def get_or_create(self, model_id: str, model_version: str) -> ModelMonitor:
        key = f"{model_id}:{model_version}"
        if key not in self.monitors:
            self.monitors[key] = ModelMonitor(model_id, model_version)
        return self.monitors[key]
    
    def get_all_health_reports(self) -> List[Dict]:
        return [m.get_health_report() for m in self.monitors.values()]


# Global registry
_monitor_registry: Optional[ModelMonitorRegistry] = None

def get_model_monitor(model_id: str, model_version: str) -> ModelMonitor:
    global _monitor_registry
    if _monitor_registry is None:
        _monitor_registry = ModelMonitorRegistry()
    return _monitor_registry.get_or_create(model_id, model_version)
