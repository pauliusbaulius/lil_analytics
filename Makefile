build:
	@sudo docker-compose up --build

lint:
	@echo "\nBLACK"
	@black api/ bot/ --config pyproject.toml
	@echo "\nISORT"
	@isort api/ bot/
