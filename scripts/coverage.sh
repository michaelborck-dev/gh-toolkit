#!/bin/bash
# Coverage report script

set -e

echo "📊 Generating test coverage report..."

# Run tests with coverage
uv run pytest tests/ \
    --cov=src/gh_toolkit \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=25

echo "📈 Coverage report generated!"
echo "📄 HTML report: htmlcov/index.html"