#!/bin/bash
# Test runner script

set -e

echo "🧪 Running gh-toolkit test suite..."

# Unit tests
echo "📋 Running unit tests..."
uv run pytest tests/unit/ -v

# Integration tests  
echo "🔗 Running integration tests..."
uv run pytest tests/integration/ -v

echo "✅ All tests completed!"