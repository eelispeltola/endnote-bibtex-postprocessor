# Bibtex postprocessor for Endnote

Process the `bibtex` file from Endnote into a nicer format:

* Citation names are changed into the format `[first author's surname][year][first word(s) from title]`.
* Filename is written with `.bib` suffix instead of `.txt`
* Filename's whitespaces are converted to underscores
* (Optionally: all notes are removed from the resulting bibliography)
* (Optionally: Encase all titles inside curly braces to preserve their capitalization)

##  Setup

### User setup (Linux/Mac)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Usage

To postprocess an EndNote-generated `bibtex` file into a format allowed by
Overleaf, try the following:

```bash
source .venv/bin/activate
bibtex-postprocessor "path/to/My EndNote Library.txt"
```

See the internal documentation for full usage instructions:

```bash
bibtex-postprocessor --help
```

## Development

### Dev setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
pre-commit install
```

### Linting, formatting, and typechecks

This project uses the following tools for autoformatting, linting and typechecking:

* mypy: typechecks
* ruff: linting and formatting

Pre-commit hooks are used to run these tools automatically when committing to git.

### Pre-commit hooks

Pre-commit hooks check and fix formatting before committing. To use them, after installing `requirements-dev.txt`, install them with `pre-commit install`. The next time you commit (or when you run `pre-commit run`), the hooks will run. If any hooks fail, `git add` the failed and reformatted files again and try `git commit` again. If the hooks still fail, you might need to manually fix errors in the files.

Update hook versions easily with `pre-commit autoupdate`.
