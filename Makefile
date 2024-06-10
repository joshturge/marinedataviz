FLASK_VARS = FLASK_APP=tasman FLASK_ENV=development

.MAIN: run
.PHONY: test run 

venv/bin/activate: requirements.txt
	python3 -m venv venv 
	pip install -r requirements.txt

test: 
	python3 -m unittest discover -p "*_test.py" -s "tests/"

run:
	$(FLASK_VARS) flask run

