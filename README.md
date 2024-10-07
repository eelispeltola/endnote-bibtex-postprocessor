# Bibtex postprocessor for Endnote

Process the `bibtex` file from Endnote into a nicer format:

* Citation names are changed into the format `[first author's surname][year][first word from title]`.
* Filename is written with `.bib` suffix instead of `.txt`

##  Setup

### User setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .
```

### Dev setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
pre-commit install
```

## Usage

```bash
source .venv/bin/activate  # If not already in virtualenv
bibtex-postprocessor --help
```

## Linting, formatting, and typechecks

This project template uses the following tools for autoformatting, linting and typechecking:

* mypy: typechecks
* ruff: linting and formatting

Pre-commit hooks are used to run these tools automatically when committing to git.

### Pre-commit hooks

Pre-commit hooks check and fix formatting before committing. To use them, after installing `requirements-dev.txt`, install them with `pre-commit install`. The next time you commit (or when you run `pre-commit run`), the hooks will run. If any hooks fail, `git add` the failed and reformatted files again and try `git commit` again. If the hooks still fail, you might need to manually fix errors in the files.

Update hook versions easily with `pre-commit autoupdate`.
