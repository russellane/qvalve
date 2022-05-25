# russellane/Python.mk

build::		__pypackages__ ctags lint test coverage doc
		pdm build

bump_micro::	_bump_micro clean build
_bump_micro:
		pdm bump micro

publish::
		cd dist; echo *.whl | cpio -pdmuv `pip config get global.find-links`

install::
		-pipx uninstall $(PROJECT)
		pipx install $(PROJECT)

__pypackages__:
		pdm install

.PHONY:		ctags
ctags::
		ctags -R $(PROJECT) tests __pypackages__ 

lint::		black isort flake8

black::
		python -m black -q $(PROJECT) tests

isort::
		python -m isort $(PROJECT) tests

flake8::
		python -m flake8 $(PROJECT) tests

test::
		python -m pytest --exitfirst --showlocals --verbose tests

test_debug::
		python -m pytest --exitfirst --showlocals --verbose --capture=no tests

coverage::
		python -m pytest --cov=$(PROJECT) tests

cov_html::
		python -m pytest --cov=$(PROJECT) --cov-report=html tests
		xdg-open htmlcov/index.html

clean::
		rm -rf .coverage .pytest_cache __pypackages__ dist htmlcov tags 
		find . -type f -name '*.py[co]' -delete
		find . -type d -name __pycache__ -delete

doc:: ;

# put `doc :: README.md` into Makefile, if desired
.PHONY:		README.md
README.md:
		python -m $(PROJECT) --md-help >$@

# vim: set ts=8 sw=8 noet:
