#!/bin/bash
set -e

echo "Seeding development data..."

# Create a test firm and get the API key
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/admin/firms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Trading Firm",
    "slug": "demo-firm",
    "plan_tier": "growth"
  }')

echo "Firm created:"
echo "$RESPONSE" | python3 -m json.tool

API_KEY=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))")

if [ -n "$API_KEY" ]; then
    echo ""
    echo "API Key: $API_KEY"
    echo ""
    echo "Test with:"
    echo "  curl -X POST http://localhost:8000/api/v1/messages \\"
    echo "    -H 'X-API-Key: $API_KEY' \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"channel\": \"web_chat\", \"sender_channel_id\": \"test-user-1\", \"content\": \"How do I request a payout?\"}'"
fi
