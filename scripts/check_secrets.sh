#!/bin/bash

# Script to check if all required secrets are configured in GitHub
# Run this locally to verify your setup

echo "🔍 Checking GitHub Secrets Configuration..."
echo "=========================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install it from: https://cli.github.com/"
    echo "   Then run: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# List of required secrets
REQUIRED_SECRETS=(
    "FLY_API_TOKEN"
    "TELEGRAM_BOT_TOKEN"
)

OPTIONAL_SECRETS=(
    "AUTODEV_API_KEY"
    "CARSXE_API_KEY"
    "UPSTASH_REDIS_REST_URL"
    "UPSTASH_REDIS_REST_TOKEN"
    "HTTP_TIMEOUT_SECONDS"
    "LOG_LEVEL"
)

echo "📋 Checking Required Secrets:"
echo "----------------------------"

missing_required=0
for secret in "${REQUIRED_SECRETS[@]}"; do
    if gh secret list | grep -q "^$secret"; then
        echo "✅ $secret - Set"
    else
        echo "❌ $secret - MISSING (Required)"
        missing_required=1
    fi
done

echo ""
echo "📋 Checking Optional Secrets:"
echo "----------------------------"

for secret in "${OPTIONAL_SECRETS[@]}"; do
    if gh secret list | grep -q "^$secret"; then
        echo "✅ $secret - Set"
    else
        echo "⚠️  $secret - Not set (Optional)"
    fi
done

echo ""
echo "🔧 Current Fly.io App Secrets:"
echo "-----------------------------"

# Check if flyctl is installed
if command -v flyctl &> /dev/null; then
    if flyctl secrets list --app vinbot-decoder 2>/dev/null; then
        echo "✅ Successfully retrieved Fly.io secrets"
    else
        echo "❌ Could not retrieve Fly.io secrets"
        echo "   Make sure you're authenticated: flyctl auth login"
        echo "   And the app exists: flyctl apps list"
    fi
else
    echo "⚠️  flyctl not installed - cannot check Fly.io secrets"
    echo "   Install from: https://fly.io/docs/hands-on/install-flyctl/"
fi

echo ""
if [ $missing_required -eq 0 ]; then
    echo "🎉 All required secrets are configured!"
    echo "   Your GitHub Actions should now work correctly."
else
    echo "💥 Missing required secrets!"
    echo "   Add them in GitHub: Settings → Secrets and variables → Actions"
fi

echo ""
echo "📚 Need help setting up secrets?"
echo "   See: docs/GITHUB_SECRETS_SETUP.md"