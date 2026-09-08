"""Builds report.pdf — a full analytical report using ReportLab Platypus.
Usage: python3 src/build_report.py  (run src/analysis.py first)"""

import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)
from PIL import Image as PILImage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "assets", "summary.json")))
D = json.load(open(os.path.join(ROOT, "assets", "dashboard_data.json")))
K = S["kpis"]

NAVY = colors.HexColor("#1f3a5f")
TEAL = colors.HexColor("#2a9d8f")
CORAL = colors.HexColor("#e76f51")
GOLD = colors.HexColor("#e9c46a")
SLATE = colors.HexColor("#57606a")
LIGHT = colors.HexColor("#eef2f6")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=17, textColor=NAVY,
                    spaceBefore=18, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, textColor=TEAL,
                    spaceBefore=12, spaceAfter=6)
BODY = ParagraphStyle("Body", parent=ss["BodyText"], fontSize=9.6, leading=14.2,
                      alignment=TA_JUSTIFY, spaceAfter=7)
BULLET = ParagraphStyle("Bullet", parent=BODY, leftIndent=14, bulletIndent=4,
                        spaceAfter=4)
NOTE = ParagraphStyle("Note", parent=BODY, fontSize=8.4, textColor=SLATE)


def img(name, width=168):
    path = os.path.join(ROOT, "charts", name)
    w, h = PILImage.open(path).size
    return Image(path, width=width * mm, height=width * mm * h / w)


def header_footer(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8.5)
        canvas.drawString(15 * mm, A4[1] - 8 * mm, "Employee Performance & Productivity — Analytics Report")
        canvas.drawRightString(A4[0] - 15 * mm, A4[1] - 8 * mm, "2026")
    canvas.setFillColor(SLATE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(15 * mm, 8 * mm, "Generated from Extended_Employee_Performance_and_Productivity_Data.csv (100,000 × 20)")
    canvas.drawRightString(A4[0] - 15 * mm, 8 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(os.path.join(ROOT, "report.pdf"), pagesize=A4,
                        leftMargin=15 * mm, rightMargin=15 * mm,
                        topMargin=18 * mm, bottomMargin=15 * mm,
                        title="Employee Performance & Productivity Analytics Report",
                        author="Analytics Pipeline")

E = []  # elements

# ------------------------------------------------------------ cover page
E += [Spacer(1, 42 * mm),
      Paragraph("Employee Performance &amp; Productivity",
                ParagraphStyle("T", fontSize=30, textColor=NAVY, leading=36, fontName="Helvetica-Bold")),
      Paragraph("Full Workforce Analytics Report",
                ParagraphStyle("T2", fontSize=19, textColor=TEAL, leading=24, fontName="Helvetica")),
      Spacer(1, 10 * mm),
      Paragraph("100,000 employees &nbsp;·&nbsp; 9 departments &nbsp;·&nbsp; 7 job titles &nbsp;·&nbsp; hiring window 2014–2024",
                ParagraphStyle("T3", fontSize=11, textColor=SLATE)),
      Spacer(1, 16 * mm)]

kpi_rows = [
    ["Avg monthly salary", f"${K['avg_salary']:,.0f}", "Attrition rate", f"{K['attrition_rate']:.1f}%"],
    ["Avg performance", f"{K['avg_performance']:.2f} / 5", "High performers (4–5)", f"{K['high_perf_pct']:.1f}%"],
    ["Avg satisfaction", f"{K['avg_satisfaction']:.2f} / 5", "Avg tenure", f"{K['avg_tenure']:.1f} years"],
    ["Avg work hours", f"{K['avg_work_hours']:.1f} / week", "Avg training", f"{K['avg_training']:.0f} h"],
]
t = Table(kpi_rows, colWidths=[42 * mm, 34 * mm, 42 * mm, 34 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
    ("TEXTCOLOR", (0, 0), (0, -1), NAVY), ("TEXTCOLOR", (2, 0), (2, -1), NAVY),
    ("FONT", (1, 0), (1, -1), "Helvetica-Bold", 10),
    ("FONT", (3, 0), (3, -1), "Helvetica-Bold", 10),
    ("FONT", (0, 0), (0, -1), "Helvetica", 8.5),
    ("FONT", (2, 0), (2, -1), "Helvetica", 8.5),
    ("GRID", (0, 0), (-1, -1), 0.6, colors.white),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
E += [t, Spacer(1, 26 * mm),
      Paragraph("Prepared by the automated analytics pipeline · September 2026",
                ParagraphStyle("F", fontSize=9.5, textColor=SLATE)),
      PageBreak()]

# ------------------------------------------------------- exec summary
E.append(Paragraph("Executive Summary", H1))
E.append(Paragraph(
    "This report analyses the full employee performance and productivity dataset — 100,000 employee "
    "records across 9 departments and 7 job titles, covering hiring dates from September 2014 to "
    "September 2024. The data is complete (no missing values, no duplicate IDs) and supports "
    "descriptive analysis, correlation studies, equity testing and predictive modelling.", BODY))
E.append(Paragraph("Headline findings", H2))
bullets = [
    f"<b>Pay equity is healthy.</b> Women earn on average ${abs(S['pay_equity']['raw_gap']):.2f} "
    f"<i>more</i> than men company-wide, and the within-title gap never exceeds ±$25 "
    f"(&lt; 0.4% of pay). No corrective compensation action is indicated.",
    "<b>Salary is almost perfectly explained by two factors.</b> A linear model on job title and "
    f"performance score reaches R² = {S['salary_model']['r2']:.3f} (MAE ≈ ${S['salary_model']['mae']:.0f}). "
    "Engineers and Managers carry a ≈ +$2,600/month title premium and every performance point adds "
    "≈ +$493/month. Department, education and gender contribute almost nothing.",
    f"<b>Attrition is 10.0% and statistically unpredictable from this data.</b> Logistic regression and "
    f"random forest both reach AUC ≈ {S['attrition_model']['auc']:.2f} — coin-flip discrimination — and "
    "every demographic, engagement and workload segment sits within 9.5–10.3% of the company rate. "
    "Departures in this dataset carry no observable signal.",
    "<b>Engagement levers show no measurable effect.</b> Training hours, overtime, sick days, team size "
    "and remote-work frequency correlate with performance and satisfaction at |r| &lt; 0.01. Only salary "
    f"tracks performance (r = {S['correlations']['performance_top']['Monthly_Salary']:.2f}), which is a "
    "definitional link (pay formula), not a causal one.",
    "<b>Departments are near-identical.</b> Headcount, salary, performance, satisfaction and attrition "
    "vary by less than 1.5% across all nine departments — an unusual uniformity.",
    "<b>Data quality caveat.</b> The independence of features, the near-perfect salary formula and the "
    "absence of any attrition signal strongly suggest a synthetically generated dataset. Findings should "
    "be read as a validated analysis methodology rather than organizational truth.",
]
for b in bullets:
    E.append(Paragraph(b, BULLET, bulletText="•"))
E.append(Spacer(1, 4 * mm))
E.append(Paragraph(
    "Recommendations focus on (1) preserving the current pay-equity position, (2) auditing the "
    "performance-measurement process given its central role in pay, and (3) improving attrition data "
    "capture — exit interviews and engagement surveys — because the current fields cannot identify "
    "flight-risk employees. Section 8 details the full recommendation set.", BODY))
E.append(PageBreak())

# ------------------------------------------------------- data overview
E.append(Paragraph("1. Data Overview &amp; Quality", H1))
p = S["profile"]
rows = [["Property", "Value"],
        ["Records", f"{p['rows']:,} employees"],
        ["Fields", f"{p['columns']} (13 numeric, 5 categorical, 1 boolean, 1 date)"],
        ["Missing values", f"{p['missing_cells']}"],
        ["Duplicate Employee IDs", f"{p['duplicate_ids']}"],
        ["Departments", f"{p['departments']} (each ≈ 11,000 staff)"],
        ["Job titles", f"{p['departments'] and 7} — Analyst, Consultant, Developer, Engineer, Manager, Specialist, Technician"],
        ["Hire-date range", p["hire_date_range"]]]
t = Table(rows, colWidths=[45 * mm, 125 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9.5),
    ("FONT", (0, 1), (0, -1), "Helvetica-Bold", 9), ("FONT", (1, 1), (1, -1), "Helvetica", 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d4e0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
E += [t, Spacer(1, 4 * mm),
      Paragraph("No cleaning was required: zero nulls, zero duplicate IDs, all ranges plausible "
                "(age 22–60, tenure 0–10 years, salary $3,850–$9,000, work hours 30–60). "
                "'Other' gender values are reported as Non-binary/Other throughout.", BODY),
      img("07_age_tenure.png", 160),
      Spacer(1, 2 * mm),
      img("16_hiring_trend.png", 150),
      PageBreak()]

# ---------------------------------------------------- workforce composition
E.append(Paragraph("2. Workforce Composition", H1))
E.append(Paragraph(
    "The workforce is evenly spread: every department employs between 10,956 (Engineering) and 11,216 "
    "(Marketing) staff. The gender mix is roughly balanced and education is dominated by Bachelor-level "
    "staff, with meaningful Master/PhD representation. Hiring volume is steady at 9,000–11,000 hires "
    "per year across the decade covered.", BODY))
E.append(img("01_department_headcount.png", 158))
E.append(Spacer(1, 3 * mm))
E.append(img("02_gender_education.png", 158))
E.append(PageBreak())

# ----------------------------------------------------------- compensation
E.append(Paragraph("3. Compensation Analysis", H1))
E.append(Paragraph(
    f"Monthly salary averages ${K['avg_salary']:,.0f} (median ${K['median_salary']:,.0f}, σ = ${K['salary_std']:,.0f}) "
    "and is roughly normally distributed. Contrary to typical HR data, salary does not vary meaningfully by "
    "department ($6,378–$6,417) or education level. What does move pay is job title and performance score — "
    "confirmed by the regression in section 3.3.", BODY))
E.append(img("08_salary_distribution.png", 158))
E.append(Spacer(1, 3 * mm))
E.append(img("03_salary_by_department.png", 152))
E.append(PageBreak())

E.append(Paragraph("3.1 Salary by education", H2))
E.append(img("09_salary_by_education.png", 150))
E.append(Paragraph(
    "Education premiums are small: PhD and Master holders earn only modestly above Bachelor graduates, "
    "and High-School-educated staff are not far behind. In this workforce, role and measured performance "
    "dominate compensation decisions.", BODY))
E.append(Paragraph("3.2 Gender pay equity", H2))
E.append(img("10_gender_pay_equity.png", 158))
gap_rows = [["Job title", "Male − Female ($/mo)"]] + \
           [[t_, f"{g:+,.1f}"] for t_, g in S["pay_equity"]["within_title_gaps"]]
t = Table(gap_rows, colWidths=[45 * mm, 45 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
    ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d4e0")),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
E += [Spacer(1, 2 * mm), KeepTogether([t, Spacer(1, 3 * mm),
      Paragraph("Company-wide, women earn $4.50/month more than men on average; within every job title "
                "the largest absolute gap is $23.10 (Consultant). At an average salary of $6,403 these "
                "differences are economically negligible and consistent with sampling noise. "
                "<b>Conclusion: no gender pay gap to remediate; maintain quarterly monitoring.</b>", BODY)])]
E.append(PageBreak())

E.append(Paragraph("3.3 What actually drives salary — regression model", H2))
m = S["salary_model"]
E.append(Paragraph(
    f"An OLS regression on all 13 numeric fields plus department, gender, job title and education "
    f"(one-hot encoded, 80/20 split) achieves <b>R² = {m['r2']:.4f}</b> with MAE = ${m['mae']:.0f} on the "
    "held-out 20% — pay is essentially a formula:", BODY))
drv = [["Term", "Effect ($/month)"],
       ["Job title: Engineer", "+2,600"],
       ["Job title: Manager", "+2,599"],
       ["Job title: Consultant", "+1,951"],
       ["Job title: Developer", "+1,300"],
       ["Job title: Specialist", "+650"],
       ["Job title: Technician", "−648"],
       ["Performance score (per point)", "+493"],
       ["Every other term (dept, gender, education, age, tenure…)", "≈ 0 (|β| < $3)"]]
t = Table(drv, colWidths=[105 * mm, 45 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d4e0")),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
E += [t, Spacer(1, 3 * mm),
      Paragraph("<b>Interpretation:</b> compensation governance is transparent and rule-based — a "
                "positive property for fairness — but it also means performance measurement quality "
                "directly determines $493/month per point (up to $1,972 between score 1 and 5). "
                "Any bias or noise in performance ratings propagates directly into pay.", BODY),
      PageBreak()]

# ------------------------------------------------------------ performance
E.append(Paragraph("4. Performance Analysis", H1))
E.append(Paragraph(
    f"Performance (1–5) averages {K['avg_performance']:.2f} with a near-uniform distribution: "
    f"{K['high_perf_pct']:.1f}% of staff score 4–5 and {K['low_perf_pct']:.1f}% score 1–2. Departmental "
    "averages range only from 2.98 (Finance, Marketing) to 3.02 (Engineering).", BODY))
E.append(img("04_performance_by_department.png", 150))
E.append(Spacer(1, 3 * mm))
E.append(img("11_performance_mix.png", 158))
E.append(PageBreak())

E.append(Paragraph("4.1 Performance vs satisfaction and training", H2))
E.append(img("19_satisfaction.png", 158))
E.append(Paragraph(
    "Satisfaction (avg 3.00) is statistically independent of performance (r = 0.002) and of attrition. "
    "Training hours — 0 to 99, averaging 50 — show no relationship with performance: every training "
    "bucket averages 2.99–3.01. In a functioning HR system one would expect at least a mild positive "
    "gradient; its total absence is a red flag about how these fields were produced.", BODY))
E.append(img("15_tenure_training.png", 158))
E.append(PageBreak())

# ------------------------------------------------------------- attrition
E.append(Paragraph("5. Attrition Analysis", H1))
E.append(Paragraph(
    f"Overall attrition is {K['attrition_rate']:.1f}% (10,010 leavers). The rate is remarkably flat: "
    "the widest departmental spread is Finance 10.5% vs Engineering/IT 9.6%.", BODY))
E.append(img("05_attrition_by_department.png", 152))
E.append(Spacer(1, 3 * mm))
E.append(img("12_attrition_drivers.png", 168))
E.append(PageBreak())

E.append(Paragraph("5.1 Predictive modelling — a negative result", H2))
am, rm = S["attrition_model"], S["rf_model"]
E.append(Paragraph(
    f"Two models were trained on an 80/20 stratified split: logistic regression "
    f"(accuracy {am['accuracy']:.3f}, AUC {am['auc']:.3f}) and a random forest "
    f"(accuracy {rm['accuracy']:.3f}, AUC {rm['auc']:.3f}). The accuracies look respectable only because "
    "the majority class ('stayed') is 90% of the data — always predicting 'stayed' scores identically. "
    "The AUC values, which measure genuine discrimination, are ≈ 0.5: <b>no better than a coin flip</b>. "
    "Every coefficient is within ±0.033 and every feature importance below 0.002.", BODY))
E.append(img("17_attrition_model.png", 152))
E.append(Spacer(1, 3 * mm))
E.append(img("18_rf_importance.png", 148))
E.append(PageBreak())

E.append(Paragraph(
    "<b>What this means practically:</b> attrition in this dataset is independent of age, tenure, pay, "
    "performance, satisfaction, workload, remote policy and promotions. Consequently, no data-driven "
    "flight-risk model can be built from the current fields. If this were live organizational data, the "
    "correct response would be: (a) audit whether the 'Resigned' flag is populated correctly, "
    "(b) enrich the record with exit-interview themes, manager ratings and compensation history, and "
    "(c) re-run this pipeline quarterly — it is fully automated.", BODY))
E.append(Spacer(1, 2 * mm))

# ---------------------------------------------------------- work & balance
E.append(Paragraph("6. Workload &amp; Work-Life Balance", H1))
E.append(Paragraph(
    f"Staff average {K['avg_work_hours']:.0f} hours/week (range 30–60) with {K['avg_overtime']:.1f} overtime "
    f"hours and {K['avg_sick_days']:.1f} sick days. Neither workload nor remote-work frequency shows any "
    "association with performance, satisfaction, or attrition — including the often-debated question of "
    "remote work: attrition is 9.5%–10.3% across all five remote-frequency levels.", BODY))
E.append(img("13_work_life.png", 162))
E.append(Spacer(1, 3 * mm))
E.append(img("14_remote_work.png", 162))
E.append(PageBreak())

E.append(Paragraph("6.1 Team size &amp; sick days", H2))
E.append(img("20_team_sick.png", 162))
E.append(Paragraph(
    "Team size (1–19) and sick days (0–14) are equally inert — performance stays at 3.00 and attrition "
    "at ~10% across every bucket. The overtime/sick-day relationship that burnout literature predicts is "
    "absent here.", BODY))

# ------------------------------------------------------------ correlations
E.append(Paragraph("7. Correlation Structure", H1))
E.append(img("06_correlation_heatmap.png", 150))
E.append(Paragraph(
    "The correlation matrix contains exactly one meaningful off-diagonal value: salary ↔ performance "
    f"(r = {S['correlations']['performance_top']['Monthly_Salary']:.2f}), explained by the pay formula in "
    "section 3.3. All remaining 90 pairwise correlations have |r| &lt; 0.01 — a signature of independently "
    "generated variables and the strongest evidence that this dataset is synthetic.", BODY))
E.append(PageBreak())

# -------------------------------------------------------- recommendations
E.append(Paragraph("8. Recommendations", H1))
recs = [
    ("Protect the pay-equity position",
     "Gaps are under 0.4% at every level. Institutionalize the quarterly gap audit (script provided in "
     "src/analysis.py) so any future drift is caught early."),
    ("Audit performance measurement",
     "Performance scores drive $493/month per point but show no correlation with training, workload, "
     "projects or tenure — and are uniformly distributed. Verify ratings are evidence-based before "
     "expanding their weight in pay."),
    ("Fix attrition data capture",
     "Attrition is unpredictable from current fields (AUC 0.49). Validate the Resigned flag, add "
     "exit-interview categories, manager relationship scores and comp-history, then re-train."),
    ("Don't over-invest in unproven levers",
     "Training hours, overtime caps and remote-work policies show zero measured effect on outcomes in "
     "this data. Run controlled pilots with clear metrics rather than blanket programs."),
    ("Use the pipeline as a standing monitor",
     "The full analysis (EDA → charts → models → dashboard → report → deck) rebuilds in under a minute "
     "with two commands; schedule it against production extracts to keep leadership reporting current."),
]
for i, (title, txt) in enumerate(recs, 1):
    E.append(Paragraph(f"<b>{i}. {title}.</b> {txt}", BULLET))
E.append(Spacer(1, 4 * mm))

# --------------------------------------------------------------- appendix
E.append(Paragraph("Appendix A — Methodology", H1))
E.append(Paragraph(
    "Pipeline: pandas 2.2 for loading/EDA, matplotlib/seaborn for 20 charts, scikit-learn 1.6 for "
    "models. Attrition models: LogisticRegression (C=0.5, standardized features, max_iter=2000) and "
    "RandomForestClassifier (250 trees, depth 8) on 17 features (13 numeric + 4 one-hot categoricals), "
    "80/20 stratified split, random_state=42; metrics: accuracy, ROC AUC. Salary model: OLS on the same "
    "feature matrix minus salary itself; metrics: R², MAE. Correlations: Pearson. All code deterministic.", BODY))
E.append(Paragraph("Appendix B — Data dictionary", H1))
dd = [["Field", "Type", "Range / values"],
      ["Employee_ID", "int", "1 – 100,000 (unique)"],
      ["Department", "cat", "9 values (IT, Finance, HR, …)"],
      ["Gender", "cat", "Male, Female, Other"],
      ["Age", "int", "22 – 60"],
      ["Job_Title", "cat", "7 values (Analyst … Technician)"],
      ["Hire_Date", "date", "2014-09 – 2024-09"],
      ["Years_At_Company", "int", "0 – 10"],
      ["Education_Level", "cat", "High School, Bachelor, Master, PhD"],
      ["Performance_Score", "int", "1 – 5"],
      ["Monthly_Salary", "float", "$3,850 – $9,000"],
      ["Work_Hours_Per_Week", "int", "30 – 60"],
      ["Projects_Handled", "int", "0 – 49"],
      ["Overtime_Hours", "int", "0 – 29"],
      ["Sick_Days", "int", "0 – 14"],
      ["Remote_Work_Frequency", "int", "0, 25, 50, 75, 100 (%)"],
      ["Team_Size", "int", "1 – 19"],
      ["Training_Hours", "int", "0 – 99"],
      ["Promotions", "int", "0 – 2"],
      ["Employee_Satisfaction_Score", "float", "1.0 – 5.0"],
      ["Resigned", "bool", "True 10.01% / False 89.99%"]]
t = Table(dd, colWidths=[58 * mm, 22 * mm, 78 * mm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.5),
    ("FONT", (0, 1), (-1, -1), "Helvetica", 8.2),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d4e0")),
    ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
E.append(t)

doc.build(E, onFirstPage=header_footer, onLaterPages=header_footer)
print("wrote report.pdf")
