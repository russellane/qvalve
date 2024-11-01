PROJECT = qvalve
include Python.mk
doc :: README.md

test :: cov_fail_under_47
cov_fail_under_47:
	python -m pytest --cov-fail-under 47 --cov=$(PROJECT) tests
