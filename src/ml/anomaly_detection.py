"""
Advanced Anomaly Detection
ML-based anomaly detection for metrics, performance, and behavior
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from loguru import logger

class AdvancedAnomalyDetector:
    """Advanced ML-based anomaly detection."""
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.models: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        logger.info("✅ Advanced Anomaly Detector initialized")
    
    def train_metric_detector(
        self,
        metric_name: str,
        historical_data: pd.DataFrame,
        contamination: float = 0.1
    ):
        """
        Train anomaly detector for a specific metric.
        
        Args:
            metric_name: Name of the metric
            historical_data: Historical metric data
            contamination: Expected proportion of anomalies
        """
        # Prepare features
        features = self._extract_features(historical_data)
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        model.fit(scaled_features)
        
        # Store model and scaler
        self.models[metric_name] = model
        self.scalers[metric_name] = scaler
        
        # Calculate baseline statistics
        self.baselines[metric_name] = {
            "mean": historical_data["value"].mean(),
            "std": historical_data["value"].std(),
            "min": historical_data["value"].min(),
            "max": historical_data["value"].max(),
            "p95": historical_data["value"].quantile(0.95),
            "p99": historical_data["value"].quantile(0.99)
        }
        
        logger.info(f"✅ Trained anomaly detector for {metric_name}")
    
    def detect_anomaly(
        self,
        metric_name: str,
        current_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Detect anomalies in current data.
        
        Args:
            metric_name: Name of the metric
            current_data: Current metric data
        
        Returns:
            Anomaly detection result
        """
        if metric_name not in self.models:
            return {
                "is_anomaly": False,
                "error": f"No model trained for {metric_name}"
            }
        
        # Extract features
        features = self._extract_features(current_data)
        
        # Scale features
        scaled_features = self.scalers[metric_name].transform(features)
        
        # Predict
        predictions = self.models[metric_name].predict(scaled_features)
        anomaly_scores = self.models[metric_name].score_samples(scaled_features)
        
        # -1 indicates anomaly, 1 indicates normal
        is_anomaly = predictions[-1] == -1
        anomaly_score = float(anomaly_scores[-1])
        
        # Get current value
        current_value = current_data["value"].iloc[-1]
        
        # Compare with baseline
        baseline = self.baselines[metric_name]
        deviation = self._calculate_deviation(current_value, baseline)
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": anomaly_score,
            "current_value": float(current_value),
            "baseline_mean": baseline["mean"],
            "deviation_from_mean": deviation,
            "severity": self._calculate_severity(deviation, anomaly_score),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_time_series_anomalies(
        self,
        metric_name: str,
        time_series: pd.DataFrame,
        window_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in time series data.
        
        Args:
            metric_name: Name of the metric
            time_series: Time series data with 'timestamp' and 'value' columns
            window_size: Rolling window size
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Calculate rolling statistics
        time_series["rolling_mean"] = time_series["value"].rolling(window=window_size).mean()
        time_series["rolling_std"] = time_series["value"].rolling(window=window_size).std()
        
        # Z-score based detection
        time_series["z_score"] = (
            (time_series["value"] - time_series["rolling_mean"]) / 
            time_series["rolling_std"]
        )
        
        # Detect anomalies (|z-score| > 3)
        anomaly_mask = abs(time_series["z_score"]) > 3
        
        for idx, row in time_series[anomaly_mask].iterrows():
            anomalies.append({
                "timestamp": row["timestamp"],
                "value": float(row["value"]),
                "expected_value": float(row["rolling_mean"]),
                "z_score": float(row["z_score"]),
                "deviation": float(abs(row["value"] - row["rolling_mean"])),
                "severity": "high" if abs(row["z_score"]) > 5 else "medium"
            })
        
        return anomalies
    
    def detect_pattern_anomalies(
        self,
        data: pd.DataFrame,
        pattern_type: str = "sudden_spike"
    ) -> List[Dict[str, Any]]:
        """
        Detect specific pattern anomalies.
        
        Args:
            data: Time series data
            pattern_type: Type of pattern (sudden_spike, gradual_drift, etc.)
        
        Returns:
            List of detected pattern anomalies
        """
        anomalies = []
        
        if pattern_type == "sudden_spike":
            anomalies = self._detect_sudden_spikes(data)
        elif pattern_type == "gradual_drift":
            anomalies = self._detect_gradual_drift(data)
        elif pattern_type == "missing_data":
            anomalies = self._detect_missing_data(data)
        elif pattern_type == "oscillation":
            anomalies = self._detect_oscillations(data)
        
        return anomalies
    
    def detect_multivariate_anomalies(
        self,
        data: pd.DataFrame,
        feature_columns: List[str]
    ) -> Dict[str, Any]:
        """
        Detect anomalies across multiple correlated metrics.
        
        Args:
            data: DataFrame with multiple metrics
            feature_columns: Columns to analyze
        
        Returns:
            Multivariate anomaly detection result
        """
        # Extract features
        features = data[feature_columns].values
        
        # Scale features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(contamination=0.1, random_state=42)
        predictions = model.fit_predict(scaled_features)
        scores = model.score_samples(scaled_features)
        
        # Find anomalies
        anomaly_indices = np.where(predictions == -1)[0]
        
        anomalies = []
        for idx in anomaly_indices:
            anomalies.append({
                "index": int(idx),
                "timestamp": data.iloc[idx]["timestamp"] if "timestamp" in data.columns else None,
                "anomaly_score": float(scores[idx]),
                "values": {
                    col: float(data.iloc[idx][col])
                    for col in feature_columns
                }
            })
        
        return {
            "total_points": len(data),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(data) * 100,
            "anomalies": anomalies
        }
    
    def _extract_features(self, data: pd.DataFrame) -> np.ndarray:
        """Extract features from data."""
        features = []
        
        # Basic features
        features.append(data["value"].values)
        
        # Time-based features if timestamp exists
        if "timestamp" in data.columns:
            data["hour"] = pd.to_datetime(data["timestamp"]).dt.hour
            data["day_of_week"] = pd.to_datetime(data["timestamp"]).dt.dayofweek
            features.append(data["hour"].values)
            features.append(data["day_of_week"].values)
        
        # Statistical features
        if len(data) > 1:
            rolling_mean = data["value"].rolling(window=min(5, len(data))).mean().fillna(data["value"].mean())
            rolling_std = data["value"].rolling(window=min(5, len(data))).std().fillna(0)
            features.append(rolling_mean.values)
            features.append(rolling_std.values)
        
        return np.column_stack(features)
    
    def _calculate_deviation(self, value: float, baseline: Dict[str, float]) -> float:
        """Calculate deviation from baseline."""
        if baseline["std"] == 0:
            return 0.0
        return (value - baseline["mean"]) / baseline["std"]
    
    def _calculate_severity(self, deviation: float, anomaly_score: float) -> str:
        """Calculate anomaly severity."""
        abs_deviation = abs(deviation)
        
        if abs_deviation > 5 or anomaly_score < -0.5:
            return "critical"
        elif abs_deviation > 3 or anomaly_score < -0.3:
            return "high"
        elif abs_deviation > 2 or anomaly_score < -0.1:
            return "medium"
        else:
            return "low"
    
    def _detect_sudden_spikes(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect sudden spikes in data."""
        anomalies = []
        
        # Calculate rate of change
        data["rate_of_change"] = data["value"].pct_change()
        
        # Detect spikes (>50% change)
        spike_threshold = 0.5
        spike_mask = abs(data["rate_of_change"]) > spike_threshold
        
        for idx, row in data[spike_mask].iterrows():
            anomalies.append({
                "type": "sudden_spike",
                "timestamp": row["timestamp"] if "timestamp" in data.columns else None,
                "value": float(row["value"]),
                "rate_of_change": float(row["rate_of_change"]),
                "severity": "high" if abs(row["rate_of_change"]) > 1.0 else "medium"
            })
        
        return anomalies
    
    def _detect_gradual_drift(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect gradual drift in data."""
        anomalies = []
        
        # Calculate trend
        if len(data) > 10:
            from scipy import stats
            x = np.arange(len(data))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, data["value"])
            
            # Significant trend detected
            if abs(r_value) > 0.7 and p_value < 0.05:
                anomalies.append({
                    "type": "gradual_drift",
                    "slope": float(slope),
                    "r_squared": float(r_value ** 2),
                    "p_value": float(p_value),
                    "direction": "increasing" if slope > 0 else "decreasing",
                    "severity": "high" if abs(r_value) > 0.9 else "medium"
                })
        
        return anomalies
    
    def _detect_missing_data(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect missing data patterns."""
        anomalies = []
        
        # Check for null values
        null_count = data["value"].isnull().sum()
        
        if null_count > 0:
            anomalies.append({
                "type": "missing_data",
                "missing_count": int(null_count),
                "missing_percentage": float(null_count / len(data) * 100),
                "severity": "high" if null_count / len(data) > 0.1 else "medium"
            })
        
        return anomalies
    
    def _detect_oscillations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect oscillating patterns."""
        anomalies = []
        
        if len(data) > 20:
            # Calculate autocorrelation
            from statsmodels.tsa.stattools import acf
            
            autocorr = acf(data["value"].dropna(), nlags=min(20, len(data) // 2))
            
            # Check for periodic pattern
            if max(abs(autocorr[1:])) > 0.7:
                anomalies.append({
                    "type": "oscillation",
                    "max_autocorrelation": float(max(abs(autocorr[1:]))),
                    "severity": "medium"
                })
        
        return anomalies


# Global instance
anomaly_detector = AdvancedAnomalyDetector()
