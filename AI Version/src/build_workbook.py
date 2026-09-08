"""Builds Employee_Insights.xlsx — a multi-sheet summary workbook.
Sheets: KPIs, Department Summary, Job Title Summary, Pay Equity,
Attrition Drivers, Salary Drivers (model), Correlations, Data Dictionary.
Usage: python3 src/build_workbook.py  (run src/analysis.py first)"""

import json
import os

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "assets", "summary.json")))
D = json.load(open(os.path.join(ROOT, "assets", "dashboard_data.json")))
K = S["kpis"]

wb = Workbook()
NAVY, TEAL, LIGHT = "1F3A5F", "2A9D8F", "EEF2F6"
H_FONT = Font(bold=True, color="FFFFFF", size=11)
H_FILL = PatternFill("solid", fgColor=NAVY)
A_FILL = PatternFill("solid", fgColor=LIGHT)
THIN = Border(*[Side(style="thin", color="C9D4E0")] * 4)


def write_sheet(ws, headers, rows, widths=None, title=None):
    r0 = 1
    if title:
        ws.cell(1, 1, title).font = Font(bold=True, size=14, color=NAVY)
        r0 = 3
    for j, h in enumerate(headers, 1):
        c = ws.cell(r0, j, h)
        c.font, c.fill, c.border = H_FONT, H_FILL, THIN
        c.alignment = Alignment(horizontal="center")
    for i, row in enumerate(rows, r0 + 1):
        for j, v in enumerate(row, 1):
            c = ws.cell(i, j, v)
            c.border = THIN
            if i % 2 == 0:
                c.fill = A_FILL
    if widths:
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(r0 + 1, 1)


# ------------------------------------------------------------- KPI sheet
ws = wb.active
ws.title = "KPIs"
kpi_rows = [
    ("Total employees", K["total_employees"], ""),
    ("Departments", 9, "each ≈ 11,000 staff"),
    ("Hire-date range", S["profile"]["hire_date_range"], ""),
    ("Average monthly salary", K["avg_salary"], "USD"),
    ("Median monthly salary", K["median_salary"], "USD"),
    ("Salary std dev", K["salary_std"], "USD"),
    ("Average performance score", K["avg_performance"], "1–5 scale"),
    ("High performers (score 4–5)", K["high_perf_pct"], "%"),
    ("Low performers (score 1–2)", K["low_perf_pct"], "%"),
    ("Attrition rate", K["attrition_rate"], "%"),
    ("Average tenure", K["avg_tenure"], "years"),
    ("Average satisfaction", K["avg_satisfaction"], "1–5 scale"),
    ("Average work hours", K["avg_work_hours"], "hours/week"),
    ("Average overtime", K["avg_overtime"], "hours/period"),
    ("Average sick days", K["avg_sick_days"], "days/period"),
    ("Average training hours", K["avg_training"], "hours"),
    ("Average projects handled", K["avg_projects"], "projects"),
    ("Average team size", K["avg_team_size"], "people"),
    ("Employees promoted", K["pct_promoted"], "% with ≥1 promotion"),
    ("Average age", K["avg_age"], "years"),
]
write_sheet(ws, ["Metric", "Value", "Unit / note"], kpi_rows, [30, 16, 26],
            "Company KPIs — 100,000 employees")

# -------------------------------------------------- department summary
ws = wb.create_sheet("Department Summary")
ds = S["tables"]["dept_summary"]
rows = [(d, v["headcount"], round(v["avg_salary"]), round(v["avg_perf"], 2),
         round(v["attrition"] * 100, 2), round(v["avg_satisfaction"], 2),
         round(v["avg_tenure"], 1)) for d, v in ds.items()]
rows.sort(key=lambda r: -r[1])
write_sheet(ws, ["Department", "Headcount", "Avg Salary ($)", "Avg Performance",
                 "Attrition (%)", "Avg Satisfaction", "Avg Tenure (y)"],
            rows, [18, 11, 14, 15, 13, 15, 14], "Department-level summary")

# ----------------------------------------------------- job title summary
ws = wb.create_sheet("Job Title Summary")
ts = S["tables"]["title_salary"]
rows = [(t, round(v["salary"]), round(v["perf"], 2), round(v["attrition"] * 100, 2))
        for t, v in ts.items()]
rows.sort(key=lambda r: -r[1])
write_sheet(ws, ["Job Title", "Avg Salary ($)", "Avg Performance", "Attrition (%)"],
            rows, [16, 14, 15, 13], "Job-title summary")

# ------------------------------------------------------------ pay equity
ws = wb.create_sheet("Pay Equity")
rows = [(t, g) for t, g in S["pay_equity"]["within_title_gaps"]]
rows.append(("COMPANY-WIDE (raw)", S["pay_equity"]["raw_gap"]))
write_sheet(ws, ["Job Title", "Male − Female ($/month)"], rows, [26, 26],
            "Gender pay gap — all within ±$25 (no gap to remediate)")

# ------------------------------------------------------ attrition drivers
ws = wb.create_sheet("Attrition Drivers")
rows = []
for dim, vals in S["attrition_drivers"].items():
    for bucket, rate in vals.items():
        rows.append((dim, bucket, rate))
write_sheet(ws, ["Dimension", "Bucket", "Attrition (%)"], rows, [24, 16, 14],
            "Attrition by segment — company rate 10.01%; all buckets 9.5–10.3%")

# --------------------------------------------------------- model results
ws = wb.create_sheet("Models")
rows = [("Salary OLS", "R²", S["salary_model"]["r2"]),
        ("Salary OLS", "MAE ($)", S["salary_model"]["mae"]),
        ("Attrition Logistic Regression", "Accuracy", S["attrition_model"]["accuracy"]),
        ("Attrition Logistic Regression", "ROC AUC", S["attrition_model"]["auc"]),
        ("Attrition Random Forest", "Accuracy", S["rf_model"]["accuracy"]),
        ("Attrition Random Forest", "ROC AUC", S["rf_model"]["auc"]),
        ("", "", ""),
        ("Salary driver", "Effect ($/mo)", "")]
for k, v in S["salary_model"]["top_positive"].items():
    rows.append(("Salary driver", f"+{v:,.0f}", k))
for k, v in S["salary_model"]["top_negative"].items():
    rows.append(("Salary driver", f"{v:,.0f}", k))
rows.append(("NOTE", "Attrition AUC ≈ 0.49 ⇒ no predictive signal in data", ""))
write_sheet(ws, ["Model / item", "Metric / effect", "Detail"], rows, [30, 44, 34],
            "Predictive model results")

# ---------------------------------------------------------- correlations
ws = wb.create_sheet("Key Correlations")
rows = []
for target, d in S["correlations"].items():
    for feat, r in d.items():
        rows.append((target, feat, r))
write_sheet(ws, ["Target variable", "Feature", "|Pearson r|"], rows, [30, 32, 12],
            "Top correlations — only Salary↔Performance (0.51) is meaningful")

# -------------------------------------------------------- data dictionary
ws = wb.create_sheet("Data Dictionary")
dd = [("Employee_ID", "int", "1 – 100,000 (unique)"),
      ("Department", "categorical", "9 values: Customer Support, Engineering, Finance, HR, IT, Legal, Marketing, Operations, Sales"),
      ("Gender", "categorical", "Male, Female, Other"),
      ("Age", "int", "22 – 60"),
      ("Job_Title", "categorical", "Analyst, Consultant, Developer, Engineer, Manager, Specialist, Technician"),
      ("Hire_Date", "datetime", "2014-09 → 2024-09"),
      ("Years_At_Company", "int", "0 – 10"),
      ("Education_Level", "categorical", "High School, Bachelor, Master, PhD"),
      ("Performance_Score", "int", "1 – 5"),
      ("Monthly_Salary", "float", "3,850 – 9,000 USD"),
      ("Work_Hours_Per_Week", "int", "30 – 60"),
      ("Projects_Handled", "int", "0 – 49"),
      ("Overtime_Hours", "int", "0 – 29"),
      ("Sick_Days", "int", "0 – 14"),
      ("Remote_Work_Frequency", "int", "0, 25, 50, 75, 100 (%)"),
      ("Team_Size", "int", "1 – 19"),
      ("Training_Hours", "int", "0 – 99"),
      ("Promotions", "int", "0 – 2"),
      ("Employee_Satisfaction_Score", "float", "1.0 – 5.0"),
      ("Resigned", "bool", "True = left company (10.01%)")]
write_sheet(ws, ["Field", "Type", "Range / values"], dd, [30, 14, 74],
            "Data dictionary — Extended_Employee_Performance_and_Productivity_Data.csv")

out = os.path.join(ROOT, "Employee_Insights.xlsx")
wb.save(out)
print("wrote", out)
