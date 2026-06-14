# This Makefile automates build, test, and project-setup tasks.
# Language-specific recipes live in Makefile.<lang> and are auto-included
# based on the contents of .scaffold (written by `make setup_scaffold`).
# Run `make help` to see all available recipes.

.SILENT:
.ONESHELL:
.PHONY: setup_scaffold setup_toolchain setup_dev setup_claude_code setup_npm_tools setup_lychee run_markdownlint lint_md lint_links help
.DEFAULT_GOAL := help

# Auto-include language-specific Makefile when .scaffold exists
-include Makefile.$(shell cat .scaffold 2>/dev/null)


# MARK: scaffold


setup_scaffold:  ## Initialize scaffold for a language. Usage: make setup_scaffold LANG=python|embedded
	if [ -z "$(LANG)" ]; then
		echo "ERROR: LANG is required. Usage: make setup_scaffold LANG=python|embedded"
		exit 1
	fi
	case "$(LANG)" in
		python|embedded) ;;
		*)
			echo "ERROR: Unsupported LANG '$(LANG)'. Supported: python, embedded"
			exit 1
		;;
	esac
	echo "$(LANG)" > .scaffold
	echo "Scaffold set to: $(LANG)"
	echo "Run 'make setup_toolchain' to install language toolchain"

setup_toolchain:  ## Install toolchain for the active scaffold (reads .scaffold)
	if [ ! -f .scaffold ]; then
		echo "ERROR: .scaffold file not found. Run 'make setup_scaffold LANG=<lang>' first"
		exit 1
	fi
	LANG=$$(cat .scaffold)
	echo "Setting up toolchain for language: $$LANG"
	case "$$LANG" in
		python)
			pip install uv -q
			uv sync --all-groups
			$(MAKE) -s setup_npm_tools
			$(MAKE) -s setup_lychee
			echo "Python toolchain ready"
		;;
		embedded)
			if ! command -v cmake > /dev/null 2>&1; then
				echo "ERROR: cmake not found — install cmake and a C compiler first"
				exit 1
			fi
			echo "Embedded toolchain ready (cmake: $$(cmake --version | head -1))"
		;;
		*)
			echo "ERROR: Unknown language '$$LANG' in .scaffold"
			exit 1
		;;
	esac


# MARK: setup


setup_dev:  ## Install uv and deps, npm tools, lychee (python scaffold)
	echo "Setting up dev environment ..."
	pip install uv -q
	uv sync --all-groups
	echo "npm version: $$(npm --version)"
	$(MAKE) -s setup_claude_code
	$(MAKE) -s setup_npm_tools
	$(MAKE) -s setup_lychee

setup_claude_code:  ## Setup claude code CLI, node.js and npm have to be present
	echo "Setting up Claude Code CLI ..."
	npm install -gs @anthropic-ai/claude-code
	echo "Claude Code CLI version: $$(claude --version)"

setup_npm_tools:  ## Setup npm-based dev tools (markdownlint, jscpd)
	echo "Setting up npm tools ..."
	npm install -gs markdownlint-cli jscpd
	echo "markdownlint: $$(markdownlint --version), jscpd: $$(jscpd --version)"

setup_lychee:  ## Install lychee link checker (Rust binary, requires sudo)
	curl -sL https://github.com/lycheeverse/lychee/releases/latest/download/lychee-x86_64-unknown-linux-gnu.tar.gz | sudo tar xz -C /usr/local/bin lychee
	echo "lychee version: $$(lychee --version)"

# MARK: run markdownlint


run_markdownlint:  ## Lint markdown files. Usage from root dir: make run_markdownlint INPUT_FILES="docs/**/*.md"
	if [ -z "$(INPUT_FILES)" ]; then
		echo "Error: No input files specified. Use INPUT_FILES=\"docs/**/*.md\""
		exit 1
	fi
	markdownlint $(INPUT_FILES) --fix


# MARK: lint


lint_md:  ## Lint markdown files - Usage: make lint_md FILES="docs/**/*.md"
	markdownlint $${FILES:-"*.md"} --fix

lint_links:  ## Check for broken links with lychee. Usage: make lint_links [INPUT_FILES="docs/**/*.md"]
	if command -v lychee > /dev/null 2>&1; then \
		lychee $(or $(INPUT_FILES),.); \
	else \
		echo "lychee not installed — skipping link check (run 'make setup_lychee' to install)"; \
	fi


# MARK: help


help:  ## Displays this message with available recipes
	echo "Usage: make [recipe]"
	echo ""
	awk '/^# MARK:/ { \
		printf "\n\033[1;33m%s\033[0m\n", substr($$0, index($$0, ":")+2) \
	} \
	/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/) ; \
		if (helpMessage) { \
			recipe = $$1 ; \
			sub(/:/, "", recipe) ; \
			printf "  \033[36m%-24s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH) \
		} \
	}' $(MAKEFILE_LIST)
