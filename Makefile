###############################################################
# Makefile Structure
# ==================
#
# This Makefile is used to manage the project. It defines the following targets:
#
# - helpcol: This is the default target. It shows a help message with the available targets and their descriptions.
# - preview: Preview the documentation with nbdev_preview on port $SERVE_PORT, default 8888.
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
# - To preview the documentation with nbdev_preview, run `make preview`.
# - To enable automatict export on modification in nbs/ folder, run `make export_on_modify`, nbdev_preview will live autoreload.
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
# define default target
.DEFAULT_GOAL := helpcol
# default port to serve the documentation at, use can overwrite this at runinng time
SERVE_PORT?=8888

###############################################################
# Main targets
#-------------
preview: ## preview documentsion with nbdev_preview on port $SERVE_PORT, default 8888
	nbdev_preview --port ${SERVE_PORT}

export_on_modify : ## watch the nbs/ directory for modification with inotifywait and run nbdev_export on changes
	inotifywait -m -e modify nbs/ | while read path action file; do     echo "file mod detected: $${file}"; nbdev_export ; done

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
	py.test --verbose --color=yes

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
