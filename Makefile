install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install pandas
	.venv/bin/pip install scikit-learn
	.venv/bin/pip install skops
	.venv/bin/pip install matplotlib



format:
	black *.py

train:
	.venv/bin/python train.py

eval:
	echo "## Model Metrics" > report.md
	cat ./results/metrics.txt >> report.md
   
	echo '\n## Confusion Matrix Plot' >> report.md
	echo '![Confusion Matrix](./results/model_results.png)' >> report.md
   
	cml comment create report.md