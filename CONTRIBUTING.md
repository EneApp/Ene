# Requirements

Python3.6+

# Setting up the development environment

1. Install [poetry](https://github.com/sdispater/poetry)

2. Create a virtual environment

```bash
python3 -m venv ene
source ene/bin/activate
```

3. Install dev dependencies

```bash
poetry install
```

# Coding Style

All code (including tests) must pass `flake8` check.

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) with a few modifications:

1. Preferable line length is under 80 characters per line, hard limit is 100 characters per line. If you are going to break lines, break at the 80th character

2. Strings are single quoted, unless there are single quotes in the string, then they are double quoted.
