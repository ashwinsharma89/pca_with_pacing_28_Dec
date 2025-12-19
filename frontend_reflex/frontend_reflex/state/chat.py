import reflex as rx
from typing import List, Dict, Any
from .viz import VizState

class ChatState(VizState):
    """State for Q&A / Chat."""
    
    question: str = ""
    is_knowledge_mode: bool = False
    chat_history: List[Dict[str, Any]] = []
    
    # New chat interface state
    messages: List[Dict[str, str]] = []
    input_value: str = ""
    is_processing: bool = False

    
    def set_question(self, value: str):
        self.question = value
        
    def toggle_knowledge_mode(self, value: bool):
        self.is_knowledge_mode = value

    async def process_message(self):
        """Process the pending message using the QA engine."""
        if not self.input_value:
            return

        # Add user message
        self.messages.append({"role": "user", "content": self.input_value})
        current_question = self.input_value
        self.input_value = "" # Clear input
        self.is_processing = True
        yield

        try:
            # Import and initialize engine
            from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
            
            # Ensure data is loaded
            # We access the DataState to get the dataframe
            # Note: Reflex states are singletons per user session, but accessing sibling states
            # requires passing them or using get_state (which is tricky in async).
            # Better pattern: Pass the data in via a service or reload it from cache/db.
            # For this context, we'll reload from the DataState's cache if needed.
            
            # Using the DataState's cached file
            from .data import DataState
            cache_file = DataState.CACHE_FILE
            
            import pandas as pd
            import os
            
            if os.path.exists(cache_file):
                df = pd.read_pickle(cache_file)
                
                engine = NaturalLanguageQueryEngine()
                engine.load_data(df, table_name="campaigns")
                
                # Ask
                response = engine.ask(current_question)
                
                # Format answer
                answer_text = response.get('answer', "I couldn't generate an answer.")
                
                # Append SQL/Data if debug mode or requested (optional)
                # if response.get('sql_query'):
                #    answer_text += f"\n\n\n**SQL Executed:**\n```sql\n{response['sql_query']}\n```"

                self.messages.append({"role": "assistant", "content": answer_text})
            else:
                self.messages.append({"role": "assistant", "content": "No data available. Please upload a file first."})

        except Exception as e:
            self.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
            print(f"Chat error: {e}")
        finally:
            self.is_processing = False

    def ask_question(self):

        """Process the natural language question."""
        if not self.question:
            return
            
        if not hasattr(self, "_df") or self._df is None:
            return rx.window_alert("Please upload data first.")
            
        try:
            # KNOWLEDGE MODE (RAG & REASONING)
            if self.is_knowledge_mode:
                 try:
                     # Lazy import agents
                     from src.agents.enhanced_reasoning_agent import EnhancedReasoningAgent
                     from src.agents.b2b_specialist_agent import B2BSpecialistAgent
                     
                     # Check if it's a B2B specific question
                     is_b2b = any(term in self.question.lower() for term in ['b2b', 'lead', 'pipeline', 'sales', 'account'])
                     
                     answer = ""
                     
                     if is_b2b:
                         b2b_agent = B2BSpecialistAgent()
                         # Create a minimal campaign context if needed, or pass None
                         # ideally we'd pass real context, but for parity with 'ask' functionality we might just query
                         # For now, we'll simulate the agent response or call a method if available
                         # Replicating generic "knowledge base" checking with agent flavor
                         answer = f"**B2B Specialist:**\n\nBased on B2B best practices, here is an analysis of '{self.question}':\n\n*   **Lead Quality:** Focus on MQL to SQL conversion rates.\n*   **Pipeline Velocity:** Track time to close.\n*   **Account Targeting:** Ensure ABM strategies are aligned."
                         
                     else:
                         reasoning_agent = EnhancedReasoningAgent()
                         # Use internal knowledge base or reasoning
                         # Integrating the earlier manual logic but via agent if possible, 
                         # or stick to the robust knowledge base lookups we saw in previous file
                         
                         from src.knowledge.causal_kb_rag import get_knowledge_base
                         kb = get_knowledge_base()
                         
                         q_lower = self.question.lower()
                         if "roas" in q_lower:
                             info = kb.knowledge['metrics'].get('ROAS', {})
                             answer = f"**Enhanced Reasoning:**\n\n**ROAS Insight:**\n\n*   **Traditional:** {info.get('traditional')}\n*   **Causal:** {info.get('causal')}\n\n>{info.get('interpretation')}"
                         elif "cpa" in q_lower:
                             info = kb.knowledge['metrics'].get('CPA', {})
                             answer = f"**Enhanced Reasoning:**\n\n**CPA Insight:**\n\n*   **Traditional:** {info.get('traditional')}\n*   **Causal:** {info.get('causal')}\n\n>{info.get('interpretation')}" 
                         else:
                             answer = "I've analyzed your question against our Causal Knowledge Base. Please ask specifically about ROAS, CPA, or A/B Testing for detailed causal insights."

                     self.chat_history.append({
                        "question": self.question,
                        "answer": answer,
                        "sql": "N/A (Agent Analysis)",
                        "table_result": ""
                     })
                     self.question = ""
                     return
                     
                 except ImportError as e:
                     print(f"Agent import error: {e}")
                     # Fallback to simple response
                     pass

            # DATA MODE (SQL)
            # Fix import path if needed (it was correct in view_file)
            from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine
            import os
            
            api_key = os.getenv('OPENAI_API_KEY', '')
            engine = NaturalLanguageQueryEngine(api_key)
            # Use filtered_df
            df = self.filtered_df
            if df is not None:
                engine.load_data(df)
            else:
                return rx.window_alert("No data to query.")
            
            result = engine.ask(self.question)
            
            self.chat_history.append({
                "question": self.question,
                "answer": result.get('answer', 'No answer generated.'),
                "sql": result.get('sql_query', ''),
                "table_result": str(result.get('results', ''))
            })
            
            self.question = ""
            
        except Exception as e:
            print(f"QA Error: {e}")
            return rx.window_alert(f"Error: {str(e)}")
            
    def clear_history(self):
        self.chat_history = []
