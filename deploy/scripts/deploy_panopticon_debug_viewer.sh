#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$HOME/projects/moscaquant}"
WEB_ROOT="${WEB_ROOT:-/var/www/moscaquant/panopticon}"
FEED_ROOT="${FEED_ROOT:-/var/lib/moscaquant/panopticon}"
NGINX_SNIPPET_DST="${NGINX_SNIPPET_DST:-/etc/nginx/snippets/moscaquant-panopticon-public-feed.conf}"

echo "[1/5] Installing Panopticon debug viewer assets"
sudo mkdir -p "$WEB_ROOT"
sudo rsync -a --delete \
  "$REPO_ROOT/panopticon/debug_viewer/" \
  "$WEB_ROOT/"

echo "[2/5] Creating public feed directory"
sudo mkdir -p "$FEED_ROOT"
sudo chown "$USER":"$USER" "$FEED_ROOT"
chmod 0755 "$FEED_ROOT"

echo "[3/5] Publishing initial public-safe reference frame"
python "$REPO_ROOT/deploy/scripts/publish_initial_panopticon_frame.py" \
  "$FEED_ROOT/latest-render-frame.json"

chmod 0644 "$FEED_ROOT/latest-render-frame.json"

echo "[4/5] Installing Nginx snippet"
sudo install -m 0644 \
  "$REPO_ROOT/deploy/nginx/panopticon-public-feed.conf.example" \
  "$NGINX_SNIPPET_DST"

echo
echo "Add these lines INSIDE the existing TLS server block for moscaquant.com:"
echo
echo "    include $NGINX_SNIPPET_DST;"
echo
echo "    location /panopticon/ {"
echo "        alias $WEB_ROOT/;"
echo "        index index.html;"
echo "        try_files \$uri \$uri/ /panopticon/index.html;"
echo "    }"
echo
echo "[5/5] Validate after editing Nginx"
echo "    sudo nginx -t"
echo "    sudo systemctl reload nginx"
echo
echo "Then verify:"
echo "    curl -fsS https://moscaquant.com/api/panopticon/render-frame | python -m json.tool"
echo "    curl -I https://moscaquant.com/panopticon/"
echo
echo "Panopticon debug viewer files are deployed."
echo "Nginx is NOT modified automatically beyond installing the snippet."
