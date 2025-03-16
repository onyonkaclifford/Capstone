# EAI Capstone Project (Spring 2025)

[![CI workflow](https://github.com/onyonkaclifford/Capstone/actions/workflows/CI.yml/badge.svg?branch=master)](https://github.com/onyonkaclifford/Capstone/actions/workflows/CI.yml)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://github.com/pycqa/isort)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-red.svg)](https://github.com/pycqa/flake8)

Using a natural language interface to control a PR2 robot via CRAM

For CRAM robot documentation, go to the CRAM robot README.md file at ./cram_robot/README.md

## Development

### Linting

NOTE: This is a one-time step, and it is required if your code changes are to be pushed upstream to GitHub

Isort, black, and flake8 are used to check that code is well formatted and styled. Pre-commit hooks are used to automate
this process.

1. Install pre-commit package: `pip install pre-commit`
2. Install git hook scripts: `pre-commit install`
3. (optional) Run against all files: `pre-commit run --all-files`

## Usage

Note: Create a `.env` file with keys similar to those of `.env.sample` and fill in the correct values before proceeding
(the `.env` file is not checked into Git because it contains secrets)

- Nomal usage during development: `chainlit run ./src/app.py --port 8000 -w`

Using Docker:

1. Build image: `docker build -t capstone .`
2. Run: `docker run -dp 0.0.0.0:8000:8000 --env-file .env capstone`
