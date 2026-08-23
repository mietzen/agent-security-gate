#!/bin/sh
set -e

# ==============================================================================
# Agent Security Gate - Updater Script
# https://github.com/mietzen/agent-security-gate
# ==============================================================================

REPO="mietzen/agent-security-gate"
INSTALL_DIR="${HOME}/.local/bin"

echo "Updating Agent Security Gate..."
curl -fsSL "https://raw.githubusercontent.com/${REPO}/main/bin/agent-guard" -o "${INSTALL_DIR}/agent-guard"
chmod +x "${INSTALL_DIR}/agent-guard"

echo "✓ Agent Security Gate updated to latest version!"
"${INSTALL_DIR}/agent-guard" --version
