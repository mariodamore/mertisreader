###############################################################
# Makefile Structure
# ==================
#
# This Makefile is used to manage the project. It defines the following targets:
#
# - helpcol: This is the default target. It shows a help message with the available targets and their descriptions.
# - preview: Preview the documentation with Quarto on port $SERVE_PORT, default 8888.
# - render: Render the Quarto documentation site.
#
# Requirements
# ------------
#
# - Python environment: Make sure to activate the appropriate virtual environment before running the Makefile.
#
# Configuration
# -------------
#
# - SERVE_PORT: This is the default port to serve the documentation at. You can overwrite this at run time.
#
# Usage
# -----
#
# - To show the available targets and their descriptions, run `make helpcol`.
# - To preview the documentation with Quarto, run `make preview`.
# - To render the documentation site, run `make render`.
#
# Note
# ----
#
# The Makefile is inspired by the article "Makefiles in Python projects" by Krzysztof Żuraw,
# see https://krzysztofzuraw.com/makefiles-in-python/
#
###############################################################
# Defintions
#-----------
.DEFAULT_GOAL := helpcol
SERVE_PORT ?= 8888

###############################################################
# Main targets
#-------------

quartodoc-build: ## build the quartodoc API reference pages into reference/
	python -m quartodoc build

readme: ## render the Quarto-backed README.md from README.qmd
	quarto render README.qmd --to gfm --output README.md

preview: quartodoc-build ## preview documentation with quarto preview on port $SERVE_PORT, default 8888
	quarto preview --port ${SERVE_PORT}

render: quartodoc-build readme ## render the Quarto documentation site and refresh README.md
	quarto render

install_develop :  ## install the package in editable mode with docs extras
	python -m pip install --verbose --editable ".[docs]"

###############################################################
# Cleaning targets
#-----------------
clean-pyc: ## remove all pyc, pyo and __pycache__
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '__pycache__'  -exec rm -rf {} +

clean-build: ## clean all build products
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

###############################################################
# Testing targets
#----------------
test: clean-pyc ## run clean-pyc and test
	pytest --verbose --color=yes

#################################################################################
# Self Documenting Commands                                                     #

help: ## Show help. Only lines with ": ##" will show up! This is a plain help, requires only grep+sed.
	@(echo "Available rules>target>description"; grep -h "^[A-z].*:.* ## " $(MAKEFILE_LIST) | sed 's/#/>/;s/:/>/' ) | column -t -s '>'

helpcol: ## Show help. Only lines with ": ##" will show up! This require columns. Shows: rules(green), targets(red), description.
	@(echo "$$(tput bold;tput setaf 6)Available rules>$$(tput sgr0;tput setaf 1) target$$(tput sgr0)>description"; \
	grep -E -h "^[A-z].*:.* ## " $(MAKEFILE_LIST) |\
	sed 's/#/>/;s/:/>/' |\
	sed -E -e 's/([^>]+)\s?>([^>]+)\s?>(.*)/'$$(tput setaf 6)'\1>'$$(tput setaf 1)'\2'$$(tput sgr0)'>\3/' ) |\
	column -t -s '>' | sort
