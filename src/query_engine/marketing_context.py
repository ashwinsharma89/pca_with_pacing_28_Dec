"""
Marketing Domain Knowledge for NL-to-SQL Query Enhancement

Provides marketing context, metrics definitions, and business rules to improve
natural language to SQL query generation.
"""

MARKETING_GLOSSARY = """
# Marketing Analytics Glossary

## Key Metrics
- **ROAS (Return on Ad Spend)**: Revenue generated per dollar spent. Formula: Revenue / Spend
- **CPA (Cost Per Acquisition)**: Cost to acquire one customer. Formula: Spend / Conversions
- **CTR (Click-Through Rate)**: Percentage of impressions that result in clicks. Formula: (Clicks / Impressions) * 100
- **CPC (Cost Per Click)**: Average cost for each click. Formula: Spend / Clicks
- **CPM (Cost Per Mille)**: Cost per 1000 impressions. Formula: (Spend / Impressions) * 1000
- **Conversion Rate**: Percentage of clicks that convert. Formula: (Conversions / Clicks) * 100
- **CAC (Customer Acquisition Cost)**: Same as CPA
- **LTV (Lifetime Value)**: Total revenue expected from a customer over their lifetime

## Marketing Funnel Stages
- **Awareness**: Top of funnel (TOFU) - Building brand awareness, reaching new audiences
- **Consideration**: Middle of funnel (MOFU) - Engaging interested prospects, nurturing leads
- **Conversion**: Bottom of funnel (BOFU) - Converting prospects to customers

## Channels
- **SEM (Search Engine Marketing)**: Paid search ads (Google Ads, Bing Ads)
- **SOC (Social)**: Social media advertising (Facebook, Instagram, LinkedIn, Twitter, TikTok)
- **DIS (Display)**: Banner ads, programmatic advertising
- **VID (Video)**: YouTube, video advertising
- **EMAIL**: Email marketing campaigns

## Common Questions & Intent
- "Best/Top performing" = High ROAS or high conversions
- "Worst/Underperforming" = Low ROAS or high CPA
- "Wasting money" = High spend with low conversions
- "Funnel" = Analysis by funnel_stage (Awareness → Consideration → Conversion)
- "Trend" = Time-series analysis, usually monthly
- "Comparison" = Side-by-side metrics across platforms/channels

## Business Rules
- Exclude campaigns with spend < $100 for "top/worst" analysis (avoid noise)
- Default date range: Last 30 days if not specified
- "Recent" = Last 7 days
- "This month" = Current calendar month
- "Last month" = Previous calendar month
"""

QUERY_CONTEXT = """
# Query Generation Guidelines

## When analyzing performance:
- "Best" campaigns = ORDER BY roas DESC or conversions DESC
- "Worst" campaigns = ORDER BY roas ASC or cpa DESC (with minimum spend filter)
- Always include LIMIT for top/bottom queries (default: 10)

## Funnel Analysis:
- Group by funnel_stage column
- Order: Awareness → Consideration → Conversion
- Calculate drop-off rates between stages

## Time-based queries:
- Use DATE_TRUNC('month', date) for monthly trends
- Use DATE_TRUNC('week', date) for weekly trends
- Always ORDER BY date/month DESC for trends

## Filters:
- Exclude NULL or 'Unknown' values in funnel_stage for funnel analysis
- For "wasting money" queries: spend > 5000 AND conversions < 100
- For platform/channel comparison: GROUP BY platform or channel

## Metrics to include:
- Always calculate CTR, CPC, CPA when relevant columns exist
- Include conversion_rate for funnel analysis
- Show both absolute numbers (spend, conversions) and rates (CTR, ROAS)
"""

def get_marketing_context_for_nl_to_sql(schema_info: dict = None) -> str:
    """
    Get marketing domain context to enhance NL-to-SQL query generation.
    Now DATA-AWARE - analyzes actual schema to provide relevant context.
    
    Args:
        schema_info: Schema information from the query engine
        
    Returns:
        Formatted context string to add to NL-to-SQL prompt
    """
    # Base marketing glossary (always included)
    base_glossary = """
# Marketing Analytics Glossary

## Key Metrics
- **ROAS (Return on Ad Spend)**: Revenue generated per dollar spent. Formula: Revenue / Spend
- **CPA (Cost Per Acquisition)**: Cost to acquire one customer. Formula: Spend / Conversions
- **CTR (Click-Through Rate)**: Percentage of impressions that result in clicks. Formula: (Clicks / Impressions) * 100
- **CPC (Cost Per Click)**: Average cost for each click. Formula: Spend / Clicks
- **CPM (Cost Per Mille)**: Cost per 1000 impressions. Formula: (Spend / Impressions) * 1000
- **Conversion Rate**: Percentage of clicks that convert. Formula: (Conversions / Clicks) * 100
- **CAC (Customer Acquisition Cost)**: Same as CPA
- **LTV (Lifetime Value)**: Total revenue expected from a customer over their lifetime

## Marketing Funnel Stages
- **Awareness / TOFU (Top of Funnel)**: Building brand awareness, reaching new audiences
- **Consideration / MOFU (Middle of Funnel)**: Engaging interested prospects, nurturing leads
- **Conversion / BOFU (Bottom of Funnel)**: Converting prospects to customers

## Common Channels
- **SEM (Search Engine Marketing)**: Paid search ads (Google Ads, Bing Ads)
- **SOC (Social)**: Social media advertising (Facebook, Instagram, LinkedIn, Twitter, TikTok)
- **DIS (Display)**: Banner ads, programmatic advertising
- **VID (Video)**: YouTube, video advertising
- **EMAIL**: Email marketing campaigns
"""

    # If no schema info, return base glossary only
    if not schema_info:
        return f"{base_glossary}\n\n{QUERY_CONTEXT}"
    
    # Analyze actual data to provide relevant context
    columns = schema_info.get('columns', [])
    sample_data = schema_info.get('sample_data', [])
    
    # Build data-specific context
    data_context = "\n## YOUR DATA CONTEXT\n"
    
    # 1. Identify available metrics
    available_metrics = []
    metric_mapping = {
        'spend': ['spend', 'cost', 'total_spent', 'budget'],
        'impressions': ['impressions', 'views', 'reach'],
        'clicks': ['clicks', 'link_clicks'],
        'conversions': ['conversions', 'site_visit', 'purchases', 'leads'],
        'revenue': ['revenue', 'conversion_value', 'sales'],
        'roas': ['roas', 'return_on_ad_spend']
    }
    
    for metric_type, possible_names in metric_mapping.items():
        for col in columns:
            if any(name in col.lower() for name in possible_names):
                available_metrics.append(f"- **{metric_type.upper()}**: Use column `{col}`")
                break
    
    if available_metrics:
        data_context += "\n**Available Metrics in Your Data**:\n" + "\n".join(available_metrics) + "\n"
    
    # 2. Identify dimensions
    dimension_cols = []
    dimension_keywords = ['platform', 'channel', 'campaign', 'funnel', 'stage', 'device', 'ad_type', 'audience']
    for col in columns:
        if any(kw in col.lower() for kw in dimension_keywords):
            dimension_cols.append(col)
    
    if dimension_cols:
        data_context += f"\n**Available Dimensions**: {', '.join([f'`{col}`' for col in dimension_cols])}\n"
    
    # 3. Identify funnel stages if available
    funnel_col = next((col for col in columns if 'funnel' in col.lower() or 'stage' in col.lower()), None)
    if funnel_col and sample_data:
        funnel_values = set()
        for row in sample_data:
            val = row.get(funnel_col)
            if val and val != 'Unknown':
                funnel_values.add(val)
        
        if funnel_values:
            data_context += f"\n**Funnel Stages in Your Data**: {', '.join(sorted(funnel_values))}\n"
            data_context += f"- Use column `{funnel_col}` for funnel analysis\n"
    
    # 4. Identify platforms/channels
    platform_col = next((col for col in columns if 'platform' in col.lower()), None)
    if platform_col and sample_data:
        platforms = set()
        for row in sample_data:
            val = row.get(platform_col)
            if val:
                platforms.add(val)
        
        if platforms:
            data_context += f"\n**Platforms in Your Data**: {', '.join(sorted(platforms))}\n"
            data_context += "- Use these EXACT platform names in queries\n"
    
    channel_col = next((col for col in columns if 'channel' in col.lower()), None)
    if channel_col and sample_data:
        channels = set()
        for row in sample_data:
            val = row.get(channel_col)
            if val:
                channels.add(val)
        
        if channels:
            data_context += f"\n**Channels in Your Data**: {', '.join(sorted(channels))}\n"
            data_context += "- Use these EXACT channel names in queries\n"
    
    # 5. Date range context
    date_col = next((col for col in columns if any(kw in col.lower() for kw in ['date', 'week', 'month', 'period'])), None)
    if date_col:
        data_context += f"\n**Time Column**: Use `{date_col}` for date-based queries\n"
    
    # Combine everything
    smart_intent_guide = """
## 🧠 INTELLIGENT QUERY UNDERSTANDING (Steve Jobs Level)

**Think like a user, not a database**. Understand INTENT, not just keywords.

### Smart Intent-to-Column Mapping
When user mentions these concepts, find the CLOSEST matching column:
- **"device/mobile/desktop/tablet"** → device_type, device, device_name, platform_type
- **"funnel/stage/TOFU/MOFU/BOFU"** → funnel_stage, stage, marketing_stage
- **"campaign/ad"** → campaign_name, campaign_id, ad_name
- **"platform/network"** → platform, ad_platform, network
- **"channel/medium"** → channel, marketing_channel, medium
- **"time/date/trend"** → date, week, month, period

### Time Period Intelligence
When user asks about time comparisons, understand these patterns:
- **"last month vs this month"** → Filter by current month and previous month, compare metrics
- **"period over period" / "vs previous period"** → Compare current period to equivalent previous period
- **"week over week" / "WoW"** → Compare this week to last week
- **"month over month" / "MoM"** → Compare this month to last month
- **"year over year" / "YoY"** → Compare this year to last year
- **"last 7 days vs previous 7 days"** → Two 7-day windows for comparison
- **"Q1 vs Q2"** → Quarter comparison
- **"compare last 3 months"** → Show each of last 3 months side by side

**How to handle period comparisons**:
1. Identify the time column (date, week, month, period)
2. Determine the two periods to compare
3. Use CASE statements or CTEs to separate periods
4. Calculate metrics for each period
5. Show side-by-side comparison with % change

### Intelligent Behavior
1. **Match semantically** - Find closest column even if names don't match exactly
2. **Understand "compare by X"** - Group by the dimension X and show key metrics
3. **Smart defaults** - "performance" = spend + conversions + CTR + ROAS
4. **Flexible** - If exact column missing, use next best alternative
5. **Explain** - If can't match, tell user what IS available
6. **Time-aware** - Recognize period comparisons and generate appropriate date filters

### Edge Case Handling (Production-Ready)

**Missing Data**:
- If device_type column doesn't exist → Explain "Your data doesn't have device information. Try: 'compare by platform' or 'compare by channel'"
- If funnel_stage column doesn't exist → Suggest "Try analyzing by platform, channel, or campaign instead"
- If date column doesn't exist → Explain "Time-based analysis not available. Try: 'compare platforms' or 'top campaigns'"

**Ambiguous Queries**:
- "show performance" (too vague) → Ask "Performance by what? Try: 'performance by platform', 'performance by channel', or 'top performing campaigns'"
- "compare" (no dimension) → Suggest "Compare what? Try: 'compare platforms', 'compare channels', or 'compare last month vs this month'"

**Invalid Time Periods**:
- "last month" when data only has current month → Explain "Only current month data available. Showing current month performance instead"
- "Q1 vs Q2" when data only has Q1 → Show Q1 data and explain Q2 not available
- Future dates requested → Explain "Future data not available. Showing latest available data"

**Empty Results**:
- Query returns 0 rows → Explain why (e.g., "No campaigns match these criteria. Try broader filters or different time period")
- All values are NULL → Explain "Data incomplete for this metric. Try different metrics like spend or impressions"

**Data Quality Issues**:
- Many NULL/Unknown values → Filter them out automatically and mention in response
- Outliers (e.g., ROAS > 1000) → Include but flag as potential data quality issue
- Zero spend campaigns → Exclude from ROAS/CPA calculations to avoid division by zero

**Fallback Strategies**:
1. **Column not found** → Search for similar column names, suggest alternatives
2. **No data for period** → Expand date range or suggest available periods
3. **Metric can't be calculated** → Explain why and suggest alternative metrics
4. **Too many results** → Automatically add LIMIT and offer to show more
5. **Complex query fails** → Simplify and retry with basic version

**User-Friendly Responses**:
- Always explain what you did and why
- If you made assumptions, state them clearly
- Provide actionable next steps
- Show what data IS available, not just what's missing
"""
    
    return f"""
{base_glossary}

{data_context}

{smart_intent_guide}

{QUERY_CONTEXT}

IMPORTANT: Use this marketing knowledge to:
1. **Understand intent, not just keywords** - Be Steve Jobs level intuitive
2. **Match semantically** - Find CLOSEST column to user's intent
3. **Be flexible** - Work with what's available, don't fail on exact matches
4. **Think holistically** - Consider full question context
5. Use EXACT column names from available dimensions
"""


def get_error_context(error_type: str, details: dict) -> str:
    """
    Generate helpful, context-aware error messages.
    
    Args:
        error_type: Type of error (e.g., 'no_data', 'invalid_column', 'sql_error')
        details: Error details
        
    Returns:
        User-friendly error message with suggestions
    """
    if error_type == 'no_data':
        return """
No data found matching your query. 

**Suggestions**:
- Try a broader date range
- Check if the platform/channel name is correct
- Try one of the suggested questions below
"""
    
    elif error_type == 'invalid_column':
        available_cols = details.get('available_columns', [])
        requested_col = details.get('requested_column', '')
        return f"""
Column '{requested_col}' not found in the data.

**Available columns**: {', '.join(available_cols)}

**Tip**: Try asking about platforms, channels, spend, conversions, or ROAS.
"""
    
    elif error_type == 'sql_error':
        return """
I had trouble understanding your question.

**Try asking**:
- "Show funnel analysis"
- "Which platform has the best ROAS?"
- "Show me top performing campaigns"
- "Compare channels"
"""
    
    elif error_type == 'timeout':
        return """
Your query is taking longer than expected.

**This might help**:
- Try a shorter date range
- Ask about specific platforms or channels
- Use one of the suggested questions for faster results
"""
    
    else:
        return "Something went wrong. Please try rephrasing your question or use one of the suggested questions."
