use projects;
-- ======================================================================
-- 1. WORKFORCE STRUCTURE & DEMOGRAPHICS
-- ======================================================================
-- Query 1: Department Distribution
-- Calculates total employee headcount workforce percentage share across each department.
select
	Department,
    count(`Employee ID`) as Head_count,
    round((count(`Employee ID`)/(select count(*) from employee_dataset))*100,2) as Distribution_Percentage
from employee_dataset
group by Department;

-- Query 2: Gender Demographics Across Departments and Job Roles
-- Evaluates workforce composition and overall representation broken down by Department, Role, and Gender.
select
	Department, Gender, `Job Title`,
    count(`Employee ID`) as Head_count,
    round((count(`Employee ID`)/(select count(*) from employee_dataset))*100,2) as Distribution_Percentage
from employee_dataset
group by Department, Gender, `Job Title`
order by Department, `Job Title`;

-- Query 3: Workforce Distribution by Education Level
-- Measures employee counts and company-wide percentage share based on educational attainment.
select
	`Education Level`,
    count(`Employee ID`) as Head_count,
    round((count(`Employee ID`)/(select count(*) from employee_dataset))*100,2) as Distribution_Percengtage
from employee_dataset
group by `Education Level`;

-- Query 4: Baseline Workforce Summary Metrics
-- Computes company-wide central tendencies for compensation, age, overtime commitments, and regular weekly hours.
select
	round(avg(`Monthly Salary`),2) as Average_monthly_salary,
    round(avg(Age)) as Average_age,
    round(avg(`Overtime Hours`),2) as Average_Overtime_Hours,
    round(avg(`Work Hours Per Week`),2) as Average_work_hour_per_week
from employee_dataset;

-- =============================================================================
-- 2. ATTRITION & TURNOVER ANALYSIS
-- =============================================================================

-- Query 5: Overall Attrition Rate
-- Calculates the company-wide churn benchmark: proportion of departed 
select
	round(count(*)/(select count(*) from employee_dataset)*100,2) as Attrition_Rate
from employee_dataset
where Resignation="Resigned";

-- Query 6: Department-Wise Attrition Share
-- Determines the proportion of company-wide turnover occurring within each specific functional area.
select
	Department,
    round(count(*)/(select count(*) from employee_dataset)*100,2) as Attrition_Rate
from employee_dataset
where Resignation="Resigned"
group by Department;

-- Query 7: Tenure vs. Resignation
-- Ranks attrition frequency by years of company service to identify critical turnover milestones.
select
	`Years At Company`,
    round(count(*)/(select count(*) from employee_dataset)*100,2) as Attrition_Rate
from employee_dataset
where Resignation="Resigned"
group by `Years At Company`
order by round(count(*)/(select count(*) from employee_dataset)*100,2) desc;

-- Query 8: Satisfaction vs. Turnover Comparison
-- Compares average employee satisfaction scores between active personnel and departed staff.
select
	Resignation,
    count(`Employee ID`) as Employee_Count,
	round(avg(`Employee Satisfaction Score`),2) as AVG_Satisfaction_Score
from employee_dataset
group by Resignation;

-- =============================================================================
-- 3. COMPENSATION & PAY EQUITY
-- =============================================================================

-- Query 9: Controlled Gender Pay Gap Analysis
-- Benchmarks Male vs Female compensation across normalized job titles and standardized tenure tiers.
with salary_comparison as(
select
	`Job Title`,
    case
		when `Years At Company` <=2 then "Entry"
        when `Years At Company` <=5 then "Mid"
        when `Years At Company` <=8 then "Senior"
	else "Lead"
    end as Experience_Band,
    count(case when Gender="Male" then 1 end) as Male_count,
    round(avg(case when Gender="Male" then`Monthly Salary` end),2) as Male_AVG_Salary,
	count(case when Gender="Female" then 1 end) as Female_count,
    round(avg(case when Gender="Female" then`Monthly Salary` end),2) as Female_AVG_Salary,
	count(case when Gender="Other" then 1 end) as Others_count,
    round(avg(case when Gender="Other" then`Monthly Salary` end),2) as Others_AVG_Salary
from employee_dataset
group by `Job Title`, Experience_Band
order by `Job Title`)
select
	`Job Title`,
    Experience_Band,
    Male_count,
    Male_AVG_Salary,
    Female_count,
    Female_AVG_Salary,
    Others_count,
    Others_AVG_Salary,
    round(Male_AVG_Salary-Female_AVG_Salary, 2) as Salary_Difference,
    round((Male_AVG_Salary-Female_AVG_Salary)/Male_AVG_Salary, 3) as Pay_Gap_Percentage
from salary_comparison
order by `Job Title`, Experience_Band;

-- Query 10: Departmental Top Earners
-- Identifies the top 3 highest-earning individual compensation packages within each department.
with ranked as(
select
	Department,
	`Employee ID`,
    `Monthly Salary`,
    row_number() over(
		partition by Department
        order by `Monthly Salary` desc) as rn
from employee_dataset)

select * from ranked
where rn<=3;

-- Query 11: Education Premium Index
-- Measures salary distribution and relative earnings premium indexed against the High School baseline.
select
	`Education Level`,
    round(avg(`Monthly Salary`)) as AVG_Monthly_Salary,
    min(`Monthly Salary`) as MIN_Monthly_Salary,
    max(`Monthly Salary`) as MAX_Monthly_Salary,
    round(avg(`Monthly Salary`)/(select 
										avg(`Monthly Salary`) 
									from employee_dataset
									where `Education Level`="High School"),3) as "Salary_difference%"
from employee_dataset
group by `Education Level`;


-- Query 12: Underpaid Top Performers
-- Flags high-performing employees (Score > 4) who are compensated below their departmental average salary.
-- Underpaid High Performers --
with salary_data as(
select
	`Employee ID`,
    Department,
    `Job Title`,
    `Performance Score`,
    `Monthly Salary`,
    round(avg(`Monthly Salary`)over(
			partition by Department)) as AVG_Monthly_Salary
from employee_dataset)
select *
from salary_data
where `Performance Score` >4 and `Monthly Salary`< AVG_Monthly_Salary;
  
  
-- =============================================================================
-- 4. WELL-BEING, BURNOUT & WORK MODES
-- =============================================================================

-- Query 13: Departmental Severe Burnout Risk
-- Tracks staff exceeding 50 hrs/week and 20 overtime hrs with satisfaction below 2.5.
select
	Department,
	count(case
				when `Work Hours Per Week` >50 and
                `Employee Satisfaction Score`<2.5 and
                `Overtime Hours`>20 then 1 end) as High_Burnout_Count,
	round(count(case
				when `Work Hours Per Week` >50 and
                `Employee Satisfaction Score`<2.5 and
                `Overtime Hours`>20 then 1 end)/
                (select count(*) from employee_dataset)*100,2) as "High_Burnout%"
from employee_dataset
group by Department
order by High_Burnout_Count desc;

-- Query 14: Overtime vs. Absenteeism Correlation
-- Evaluates whether excessive overtime commitments correspond to increased employee sick day usage.
select
	case
		when `Overtime Hours` = 0 then "No Overtime (0 Hours)"
        when `Overtime Hours` between 1 and 10 then "Low (1-10 Hours)"
		when `Overtime Hours` between 11 and 25 then "Moderate (11-25 Hours)"
        else "Extreme (>25 Hours)"
	end as overtime_tier,
    count(`Employee ID`) as Employee_Count,
    round(avg(`Sick Days`),2) as AVG_Sick_Days,
    min(`Sick Days`) as Min_Sick_Days,
    max(`Sick Days`) as Max_Sick_Days
from employee_dataset
group by overtime_tier
order by AVG_Sick_Days desc;

-- Query 15: Impact of Work Mode Flexibility
-- Evaluates satisfaction, workload parameters, and attrition rates across Onsite, Hybrid, and Remote arrangements.
select
	case
		when `Remote Work Frequency`=0 then "On Site"
        when `Remote Work Frequency`=100 then "Fully Remote"
        else "HyBrid"
	end as WorK_Mode,
    count(`Employee ID`) as Employee_Count,
    round(avg(`Employee Satisfaction Score`),2) as AVG_Employee_Satisfaction,
    round(avg(`Work Hours Per Week`),2) as AVG_Work_Hrs_Per_Week,
    round(avg(`Overtime Hours`),2) as AVG_Overtime_Hrs,
    count(case
		when Resignation = "Resigned" then 1
	end) as resigned_count,
    round(count(case
		when Resignation = "Resigned" then 1
	end)/count(`Employee ID`)*100,2) as "Attrition_rate%"
from employee_dataset
group by Work_Mode
order by "Attrition_rate%";

-- =============================================================================
-- 5. PERFORMANCE, PROMOTION & L&D ROI
-- =============================================================================

-- Query 16: Performance-to-Promotion Alignment
-- Evaluates meritocratic progression by assessing whether top-tier performance ratings correlate with promotions.
select 
	`Performance Score`,
    count(`Employee ID`) as Headcount,
    round(avg(`Work Hours Per Week`),2) as AVG_Work_HRS,
    sum(Promotions) as Promotion_Count,
    round(avg(Promotions)) as AVG_Promotion,
    round(avg(`Employee Satisfaction Score`),2) as AVG_Satisfaction
from employee_dataset
group by `Performance Score`
order by `Performance Score` desc;

-- Query 17: Learning & Development (L&D) Training ROI
-- Analyzes whether higher training volume yields higher performance scores and accelerated promotions.
select
	case
		when `Training Hours` <20 then "1. Low Training (<20)"
        when `Training Hours` between 20 and 49 then "2. Moderate (20-49)"
        when `Training Hours` between 50 and 79 then "3. High (50-79)"
        else "4. Extensive (80+)"
	end as Training_Tier,
    count(`Employee ID`) as Headcount,
    round(avg(`Training Hours`),2) as AVG_Training_HRS,
    round(avg(`Performance Score`),2) as AVG_Performance_Score,
    round(avg(Promotions),2) as AVG_Promotion,
    round(avg(case when `Performance Score` >=4 then 100.0 else 0.0 end),2) as Top_Performer_Pct,
    round(avg(case when Promotions >=0 then 100.0 else 0.0 end),2) as Promoted_Employee_Pct
from employee_dataset
group by Training_Tier
order by Training_Tier;

-- =============================================================================
-- 6. ADVANCED SEGMENTATION
-- =============================================================================

-- Query 18: Intra-Department Salary Quartile Segmentation
-- Segments each department's workforce into 4 equal salary quartiles (NTILE) to assess internal pay dispersion.
with ranked_employees as(
select
	`Employee ID`,
    Department,
    `Job Title`,
    `Monthly Salary`,
    ntile(4) over(
		partition by Department
        order by `Monthly Salary` asc) as Quartile
from employee_dataset)

select
	Department,
    case
		when Quartile = 1 then "Q1 (Bottom 25%)"
        when Quartile = 2 then "Q2 (25%-50%)"
        when Quartile = 3 then "Q3 (50%-75%)"
        else "Q4 (75%-100%)"
	end as Salary_Band,
    count(`Employee ID`) as Headcount,
	round(avg(`Monthly Salary`)) as AVG_Monthly_Salary,
    round(min(`Monthly Salary`)) as Min_Monthly_Salary,
    round(max(`Monthly Salary`)) as Max_Monthly_Salary
from ranked_employees
group by Department, Quartile, Salary_Band
order by Quartile;