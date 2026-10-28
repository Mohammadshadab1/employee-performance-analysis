![Employee Performance & Productivity Analytics — Mohammad Shadab, Data Analyst](Banner/banner.jpeg)

# Employee Performance & Productivity Analytics

### 📊 100,000 employees · 9 departments · 7 job titles · hires 2014 → 2024

_What a decade of employee records reveals about pay, performance and attrition — and the HR myths the data dismantles._

[![Python](https://img.shields.io/badge/Python-pandas%20·%20scikit--learn-3776AB?logo=python&logoColor=white)](Notebook)
[![SQL](https://img.shields.io/badge/SQL-MySQL%208%20·%2024%20queries-4479A1?logo=mysql&logoColor=white)](SQL)
[![Power BI](https://img.shields.io/badge/Power%20BI-4--tab%20dashboard-F2C811?logo=powerbi&logoColor=black)](Power%20BI%20pbix)
[![Excel](https://img.shields.io/badge/Excel-SQL%20outputs%20·%20CSV-217346?logo=microsoftexcel&logoColor=white)](SQL%20Outputs)
[![Report](https://img.shields.io/badge/Report-13--page%20PDF-f28c5b)](Employee%20Report)
[![CI](https://img.shields.io/badge/CI-SQL%20%2B%20report%20rebuild-2A9D8F)](.github/workflows/sql-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ 30-second summary (for reviewers)

| | |
| --- | --- |
| **What this is** | An end-to-end people-analytics project on a 100,000-row HR extract: a SQL warehouse layer → Python EDA → predictive models → Power BI + reporting → an audit trail of every number. |
| **Stack** | `MySQL 8` · `Python` (pandas, scikit-learn, matplotlib) · `Power BI` · `Excel/CSV` · `ReportLab` |
| **My role** | Everything — schema design, 24 analytical SQL queries, data-quality suite, EDA, modelling, visualisation, the 13-page report and the pipeline that rebuilds it. |
| **The insight** | Pay is a **formula** (job title + rating, R² = 0.991); attrition is **statistically unpredictable** (ROC AUC 0.49); and the only "big" trend in the data — a 31% hiring collapse in 2024 — turned out to be a **partial-year artefact I caught and corrected**. |
| **Where to look first** | [`SQL/`](SQL) (queries + QA suite) · [`Employee Report/Employee_Analytics_Report.pdf`](Employee%20Report/Employee_Analytics_Report.pdf) (13 pp) · [`Modelling/`](Modelling) (model results) |

---

## 🎯 Headline Findings

| # | Finding | Evidence |
| --- | --- | --- |
| 1️⃣ | **Job title is the only real pay lever** | Technician **$4,545** → Engineer **$7,799** per month — a **72%** gap |
| 2️⃣ | **Education barely affects pay** | PhD **$6,431.55** vs Bachelor **$6,398.42** → **0.52%** (≈ $1/day) |
| 3️⃣ | **Gender pay equity is achieved** | Male $6,400.48 · Female $6,404.99 · Other $6,414.77 → **0.2%**; within title × tenure band every gap ≤ 0.9% |
| 4️⃣ | **Tenure is not priced** | Average salary **$6,390 → $6,420** between year 1 and year 9 (0.5% spread) |
| 5️⃣ | **Performance ratings carry no information** | **20,120 / 20,013 / 19,999 / 19,940 / 19,928** employees at scores 1–5 — a flat line, not a curve |
| 6️⃣ | **Training does not move performance** | 49.28–49.70 training hours at *every* rating; average rating 2.99–3.01 in every training tier |
| 7️⃣ | **Promotions are equally flat** | 1.00 average promotions at every rating; 66.4–67.1% "promoted" in every training tier |
| 8️⃣ | **Satisfaction does not predict attrition** | Stayed **3.00** vs Resigned **2.99** (both SD ≈ 1.15) — no signal |
| 9️⃣ | **Attrition is a 10.01% constant** | 10,010 resignations, **95% CI 9.82–10.20**; departments 9.56%–10.54% and **25 of 26 segments are statistically indistinguishable** from the company rate (z-test) |
| 🔟 | **Only meaningful correlation** | Performance ↔ Salary **r = 0.51** — every other relationship ≈ 0.00 |
| 1️⃣1️⃣ | **Pay is literally a formula** | OLS on title + performance: **R² = 0.991**, **+$493/month per rating point**; pay range inside *every* job title is exactly **36.4%** of its minimum; **5,673 employees sit on the $9,000 ceiling** |
| 1️⃣2️⃣ | **🆕 The "2024 hiring cliff" does not exist** | 2024 holds only 8 complete months; on a complete-month basis hiring is **850.6 hires/month vs 831.1 in 2023 (+2.4%)** — my own earlier "-31%" headline was a partial-year artefact |

---

## 🗄 SQL Analytics Layer

```
SQL/
├── 01_setup_and_load.sql        # schema, constraints, indexes + bulk load (LOAD DATA / pandas)
├── 02_analytics_queries.sql     # 24 business queries in 7 sections — every one annotated
├── 03_qa_checks.sql             # 6 integrity & validity checks with PASS/FAIL verdicts
├── run_queries.py               # executes the pack in DuckDB, rewrites SQL Outputs/, --check mode
└── load_data_to_mysql.ipynb     # notebook loader (credentials via env vars, no hard-coded secrets)

SQL Outputs/                     # 32 committed CSVs — one per query + 6 QA files
```

**Table design:** snake_case columns, `employee_id` PRIMARY KEY, `DECIMAL(10,2)` money, `CHECK` constraints on rating/satisfaction/remote/salary ranges, a **generated `resignation_status`** column (the CSV's boolean `resigned` → 'Resigned'/'Stayed' in one place), and indexes on the three columns the segmentation queries touch.

**Query coverage** — 7 sections, each written as *business question → method → the CSV it produces*:

| Section | Queries | Examples |
| --- | --- | --- |
| Workforce structure | 01–04 | headcount distribution, gender × dept × title, education mix, baseline + salary percentiles |
| Attrition | 05–08 | overall rate **with 95% CI**, department rate **with z-score vs company**, tenure cohorts, satisfaction comparison |
| Compensation & equity | 09–13 | gender gap **controlled for title × tenure band**, tie-aware top earners, education premium index, underpaid top performers, burnout risk |
| Well-being & work modes | 14–15 | overtime → sick days → satisfaction, onsite/hybrid/remote comparison |
| Performance, promotion & L&D | 16–17 | rating → promotion alignment, training-hours ROI |
| Segmentation | 18 | intra-department salary quartiles (`NTILE`) |
| Trends & business impact | 19–24 | hire-cohort attrition, **partial-year-normalised hiring trend**, pay dispersion, **significance testing of every churn "hot spot"**, annualised cost of attrition |

### Sample: one query, end to end

Every query carries its business question, its method and the CSV it writes — so a reader never has to guess why a number exists. This is Q23, the query behind finding 9️⃣ (`SQL Outputs/23_attrition_segment_significance.csv`):

```sql
WITH company AS (
    SELECT AVG(resigned) AS p_company FROM employees
),
segments AS (
    SELECT 'department' AS dimension, department AS segment, COUNT(*) AS n, AVG(resigned) AS p
    FROM employees GROUP BY department
    UNION ALL
    SELECT 'job_title', job_title, COUNT(*), AVG(resigned) FROM employees GROUP BY job_title
    UNION ALL
    SELECT 'education', education_level, COUNT(*), AVG(resigned) FROM employees GROUP BY education_level
)
SELECT dimension, segment, n,
       ROUND(100.0 * p, 2) AS attrition_rate_pct,
       ROUND((p - (SELECT p_company FROM company))
             / SQRT((SELECT p_company * (1 - p_company) FROM company) / n), 2) AS z_score,
       CASE WHEN ABS((p - (SELECT p_company FROM company))
                 / SQRT((SELECT p_company * (1 - p_company) FROM company) / n)) < 1.96
            THEN 'not significant' ELSE 'significant' END AS verdict
FROM segments
ORDER BY dimension, attrition_rate_pct DESC;
```

| segment | attrition | z-score | verdict |
| --- | --- | --- | --- |
| Finance (highest dept) | 10.54% | +1.85 | not significant |
| IT (lowest dept) | 9.56% | −1.59 | not significant |
| Fully remote | 10.17% | +0.73 | not significant |
| Onsite | 9.48% | **−2.48** | significant — but only 0.65 pt |

That is the whole attrition story in one table: **25 of 26 segments are indistinguishable from the company average.**

**Data-quality suite** (`03_qa_checks.sql`): grain/completeness (100,000 unique IDs, 0 null keys) · domain validity (0 violations) · tenure vs `hire_date` consistency (PASS) · segment reconciliation (every split sums back to 100,000) · salary outlier scan (0 beyond 3σ) · **snapshot coverage** (latest year = 9 calendar months → annualise before comparing).

**Two ways to run it**

```bash
# A) MySQL 8 (primary path)
mysql -u root -p < SQL/01_setup_and_load.sql
mysql -u root -p projects < SQL/02_analytics_queries.sql
mysql -u root -p projects < SQL/03_qa_checks.sql

# B) No server needed — regenerates every committed output CSV
pip install -r requirements.txt
python3 SQL/run_queries.py            # rewrites SQL Outputs/
python3 SQL/run_queries.py --check    # CI-style check: fails if an output drifts
```

**Automated in CI** — [`.github/workflows/sql-check.yml`](.github/workflows/sql-check.yml) re-runs the whole pack with `--check` on every push, re-runs the models with a fixed seed, and rebuilds the report PDF, so a committed output can never drift from the query that produced it.

---

## 🧪 Modelling — what the data can and cannot predict

```
Modelling/
├── model_attrition_and_salary.py   # one command, fixed seed (42), 80/20 stratified split
├── results/                        # metrics.csv, roc_curve.csv, salary_coefficients.csv, rf_importance.csv
└── figures/                        # roc_attrition.png, salary_predicted_vs_actual.png
```

| Task | Model | Primary metric | Result |
| --- | --- | --- | --- |
| Attrition (`Resigned`) | Logistic Regression (C = 0.5, scaled) | ROC AUC | **0.490** |
| Attrition (`Resigned`) | Random Forest (250 trees, depth 8) | ROC AUC | **0.490** |
| Salary (`Monthly_Salary`) | OLS — all features | R² | **0.9914** (MAE $95/month) |
| Salary (`Monthly_Salary`) | OLS — job title + performance only | R² | **0.9914** |

Two uncomfortable conclusions:

1. **Attrition is not predictable from these fields.** Accuracy is 90% — exactly the share of employees who stay, so a "nobody leaves" rule scores the same. AUC is the honest metric and it is a coin flip.
2. **Salary is a formula.** Engineer +$2,600 / Technician −$649 per month, plus **+$493 per performance point**; department, gender and education coefficients sit within ±$10 of zero.

The report reads `results/metrics.csv`, so no model number in the PDF is typed by hand: re-run the model, rebuild the report, and every figure updates.

---

## 🔧 What re-running the numbers changed

Re-executing the first draft of the SQL pack against the raw CSV (and reconciling it with the Python results) exposed real bugs. Fixing them changed three published conclusions — all documented query-by-query in [`SQL/README.md`](SQL/README.md#corrections-made-in-this-version):

| Bug | Was reported | Correct value |
| --- | --- | --- |
| Department & tenure attrition divided by **company** headcount instead of the segment's own (Q06/Q07) | Finance 1.18%, year-8 cohort 1.06% | Finance **10.54%**, year 8 **10.60%** |
| Pay ratios missing ×100 (Q09/Q11) | "pay gap 0.004%" | **0.4–0.9%** for the widest within-title gap |
| `ROW_NUMBER()` on a tied salary (Q10) | 5,673 rows returned as "top 3" | tie count exposed instead |
| Department average used as an *individual* pay benchmark (Q12) | 5,599 "underpaid top performers" | **0** after controlling for job title × rating |
| Burnout % divided by company, not department, headcount (Q13) | 0.38–0.43% | **3.4–3.9%** per department |
| Promotion filter `Promotions >= 0` — always true (Q17) | 100% promoted | **66–67%** |
| Annual hiring compared across two **partial** years (Q20) | "2024 hiring −31%, a restructuring shock" | **+2.4%** vs 2023 on a complete-month basis — **no cliff** |
| Column/file typos (`Distribution_Percengtage`, `WorK_Mode`, `…_ro.csv`) | — | normalised snake_case throughout |

Two claims were also *softened* rather than corrected: "year-10 employees earn the least" rested on **44 employees** and is now stated as *"pay is flat across tenure (+0.5% from year 1 to year 9)"*, and the 5,599 "underpaid" list was reframed as a role-mix artefact rather than an equity problem.

The hiring-trend chart in [`Charts/`](Charts) was rebuilt for the same reason — partial years are now hatched and labelled, and a second panel shows the comparable per-month series (`Charts/rebuild_hiring_trend.py` regenerates it):

| Before | After |
| --- | --- |
| raw annual hires → looks like a 2024 collapse | [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Charts/15_hiring_trend.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Charts/15_hiring_trend.png) |

Keeping these corrections visible is deliberate: **the job is to find the artefact before the stakeholder does.**

---

## 📦 Deliverables

| | Path | What it is |
| --- | --- | --- |
| 🗄 | [`SQL/`](SQL) + [`SQL Outputs/`](SQL%20Outputs) | 24 annotated queries, 6 QA checks, 32 result CSVs, reproducible runner |
| 🧪 | [`Modelling/`](Modelling) | Attrition + salary models, metrics, ROC and fit figures |
| 📓 | [`Notebook/`](Notebook) | Full Python EDA walkthrough (+ PDF export) |
| 📊 | [`Power BI pbix/`](Power%20BI%20pbix) | Interactive 4-tab dashboard (Overview · Compensation · Performance · Attrition & Satisfaction) |
| 🖼 | [`Charts/`](Charts) | 21 analysis charts (PNG) |
| 📄 | [`Employee Report/`](Employee%20Report) | **13-page analysis report** + `build_report.py`, which regenerates the PDF and its 8 figures from `Dataset.zip` |
| 🎤 | [`Presentation/`](Presentation) | Slide deck — `Employee Performance Presentation.pptx` + PDF export |

---

## 📊 Power BI Dashboard

| | |
| --- | --- |
| **1 · Overview** — headcount, hiring trend, demographics | **2 · Compensation** — pay across role, education & gender |
| [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Power%20BI%20Dashboard/1.%20Overview.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Power%20BI%20Dashboard/1.%20Overview.png) | [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Power%20BI%20Dashboard/2.%20Compensation.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Power%20BI%20Dashboard/2.%20Compensation.png) |
| **3 · Performance** — ratings, training, tenure | **4 · Attrition & Satisfaction** — turnover drivers & the satisfaction paradox |
| [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Power%20BI%20Dashboard/3.%20Performance.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Power%20BI%20Dashboard/3.%20Performance.png) | [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Power%20BI%20Dashboard/4.%20Attrition%20%26%20Satisfaction.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Power%20BI%20Dashboard/4.%20Attrition%20%26%20Satisfaction.png) |

Open [`Power BI pbix/Employee Performance & Productivity Dashboard.pbix`](Power%20BI%20pbix) in Power BI Desktop.

---

## 📈 A few of the 21 charts

| | |
| --- | --- |
| **Average salary by job title — the 72% gap** | **Satisfaction: stayed vs resigned — 3.00 vs 2.99** |
| [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Charts/05_avg_monthly_salary_by_job.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Charts/05_avg_monthly_salary_by_job.png) | [![](https://github.com/Mohammadshadab1/employee-performance-analysis/raw/main/Charts/09_avg_satisfaction_resignation.png)](https://github.com/Mohammadshadab1/employee-performance-analysis/blob/main/Charts/09_avg_satisfaction_resignation.png) |

The suite covers **workforce** (headcount, hiring trend, tenure), **compensation** (salary by department / education / job title / gender, experience vs salary), **performance** (score distribution, training hours, ratings by job & education), **attrition** (by department / education / remote frequency) and **correlation matrices**.

---

## 📂 Repository Structure

```
employee-performance-analysis/
│
├── SQL/                          # SQL analytics layer
│   ├── Employee_Analytics_Queries.sql  #   24 annotated business queries
│   └── load_data_to_mysql.ipynb  #   notebook loader (env-var credentials)
│   
│
├── SQL Outputs/                  # 18 result CSVs 
│
├── Employee Report/              # 13-page analysis report
│   └── Employee_Analytics_Report.pdf
│
├── Notebook/                     # Full Python EDA — notebook + PDF export
├── Charts/                       # 21 analysis charts (PNG) 
├── Power BI Dashboard/           # 4 dashboard tab screenshots + dashboard PDF
├── Power BI pbix/                # Interactive Power BI dashboard (.pbix)
├── Presentation/                 # Slide deck (PPTX + PDF export)
├── Banner/                       # Project banner
│
├── Dataset.zip                   # Source extract — 100,000 × 20…
├── LICENSE · .gitignore
└── README.md
```

---

## 🧠 Methodology

1. **SQL modelling & extraction** — normalised `employees` table with constraints and a generated status column; 24 analytical queries (CTEs, `RANK`/`ROW_NUMBER`/`NTILE`/`LAG`, conditional aggregation, z-tests, confidence intervals) plus a 6-check QA suite, all re-runnable from one script.
2. **Data preparation** — validated 100,000 records: primary-key uniqueness, categorical domains, numeric ranges, tenure-vs-hire-date consistency, segment reconciliation.
3. **Descriptive analytics** — aggregates across department, education, gender, job title, tenure, tenure band and age; salary percentiles alongside means.
4. **Attrition analysis** — per-segment rates with **correct denominators**, 95% confidence intervals and a significance test against the company benchmark; remote-work and tenure-cohort curves.
5. **Correlation analysis** — Pearson matrices across 6 and 15 numeric features (only **Performance ↔ Salary, r = 0.51**, survives).
6. **Predictive modelling** — logistic regression and random forest for attrition; OLS for salary; 80/20 stratified split, seed 42, accuracy **and** ROC AUC reported side by side.
7. **Storytelling & visualisation** — 21 charts, 4-tab Power BI dashboard, slide deck, and a 13-page report that rebuilds itself from the raw data.

### 🛠 Tools & skills

`SQL (MySQL 8)` · `CTEs` · `Window functions` · `Conditional aggregation` · `Data-quality testing` · `Python` · `pandas` · `NumPy` · `matplotlib` · `seaborn` · `scikit-learn` · `Jupyter` · `Power BI` · `DAX` · `Excel` · `EDA` · `Hypothesis testing` · `Predictive modelling` · `ReportLab` · `Data storytelling`

---

## 💡 Recommendations for leadership

1. **Rebuild job levelling and publish salary bands.** The 72% title gap *is* the pay story: Technicians ($4,545) and Analysts ($5,196) sit far below the $6,403 average while Engineers/Managers earn $7,799.
2. **Price tenure and skill into compensation.** Pay is flat from year 1 to year 9 (0.5% spread) — skills-based or time-in-role increments are cheaper than replacing institutional knowledge.
3. **Stop tuning remote policy for retention.** Onsite 9.48% vs hybrid 10.13% vs fully remote 10.17% — the gap is under a point, and onsite is the *only* segment that clears a significance test (barely).
4. **Rebuild the churn early-warning system.** Satisfaction cannot separate leavers from stayers (3.00 vs 2.99) and no field predicts exit (AUC 0.49): capture intent-to-stay pulses, manager-quality signals and compa-ratio flags, then re-run the model.
5. **Target training instead of rationing it.** 49.5 hours for everyone produces the same 3.0 rating everywhere; aim hours at low-rated employees and measure lift against a control group.
6. **Calibrate performance reviews.** Uniform ratings still drive pay (r = 0.51) while measuring nothing else — add evidence anchors, forced distribution and manager calibration.
7. **Cost the churn you are not seeing.** ~993 leavers/year at $76.8k average salary ≈ **$23M–$76M/year** in replacement cost (30–100% of salary) — that is the budget available for retention work.
8. **Fix HR data instrumentation before the next analysis.** A 5,673-person salary ceiling and job title alone explaining 99% of pay variance mean the data cannot answer the questions leadership actually asks.

---

## ⚠️ Honest limitations

- **The extract behaves like a simulated dataset.** Independent features, ~20,000 employees in every rating bucket, and salary as a near-deterministic function of title + rating. Treat the results as a **validated methodology demonstration** — and read the "no signal" findings as *"these fields cannot answer this question"*.
- **The window is a snapshot, not a full decade.** Hires run 2014-09 → 2024-09, so 2014 and 2024 are partial years. Every year-over-year comparison is normalised (`SQL Outputs/20_hiring_trend_yoy.csv`); raw annual counts are not comparable.
- **Resignation is a static flag, not an event.** There is no termination date, so "attrition rate" here is a decade-wide share of records flagged resigned, not a time-series hazard rate.
- **Small cohorts are flagged, not hidden.** Tenure year 10 has 44 employees; it is labelled *low confidence* rather than read as a spike.
- **Cost of attrition is an assumption-flagged estimate** (30–100% of annual salary), not a booked number.


## 👤 Author

**Mohammad Shadab** — Data Analyst
_SQL · Python · Power BI · Excel · Data Storytelling_

Open to Data Analyst / Business Analyst / MIS roles — feedback and collaboration welcome.

- 📧 [jrshadab921@gmail.com](mailto:jrshadab921@gmail.com)
- 💼 [LinkedIn — Mohammad Shadab](https://www.linkedin.com/in/mohammad-shadab-550aab24b)
- 🐙 [GitHub — Mohammadshadab1](https://github.com/Mohammadshadab1)
- 🌐 [Portfolio](https://myportfoliowebsite-lyart.vercel.app/)

⭐ **If you find this project useful, please give it a star!** ⭐

_Licensed under the [MIT License](LICENSE)._
