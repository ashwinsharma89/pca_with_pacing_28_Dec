import reflex as rx
from typing import Dict, List, Any, Optional
from .diagnostics import DiagnosticsState
import pandas as pd
import os

# Import predictive modules from backend (reusing existing logic)
# We use try/except to avoid crashing if backend modules aren't found or have missing deps
try:
    from src.predictive import (
        CampaignSuccessPredictor,
        BudgetAllocationOptimizer
    )
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("Warning: Predictive backend modules not found.")

class PredictiveState(DiagnosticsState):
    """State for Predictive Analytics."""
    
    # Campaign Predictor Inputs
    campaign_name: str = "New Campaign"
    budget: float = 25000.0
    duration: int = 30
    audience_size: int = 500000
    selected_channels: List[str] = ["Meta", "Google"]
    creative_type: str = "video"
    objective: str = "conversion"
    
    # Predictor Outputs
    prediction_result: Dict[str, Any] = {}
    is_predicting: bool = False
    
    # Budget Optimizer Inputs
    opt_budget: float = 100000.0
    opt_goal: str = "roas"
    opt_min_spend: float = 5000.0
    
    # Optimizer Outputs
    optimization_result: Dict[str, Any] = {}
    optimization_chart: Optional[rx.Component] = None # Will store chart data structure if needed, or we rebuild in UI
    is_optimizing: bool = False
    
    # Model Training
    target_roas: float = 3.0
    target_cpa: float = 75.0
    training_metrics: Dict[str, Any] = {}
    is_training: bool = False

    def set_duration(self, val: List[int]):
         self.duration = val[0]
         
    def set_selected_channels(self, val: bool, channel: str):
        if val:
            self.selected_channels.append(channel)
        elif channel in self.selected_channels:
            self.selected_channels.remove(channel)

    def run_prediction(self):
        """Run campaign success prediction."""
        if not BACKEND_AVAILABLE:
            yield rx.window_alert("Predictive backend not available.")
            return
            
        self.is_predicting = True
        yield
        
        try:
            # Check for model existence (mock check or real check)
            predictor = CampaignSuccessPredictor()
            # Try load model, if fail, maybe train on the fly or warn?
            # For MVP we assume model exists or we handle error inside predictor
            
            # Construct plan
            plan = {
                'name': self.campaign_name,
                'budget': self.budget,
                'duration': self.duration,
                'audience_size': self.audience_size,
                'channels': ','.join(self.selected_channels),
                'creative_type': self.creative_type,
                'objective': self.objective,
                'start_date': "2024-01-01", # simplified
                'roas': 3.5 # default assumption
            }
            
            # Predict
            # Note: This might block. In real prod, offload to worker or async.
            result = predictor.predict_success_probability(plan)
            self.prediction_result = result
            
        except Exception as e:
            yield rx.window_alert(f"Prediction Error: {e}")
        finally:
            self.is_predicting = False

    def run_optimization(self):
        """Run budget optimization."""
        if not hasattr(self, "_df") or self._df is None:
             yield rx.window_alert("Please upload historical data first.")
             return
             
        self.is_optimizing = True
        yield
        
        try:
            optimizer = BudgetAllocationOptimizer(self.filtered_df) # Use filtered data for optimization
            
            result = optimizer.optimize_allocation(
                total_budget=self.opt_budget,
                campaign_goal=self.opt_goal,
                constraints={'min_spend_per_channel': self.opt_min_spend}
            )
            
            self.optimization_result = result
            
            # Format data for chart (Pie)
            # Pie charts in Reflex/Plotly take labels/values
            self.optimization_result['chart_labels'] = list(result['allocation'].keys())
            self.optimization_result['chart_values'] = [x['recommended_budget'] for x in result['allocation'].values()]
            
        except Exception as e:
             yield rx.window_alert(f"Optimization Error: {e}")
        finally:
            self.is_optimizing = False

    def train_model(self):
        """Train the predictive model with current data."""
        if not hasattr(self, "_df") or self._df is None:
             yield rx.window_alert("Please upload historical data first.")
             return
             
        self.is_training = True
        yield
        
        try:
            predictor = CampaignSuccessPredictor()
            metrics = predictor.train(
                self.filtered_df,
                success_threshold={'roas': self.target_roas, 'cpa': self.target_cpa}
            )
            
            self.training_metrics = metrics
            # Persist model
            os.makedirs('models', exist_ok=True)
            predictor.save_model('models/campaign_success_predictor.pkl')
            
        except Exception as e:
            yield rx.window_alert(f"Training Error: {e}")
        finally:
            self.is_training = False
