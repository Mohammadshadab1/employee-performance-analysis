PY ?= python3

all: analysis dashboard report pptx workbook

analysis:
	$(PY) src/analysis.py

dashboard: analysis
	$(PY) src/build_dashboard.py

report: analysis
	$(PY) src/build_report.py

pptx: analysis
	$(PY) src/build_pptx.py

workbook: analysis
	$(PY) src/build_workbook.py

clean:
	rm -f charts/*.png assets/summary.json assets/dashboard_data.json \
	      dashboard.html report.pdf presentation.pptx Employee_Insights.xlsx

.PHONY: all analysis dashboard report pptx workbook clean
