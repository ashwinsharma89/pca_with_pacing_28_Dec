import reflex as rx
from typing import Dict, Any, List, Optional
from .filter import FilterState
from src.analytics import MediaAnalyticsExpert
try:
    from src.utils.summary_formatter import _format_text
    FORMATTER_AVAILABLE = True
except ImportError:
    def _format_text(x): return x
    FORMATTER_AVAILABLE = False

class AnalysisState(FilterState):
    """State for AI Analysis."""
    
    # Analysis Options
    use_rag: bool = True
    include_benchmarks: bool = True
    depth: str = "Standard"
    
    # Results
    analysis_complete: bool = False
    executive_summary: str = ""
    detailed_summary: str = ""
    insights: List[str] = []
    recommendations: List[str] = []
    
    # Progress
    is_analyzing: bool = False
    
    def run_analysis(self):
        """Run the AI analysis on the current data."""
        # Use filtered_df property
        df = self.filtered_df
        
        if df is None or df.empty:
            return rx.window_alert("No data loaded or data is empty after filtering.")
            
        self.is_analyzing = True
        yield
        
        try:
            analytics = MediaAnalyticsExpert()
            
            # Run analysis
            results = analytics.analyze_all(
                df, # Use filtered df
                use_parallel=True
            )
            
            if results:
                summary = results.get('executive_summary', {})
                
                # REPLICATING STREAMLIT BEHAVIOR:
                # Explicitly call the specific RAG summary method if requested
                if self.use_rag:
                    try:
                        rag_summary = analytics._generate_executive_summary_with_rag(
                            results.get('metrics', {}),
                            results.get('insights', []),
                            results.get('recommendations', [])
                        )
                        if rag_summary:
                            summary = rag_summary
                            self.log("RAG summary generated successfully via explicit call.")
                    except Exception as e:
                        self.log(f"RAG summary generation failed, falling back to standard: {e}", level="warning")

                if isinstance(summary, dict):
                    # Apply formatting to both brief and detailed summaries
                    brief = summary.get('brief', "Analysis complete.")
                    detailed = summary.get('detailed', "")
                    
                    if FORMATTER_AVAILABLE:
                        brief = _format_text(brief)
                        detailed = _format_text(detailed)
                        
                    self.executive_summary = brief
                    self.detailed_summary = detailed
                else:
                    text = str(summary)
                    if FORMATTER_AVAILABLE:
                        text = _format_text(text)
                    self.executive_summary = text
                
                self.insights = results.get('insights', [])
                self.recommendations = results.get('recommendations', [])
                self.analysis_complete = True
            else:
                return rx.window_alert("Analysis failed to generate results.")
                
        except Exception as e:
            print(f"Analysis error: {e}")
            self.log(f"Analysis error: {e}", level="error")
            return rx.window_alert(f"Analysis Error: {str(e)}")
        finally:
            self.is_analyzing = False
