
link to spider:
https://yale-lily.github.io/spider

link to parts of the spider evaluation (code):
https://github.com/taoyds/spider
https://github.com/taoyds/test-suite-sql-eval

Step 1:
download the spider folder (Dataset) & insert into spider:
https://drive.google.com/file/d/1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J/view?usp=sharing

Step 2:
create .env with API_USERNAME & API_PASSWORD 

Step 3:
start generate_sql.py (maybe change model: model_name)
--> creates prediciton.txt

Step 4:
start evaluation.py to see the benchmark results 
--> creates results (terminal) + unequal.txt

Step 5:
start error_analysis.py to get more insights 
--> creates error_analysis.txt 

Results:
the generated SQL-Queries for each model can be found under generated_predictions
the results of the error analysis for each model can be found under error_analysis_results