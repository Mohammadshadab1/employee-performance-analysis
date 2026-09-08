"""Builds presentation.pptx — 16:9 executive deck via python-pptx.
Usage: python3 src/build_pptx.py  (run src/analysis.py first)"""

import json
import os

from PIL import Image as PILImage
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "assets", "summary.json")))
K = S["kpis"]

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
NAVY2 = RGBColor(0x16, 0x2B, 0x47)
TEAL = RGBColor(0x2A, 0x9D, 0x8F)
CORAL = RGBColor(0xE7, 0x6F, 0x51)
GOLD = RGBColor(0xE9, 0xC4, 0x6A)
SLATE = RGBColor(0x57, 0x60, 0x6A)
LIGHT = RGBColor(0xEE, 0xF2, 0xF6)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x2D, 0x33, 0x39)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
PAGE = [0]


def new_slide(dark=False):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY2 if dark else WHITE
    PAGE[0] += 1
    if not dark:
        foot = s.shapes.add_textbox(Inches(0.45), Inches(7.08), Inches(12.4), Inches(0.35))
        p = foot.text_frame.paragraphs[0]
        p.text = "Employee Performance & Productivity Analytics  ·  100,000 employees  ·  2026"
        p.font.size = Pt(9)
        p.font.color.rgb = SLATE
        num = s.shapes.add_textbox(Inches(12.55), Inches(7.08), Inches(0.6), Inches(0.35))
        np_ = num.text_frame.paragraphs[0]
        np_.text = str(PAGE[0])
        np_.font.size = Pt(9)
        np_.font.color.rgb = SLATE
        np_.alignment = PP_ALIGN.RIGHT
    return s


def title_bar(s, title, sub=None):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.16))
    bar.fill.solid(); bar.fill.fore_color.rgb = TEAL; bar.line.fill.background()
    tb = s.shapes.add_textbox(Inches(0.45), Inches(0.30), Inches(12.4), Inches(0.75))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title
    p.font.size = Pt(27); p.font.bold = True; p.font.color.rgb = NAVY
    if sub:
        p2 = tf.add_paragraph(); p2.text = sub
        p2.font.size = Pt(12.5); p2.font.color.rgb = SLATE


def pic(s, name, left, top, width):
    path = os.path.join(ROOT, "charts", name)
    w, h = PILImage.open(path).size
    return s.shapes.add_picture(path, Inches(left), Inches(top), Inches(width),
                                Inches(width * h / w))


def bullets(s, items, left, top, width, height, size=13.5, dark=False):
    tb = s.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = it; p.font.size = Pt(size); p.space_after = Pt(9)
        p.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1) if dark else DARK
    return tb


def card(s, value, label, left, top, w, h, color):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = LIGHT; sh.line.color.rgb = color; sh.line.width = Pt(1.4)
    sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = value
    p.font.size = Pt(21); p.font.bold = True; p.font.color.rgb = color; p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph(); p2.text = label
    p2.font.size = Pt(9.5); p2.font.color.rgb = SLATE; p2.alignment = PP_ALIGN.CENTER
    return sh


# ---------------------------------------------------------- 1 title slide
s = new_slide(dark=True)
strip = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(2.62), prs.slide_width, Inches(0.06))
strip.fill.solid(); strip.fill.fore_color.rgb = TEAL; strip.line.fill.background()
tb = s.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(11.5), Inches(1.1))
p = tb.text_frame.paragraphs[0]
p.text = "Employee Performance & Productivity"
p.font.size = Pt(44); p.font.bold = True; p.font.color.rgb = WHITE
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.85), Inches(11.5), Inches(0.6))
p = tb.text_frame.paragraphs[0]
p.text = "Full Workforce Analytics — Findings, Models & Recommendations"
p.font.size = Pt(20); p.font.color.rgb = GOLD
tb = s.shapes.add_textbox(Inches(0.9), Inches(5.9), Inches(11.5), Inches(0.9))
tf = tb.text_frame
p = tf.paragraphs[0]
p.text = "100,000 employees   ·   9 departments   ·   7 job titles   ·   hires 2014 – 2024"
p.font.size = Pt(14); p.font.color.rgb = RGBColor(0x9C, 0xB3, 0xC9)
p2 = tf.add_paragraph()
p2.text = "Automated analytics pipeline  ·  September 2026"
p2.font.size = Pt(12); p2.font.color.rgb = RGBColor(0x7A, 0x8F, 0xA5)

# ------------------------------------------------------------ 2 agenda
s = new_slide()
title_bar(s, "Agenda")
items = [
    ("1", "Executive summary & KPIs"), ("2", "Workforce composition"),
    ("3", "Compensation & pay equity"), ("4", "Performance analysis"),
    ("5", "Attrition & predictive models"), ("6", "Workload, remote work & balance"),
    ("7", "Key takeaways & recommendations"), ("8", "Methodology"),
]
for i, (n, t) in enumerate(items):
    col, row = i % 2, i // 2
    left, top = 0.7 + col * 6.2, 1.5 + row * 1.35
    c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(0.55), Inches(0.55))
    c.fill.solid(); c.fill.fore_color.rgb = NAVY; c.line.fill.background(); c.shadow.inherit = False
    c.text_frame.paragraphs[0].text = n
    c.text_frame.paragraphs[0].font.size = Pt(16)
    c.text_frame.paragraphs[0].font.bold = True
    c.text_frame.paragraphs[0].font.color.rgb = WHITE
    c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    tb = s.shapes.add_textbox(Inches(left + 0.8), Inches(top + 0.05), Inches(5.1), Inches(0.6))
    p = tb.text_frame.paragraphs[0]; p.text = t
    p.font.size = Pt(17); p.font.color.rgb = DARK; p.font.bold = True

# ------------------------------------------------- 3 executive summary
s = new_slide()
title_bar(s, "Executive Summary", "Six numbers and one surprising negative result")
cards = [
    (f"${K['avg_salary']:,.0f}", "avg monthly salary", TEAL),
    (f"{K['avg_performance']:.2f}/5", "avg performance", NAVY),
    (f"{K['attrition_rate']:.1f}%", "attrition rate", CORAL),
    (f"{K['avg_satisfaction']:.2f}/5", "avg satisfaction", GOLD),
    (f"{K['avg_tenure']:.1f} yrs", "avg tenure", TEAL),
    (f"{K['avg_work_hours']:.0f} hrs", "avg work week", NAVY),
]
for i, (v, l, c) in enumerate(cards):
    card(s, v, l, 0.55 + i * 2.11, 1.42, 1.93, 1.0, c)
bullets(s, [
    "✓  Pay equity is healthy — women earn $4.50/mo more on average; within-title gaps ≤ ±$25 (<0.4%).",
    "✓  Salary is a formula: job-title premium (±$2,600) + $493 per performance point — model R² = 0.99.",
    "✗  Attrition (10.0%) is statistically unpredictable — both ML models score AUC ≈ 0.49 (coin flip); every segment sits within 9.5–10.3%.",
    "✗  Engagement levers (training, overtime, remote work, team size) show zero measured effect: |r| < 0.01 vs performance & satisfaction.",
    "⚑  Departments are near-identical on every metric (salary spread $39, attrition spread 0.9 pt) — consistent with synthetic data.",
], 0.55, 2.75, 12.2, 4.1, size=14.5)

# ------------------------------------------------- 4 workforce overview
s = new_slide()
title_bar(s, "Workforce Composition", "Evenly balanced across departments, gender and education")
pic(s, "01_department_headcount.png", 0.5, 1.55, 6.1)
pic(s, "02_gender_education.png", 6.9, 1.9, 6.0)
bullets(s, [
    "All 9 departments employ 10,956–11,216 staff (11% each).",
    "Education skews to Bachelor; ~9,300 hires/year over the decade.",
], 0.6, 5.7, 12.1, 1.2, size=13)

# ------------------------------------------------- 5 hiring & demographics
s = new_slide()
title_bar(s, "Hiring Trends & Age Profile", "Steady hiring 2014–2024; age peaks in the 40s")
pic(s, "16_hiring_trend.png", 0.5, 1.6, 6.05)
pic(s, "07_age_tenure.png", 6.85, 2.05, 6.0)
bullets(s, ["Average age 41 · average tenure 4.5 years — a mature, stable workforce profile."],
        0.6, 5.9, 12.1, 0.8, size=13)

# ------------------------------------------------- 6 compensation
s = new_slide()
title_bar(s, "Compensation Overview", f"Mean ${K['avg_salary']:,.0f} · median ${K['median_salary']:,.0f} · σ ${K['salary_std']:,.0f}")
pic(s, "08_salary_distribution.png", 0.5, 1.55, 6.1)
pic(s, "03_salary_by_department.png", 6.9, 1.6, 6.0)
bullets(s, [
    "Near-normal salary distribution, $3,850–$9,000.",
    "Departments differ by just $39/month on average — pay is not department-driven.",
], 0.6, 5.75, 12.1, 1.1, size=13)

# ------------------------------------------------- 7 salary by education + equity
s = new_slide()
title_bar(s, "Education & Gender Pay Equity", "Small education premiums · no gender gap to remediate")
pic(s, "09_salary_by_education.png", 0.5, 1.55, 5.6)
pic(s, "10_gender_pay_equity.png", 6.35, 1.55, 6.55)
bullets(s, [
    "Company-wide: women +$4.50/mo vs men. Largest within-title gap: Consultant +$23 (0.3%).",
    "Verdict: pay equity is healthy — institutionalize quarterly monitoring.",
], 0.6, 5.85, 12.1, 1.1, size=13)

# ------------------------------------------------- 8 salary drivers model
s = new_slide()
title_bar(s, "What Drives Salary — OLS Model", "R² = 0.991 · MAE = $95 on 20% hold-out — pay is essentially a formula")
rows = [
    ("Job title: Engineer", "+$2,600 /mo", TEAL),
    ("Job title: Manager", "+$2,599 /mo", TEAL),
    ("Job title: Consultant", "+$1,951 /mo", TEAL),
    ("Job title: Developer", "+$1,300 /mo", TEAL),
    ("Job title: Specialist", "+$650 /mo", TEAL),
    ("Job title: Technician", "−$648 /mo", CORAL),
    ("Performance score, per point", "+$493 /mo", NAVY),
    ("Dept, gender, education, age, tenure…", "≈ $0  (|β| < $3)", SLATE),
]
for i, (lbl, val, c) in enumerate(rows):
    top = 1.62 + i * 0.56
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(top), Inches(7.4), Inches(0.48))
    sh.fill.solid(); sh.fill.fore_color.rgb = LIGHT; sh.line.fill.background(); sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]
    r1 = p.add_run(); r1.text = lbl + "    "
    r1.font.size = Pt(13.5); r1.font.color.rgb = DARK
    r2 = p.add_run(); r2.text = val
    r2.font.size = Pt(13.5); r2.font.bold = True; r2.font.color.rgb = c
bullets(s, [
    "Pay governance is transparent and rule-based — good for fairness.",
    "But performance ratings now directly move pay by up to $1,972/mo (score 1→5) — rating quality is a compensation-control issue.",
    "Score 1–5 maps to ≈ $4,430–$6,400/mo for a Specialist; titles shift the whole curve.",
], 8.45, 1.8, 4.35, 4.6, size=13.5)

# ------------------------------------------------- 9 performance
s = new_slide()
title_bar(s, "Performance Analysis", "Uniform 1–5 distribution · department averages 2.98 – 3.02")
pic(s, "04_performance_by_department.png", 0.5, 1.55, 6.0)
pic(s, "11_performance_mix.png", 6.8, 1.6, 6.1)
bullets(s, [
    "39.9% high performers (4–5) vs 40.1% low (1–2) — a perfectly symmetric spread, unusual for real ratings.",
], 0.6, 5.9, 12.1, 0.8, size=13)

# ------------------------------------------------- 10 performance vs satisfaction/training
s = new_slide()
title_bar(s, "Satisfaction & Training vs Performance", "No gradient anywhere — a red flag about measurement")
pic(s, "19_satisfaction.png", 0.5, 1.55, 6.2)
pic(s, "15_tenure_training.png", 6.95, 1.75, 5.95)
bullets(s, [
    "Satisfaction ⊥ performance (r = 0.002) and ⊥ attrition; training hours (0–99) don't move performance at all.",
], 0.6, 5.95, 12.1, 0.8, size=13)

# ------------------------------------------------- 11 attrition overview
s = new_slide()
title_bar(s, "Attrition Overview", "10.01% resigned (10,010) — remarkably flat across the organization")
pic(s, "05_attrition_by_department.png", 0.5, 1.55, 6.1)
pic(s, "12_attrition_drivers.png", 6.9, 1.5, 6.05)
bullets(s, [
    "Widest department spread: Finance 10.5% vs Engineering/IT 9.6% — well within noise.",
], 0.6, 6.0, 12.1, 0.8, size=13)

# ------------------------------------------------- 12 attrition models
s = new_slide()
title_bar(s, "Predicting Attrition — An Honest Negative Result", "Both models discriminate no better than a coin flip")
pic(s, "18_rf_importance.png", 0.5, 1.6, 5.6)
for i, (v, l, c) in enumerate([
        ("0.49", "Logistic AUC", CORAL), ("0.49", "Random Forest AUC", CORAL),
        ("0.90", "Accuracy = majority-class baseline", SLATE)]):
    card(s, v, l, 6.5 + (i % 2) * 3.25, 1.75 + (i // 2) * 1.5, 3.0, 1.25, c)
bullets(s, [
    "All coefficients within ±0.033; all feature importances < 0.002.",
    "Every segment (satisfaction, performance, tenure, remote, overtime) sits within 9.5–10.3% of the 10.0% rate.",
    "⇒ No flight-risk model is buildable from current fields.",
    "⇒ Action: audit the Resigned flag, capture exit-interview themes & manager ratings, then re-run this pipeline.",
], 6.5, 3.45, 6.3, 3.2, size=13.5)

# ------------------------------------------------- 13 work-life balance
s = new_slide()
title_bar(s, "Workload, Remote Work & Balance", "45h weeks · 14.5h overtime — and no measurable cost or benefit")
pic(s, "13_work_life.png", 0.5, 1.55, 6.2)
pic(s, "14_remote_work.png", 6.95, 1.85, 5.95)
bullets(s, [
    "Attrition is 9.5–10.3% at every remote-work level; overtime and sick days show no burnout signal.",
], 0.6, 6.0, 12.1, 0.8, size=13)

# ------------------------------------------------- 14 takeaways
s = new_slide()
title_bar(s, "Key Takeaways & Recommendations")
recs = [
    ("1", "Protect pay equity", "Gaps < 0.4% everywhere. Automate the quarterly audit (already scripted).", TEAL),
    ("2", "Audit performance measurement", "Scores drive $493/mo per point yet correlate with nothing — verify they are evidence-based.", NAVY),
    ("3", "Fix attrition data capture", "AUC 0.49 means leavers are invisible. Validate the flag; add exit themes & manager scores.", CORAL),
    ("4", "Pilot, don't blanket-invest", "Training/overtime/remote levers show zero effect — test with controlled pilots.", GOLD),
    ("5", "Automate the monitor", "The pipeline rebuilds everything (charts → dashboard → report → deck) in < 1 min. Schedule it.", TEAL),
]
for i, (n, t, d, c) in enumerate(recs):
    top = 1.55 + i * 1.06
    cshape = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), Inches(top + 0.08), Inches(0.5), Inches(0.5))
    cshape.fill.solid(); cshape.fill.fore_color.rgb = c; cshape.line.fill.background(); cshape.shadow.inherit = False
    cshape.text_frame.paragraphs[0].text = n
    cshape.text_frame.paragraphs[0].font.size = Pt(15)
    cshape.text_frame.paragraphs[0].font.bold = True
    cshape.text_frame.paragraphs[0].font.color.rgb = WHITE
    cshape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    tb = s.shapes.add_textbox(Inches(1.45), Inches(top), Inches(11.3), Inches(0.95))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = t
    p.font.size = Pt(15.5); p.font.bold = True; p.font.color.rgb = NAVY
    p2 = tf.add_paragraph(); p2.text = d
    p2.font.size = Pt(11.5); p2.font.color.rgb = SLATE

# ------------------------------------------------- 15 methodology
s = new_slide(dark=True)
title_bar_made = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, Inches(0.16))
title_bar_made.fill.solid(); title_bar_made.fill.fore_color.rgb = TEAL; title_bar_made.line.fill.background()
tb = s.shapes.add_textbox(Inches(0.6), Inches(0.4), Inches(12), Inches(0.7))
p = tb.text_frame.paragraphs[0]; p.text = "Methodology & Reproducibility"
p.font.size = Pt(26); p.font.bold = True; p.font.color.rgb = WHITE
bullets(s, [
    "Data: 100,000 × 20 CSV — zero nulls, zero duplicate IDs, no cleaning required.",
    "EDA: pandas 2.2 · 20 publication charts in matplotlib/seaborn · Pearson correlations.",
    "Models: scikit-learn 1.6 — LogisticRegression (C=0.5, scaled) & RandomForest (250 trees, depth 8) for attrition; OLS for salary. 80/20 stratified split, seed 42.",
    "Deliverables generated by one pipeline: charts/, dashboard.html (offline, Chart.js inlined), report.pdf (16 pp), presentation.pptx, insights workbook (xlsx), README for GitHub.",
    "Rebuild: python3 src/analysis.py → build_dashboard.py → build_report.py → build_pptx.py → build_workbook.py",
    "Caveat: feature independence + near-perfect salary formula indicate synthetic data — treat results as a validated methodology demo.",
], 0.6, 1.5, 12.1, 5.2, size=14.5, dark=True)

prs.save(os.path.join(ROOT, "presentation.pptx"))
print("wrote presentation.pptx with", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
