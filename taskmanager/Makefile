.PHONY: runserver fixmymess
runserver:
	python taskmanager/manage.py runserver 0.0.0.0:8000
fixmymess:
	ruff check
	ruff format