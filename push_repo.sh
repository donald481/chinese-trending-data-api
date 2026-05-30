#!/bin/bash
# Push repo to GitHub - needs TOKEN with repo scope
if [ -z "$GITHUB_TOKEN" ]; then echo "ERROR: Set GITHUB_TOKEN env var"; exit 1; fi

REPO_NAME="chinese-trending-data-api"
API_URL="https://api.github.com/user/repos"

# Create repo
echo "Creating repo $REPO_NAME..."
RESULT=$(curl -s -X POST "$API_URL" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$REPO_NAME\",\"description\":\"The pulse of China, in one API. 3500+ trends from 8 Chinese platforms with LLM-translated English. Webhook notifications, cross-platform comparison, category filtering.\",\"public\":true,\"homepage\":\"http://161.153.56.113:8900/\"}")

CLONE_URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('clone_url','ERROR'))" 2>/dev/null)
echo "Clone URL: $CLONE_URL"

if [ "$CLONE_URL" = "ERROR" ] || [ -z "$CLONE_URL" ]; then
  echo "Failed to create repo. Response:"
  echo "$RESULT" | head -10
  exit 1
fi

# Set remote and push
cd /home/ubuntu/projects/arbitrage_api
git remote remove origin 2>/dev/null
git remote add origin "$CLONE_URL"
git push -u origin master

echo "DONE! Repo pushed to $CLONE_URL"
