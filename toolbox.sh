#!/bin/bash

setup () {
	# Setup dirs.
	mkdir -p data/{databases,media,logs,tmp,reports}
	# Create blank db if does not exist.
	touch data/databases/data.db
	# Install dependencies.
	pip3 install -r requirements.txt
}

run_tests () {
	rm -rf data/reports
	mkdir data/reports
	# Run tests/ with coverage.
	pytest --cov-config=setup.cfg
	# Run flake8 and generate report in reports dir!
	flake8 > data/reports/flake8.txt
}

clean_data () {
	# Delete all generated data, leave code and venv.
	rm -rf __pycache__ data/logs data/reports data/tmp
	#rm data/databases/data.db #TODO ask first before nuking whole db lol.
	rm data/tmp/*
}


select opt in setup run_tests clean_data quit; do
	case $opt in
		setup) 
			setup
			exit;;
		run_tests) 
			run_tests 
			exit;;
		clean_data) 
			clean_data 
			exit;;
		quit) 
			break;;
		*) 
			echo "Wrong option!";;
	esac
done
