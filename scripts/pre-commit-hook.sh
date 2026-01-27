#!/bin/bash
# Market Cockpit Pro - Pre-commit Hook
# ================================================================================
# This hook runs before each commit to verify that:
# 1. All indicators in indicators.py are referenced in their respective pages
# 2. i18n translations are consistent
#
# If any check fails, the commit is blocked.
# ================================================================================

echo "🔍 Running pre-commit verification..."
echo ""

# Get the project root (where .git is located)
PROJECT_ROOT=$(git rev-parse --show-toplevel)

# Run baseline verification
echo "📊 Checking indicator references..."
python "$PROJECT_ROOT/scripts/verify_baseline.py"
BASELINE_STATUS=$?

if [ $BASELINE_STATUS -ne 0 ]; then
    echo ""
    echo "❌ Baseline verification failed!"
    echo "   Some indicators may be missing from their UI pages."
    echo "   Please fix the issues above before committing."
    echo ""
    exit 1
fi

echo ""
echo "✅ All pre-commit checks passed!"
echo ""
exit 0
