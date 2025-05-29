#!/bin/sh
echo "Generating runtime environment variables..."

cat <<EOF > /usr/share/nginx/html/env-config.js
window.ENV = {
    VITE_API_BASE_URL: "${VITE_API_BASE_URL:-http://localhost:8009}"
};
EOF

echo "env-config.js has been created successfully!"

exec "$@"  # Continue with the default command (Nginx)