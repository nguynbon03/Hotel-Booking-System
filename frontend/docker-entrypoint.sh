#!/bin/sh

# ============================================================
# 🚀 Frontend Docker Entrypoint Script
# ============================================================

set -e

# Default values
VITE_API_URL=${VITE_API_URL:-"http://localhost:8000"}

# Generate environment configuration
cat > /usr/share/nginx/html/env.js << EOF
window.ENV = {
  VITE_API_URL: "${VITE_API_URL}",
  NODE_ENV: "${NODE_ENV:-production}"
};
EOF

echo "🚀 Frontend environment configured:"
echo "   API_URL: ${VITE_API_URL}"
echo "   NODE_ENV: ${NODE_ENV:-production}"

# Execute the main command
exec "$@"
