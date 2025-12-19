# Using Your Local Template for Automated Reporting

## Quick Start

### Step 1: Prepare Your Template

Add placeholders to your Excel template where you want automated data:

```
Campaign Performance Report
===========================

Report Date: {{Report_Date}}

OVERALL METRICS
---------------
Total Spend: {{Total_Spend}}
Total Revenue: {{Total_Revenue}}
Overall ROAS: {{Overall_ROAS}}

Average CPC: {{Avg_CPC}}
Average CTR: {{Avg_CTR}}%
Conversion Rate: {{Conversion_Rate}}%

BUDGET TRACKING
---------------
Total Budget: {{Budget_Total}}
Budget Spent: {{Budget_Spent}} ({{Budget_Spent_Pct}}%)
Budget Remaining: {{Budget_Remaining}}

TOP CAMPAIGNS
-------------
1. {{Campaign1_Name}}
   Spend: {{Campaign1_Spend}} | ROAS: {{Campaign1_ROAS}}x

2. {{Campaign2_Name}}
   Spend: {{Campaign2_Spend}} | ROAS: {{Campaign2_ROAS}}x
```

### Step 2: Run the Test Script

```bash
# Use your template
python test_reporting_with_template.py --template "C:/path/to/your/template.xlsx"

# With your own data
python test_reporting_with_template.py --template "C:/path/to/your/template.xlsx" --data "C:/path/to/data.csv"

# Specify output location
python test_reporting_with_template.py --template "C:/path/to/your/template.xlsx" --output "reports/my_report.xlsx"
```

### Step 3: Review Output

The script will:
1. ✅ Analyze your template for placeholders
2. ✅ Calculate all KPIs from your data
3. ✅ Replace placeholders with actual values
4. ✅ Add a "Campaign_Data" sheet with detailed metrics
5. ✅ Save the populated report

---

## Available Placeholders

### Overall Metrics
- `{{Total_Spend}}` - Sum of all campaign spend
- `{{Total_Revenue}}` - Sum of all revenue
- `{{Total_Impressions}}` - Total impressions
- `{{Total_Clicks}}` - Total clicks
- `{{Total_Conversions}}` - Total conversions
- `{{Campaign_Count}}` - Number of campaigns

### Calculated KPIs
- `{{Overall_ROAS}}` - Revenue / Spend
- `{{Avg_CPC}}` - Average Cost Per Click
- `{{Avg_CPM}}` - Average Cost Per Mille
- `{{Avg_CPA}}` - Average Cost Per Acquisition
- `{{Avg_CTR}}` - Average Click-Through Rate
- `{{Conversion_Rate}}` - Overall Conversion Rate

### Budget Tracking
- `{{Budget_Total}}` - Total allocated budget
- `{{Budget_Spent}}` - Amount spent so far
- `{{Budget_Remaining}}` - Budget left
- `{{Budget_Spent_Pct}}` - Percentage of budget spent

### Date/Time
- `{{Report_Date}}` - Report generation date (YYYY-MM-DD)
- `{{Report_Month}}` - Current month (e.g., "December 2024")

### Per-Campaign Metrics
For each campaign (1-5):
- `{{Campaign1_Name}}` - Campaign name
- `{{Campaign1_Spend}}` - Campaign spend
- `{{Campaign1_Clicks}}` - Campaign clicks
- `{{Campaign1_Conversions}}` - Campaign conversions
- `{{Campaign1_ROAS}}` - Campaign ROAS
- `{{Campaign1_CPC}}` - Campaign CPC
- `{{Campaign1_CTR}}` - Campaign CTR

(Replace `1` with `2`, `3`, `4`, or `5` for other campaigns)

---

## Example Template Layouts

### Layout 1: Executive Summary

```
┌─────────────────────────────────────────┐
│  CAMPAIGN PERFORMANCE REPORT            │
│  {{Report_Month}}                       │
├─────────────────────────────────────────┤
│                                         │
│  KEY METRICS                            │
│  ────────────                           │
│  Total Investment: {{Total_Spend}}      │
│  Total Revenue: {{Total_Revenue}}       │
│  ROAS: {{Overall_ROAS}}x                │
│                                         │
│  EFFICIENCY                             │
│  ──────────                             │
│  Avg CPC: {{Avg_CPC}}                   │
│  Avg CTR: {{Avg_CTR}}%                  │
│  Conv Rate: {{Conversion_Rate}}%        │
│                                         │
│  BUDGET STATUS                          │
│  ─────────────                          │
│  Spent: {{Budget_Spent_Pct}}%           │
│  Remaining: {{Budget_Remaining}}        │
│                                         │
└─────────────────────────────────────────┘
```

### Layout 2: Campaign Comparison

```
┌──────────────────────────────────────────────────────────┐
│  TOP PERFORMING CAMPAIGNS                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  #1: {{Campaign1_Name}}                                  │
│      Spend: {{Campaign1_Spend}}                          │
│      ROAS: {{Campaign1_ROAS}}x                           │
│      Conversions: {{Campaign1_Conversions}}              │
│                                                          │
│  #2: {{Campaign2_Name}}                                  │
│      Spend: {{Campaign2_Spend}}                          │
│      ROAS: {{Campaign2_ROAS}}x                           │
│      Conversions: {{Campaign2_Conversions}}              │
│                                                          │
│  #3: {{Campaign3_Name}}                                  │
│      Spend: {{Campaign3_Spend}}                          │
│      ROAS: {{Campaign3_ROAS}}x                           │
│      Conversions: {{Campaign3_Conversions}}              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Layout 3: Budget Dashboard

```
┌─────────────────────────────────────────┐
│  BUDGET UTILIZATION                     │
├─────────────────────────────────────────┤
│                                         │
│  Total Budget:     {{Budget_Total}}     │
│  Amount Spent:     {{Budget_Spent}}     │
│  Remaining:        {{Budget_Remaining}} │
│                                         │
│  Utilization:      {{Budget_Spent_Pct}}%│
│                                         │
│  ████████████░░░░░░  ({{Budget_Spent_Pct}}%)│
│                                         │
│  Status: On Track ✓                     │
│                                         │
└─────────────────────────────────────────┘
```

---

## Data Format Requirements

Your campaign data CSV should have these columns:

```csv
Date,Campaign_ID,Campaign_Name,Spend,Impressions,Clicks,Conversions,Revenue
2024-12-04,CAMP001,Q4 Brand Campaign,1500.50,45000,450,25,7500.00
2024-12-04,CAMP002,Holiday Sales,2800.75,68000,820,45,14000.00
```

**Required Columns:**
- `Date` - Campaign date (YYYY-MM-DD)
- `Campaign_ID` - Unique campaign identifier
- `Campaign_Name` - Campaign name
- `Spend` - Amount spent
- `Impressions` - Ad impressions
- `Clicks` - Ad clicks
- `Conversions` - Conversions/leads
- `Revenue` - Revenue generated

---

## Example Commands

### Test with Sample Data
```bash
python test_reporting_with_template.py --template "templates/my_template.xlsx"
```

### Use Your Own Data
```bash
python test_reporting_with_template.py \
  --template "C:/Users/yourname/Documents/report_template.xlsx" \
  --data "C:/Users/yourname/Documents/campaign_data.csv"
```

### Include Budget Tracking
```bash
python test_reporting_with_template.py \
  --template "templates/my_template.xlsx" \
  --budgets "config/campaign_budgets.csv"
```

### Custom Output Location
```bash
python test_reporting_with_template.py \
  --template "templates/my_template.xlsx" \
  --output "reports/weekly_report_2024_12_04.xlsx"
```

---

## What Happens

### 1. Template Analysis
```
🔍 Analyzing your template...
   Template: my_template.xlsx
   Sheets: Summary, Details
   Found: {{Total_Spend}} at Summary!B5
   Found: {{Overall_ROAS}} at Summary!B8
   Found: {{Campaign1_Name}} at Details!A2
   ...
```

### 2. Data Processing
```
📊 Calculating KPIs...
   ✓ Processed 5 campaigns
   
   Campaign Metrics:
   - Q4 Brand Campaign
     Spend: $1,500.50 | ROAS: 5.00x | CTR: 1.00%
     CPC: $3.33 | CPA: $60.00 | Conv Rate: 5.56%
     Budget: $35,426.20 / $50,000.00 (70.9%)
```

### 3. Template Population
```
📝 Populating template...
   ✓ Made 23 replacements
   ✓ Adding Campaign_Data sheet...
   ✓ Saved to: reports/my_template_populated_20241204_160000.xlsx
```

### 4. Final Output
```
✅ Report Generated Successfully!

📊 Summary:
   Template Used: my_template.xlsx
   Campaigns Processed: 5
   Total Spend: $6,901.50
   Total Revenue: $38,900.00
   Overall ROAS: 5.64x

📁 Output: reports/my_template_populated_20241204_160000.xlsx
```

---

## Tips & Best Practices

### 1. Template Design
- ✅ Use clear, descriptive placeholder names
- ✅ Add formatting (colors, borders, fonts) to your template
- ✅ Include charts - they'll be preserved!
- ✅ Use formulas for additional calculations
- ✅ Test with sample data first

### 2. Placeholder Naming
- ✅ Use `{{}}` for best compatibility
- ✅ Be consistent with naming
- ✅ Use underscores instead of spaces
- ✅ Match placeholder names to data columns when possible

### 3. Data Preparation
- ✅ Ensure all required columns are present
- ✅ Use consistent date format (YYYY-MM-DD)
- ✅ Remove any duplicate rows
- ✅ Validate numeric columns are actually numbers

### 4. Testing
- ✅ Start with sample data
- ✅ Verify all placeholders are replaced
- ✅ Check calculations are correct
- ✅ Review the Campaign_Data sheet

---

## Troubleshooting

### Placeholder Not Replaced
**Issue:** `{{Total_Spend}}` still shows in output

**Solutions:**
- Check spelling matches exactly (case-sensitive)
- Ensure placeholder is in `{{}}` format
- Verify data column exists
- Check for extra spaces

### Wrong Values
**Issue:** Numbers don't match expectations

**Solutions:**
- Verify data is for correct date
- Check aggregation logic (sum vs. average)
- Review budget configuration
- Validate source data

### Template Not Found
**Issue:** "Template not found" error

**Solutions:**
- Use full absolute path
- Check file extension (.xlsx)
- Verify file exists at location
- Use quotes around path if it has spaces

---

## Next Steps

1. ✅ Create or modify your template with placeholders
2. ✅ Run the test script with your template
3. ✅ Review the generated report
4. ✅ Adjust placeholders as needed
5. ✅ Integrate with automated daily/weekly reporting
6. ✅ Schedule for automatic generation

---

## Integration with Automated Reporting

Once your template works, integrate it:

```python
from src.reporting.automated_reporter import AutomatedReporter

# Initialize
reporter = AutomatedReporter()
reporter.load_budgets('config/campaign_budgets.csv')

# Generate report
daily_report = reporter.generate_daily_report()

# Use your template
from test_reporting_with_template import populate_template

metrics_df = pd.DataFrame(daily_report['campaigns'])
populate_template(
    'templates/my_template.xlsx',
    mapping,
    'reports/daily_report.xlsx',
    metrics_df
)
```

---

**Questions?** Check the main documentation or run with `--help` flag.
