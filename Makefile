install:
	python3 -m venv .venv
	. .venv/bin/activate &&\
	pip install --upgrade pip &&\
	pip install -r requirements.txt
	pip install pandas



format:
	black *.py

train:
	. .venv/bin/activate &&\
	python train.py

eval:
	echo "## Model Metrics" > report.md
	cat ./Results/metrics.txt >> report.md
   
	echo '\n## Confusion Matrix Plot' >> report.md
	echo '![Confusion Matrix](./Results/model_results.png)' >> report.md
   
	cml comment create report.md