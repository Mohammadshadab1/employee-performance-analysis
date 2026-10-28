![Employee Performance and Productivity Analysis](Banner/banner.jpeg)

# Employee Performance & Productivity Analysis

This project explores employee pay, performance, satisfaction and resignation patterns using a 100,000-row HR dataset. I used Python for exploratory analysis, MySQL for business queries and Power BI to present the results.

The main questions were:

- How is the workforce distributed across departments and roles?
- How do salaries vary by job title, education and gender?
- What differences appear between employees who stayed and those who resigned?
- How do training hours relate to performance scores?

## Start here

- [Python analysis notebook](Notebook/Employee%20Performance%20%26%20Productivity.ipynb)
- [SQL queries](SQL%20Script/Employee_Analytics_Queries.sql) and [saved results](SQL%20Outputs/)
- [Power BI dashboard PDF](Powe%20BI%20Dashboard/Employee%20Performance%20%26%20Productivity%20Dashboard.pdf)
- [Editable Power BI file](Power%20BI%20pbix/Employee%20Performance%20%26%20Productivity%20Dashboard.pbix)

## Dataset

[Dataset.zip](Dataset.zip) contains `Dataset/Extended_Employee_Performance_and_Productivity_Data.csv`: **100,000 records and 20 columns**.

The fields cover employee demographics, job details, hire dates, salary, performance, working hours, training, satisfaction and a resignation flag. There are 9 departments and 7 job titles. Hire dates range from September 2014 to September 2024.

The data shows unusually regular patterns, so I treat this as a practice analysis rather than evidence about a real employer. A source URL and the dataset's original documentation are not currently included in the repository.

## Tools and analysis

| Tool | Work included |
| --- | --- |
| Python — pandas, matplotlib, seaborn | Data inspection, duplicate-ID checks, grouped analysis and visualisation |
| MySQL | 18 queries covering workforce structure, resignation patterns, compensation, work modes, promotions and salary quartiles |
| Power BI | Four dashboard pages: Overview, Compensation, Performance, and Attrition & Satisfaction |
| Jupyter | Analysis notebook and a separate MySQL loading notebook |

The SQL includes CTEs, conditional aggregation and window functions such as `ROW_NUMBER` and `NTILE`. The Python notebook is descriptive analysis; it does not contain predictive models.

## Selected observations

| Observation | Result |
| --- | --- |
| Employees flagged as resigned | 10,010 out of 100,000 records — **10.01%** |
| Average monthly salary | **6,403.21**, in the dataset's salary units |
| Average monthly salary by role | Approximately **4,545 for Technicians** and **7,799 for Engineers** |
| Average satisfaction: stayed vs resigned | **3.00 vs 2.99** |
| Average training hours across performance scores | Approximately **49.28–49.70 hours** |

These are descriptive comparisons, not causal findings. Similar average training hours do not establish that training is ineffective, and similar average salaries across genders do not by themselves prove pay equity.

### Reading the results carefully

- **10.01% is the share of records flagged as resigned**, not an annual turnover rate. The dataset has no resignation date.
- **2014 and 2024 are partial hire years.** Raw annual hire counts should not be used to claim a hiring decline without adjusting the comparison period.
- Tenure year 10 contains only **44 records**, so comparisons involving that group need extra care.

## Power BI preview

![Power BI Overview page](Powe%20BI%20Dashboard/1.%20Overview.png)

The other pages and a PDF export are in [Powe BI Dashboard](Powe%20BI%20Dashboard/). The folder name below matches the current repository spelling.

## Repository contents

```text
employee-performance-analysis/
├── Banner/                 Project banner
├── Charts/                 21 analysis charts
├── Dataset.zip             Source CSV archive
├── Employee Report/        Analysis report PDF
├── Notebook/               Python EDA notebook and PDF export
├── Powe BI Dashboard/      Four dashboard screenshots and PDF export
├── Power BI pbix/          Editable dashboard
├── Presentation/           PowerPoint and PDF files
├── SQL Outputs/            18 saved query-result CSVs
├── SQL Script/             SQL queries and MySQL loader notebook
├── index.html              Standalone HTML dashboard
├── LICENSE.txt
└── README.md
```

## Opening and running the project

### Python analysis

1. Clone or download the repository and extract `Dataset.zip` in the repository root.
2. Install the notebook dependencies:

   ```bash
   pip install pandas matplotlib seaborn jupyter
   ```

3. Open the analysis notebook from the `Notebook` folder. Replace the Windows-specific path in its CSV-loading cell with the extracted file's location. If Jupyter is running from the repository root, use:

   ```python
   data = pd.read_csv("Dataset/Extended_Employee_Performance_and_Productivity_Data.csv")
   ```

### SQL analysis

The queries use MySQL 8-compatible window functions and expect a database named `projects` with a table named `employee_dataset`.

The loading notebook needs `sqlalchemy` and `pymysql`, a local MySQL database, an updated CSV path and connection details. **It currently uploads underscore-separated column names, while the queries expect spaced names and an additional `Resignation` column.** Before exporting the dataframe, prepare it with:

```python
data.columns = data.columns.str.replace("_", " ", regex=False)
data["Resignation"] = data["Resigned"].map({True: "Resigned", False: "Stayed"})
```

This assumes `Resigned` was read as a Boolean column; check its dtype before mapping. The loader uses `if_exists="replace"`, so use a practice database rather than a table you need to preserve. The saved output CSVs are available for browsing without MySQL.

### Power BI and HTML

Open the `.pbix` in Power BI Desktop. Refreshing may require updating its local data-source path. Alternatively, download `index.html` and open it in a browser to view the standalone HTML dashboard.

## Current limitations

Some SQL calculations and exported materials still need reconciliation:

- Q6 and Q7 divide resigned counts by total company headcount, not the department or tenure group's headcount. Their output labels should not be read as within-group resignation rates.
- Q9 reports a pay-gap ratio under a percentage label; Q11 reports a salary index under a percentage label.
- Q13 uses company headcount for a department-level burnout percentage. Its rule is a screening assumption, not a validated burnout measure.
- Q17 uses `Promotions >= 0`, which counts every employee in this dataset as promoted.
- The report includes model and automation claims whose supporting scripts are not present in this repository. Those sections are not reproducible from the committed code.

The notebook, SQL outputs and dashboard should be checked together before using their results in a business decision.

## Author

**Mohammad Shadab**

- [LinkedIn](https://www.linkedin.com/in/mohammad-shadab-550aab24b)
- [GitHub](https://github.com/Mohammadshadab1)
- [Portfolio](https://myportfoliowebsite-lyart.vercel.app/)
- [Email](mailto:jrshadab921@gmail.com)

Project code is available under the [MIT License](LICENSE.txt). The original dataset's usage terms should be checked separately.
