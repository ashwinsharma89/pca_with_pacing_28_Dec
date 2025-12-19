import reflex as rx
from typing import Dict, List, Any, Optional
from .chat import ChatState
import plotly.graph_objects as go
from src.knowledge.causal_kb_rag import get_knowledge_base


class DiagnosticsState(ChatState):
    """State for Performance Diagnostics."""
    
    # Causal Analysis Inputs
    causal_metric: str = "ROAS"
    lookback_days: int = 30
    causal_result: Dict[str, Any] = {}
    causal_waterfall: Optional[go.Figure] = None 
    causal_insights: List[str] = [] # Typed list for foreach
    causal_recommendations: List[str] = [] # Typed list for KB best practices
    is_running_causal: bool = False

    
    # Driver Analysis Inputs
    driver_target: str = "ROAS"
    driver_result: Dict[str, Any] = {}
    driver_chart: Optional[go.Figure] = None
    is_running_driver: bool = False
    
    def set_causal_metric(self, value: str):
        self.causal_metric = value
        
    def set_lookback_days(self, value: List[int]): 
        self.lookback_days = value[0]
            
    def set_driver_target(self, value: str):
        self.driver_target = value
            
    def run_causal_analysis(self):
        """Run Causal Analysis."""
        if not hasattr(self, "_df") or self._df is None:
            yield rx.window_alert("Please upload data first.")
            return
            
        self.is_running_causal = True
        yield
        
        try:
            from src.analytics.causal_analysis import CausalAnalysisEngine, DecompositionMethod
            
            engine = CausalAnalysisEngine()
            df = self.filtered_df
            if df is None or df.empty:
                self.is_running_causal = False
                return rx.window_alert("No data available.")

            # Find date col
            date_col = next((c for c in df.columns if 'date' in c.lower()), 'Date')
            
            if self.causal_metric not in df.columns:
                 self.is_running_causal = False
                 yield rx.window_alert(f"Metric {self.causal_metric} not found in data.")
                 return
            
            # Run analysis
            result = engine.analyze(
                df=df,
                metric=self.causal_metric,
                date_col=date_col,
                lookback_days=self.lookback_days,
                method=DecompositionMethod.HYBRID
            )
            
            self.causal_waterfall = self._create_waterfall_chart(result)
            self.causal_insights = result.insights # Update list var
            
            # Enhance with Knowledge Base
            kb = get_knowledge_base()
            enhanced = kb.enhance_causal_result(result)
            
            self.causal_recommendations = enhanced.get("enhanced_recommendations", [])
            
            self.causal_result = {
                "total_change": result.total_change,
                "total_change_pct": result.total_change_pct,
                "confidence": result.confidence,
                "insights": result.insights,
                "interpretation": enhanced.get("interpretation", {}),
            }
            
        except Exception as e:
            print(f"Causal analysis error: {e}")
            yield rx.window_alert(f"Error: {str(e)}")
        finally:
            self.is_running_causal = False

    def _create_waterfall_chart(self, result):
        sorted_contribs = sorted(result.contributions, key=lambda x: abs(x.absolute_change), reverse=True)
        components = [c.component for c in sorted_contribs]
        values = [c.absolute_change for c in sorted_contribs]
        
        fig = go.Figure(go.Waterfall(
            name="Component Contribution",
            orientation="v",
            measure=["relative"] * len(components) + ["total"],
            x=components + ["Total Change"],
            y=values + [result.total_change],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "green"}},
            decreasing={"marker": {"color": "red"}},
            totals={"marker": {"color": "blue"}}
        ))
        fig.update_layout(title=f"{result.metric} Decomposition", template="plotly_dark")
        return fig

    def run_driver_analysis(self):
        """Run Driver Analysis."""
        if not hasattr(self, "_df") or self._df is None:
            yield rx.window_alert("Please upload data first.")
            return
            
        self.is_running_driver = True
        yield
        
        try:
            from src.analytics.performance_diagnostics import PerformanceDiagnostics
            
            engine = PerformanceDiagnostics()
            df = self.filtered_df
            if df is None:
                 self.is_running_driver = False
                 yield rx.window_alert("No data.")
                 return

            if self.driver_target not in df.columns:
                 self.is_running_driver = False
                 yield rx.window_alert(f"Metric {self.driver_target} not found.")
                 return

            analysis = engine.analyze_drivers(
                df=df,
                target_metric=self.driver_target
            )
            
            sorted_features = sorted(analysis.feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            features, importances = zip(*sorted_features) if sorted_features else ([], [])
            
            fig = go.Figure(go.Bar(
                x=list(importances),
                y=list(features),
                orientation='h'
            ))
            fig.update_layout(title=f"Top Drivers of {self.driver_target}", template="plotly_dark")
            
            self.driver_chart = fig
            
            self.driver_result = {
                "model_score": analysis.model_score,
                "insights": analysis.insights,
            }
            
        except Exception as e:
            print(f"Driver analysis error: {e}")
            yield rx.window_alert(f"Error: {str(e)}")
        finally:
            self.is_running_driver = False
