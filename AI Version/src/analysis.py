"""
Employee Performance & Productivity — Full Analysis Pipeline
=============================================================
Loads the raw CSV, performs data profiling, descriptive & inferential
analysis, builds predictive models (attrition + salary), renders all
charts, and exports JSON aggregates used by the dashboard, PDF report
and PowerPoint deck.

Usage:  python3 src/analysis.py
Output: charts/*.png, assets/summary.json, assets/dashboard_data.json
"""

import json
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------- config
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "Extended_Employee_Performance_and_Productivity_Data.csv")
CHARTS = os.path.join(ROOT, "charts")
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(CHARTS, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
PALETTE = ["#264653", "#2a9d8f", "#e9c46a", "#e76f51", "#8ab17d", "#f4a261", "#457b9d", "#9b5de5", "#ef476f"]
sns.set_palette(PALETTE)
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#d0d7de",
    "axes.labelcolor": "#2d3339",
    "text.color": "#2d3339",
    "xtick.color": "#57606a",
    "ytick.color": "#57606a",
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "axes.titlepad": 14,
    "figure.dpi": 150,
})

NUMERIC = ["Age", "Years_At_Company", "Performance_Score", "Monthly_Salary",
           "Work_Hours_Per_Week", "Projects_Handled", "Overtime_Hours", "Sick_Days",
           "Remote_Work_Frequency", "Team_Size", "Training_Hours", "Promotions",
           "Employee_Satisfaction_Score"]

# ---------------------------------------------------------------- load
df = pd.read_csv(DATA, parse_dates=["Hire_Date"])
df["Hire_Year"] = df["Hire_Date"].dt.year
df["Resigned"] = df["Resigned"].astype(int)
df["Gender"] = df["Gender"].replace({"Other": "Non-binary/Other"})

summary = {}
summary["profile"] = {
    "rows": int(len(df)),
    "columns": int(df.shape[1]),
    "missing_cells": int(df.isnull().sum().sum()),
    "duplicate_ids": int(df.Employee_ID.duplicated().sum()),
    "departments": int(df.Department.nunique()),
    "job_titles": int(df.Job_Title.nunique()),
    "hire_date_range": f"{df.Hire_Date.min():%Y-%m} → {df.Hire_Date.max():%Y-%m}",
}

# ---------------------------------------------------------------- KPIs
kpis = {
    "total_employees": int(len(df)),
    "avg_salary": round(float(df.Monthly_Salary.mean()), 0),
    "median_salary": round(float(df.Monthly_Salary.median()), 0),
    "salary_std": round(float(df.Monthly_Salary.std()), 0),
    "avg_performance": round(float(df.Performance_Score.mean()), 2),
    "high_perf_pct": round(float((df.Performance_Score >= 4).mean() * 100), 1),
    "low_perf_pct": round(float((df.Performance_Score <= 2).mean() * 100), 1),
    "attrition_rate": round(float(df.Resigned.mean() * 100), 2),
    "avg_tenure": round(float(df.Years_At_Company.mean()), 1),
    "avg_satisfaction": round(float(df.Employee_Satisfaction_Score.mean()), 2),
    "avg_work_hours": round(float(df.Work_Hours_Per_Week.mean()), 1),
    "avg_overtime": round(float(df.Overtime_Hours.mean()), 1),
    "avg_training": round(float(df.Training_Hours.mean()), 1),
    "avg_projects": round(float(df.Projects_Handled.mean()), 1),
    "avg_sick_days": round(float(df.Sick_Days.mean()), 1),
    "avg_team_size": round(float(df.Team_Size.mean()), 1),
    "avg_promotions": round(float(df.Promotions.mean()), 2),
    "pct_promoted": round(float((df.Promotions > 0).mean() * 100), 1),
    "avg_age": round(float(df.Age.mean()), 1),
}
summary["kpis"] = kpis

# ---------------------------------------------------------------- helpers
def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(CHARTS, name), bbox_inches="tight")
    plt.close(fig)
    print("  chart:", name)

# ---------------------------------------------------------- 1. headcount
order = df.Department.value_counts()
fig, ax = plt.subplots(figsize=(11, 5.6))
bars = ax.bar(order.index, order.values, color=sns.color_palette("viridis", len(order)))
ax.bar_label(bars, fmt="%.1f%%", labels=[f"{v/len(df)*100:.1f}%" for v in order.values], padding=3, fontsize=13)
ax.set(title="Headcount by Department", ylabel="Employees", xlabel="")
ax.set_yticklabels([]); ax.grid(axis="y", alpha=0.4)
plt.xticks(rotation=25, ha="right")
save(fig, "01_department_headcount.png")

# ------------------------------------------------- 2. gender & education
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
g = df.Gender.value_counts()
axes[0].pie(g.values, labels=[f"{i}\n{v/len(df)*100:.1f}%" for i, v in g.items()],
            autopct="", colors=sns.color_palette("Set2", len(g)), startangle=90,
            wedgeprops={"width": 0.42, "edgecolor": "white"}, textprops={"fontsize": 13})
axes[0].set_title("Gender Mix")
e = df.Education_Level.value_counts()
axes[1].pie(e.values, labels=[f"{i}\n{v/len(df)*100:.1f}%" for i, v in e.items()],
            colors=sns.color_palette("Set3", len(e)), startangle=90,
            wedgeprops={"width": 0.42, "edgecolor": "white"}, textprops={"fontsize": 13})
axes[1].set_title("Education Level Mix")
save(fig, "02_gender_education.png")

# --------------------------------------------------- 3. salary by dept
sal = df.groupby("Department").Monthly_Salary.agg(["mean", "median"]).sort_values("mean")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
y = np.arange(len(sal))
ax.barh(y - 0.2, sal["mean"], 0.4, label="Mean", color="#264653")
ax.barh(y + 0.2, sal["median"], 0.4, label="Median", color="#2a9d8f")
ax.set_yticks(y, sal.index)
ax.bar_label(ax.containers[0], fmt="$%.0f", padding=3, fontsize=11)
ax.set(title="Monthly Salary by Department", xlabel="USD / month")
ax.legend(frameon=False)
save(fig, "03_salary_by_department.png")

# ------------------------------------------------ 4. performance by dept
perf = df.groupby("Department").Performance_Score.mean().sort_values()
fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = ["#e76f51" if v < 2.95 else "#2a9d8f" if v > 3.05 else "#e9c46a" for v in perf]
bars = ax.barh(perf.index, perf.values, color=colors)
ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=12)
ax.axvline(kpis["avg_performance"], ls="--", color="#57606a", lw=1.5, label=f"Company avg {kpis['avg_performance']:.2f}")
ax.set(title="Average Performance Score by Department", xlabel="Score (1–5)")
ax.set_xlim(0, 3.8); ax.legend(frameon=False, loc="lower right")
save(fig, "04_performance_by_department.png")

# ------------------------------------------------- 5. attrition by dept
att = df.groupby("Department").Resigned.mean().mul(100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = ["#e76f51" if v > 10.5 else "#2a9d8f" if v < 9.5 else "#e9c46a" for v in att]
bars = ax.bar(att.index, att.values, color=colors)
ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=12)
ax.axhline(kpis["attrition_rate"], ls="--", color="#57606a", lw=1.5, label=f"Company avg {kpis['attrition_rate']:.1f}%")
ax.set(title="Attrition Rate by Department", ylabel="% resigned")
plt.xticks(rotation=25, ha="right"); ax.legend(frameon=False)
save(fig, "05_attrition_by_department.png")

# ------------------------------------------------------- 6. correlation
fig, ax = plt.subplots(figsize=(12.5, 10))
cm = df[NUMERIC + ["Resigned"]].corr()
mask = np.triu(np.ones_like(cm, dtype=bool), k=1)
sns.heatmap(cm, mask=mask, cmap="RdBu_r", center=0, vmin=-0.15, vmax=0.15,
            annot=True, fmt=".2f", annot_kws={"size": 9}, square=True,
            cbar_kws={"shrink": 0.7, "label": "Pearson r"}, ax=ax,
            linewidths=0.4, linecolor="white")
ax.set_title("Correlation Matrix — Key Drivers", fontsize=22, fontweight="bold")
plt.xticks(rotation=45, ha="right", fontsize=11); plt.yticks(fontsize=11)
save(fig, "06_correlation_heatmap.png")
summary["correlations"] = {
    "performance_top": cm["Performance_Score"].drop(["Performance_Score"]).abs().sort_values(ascending=False).head(4).round(3).to_dict(),
    "salary_top": cm["Monthly_Salary"].drop(["Monthly_Salary"]).abs().sort_values(ascending=False).head(4).round(3).to_dict(),
    "attrition_top": cm["Resigned"].drop(["Resigned"]).abs().sort_values(ascending=False).head(4).round(3).to_dict(),
    "satisfaction_top": cm["Employee_Satisfaction_Score"].drop(["Employee_Satisfaction_Score"]).abs().sort_values(ascending=False).head(4).round(3).to_dict(),
}

# ------------------------------------------------------- 7. age & tenure
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.histplot(df.Age, bins=30, kde=True, color="#457b9d", ax=axes[0])
axes[0].set(title="Age Distribution", xlabel="Age (years)", ylabel="Employees")
sns.histplot(df.Years_At_Company, bins=11, kde=True, color="#2a9d8f", ax=axes[1])
axes[1].set(title="Tenure Distribution", xlabel="Years at company", ylabel="Employees")
save(fig, "07_age_tenure.png")

# ------------------------------------------------- 8. salary distribution
fig, ax = plt.subplots(figsize=(11, 5.6))
sns.histplot(df.Monthly_Salary, bins=50, kde=True, color="#264653", ax=ax)
ax.axvline(kpis["avg_salary"], color="#e76f51", ls="--", lw=2, label=f"Mean ${kpis['avg_salary']:,.0f}")
ax.axvline(kpis["median_salary"], color="#2a9d8f", ls="--", lw=2, label=f"Median ${kpis['median_salary']:,.0f}")
ax.set(title="Monthly Salary Distribution", xlabel="USD / month", ylabel="Employees")
ax.legend(frameon=False)
save(fig, "08_salary_distribution.png")

# ------------------------------------------------ 9. salary by education
edu_order = ["High School", "Bachelor", "Master", "PhD"]
fig, ax = plt.subplots(figsize=(10, 5.8))
sns.boxplot(data=df, x="Education_Level", y="Monthly_Salary", order=edu_order,
            hue="Education_Level", palette="Set2", legend=False, ax=ax, fliersize=1.5)
means = df.groupby("Education_Level").Monthly_Salary.mean().reindex(edu_order)
ax.scatter(range(4), means.values, color="#e76f51", zorder=5, s=70, label="Mean")
ax.set(title="Salary by Education Level", xlabel="", ylabel="USD / month")
ax.legend(frameon=False)
save(fig, "09_salary_by_education.png")

# ------------------------------------------------- 10. gender pay equity
titles = sorted(df.Job_Title.unique())
gp = df.pivot_table(index="Job_Title", columns="Gender", values="Monthly_Salary", aggfunc="mean").reindex(titles)
fig, ax = plt.subplots(figsize=(12.5, 5.8))
x = np.arange(len(titles)); w = 0.27
for i, gname in enumerate(gp.columns):
    ax.bar(x + (i - 1) * w, gp[gname], w, label=gname)
ax.set_xticks(x, titles, rotation=20, ha="right")
ax.set(title="Average Salary by Job Title & Gender", ylabel="USD / month")
ax.legend(title="Gender", frameon=False)
save(fig, "10_gender_pay_equity.png")

raw_gap = (df[df.Gender == "Male"].Monthly_Salary.mean() - df[df.Gender == "Female"].Monthly_Salary.mean())
within = []
for t in titles:
    sub = df[df.Job_Title == t]
    m, f = sub[sub.Gender == "Male"].Monthly_Salary.mean(), sub[sub.Gender == "Female"].Monthly_Salary.mean()
    within.append((t, round(m - f, 1)))
summary["pay_equity"] = {"raw_gap": round(raw_gap, 1), "within_title_gaps": within}

# ------------------------------------------- 11. performance mix by dept
pd_mix = pd.crosstab(df.Department, df.Performance_Score, normalize="index").mul(100).reindex(order.index[::-1])
fig, ax = plt.subplots(figsize=(12, 6))
pd_mix.plot(kind="barh", stacked=True, ax=ax,
            color=["#e63946", "#f4a261", "#e9c46a", "#8ab17d", "#2a9d8f"], width=0.72)
ax.set(title="Performance Score Mix by Department (% of staff)", xlabel="% of employees", ylabel="")
ax.legend(title="Score", labels=["1", "2", "3", "4", "5"], frameon=False, loc="lower right", ncol=5)
save(fig, "11_performance_mix.png")

# ------------------------------------------------- 12. attrition drivers
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
panels = [
    ("Satisfaction bucket", pd.cut(df.Employee_Satisfaction_Score, [1, 2, 3, 4, 5],
     labels=["1–2 (low)", "2–3", "3–4", "4–5 (high)"], include_lowest=True)),
    ("Performance score", df.Performance_Score),
    ("Remote work %", df.Remote_Work_Frequency),
    ("Promotions", df.Promotions),
    ("Tenure bucket", pd.cut(df.Years_At_Company, [-1, 1, 3, 5, 7, 10], labels=["0–1", "2–3", "4–5", "6–7", "8–10"])),
    ("Overtime bucket", pd.cut(df.Overtime_Hours, [-1, 5, 10, 15, 20, 30], labels=["0–5", "6–10", "11–15", "16–20", "21–29"])),
]
driver_data = {}
for ax, (name, series) in zip(axes.flat, panels):
    s = df.groupby(series, observed=True).Resigned.mean().mul(100)
    driver_data[name] = {str(k): round(float(v), 2) for k, v in s.items()}
    bars = ax.bar(s.index.astype(str), s.values, color="#457b9d")
    ax.bar_label(bars, fmt="%.1f%%", fontsize=11, padding=2)
    ax.axhline(kpis["attrition_rate"], ls="--", color="#e76f51", lw=1.5)
    ax.set(title=f"Attrition by {name}", ylabel="% resigned", xlabel="")
    ax.tick_params(labelsize=11)
fig.suptitle("Attrition Drivers — Rate vs. Company Average (dashed line)", y=1.0, fontsize=22, fontweight="bold")
save(fig, "12_attrition_drivers.png")
summary["attrition_drivers"] = driver_data

# ------------------------------------------------- 13. work-life balance
fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
sns.scatterplot(data=df.sample(6000, random_state=42), x="Work_Hours_Per_Week", y="Performance_Score",
                hue="Performance_Score", palette="coolwarm", legend=False, alpha=0.35, s=18, ax=axes[0])
axes[0].set(title="Work Hours vs Performance", xlabel="Hours / week", ylabel="Performance score")
wh = df.groupby("Work_Hours_Per_Week").agg(p=("Performance_Score", "mean"), s=("Monthly_Salary", "mean"))
ax2 = axes[1]
ax2.plot(wh.index, wh.p, color="#264653", lw=2.5, label="Avg performance")
ax2.set_xlabel("Hours / week"); ax2.set_ylabel("Avg performance score", color="#264653")
ax3 = ax2.twinx()
ax3.plot(wh.index, wh.s, color="#e76f51", lw=2.5, ls="--", label="Avg salary")
ax3.set_ylabel("Avg salary (USD)", color="#e76f51"); ax3.grid(False)
ax2.set_title("Work Hours vs Performance & Salary")
lines1, labels1 = ax2.get_legend_handles_labels(); lines2, labels2 = ax3.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="lower right")
save(fig, "13_work_life.png")

# --------------------------------------------------- 14. remote vs tenure
fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
rm = df.groupby("Remote_Work_Frequency").agg(attr=("Resigned", "mean"), sat=("Employee_Satisfaction_Score", "mean"),
                                             perf=("Performance_Score", "mean")).mul(1)
rm["attr"] *= 100
ax = axes[0]
bars = ax.bar(rm.index.astype(str), rm.attr, color="#2a9d8f")
ax.bar_label(bars, fmt="%.1f%%", fontsize=12)
ax.set(title="Attrition by Remote-Work %", ylabel="% resigned", xlabel="Remote frequency")
ax = axes[1]
x = np.arange(len(rm)); w = 0.38
ax.bar(x - w/2, rm.sat, w, label="Satisfaction", color="#e9c46a")
ax.bar(x + w/2, rm.perf, w, label="Performance", color="#457b9d")
ax.set_xticks(x, rm.index.astype(str)); ax.set_xlabel("Remote frequency")
ax.set(title="Satisfaction & Performance by Remote-Work %", ylabel="Score (1–5)")
ax.legend(frameon=False)
save(fig, "14_remote_work.png")

# ----------------------------------------- 15. salary vs tenure & training
fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
ten = df.groupby("Years_At_Company").agg(sal=("Monthly_Salary", "mean"), sat=("Employee_Satisfaction_Score", "mean"))
ax = axes[0]
ax.plot(ten.index, ten.sal, marker="o", lw=2.5, color="#264653", label="Avg salary")
ax.set(title="Salary & Satisfaction vs Tenure", xlabel="Years at company", ylabel="Avg salary (USD)")
ax2 = ax.twinx(); ax2.plot(ten.index, ten.sat, marker="s", ls="--", lw=2, color="#e76f51", label="Satisfaction")
ax2.set_ylabel("Satisfaction", color="#e76f51"); ax2.grid(False)
l1, la1 = ax.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
ax.legend(l1 + l2, la1 + la2, frameon=False, loc="upper left")
tr = pd.cut(df.Training_Hours, [-1, 15, 30, 50, 70, 100], labels=["0–15", "16–30", "31–50", "51–70", "71–99"])
tp = df.groupby(tr, observed=True).Performance_Score.mean()
bars = axes[1].bar(tp.index.astype(str), tp.values, color="#8ab17d")
axes[1].bar_label(bars, fmt="%.2f", fontsize=12)
axes[1].axhline(kpis["avg_performance"], ls="--", color="#e76f51")
axes[1].set(title="Performance by Training Hours", xlabel="Training hours bucket", ylabel="Avg performance")
save(fig, "15_tenure_training.png")

# ------------------------------------------------------ 16. hire-year trend
fig, ax = plt.subplots(figsize=(11, 5.4))
hy = df.groupby("Hire_Year").size()
ax.bar(hy.index.astype(str), hy.values, color="#9b5de5")
ax.bar_label(ax.containers[0], fmt="%d", fontsize=11)
ax.set(title="Hiring Volume by Year", ylabel="New hires", xlabel="Hire year")
plt.xticks(rotation=45)
save(fig, "16_hiring_trend.png")

# ================================================ ML: attrition model
feat_num = ["Age", "Years_At_Company", "Performance_Score", "Monthly_Salary", "Work_Hours_Per_Week",
            "Projects_Handled", "Overtime_Hours", "Sick_Days", "Remote_Work_Frequency", "Team_Size",
            "Training_Hours", "Promotions", "Employee_Satisfaction_Score"]
X = pd.get_dummies(df[feat_num + ["Department", "Gender", "Job_Title", "Education_Level"]],
                   columns=["Department", "Gender", "Job_Title", "Education_Level"], drop_first=True)
y = df.Resigned
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
sc = StandardScaler().fit(Xtr)
lr = LogisticRegression(max_iter=2000, C=0.5)
lr.fit(sc.transform(Xtr), ytr)
p = lr.predict_proba(sc.transform(Xte))[:, 1]
attr_model = {
    "accuracy": round(float(accuracy_score(yte, p > 0.5)), 4),
    "auc": round(float(roc_auc_score(yte, p)), 4),
}
coefs = pd.Series(lr.coef_[0], index=X.columns).sort_values()
attr_model["top_risk"] = {k: round(float(v), 3) for k, v in coefs.head(8).items()}
attr_model["top_protective"] = {k: round(float(v), 3) for k, v in coefs.tail(8)[::-1].items()}
summary["attrition_model"] = attr_model

fig, ax = plt.subplots(figsize=(11.5, 6.5))
top = pd.concat([coefs.head(8), coefs.tail(8)])
colors = ["#e76f51" if v < 0 else "#2a9d8f" for v in top.values]
bars = ax.barh([i.replace("_", " ") for i in top.index], top.values, color=colors)
ax.bar_label(bars, fmt="%.2f", fontsize=11, padding=2)
ax.axvline(0, color="#57606a")
ax.set(title="Logistic Regression — Attrition Drivers (standardized coefficients)",
       xlabel="Coefficient (negative = higher attrition risk)")
save(fig, "17_attrition_model.png")

rf = RandomForestClassifier(n_estimators=250, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(Xtr, ytr)
rf_model = {"accuracy": round(float(accuracy_score(yte, rf.predict(Xte))), 4),
            "auc": round(float(roc_auc_score(yte, rf.predict_proba(Xte)[:, 1])), 4)}
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
rf_model["importances"] = {k: round(float(v), 4) for k, v in imp.items()}
summary["rf_model"] = rf_model

fig, ax = plt.subplots(figsize=(10.5, 6))
bars = ax.barh([i.replace("_", " ") for i in imp.index[::-1]], imp.values[::-1], color="#264653")
ax.bar_label(bars, fmt="%.3f", fontsize=11, padding=2)
ax.set(title="Top Attrition Predictors — Random Forest Importance")
save(fig, "18_rf_importance.png")

# ================================================ ML: salary model
Xs = pd.get_dummies(df[feat_num[:4] + feat_num[4:] + ["Department", "Gender", "Job_Title", "Education_Level"]],
                    columns=["Department", "Gender", "Job_Title", "Education_Level"], drop_first=True)
Xs = Xs.drop(columns=["Monthly_Salary"])
Xstr, Xste, ystr, yste = train_test_split(Xs, df.Monthly_Salary, test_size=0.2, random_state=42)
reg = LinearRegression().fit(Xstr, ystr)
sal_model = {
    "r2": round(float(r2_score(yste, reg.predict(Xste))), 4),
    "mae": round(float(mean_absolute_error(yste, reg.predict(Xste))), 1),
}
scoefs = pd.Series(reg.coef_, index=Xs.columns).sort_values()
sal_model["top_negative"] = {k: round(float(v), 1) for k, v in scoefs.head(6).items()}
sal_model["top_positive"] = {k: round(float(v), 1) for k, v in scoefs.tail(6)[::-1].items()}
summary["salary_model"] = sal_model

# ------------------------------------------------------- 19. satisfaction
fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
sns.countplot(data=df, x="Performance_Score", hue="Employee_Satisfaction_Score",
              palette="RdYlGn", ax=axes[0])
axes[0].set(title="Satisfaction by Performance Score", xlabel="Performance score", ylabel="Employees")
axes[0].legend(title="Satisfaction", frameon=False)
sat = df.groupby(df.Employee_Satisfaction_Score.round()).agg(perf=("Performance_Score", "mean"), attr=("Resigned", "mean")).mul(1)
sat["attr"] *= 100
ax = axes[1]
ax.bar(sat.index, sat.perf, color="#457b9d", label="Avg performance")
ax.set_xlabel("Satisfaction (rounded)"); ax.set_ylabel("Avg performance")
axr = ax.twinx(); axr.plot(sat.index, sat.attr, color="#e76f51", marker="o", lw=2.5, label="Attrition %")
axr.set_ylabel("Attrition %", color="#e76f51"); axr.grid(False)
l1, la1 = ax.get_legend_handles_labels(); l2, la2 = axr.get_legend_handles_labels()
ax.legend(l1 + l2, la1 + la2, frameon=False)
ax.set_title("Performance & Attrition by Satisfaction")
save(fig, "19_satisfaction.png")

# -------------------------------------------------------- 20. team & sick
fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
tb = pd.cut(df.Team_Size, [0, 4, 8, 12, 15, 19], labels=["1–4", "5–8", "9–12", "13–15", "16–19"])
t = df.groupby(tb, observed=True).agg(perf=("Performance_Score", "mean"), attr=("Resigned", "mean")).mul(1)
t["attr"] *= 100
ax = axes[0]
x = np.arange(len(t)); w = 0.38
ax.bar(x - w/2, t.perf, w, color="#457b9d", label="Avg performance")
axr = ax.twinx(); axr.bar(x + w/2, t.attr, w, color="#e9c46a", label="Attrition %")
ax.set_xticks(x, t.index.astype(str)); ax.set_xlabel("Team size"); ax.set_ylabel("Avg performance")
axr.set_ylabel("Attrition %"); axr.grid(False)
l1, la1 = ax.get_legend_handles_labels(); l2, la2 = axr.get_legend_handles_labels()
ax.legend(l1 + l2, la1 + la2, frameon=False, loc="upper right")
ax.set_title("Outcomes by Team Size")
sb = pd.cut(df.Sick_Days, [-1, 2, 5, 8, 11, 14], labels=["0–2", "3–5", "6–8", "9–11", "12–14"])
s = df.groupby(sb, observed=True).agg(perf=("Performance_Score", "mean"), attr=("Resigned", "mean")).mul(1)
s["attr"] *= 100
ax = axes[1]
ax.bar(s.index.astype(str), s.perf, color="#8ab17d", label="Avg performance")
ax.set_xlabel("Sick days / period"); ax.set_ylabel("Avg performance")
axr = ax.twinx(); axr.plot(s.index.astype(str), s.attr, color="#e76f51", marker="o", lw=2.5, label="Attrition %")
axr.set_ylabel("Attrition %"); axr.grid(False)
l1, la1 = ax.get_legend_handles_labels(); l2, la2 = axr.get_legend_handles_labels()
ax.legend(l1 + l2, la1 + la2, frameon=False, loc="center left")
ax.set_title("Outcomes by Sick Days")
save(fig, "20_team_sick.png")

# ============================ dashboard aggregates ====================
def dept_block(sub):
    return {
        "headcount": int(len(sub)),
        "avg_salary": round(float(sub.Monthly_Salary.mean()), 0),
        "median_salary": round(float(sub.Monthly_Salary.median()), 0),
        "avg_performance": round(float(sub.Performance_Score.mean()), 2),
        "attrition": round(float(sub.Resigned.mean() * 100), 1),
        "avg_satisfaction": round(float(sub.Employee_Satisfaction_Score.mean()), 2),
        "avg_hours": round(float(sub.Work_Hours_Per_Week.mean()), 1),
        "avg_overtime": round(float(sub.Overtime_Hours.mean()), 1),
        "avg_tenure": round(float(sub.Years_At_Company.mean()), 1),
        "avg_training": round(float(sub.Training_Hours.mean()), 0),
        "avg_projects": round(float(sub.Projects_Handled.mean()), 1),
        "high_perf_pct": round(float((sub.Performance_Score >= 4).mean() * 100), 1),
        "gender": {k: int(v) for k, v in sub.Gender.value_counts().items()},
        "education": {k: int(v) for k, v in sub.Education_Level.value_counts().items()},
        "job_titles": {k: int(v) for k, v in sub.Job_Title.value_counts().items()},
        "perf_dist": {str(int(k)): int(v) for k, v in sub.Performance_Score.value_counts().sort_index().items()},
        "salary_bins": np.histogram(sub.Monthly_Salary, bins=12, range=(3500, 9000))[0].tolist(),
        "remote_attrition": {str(k): round(float(v) * 100, 1) for k, v in sub.groupby("Remote_Work_Frequency").Resigned.mean().items()},
        "tenure_salary": {str(k): round(float(v), 0) for k, v in sub.groupby("Years_At_Company").Monthly_Salary.mean().items()},
        "title_salary": {k: round(float(v), 0) for k, v in sub.groupby("Job_Title").Monthly_Salary.mean().items()},
    }

bins_labels = [f"{int(a/1000)*1000 if a >= 1000 else a}" for a in np.linspace(3500, 9000, 13)[:-1]]
salary_bin_labels = [f"{int(x)}" for x in np.linspace(3500, 8542, 12)]

dash = {
    "kpis": kpis,
    "depts": {d: dept_block(df[df.Department == d]) for d in sorted(df.Department.unique())},
    "all": dept_block(df),
    "salary_bin_labels": salary_bin_labels,
    "attrition_by_dept": {k: round(float(v) * 100, 1) for k, v in df.groupby("Department").Resigned.mean().items()},
    "perf_by_dept": {k: round(float(v), 2) for k, v in df.groupby("Department").Performance_Score.mean().items()},
    "salary_by_dept": {k: round(float(v), 0) for k, v in df.groupby("Department").Monthly_Salary.mean().items()},
    "gender_by_title": {t: {g: round(float(v), 0) for g, v in sub.groupby("Gender").Monthly_Salary.mean().items()}
                        for t, sub in df.groupby("Job_Title")},
    "attrition_drivers": driver_data,
    "models": {"logistic": attr_model, "rf": rf_model, "salary": sal_model},
}
with open(os.path.join(ASSETS, "dashboard_data.json"), "w") as f:
    json.dump(dash, f)

summary["tables"] = {
    "dept_summary": df.groupby("Department").agg(
        headcount=("Employee_ID", "count"), avg_salary=("Monthly_Salary", "mean"),
        avg_perf=("Performance_Score", "mean"), attrition=("Resigned", "mean"),
        avg_satisfaction=("Employee_Satisfaction_Score", "mean"), avg_tenure=("Years_At_Company", "mean"),
    ).round(3).to_dict(orient="index"),
    "edu_salary": df.groupby("Education_Level").Monthly_Salary.agg(["mean", "count"]).round(0).to_dict(orient="index"),
    "title_salary": df.groupby("Job_Title").agg(salary=("Monthly_Salary", "mean"), perf=("Performance_Score", "mean"),
                                                attrition=("Resigned", "mean")).round(3).to_dict(orient="index"),
}
with open(os.path.join(ASSETS, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\nKPIs:", json.dumps(kpis, indent=1))
print("\nAttrition model:", attr_model["accuracy"], attr_model["auc"])
print("RF model:", rf_model["accuracy"], rf_model["auc"])
print("Salary model R2:", sal_model["r2"], "MAE:", sal_model["mae"])
print("Pay gap raw:", summary["pay_equity"]["raw_gap"], "| within-title:", within)
print("\nDONE — charts in charts/, JSON in assets/")
