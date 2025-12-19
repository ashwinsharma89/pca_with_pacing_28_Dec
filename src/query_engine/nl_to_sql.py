"""
Natural Language to SQL Query Engine
Converts natural language questions into SQL queries using LLM
"""
import duckdb
import pandas as pd
from typing import Dict, Any, Optional, List
from openai import OpenAI
import os
from loguru import logger
import sys

from .sql_knowledge import SQLKnowledgeHelper
from src.utils.anthropic_helpers import create_anthropic_client

# Configure logger to also write to file
logger.add("query_debug.log", rotation="1 MB", level="INFO")

# Try to import Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")

# Try to import Groq (FREE fallback)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("groq not installed. Install with: pip install groq")

# Try to import DeepSeek (FREE, excellent at coding)
DEEPSEEK_AVAILABLE = True  # Uses OpenAI-compatible API


class NaturalLanguageQueryEngine:
    """Engine to convert natural language questions to SQL queries and execute them."""
    
    def __init__(self, api_key: str):
        """
        Initialize the query engine.
        
        Args:
            api_key: OpenAI API key for LLM
        """
        self.openai_client = OpenAI(api_key=api_key)
        
        # Setup available models in priority order
        self.available_models = []
        self.sql_helper = SQLKnowledgeHelper(enable_hybrid=True)
        
        # 1. Gemini 2.5 Flash (FREE & FAST)
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key and GEMINI_AVAILABLE:
            genai.configure(api_key=google_key)
            self.available_models.append(('gemini', 'gemini-2.5-flash'))
            logger.info("Tier 1: Gemini 2.5 Flash (FREE)")
        
        # 2. DeepSeek (FREE CODING SPECIALIST)
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key and DEEPSEEK_AVAILABLE:
            self.deepseek_client = OpenAI(
                api_key=deepseek_key,
                base_url="https://api.deepseek.com"
            )
            self.available_models.append(('deepseek', 'deepseek-chat'))
            logger.info("Tier 2: DeepSeek Chat (FREE CODING SPECIALIST)")
        
        # 3. OpenAI GPT-5.1 Codex
        if self.openai_client:
            self.available_models.append(('openai', 'gpt-4o'))
            logger.info("Tier 3: OpenAI GPT-4o")
        
        # 4. Claude Sonnet 4.5
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key.startswith('sk-ant-'):
            self.anthropic_client = create_anthropic_client(anthropic_key)
            if self.anthropic_client:
                self.available_models.append(('claude', 'claude-sonnet-4-5-20250929'))
                logger.info("Tier 4: Claude Sonnet 4.5")
            else:
                logger.warning("Anthropic client unavailable. Skipping Claude tier.")
        
        # 5. Groq (ULTIMATE FREE FALLBACK)
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key and GROQ_AVAILABLE:
            self.groq_client = Groq(api_key=groq_key)
            self.available_models.append(('groq', 'llama-3.3-70b-versatile'))
            logger.info("Tier 5: Groq Llama 3.3 70B (FREE & SUPER FAST)")
        
        logger.info(f"Available models: {[m[0] for m in self.available_models]}")
        
        self.conn = None
        self.schema_info = None
        logger.info("Initialized NaturalLanguageQueryEngine")
    
    def load_data(self, df: pd.DataFrame, table_name: str = "campaigns"):
        """
        Load data into DuckDB.
        
        Args:
            df: DataFrame with campaign data
            table_name: Name for the table
        """
        # Convert Date-related columns to datetime if they exist
        df_copy = df.copy()
        
        # Detect date-related columns (date, week, week range, day, month, etc.)
        date_keywords = ['date', 'week', 'day', 'month', 'year', 'time', 'period']
        date_columns = [col for col in df_copy.columns 
                       if any(keyword in col.lower() for keyword in date_keywords)]
        
        for col in date_columns:
            try:
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
                logger.info(f"Converted {col} to datetime")
            except:
                logger.warning(f"Could not convert {col} to datetime")
        
        self.conn = duckdb.connect(':memory:')
        self.conn.register(table_name, df_copy)
        
        # Store schema information
        self.schema_info = {
            "table_name": table_name,
            "columns": df_copy.columns.tolist(),
            "dtypes": df_copy.dtypes.to_dict(),
            "sample_data": df_copy.head(3).to_dict('records')
        }
        
        logger.info(f"Loaded {len(df_copy)} rows into table '{table_name}'")

    def _get_schema_description(self) -> str:
        """Return a formatted schema description for prompt injection."""
        if not self.schema_info:
            raise ValueError(
                "Schema information not available. Call load_data() before asking questions."
            )

        columns = self.schema_info.get("columns", [])
        dtypes = self.schema_info.get("dtypes", {})
        sample_rows = self.schema_info.get("sample_data", [])
        table_name = self.schema_info.get("table_name", "campaigns")

        lines = [f"Table: {table_name}"]
        if columns:
            lines.append("Columns:")
            for col in columns:
                dtype = dtypes.get(col)
                lines.append(f"- {col} ({dtype})")
        
        # Include unique values for key categorical columns (CRITICAL for filters)
        if self.conn:
            try:
                categorical_cols = ['platform', 'channel', 'funnel', 'ad_type', 'device_type', 'campaign_name']
                lines.append("\n🔑 IMPORTANT - Actual values in data (use these EXACTLY for filters):")
                for col in columns:
                    col_lower = col.lower().replace(' ', '_')
                    if col_lower in categorical_cols or any(cat in col_lower for cat in categorical_cols):
                        try:
                            unique_query = f'SELECT DISTINCT "{col}" FROM {table_name} LIMIT 20'
                            unique_df = self.conn.execute(unique_query).fetchdf()
                            if not unique_df.empty:
                                unique_vals = unique_df.iloc[:, 0].dropna().tolist()[:10]
                                if unique_vals:
                                    lines.append(f"  {col}: {unique_vals}")
                        except:
                            pass
            except Exception as e:
                logger.warning(f"Could not get unique values: {e}")

        if sample_rows:
            lines.append("\nSample rows:")
            for row in sample_rows:
                lines.append(f"- {row}")

        return "\n".join(lines)

    def generate_sql(self, question: str) -> str:
        """
        Convert natural language question to SQL query.
        
        Args:
            question: Natural language question
            
        Returns:
            SQL query string
        """
        schema_description = self._get_schema_description()
        sql_context = self.sql_helper.build_context(question, self.schema_info)
        
        # Get marketing domain context for better query understanding (DATA-AWARE)
        from src.query_engine.marketing_context import get_marketing_context_for_nl_to_sql
        marketing_context = get_marketing_context_for_nl_to_sql(self.schema_info)
        
        logger.info(f"=== GENERATING SQL FOR QUESTION: {question} ===")
        logger.info(f"Schema info available: {self.schema_info is not None}")
        if self.schema_info:
            logger.info(f"Columns: {self.schema_info.get('columns', [])}")
        logger.info(f"Schema description length: {len(schema_description)} chars")
        logger.info(f"Schema description preview: {schema_description[:300]}...")
        
        prompt = f"""You are a SQL expert specializing in marketing campaign analytics. Convert the following natural language question into a DuckDB SQL query.

{marketing_context}

Database Schema:
{schema_description}

SQL Knowledge & Reference:
{sql_context}

🔴 CRITICAL AGGREGATION RULES - NEVER VIOLATE:

For calculated/rate metrics (CTR, CPC, CPM, CPA, ROAS, Conversion Rate), you MUST:
✓ ALWAYS compute from aggregates: SUM(numerator) / SUM(denominator)
✗ NEVER use AVG() on pre-calculated rate columns

Examples:
- CTR = (SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100
- CPC = SUM(Spend) / NULLIF(SUM(Clicks), 0)
- CPM = (SUM(Spend) / NULLIF(SUM(Impressions), 0)) * 1000
- CPA = SUM(Spend) / NULLIF(SUM(Conversions), 0)
- ROAS = SUM(Revenue) / NULLIF(SUM(Spend), 0)  [or use Conversion_Value if Revenue not available]
- Conversion_Rate = (SUM(Conversions) / NULLIF(SUM(Clicks), 0)) * 100

⏰ TEMPORAL COMPARISON PATTERNS (ANCHOR ON DATA, NOT CURRENT_DATE):

Always anchor relative time windows on the *latest date present in the data*, not on CURRENT_DATE.

🔴 CRITICAL: DATE COLUMN FLEXIBILITY
- The date column may NOT be named "Date"
- Look for columns with these keywords: date, week, week_range, week range, day, month, year, time, period
- Common examples: "Week Range", "Week", "Date Range", "Day", "Month", "Period"
- ALWAYS check the schema for the actual date column name before writing queries
- Use the EXACT column name from the schema (case-sensitive)

1) Find the campaign end date (max_date) from the table first, using a CTE pattern like:

   WITH bounds AS (
       SELECT MAX([actual_date_column_name]) AS max_date
       FROM campaigns
   )
   
   Replace [actual_date_column_name] with the real column name from the schema.

2) Then express natural language time windows relative to bounds.max_date (campaign life):

- "last 2 weeks"      -> [date_col] >= max_date - INTERVAL 14 DAY
- "previous 2 weeks"  -> [date_col] >= max_date - INTERVAL 28 DAY AND [date_col] < max_date - INTERVAL 14 DAY
- "last month"        -> [date_col] >= DATE_TRUNC('month', max_date - INTERVAL 1 MONTH)
- "last 2 months"     -> [date_col] >= max_date - INTERVAL 2 MONTH
- "last 6 months"     -> [date_col] >= max_date - INTERVAL 6 MONTH
- "last 2 years"      -> [date_col] >= max_date - INTERVAL 2 YEAR
- "couple of months"  -> treat as 2 months (use 2 MONTH window)
- "week-over-week"    -> GROUP BY DATE_TRUNC('week', [date_col])
- "month-over-month"  -> GROUP BY DATE_TRUNC('month', [date_col])
- "Q3 vs Q2"          -> use QUARTER([date_col]) or DATE_TRUNC('quarter', [date_col])
- "year-over-year"    -> compare same period across different years using YEAR([date_col])
- "by day"            -> GROUP BY [date_col] (use the actual date column name)
- "by week"           -> GROUP BY [date_col] or DATE_TRUNC('week', [date_col])
- "by month"          -> GROUP BY DATE_TRUNC('month', [date_col])

EXAMPLE: If schema has "Week Range" column and user asks "show total spend by day":
SELECT "Week Range", SUM(Cost) AS Total_Spend
FROM campaigns
GROUP BY "Week Range"
ORDER BY "Week Range"

For comparisons ("last X vs previous X") you should:
- Use a CTE that joins every row with max_date from bounds
- Create a period label using CASE WHEN, for example for last 2 months vs previous 2 months:

   WITH bounds AS (
       SELECT MAX(Date) AS max_date FROM campaigns
   ),
   periods AS (
       SELECT
           c.*,
           CASE
               WHEN Date >= max_date - INTERVAL 2 MONTH
                    THEN 'last_period'
               WHEN Date >= max_date - INTERVAL 4 MONTH
                AND Date <  max_date - INTERVAL 2 MONTH
                    THEN 'previous_period'
               ELSE 'other'
           END AS period
       FROM campaigns c
       CROSS JOIN bounds
   )
   SELECT period, ...
   FROM periods
   WHERE period IN ('last_period', 'previous_period')
   GROUP BY period;

- Calculate metrics separately for each period
- Use CTEs or subqueries for clarity

📊 MULTI-DIMENSIONAL ANALYSIS:

- Channel analysis: GROUP BY Platform or Channel
- Funnel analysis: Calculate conversion rates between stages
- Segment analysis: GROUP BY demographic/audience columns
- Creative analysis: GROUP BY creative_variant, ad_copy, subject_line columns
- Time analysis: GROUP BY hour, day_of_week, or use DATE_TRUNC

🎯 PERFORMANCE ANALYSIS - CRITICAL:

When user asks about "performance", "best performing", "top performing", or "sort by performance", you MUST include ALL applicable KPIs:

✓ Raw Metrics (ALWAYS include):
  - Total_Spend = SUM("Total Spent")
  - Total_Impressions = SUM(Impressions)
  - Total_Clicks = SUM(Clicks)
  - Total_Conversions = SUM("Site Visit") or SUM(Conversions) [if exists]

✓ Calculated KPIs (ALWAYS include all applicable):
  - CTR (Click-Through Rate) = ROUND((SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100, 2)
  - CPC (Cost Per Click) = ROUND(SUM("Total Spent") / NULLIF(SUM(Clicks), 0), 2)
  - CPM (Cost Per Mille) = ROUND((SUM("Total Spent") / NULLIF(SUM(Impressions), 0)) * 1000, 2)
  - CPA (Cost Per Acquisition) = ROUND(SUM("Total Spent") / NULLIF(SUM("Site Visit"), 0), 2) [if conversions exist]
  - Conversion_Rate = ROUND((SUM("Site Visit") / NULLIF(SUM(Clicks), 0)) * 100, 2) [if conversions exist]
  - ROAS (Return on Ad Spend) = ROUND(SUM(Revenue) / NULLIF(SUM("Total Spent"), 0), 2) [if Revenue exists]

✓ ORDER BY: Use the most relevant metric (CTR, ROAS, Conversion_Rate, or CPA depending on context)

❌ NEVER return just the dimension name (Channel, Funnel, etc.) without metrics
❌ NEVER return only one calculated metric - include ALL applicable KPIs

Examples:
1. "which is the best performing channel" should include:
   - Channel
   - Total_Spend, Total_Impressions, Total_Clicks, Total_Conversions
   - CTR, CPC, CPM, CPA, Conversion_Rate, ROAS (if applicable)
   - ORDER BY Conversion_Rate DESC or ROAS DESC (most relevant for "best")
   - LIMIT 1 (if asking for single best)

2. "sort by funnel performance" should include:
   - Funnel
   - All raw metrics + all calculated KPIs
   - ORDER BY the most relevant metric

🎯 ADVANCED PATTERNS:

- ROI calculation: (SUM(Revenue) - SUM(Spend)) / NULLIF(SUM(Spend), 0)
- Budget variance: SUM(Actual_Spend) - SUM(Budgeted_Spend)
- Growth rate: ((current - previous) / NULLIF(previous, 0)) * 100
- Drop-off rate: (stage1_count - stage2_count) / NULLIF(stage1_count, 0) * 100

📝 SQL BEST PRACTICES:

- Use NULLIF to prevent division by zero
- Cast Date columns: CAST(Date AS DATE) or TRY_CAST(Date AS DATE)
- Use CTEs for complex multi-step queries
- Round decimals appropriately: ROUND(value, 2)
- Use descriptive column aliases
- For percentages, multiply by 100
- Column names are case-sensitive
- ⚠️ IMPORTANT: If column names contain underscores (e.g., Ad_Type, Device_Type), use them AS-IS without quotes
- ⚠️ If a column name is a SQL keyword (Type, Order, Group), wrap it in double quotes: "Type"
- Always reference columns exactly as they appear in the schema

🔬 ADVANCED ANALYTICAL PATTERNS:

**Anomaly Detection:**
- Use STDDEV() and AVG() to identify outliers: WHERE metric > AVG(metric) + 2*STDDEV(metric)
- Window functions for moving averages: AVG(metric) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
- Percent change from baseline: ((current - baseline) / NULLIF(baseline, 0)) * 100

**Cohort Analysis:**
- Use DATE_TRUNC to group by acquisition period
- Self-joins or window functions to compare cohorts
- Retention analysis: COUNT(DISTINCT user_id) by time period

**Trend Analysis:**
- Linear regression slope: REGR_SLOPE(y, x) for trend direction
- Moving averages: AVG(metric) OVER (ORDER BY date ROWS BETWEEN n PRECEDING AND CURRENT ROW)
- Growth rate: ((current - previous) / NULLIF(previous, 0)) * 100
- Cumulative metrics: SUM(metric) OVER (ORDER BY date)

**Statistical Analysis:**
- Standard deviation: STDDEV(metric) for volatility
- Variance: VARIANCE(metric)
- Percentiles: PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY metric) for median
- Correlation: CORR(metric1, metric2)

**Efficiency Analysis:**
- Pareto analysis: Use window functions with PERCENT_RANK() or cumulative sums
- Efficiency frontier: Rank by multiple criteria (volume AND efficiency)
- Marginal analysis: Compare incremental performance at different levels

**Segmentation:**
- CASE WHEN for bucketing (high/medium/low performers)
- NTILE(n) for equal-sized segments
- Clustering by multiple dimensions

**Forecasting Patterns:**
- Historical averages with trend adjustment
- Seasonality detection: GROUP BY DAYOFWEEK(Date) or MONTH(Date)
- Extrapolation: Use historical growth rates to project forward

**Multi-Touch Attribution:**
- Use ARRAY_AGG or STRING_AGG to track journey paths
- Window functions to identify first/last touch: FIRST_VALUE(), LAST_VALUE()
- Count touchpoints: COUNT(*) OVER (PARTITION BY user_id)

**Strategic Insights:**
- Scenario analysis: Use CASE WHEN to model different budget levels
- Optimization: Identify top performers with RANK() or ROW_NUMBER()
- Risk analysis: Calculate concentration with cumulative percentages

🔴 CRITICAL VALUE MATCHING RULE:
When filtering by categorical columns (platform, channel, funnel, ad_type, device_type, campaign_name):
- You MUST use ONLY the EXACT values listed in the "IMPORTANT - Actual values in data" section above
- If the user mentions "Google Ads" but the data has "google_ads" or "Google Display Network", use the ACTUAL value from the schema
- If you cannot find a matching value, suggest similar values from the list
- NEVER guess or invent platform/channel names - only use values explicitly shown in the schema
- Platform names are case-sensitive and must match exactly

Question: {question}

SQL Query:"""
        
        logger.info(f"FULL PROMPT LENGTH: {len(prompt)} chars")
        logger.info(f"PROMPT PREVIEW (first 500 chars):\n{prompt[:500]}")
        logger.info(f"PROMPT END (last 200 chars):\n{prompt[-200:]}")
        
        # Try each available model in order
        sql_query = None
        last_error = None
        
        for provider, model_name in self.available_models:
            try:
                logger.info(f"Attempting to use {provider} ({model_name})...")
                
                if provider == 'claude':
                    response = self.anthropic_client.messages.create(
                        model=model_name,
                        max_tokens=1000,
                        temperature=0.1,
                        messages=[{
                            "role": "user",
                            "content": f"You are a SQL expert. Generate ONLY the SQL query, no explanations or markdown.\n\n{prompt}"
                        }]
                    )
                    sql_query = response.content[0].text.strip()
                    self._last_model_used = f"{provider} ({model_name})"
                    logger.info(f"✅ Successfully used {provider}")
                    break
                    
                elif provider == 'gemini':
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        f"You are a SQL expert. Generate ONLY the SQL query, no explanations or markdown.\n\n{prompt}",
                        generation_config=genai.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=1000
                        )
                    )
                    sql_query = response.text.strip()
                    self._last_model_used = f"{provider} ({model_name})"
                    logger.info(f"✅ Successfully used {provider} (FREE)")
                    break
                    
                elif provider == 'openai':
                    response = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a SQL expert. Generate ONLY the SQL query, no explanations or markdown."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=1000
                    )
                    sql_query = response.choices[0].message.content.strip()
                    self._last_model_used = f"{provider} ({model_name})"
                    logger.info(f"✅ Successfully used {provider}")
                    break
                    
                elif provider == 'groq':
                    response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a SQL expert. Generate ONLY the SQL query, no explanations or markdown."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=1000
                    )
                    sql_query = response.choices[0].message.content.strip()
                    self._last_model_used = f"{provider} ({model_name})"
                    logger.info(f"✅ Successfully used {provider} (FREE & FAST)")
                    break
                    
                elif provider == 'deepseek':
                    response = self.deepseek_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": "You are a SQL expert. Generate ONLY the SQL query, no explanations or markdown."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=1000
                    )
                    sql_query = response.choices[0].message.content.strip()
                    self._last_model_used = f"{provider} ({model_name})"
                    logger.info(f"✅ Successfully used {provider} (FREE CODING SPECIALIST)")
                    break
                    
            except Exception as e:
                last_error = e
                logger.warning(f"❌ {provider} failed: {e}")
                continue
        
        if not sql_query:
            logger.error(f"All models failed. Last error: {last_error}")
            raise Exception(f"All LLM providers failed. Last error: {last_error}")
        logger.info(f"RAW LLM RESPONSE: {sql_query}")
        
        # Clean up the query (remove markdown code blocks if present)
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        logger.info(f"AFTER CLEANUP: {sql_query}")
        
        # Sanitize SQL query to fix common issues
        sql_query = self._sanitize_sql(sql_query)
        logger.info(f"AFTER SANITIZE: {sql_query}")
        
        # Validate SQL is not a dummy query
        if sql_query.upper().strip() == "SELECT 1" or not sql_query or len(sql_query) < 10:
            logger.error(f"LLM returned invalid/dummy query: '{sql_query}'")
            logger.error(f"Question was: {question}")
            logger.error(f"Schema had {len(self.schema_info.get('columns', []))} columns")
            raise ValueError(f"Failed to generate valid SQL for question: {question}. Got: {sql_query}")
        
        return sql_query
    
    def _sanitize_sql(self, sql_query: str) -> str:
        """
        Sanitize SQL query to fix common issues.
        
        Args:
            sql_query: Original SQL query
            
        Returns:
            Sanitized SQL query
        """
        import re
        
        # Fix double-quoted identifiers that result from over-escaping
        # Pattern: ""identifier" or ""identifier".something"
        # This happens when LLM generates "Column.2" and we try to quote it again
        sql_query = re.sub(r'""([^"]+)"', r'"\1', sql_query)  # ""Campaign_Name" -> "Campaign_Name
        
        # Check if we need to use quoted column names (spaces in original data)
        # Look at the actual schema to determine the format
        if self.schema_info and 'columns' in self.schema_info:
            columns = self.schema_info['columns']
            
            # If columns have spaces, we need to quote them in SQL
            has_spaces = any(' ' in col for col in columns)
            
            if has_spaces:
                # Replace underscored versions with quoted space versions
                # But only if not already quoted
                patterns = [
                    (r'(?<!")Total_Spent(?!")', '"Total Spent"'),
                    (r'(?<!")Site_Visit(?!")', '"Site Visit"'),
                    (r'(?<!")Ad_Type(?!")', '"Ad Type"'),
                    (r'(?<!")Device_Type(?!")', '"Device Type"'),
                ]
            else:
                # Replace space versions with underscored versions
                patterns = [
                    (r'\bAd Type\b', 'Ad_Type'),
                    (r'\bDevice Type\b', 'Device_Type'),
                    (r'\bTotal Spent\b', 'Total_Spent'),
                    (r'\bSite Visit\b', 'Site_Visit'),
                ]
            
            for pattern, replacement in patterns:
                sql_query = re.sub(pattern, replacement, sql_query, flags=re.IGNORECASE)

            # If the schema has no Revenue column, replace any ROAS expression that
            # references SUM(Revenue) with a NULL placeholder to avoid binder errors.
            if 'Revenue' not in columns:
                sql_query = re.sub(
                    r'ROUND\s*\(\s*SUM\s*\(\s*Revenue\s*\)[^)]*\)\s+AS\s+ROAS',
                    'NULL AS ROAS',
                    sql_query,
                    flags=re.IGNORECASE,
                )
        
        return sql_query
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            DataFrame with query results
        """
        try:
            result = self.conn.execute(sql_query).fetchdf()
            logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a natural language question and get results.
        
        Args:
            question: Natural language question
        
        Returns:
            Dictionary with SQL query, results, and metadata
        """
        import time

        context_package: Optional[Dict[str, Any]] = None

        try:
            start_time = time.time()

            # 1) Generate SQL with normal provider priority
            sql_query = self.generate_sql(question)

            # 2) Execute query
            results = self.execute_query(sql_query)

            context_package = self.sql_helper.get_last_context_package() or {}

            # 3) If no rows returned, optionally try a semantic fallback with DeepSeek
            if results.empty and any(m[0] == 'deepseek' for m in self.available_models):
                logger.warning(
                    "Primary model returned no rows. Attempting DeepSeek fallback for better SQL."
                )
                original_models = list(self.available_models)
                try:
                    # Prioritize DeepSeek for this retry only
                    deepseek_first = [m for m in original_models if m[0] == 'deepseek']
                    others = [m for m in original_models if m[0] != 'deepseek']
                    if deepseek_first:
                        self.available_models = deepseek_first + others
                        fallback_sql = self.generate_sql(question)
                        fallback_results = self.execute_query(fallback_sql)
                        if not fallback_results.empty:
                            logger.info("DeepSeek fallback produced non-empty results. Using fallback SQL.")
                            sql_query = fallback_sql
                            results = fallback_results
                            context_package = self.sql_helper.get_last_context_package() or context_package
                except Exception as fe:
                    logger.warning(f"DeepSeek semantic fallback failed: {fe}")
                finally:
                    # Restore original provider order for future calls
                    self.available_models = original_models

            # 4) Generate answer
            answer = self._generate_answer(question, results)

            execution_time = time.time() - start_time

            return {
                "question": question,
                "sql_query": sql_query,
                "results": results,
                "answer": answer,
                "execution_time": execution_time,
                "model_used": getattr(self, '_last_model_used', 'unknown'),
                "sql_context": context_package,
                "success": True,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                "question": question,
                "sql_query": None,
                "results": None,
                "answer": None,
                "sql_context": context_package if 'context_package' in locals() else self.sql_helper.get_last_context_package(),
                "success": False,
                "error": str(e)
            }

    def _generate_answer(self, question: str, results: pd.DataFrame) -> str:
        """
        Generate strategic insights and recommendations from query results.
        
        Args:
            question: Original question
            results: Query results
            
        Returns:
            Strategic analysis with insights and recommendations
        """
        if results.empty:
            return "No results found for your question."
        
        # Convert results to text summary
        results_text = results.to_string(index=False, max_rows=20)
        
        # Extract date context from the data if available
        date_context = ""
        if self.schema_info:
            # Check for date columns in results
            date_cols = [col for col in results.columns if any(kw in col.lower() for kw in ['date', 'week', 'month', 'year', 'period'])]
            if date_cols:
                for col in date_cols:
                    try:
                        dates = pd.to_datetime(results[col], errors='coerce').dropna()
                        if not dates.empty:
                            min_date = dates.min()
                            max_date = dates.max()
                            date_context = f"\n\nDate Range in Results: {min_date.strftime('%B %Y')} to {max_date.strftime('%B %Y')}"
                            break
                    except:
                        pass
            
            # If no date in results, check original data for context
            if not date_context and hasattr(self, 'conn') and self.conn:
                try:
                    # Get date range from original data
                    date_check = self.conn.execute("SELECT MIN(Date) as min_date, MAX(Date) as max_date FROM campaigns").fetchdf()
                    if not date_check.empty:
                        min_d = pd.to_datetime(date_check['min_date'].iloc[0])
                        max_d = pd.to_datetime(date_check['max_date'].iloc[0])
                        date_context = f"\n\nData covers: {min_d.strftime('%B %d, %Y')} to {max_d.strftime('%B %d, %Y')}"
                except:
                    pass
        
        # Determine if this is an insight or recommendation question
        is_insight_question = any(keyword in question.lower() for keyword in [
            'why', 'what explains', 'root cause', 'underlying', 'story', 'pattern', 
            'hidden', 'surprising', 'counterintuitive', 'narrative', 'drivers'
        ])
        
        is_recommendation_question = any(keyword in question.lower() for keyword in [
            'recommend', 'should we', 'how should', 'what should', 'suggest', 
            'optimize', 'improve', 'action plan', 'strategy', 'roadmap'
        ])
        
        if is_recommendation_question:
            system_prompt = """You are a strategic marketing analyst providing actionable recommendations.

For RECOMMENDATIONS, you MUST:
✓ Be specific and actionable (not vague suggestions)
✓ Quantify expected impact where possible
✓ Consider implementation difficulty and timeline
✓ Assess risks and trade-offs
✓ Prioritize by potential business impact
✓ Provide clear success metrics

Format your recommendation as:
**Recommendation:** [Clear, specific action]
**Rationale:** [Data-driven evidence]
**Expected Impact:** [Quantified outcomes, e.g., "15-20% CPA reduction"]
**Implementation:** [How to execute, timeline]
**Risks:** [What could go wrong]
**Success Metrics:** [How to measure]
**Priority:** [High/Medium/Low]"""
            
            user_prompt = f"""Based on the data below, provide a strategic recommendation.

Question: {question}
{date_context}

Data:
{results_text}

IMPORTANT: If the question mentions a time period, explicitly state the specific dates/months/years in your response.

Provide a structured, actionable recommendation:"""
            max_tokens = 500
            
        elif is_insight_question:
            system_prompt = """You are a strategic marketing analyst uncovering deep insights.

For INSIGHTS, you MUST:
✓ Go beyond surface-level observations
✓ Connect multiple data points into coherent narratives
✓ Identify "so what" implications for business
✓ Distinguish correlation from causation
✓ Provide confidence levels for conclusions
✓ Explain the "why" behind patterns
✓ Compare against benchmarks when relevant

Provide insights that tell a story and reveal the underlying drivers of performance."""
            
            user_prompt = f"""Based on the data below, provide strategic insights that explain the underlying story.

Question: {question}
{date_context}

Data:
{results_text}

IMPORTANT: If the question mentions a time period (like "last month", "this week", etc.), explicitly state the specific dates/months/years the data covers in your response.

Provide deep insights with context and business implications:"""
            max_tokens = 400
            
        else:
            # Standard analytical answer
            system_prompt = "You are a data analyst providing clear, insightful answers with business context. Always include specific date ranges when discussing time-based queries."
            user_prompt = f"""Based on the following query results, provide a clear answer with context.

Question: {question}
{date_context}

Query Results:
{results_text}

IMPORTANT: If the question mentions a time period (like "last month", "this week", "performance of last month", etc.), you MUST explicitly state the specific month and year (e.g., "November 2024") in your response. Never give a response about time periods without specifying the actual dates.

Provide an informative answer with key takeaways:"""
            max_tokens = 300
        
        # Use same fallback system as SQL generation
        for provider, model_name in self.available_models:
            try:
                if provider == 'claude':
                    response = self.anthropic_client.messages.create(
                        model=model_name,
                        max_tokens=max_tokens,
                        temperature=0.7,
                        messages=[{
                            "role": "user",
                            "content": f"{system_prompt}\n\n{user_prompt}"
                        }]
                    )
                    return response.content[0].text.strip()
                    
                elif provider == 'gemini':
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(
                        f"{system_prompt}\n\n{user_prompt}",
                        generation_config=genai.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=max_tokens
                        )
                    )
                    return response.text.strip()
                    
                elif provider == 'openai':
                    response = self.openai_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=max_tokens
                    )
                    return response.choices[0].message.content.strip()
                    
                elif provider == 'groq':
                    response = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=max_tokens
                    )
                    return response.choices[0].message.content.strip()
                    
                elif provider == 'deepseek':
                    response = self.deepseek_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=max_tokens
                    )
                    return response.choices[0].message.content.strip()
                    
            except Exception as e:
                logger.warning(f"Insights generation failed with {provider}: {e}")
                continue
        
        return "Unable to generate insights - all AI providers failed."
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions based on the data schema."""
        return [
            # Temporal Comparisons
            "Compare campaign performance between the last 2 weeks vs. the previous 2 weeks",
            "Show me the week-over-week trend for conversions over the last 2 months",
            "How did our CTR in the last month compare to the month before?",
            "What's the month-over-month growth in leads for the past 6 months?",
            "Compare Q3 2024 vs Q2 2024 performance for ROAS and CPA",
            
            # Channel & Performance Analysis
            "Which marketing channel generated the highest ROI?",
            "Compare the cost per acquisition (CPA) across different channels",
            "Which platform performs best in terms of ROAS? Calculate from total revenue and spend",
            "Show me the top 5 campaigns by conversions with their ROAS",
            
            # Funnel & Conversion Analysis
            "What was the conversion rate at each stage: impressions to clicks to conversions?",
            "Calculate the click-through rate and conversion rate for each platform",
            "Where did we see the highest drop-off in the funnel?",
            
            # Budget & ROI Analysis
            "Calculate the return on ad spend (ROAS) for each campaign",
            "What is the total spend vs total revenue across all campaigns?",
            "Which channel should we invest more in based on ROAS performance?",
            
            # Creative & Timing
            "What were the best performing days for campaign engagement?",
            "Show me performance trends by day of week",
            
            # Comparative Analysis
            "Compare new vs returning customer conversion metrics",
            "How did different audience segments perform in terms of engagement rate?"
        ]
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


class QueryTemplates:
    """Pre-built query templates for common questions."""
    
    @staticmethod
    def get_templates() -> Dict[str, str]:
        """Get dictionary of query templates."""
        return {
            "top_campaigns_by_roas": """
                SELECT Campaign_Name, Platform, ROAS, Spend, Conversions
                FROM campaigns
                ORDER BY ROAS DESC
                LIMIT 10
            """,
            
            "total_spend_by_platform": """
                SELECT Platform, 
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA
                FROM campaigns
                GROUP BY Platform
                ORDER BY Total_Spend DESC
            """,
            
            "campaign_performance_summary": """
                SELECT Campaign_Name,
                       COUNT(DISTINCT Platform) as Platforms,
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA,
                       ROUND((SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100, 2) as CTR
                FROM campaigns
                GROUP BY Campaign_Name
                ORDER BY Total_Spend DESC
            """,
            
            "monthly_trends": """
                SELECT DATE_TRUNC('month', CAST(Date AS DATE)) as Month,
                       SUM(Spend) as Total_Spend,
                       SUM(Conversions) as Total_Conversions,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA
                FROM campaigns
                GROUP BY Month
                ORDER BY Month
            """,
            
            "platform_comparison": """
                SELECT Platform,
                       COUNT(*) as Campaign_Count,
                       SUM(Impressions) as Total_Impressions,
                       SUM(Clicks) as Total_Clicks,
                       ROUND((SUM(Clicks) / NULLIF(SUM(Impressions), 0)) * 100, 2) as CTR,
                       ROUND(SUM(Spend) / NULLIF(SUM(Clicks), 0), 2) as CPC,
                       ROUND((SUM(Spend) / NULLIF(SUM(Impressions), 0)) * 1000, 2) as CPM,
                       SUM(Conversions) as Total_Conversions,
                       SUM(Spend) as Total_Spend,
                       ROUND(SUM(Spend) / NULLIF(SUM(Conversions), 0), 2) as CPA,
                       ROUND(SUM(Revenue) / NULLIF(SUM(Spend), 0), 2) as ROAS
                FROM campaigns
                GROUP BY Platform
                ORDER BY Total_Spend DESC
            """,
            
            "best_worst_performers": """
                (SELECT 'Top 5' as Category, Campaign_Name, Platform, ROAS, Spend
                 FROM campaigns
                 ORDER BY ROAS DESC
                 LIMIT 5)
                UNION ALL
                (SELECT 'Bottom 5' as Category, Campaign_Name, Platform, ROAS, Spend
                 FROM campaigns
                 ORDER BY ROAS ASC
                 LIMIT 5)
            """,
            
            "efficiency_analysis": """
                SELECT Campaign_Name,
                       Platform,
                       Spend,
                       Conversions,
                       CPA,
                       ROAS,
                       CASE 
                           WHEN ROAS >= 4.0 THEN 'Excellent'
                           WHEN ROAS >= 3.0 THEN 'Good'
                           WHEN ROAS >= 2.0 THEN 'Average'
                           ELSE 'Needs Improvement'
                       END as Performance_Category
                FROM campaigns
                ORDER BY ROAS DESC
            """
        }
