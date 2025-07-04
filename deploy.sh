#!/usr/bin/env bash
set -euo pipefail

# CONFIGURATION — replace or export these beforehand
HEROKU_APP_NAME="${HEROKU_APP_NAME:-vitanet-hospital}"
GIT_REMOTE="${GIT_REMOTE:-origin}"
BRANCH="${BRANCH:-main}"

# 1) Run tests
echo "🧪 Running pytest…"
pytest

# 2) Stage & commit
echo "📝 Staging changes…"
git add .
MSG="Auto deploy: $(date +'%Y-%m-%d %H:%M:%S')"
git commit -m "$MSG" || echo "No changes to commit."

# 3) Push to GitHub (triggers CI → Heroku)
echo "🚀 Pushing to $GIT_REMOTE/$BRANCH…"
git push "$GIT_REMOTE" "$BRANCH"

# 4) (Optional) Follow logs & open site
echo "⏳ Waiting for Heroku to deploy…"
heroku logs --tail --app "$HEROKU_APP_NAME" &
sleep 5
if command -v xdg-open &> /dev/null; then
  xdg-open "https://${HEROKU_APP_NAME}.herokuapp.com"
elif command -v open &> /dev/null; then
  open "https://${HEROKU_APP_NAME}.herokuapp.com"
else
  echo "👉 Visit https://${HEROKU_APP_NAME}.herokuapp.com in your browser"
fi

