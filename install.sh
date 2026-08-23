#!/bin/sh
set -e

# ==============================================================================
# Agent Security Gate - Universal One-Line Installer
# https://github.com/mietzen/agent-security-gate
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/mietzen/agent-security-gate/main/install.sh | sh
# ==============================================================================

REPO="mietzen/agent-security-gate"
INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.config/agent-security-gate"

echo "=== Agent Security Gate Installer ==="

# 1. Create Directories
mkdir -p "${INSTALL_DIR}"
mkdir -p "${CONFIG_DIR}"

# 2. Check Python & Dependencies
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but not found in PATH." >&2
    exit 1
fi

# Ensure PyYAML is available
if ! python3 -c "import yaml" >/dev/null 2>&1; then
    echo "Installing PyYAML dependency..."
    python3 -m pip install --quiet PyYAML || pip install --quiet PyYAML || true
fi

# 3. Install agent-guard binary
if [ -f "./bin/agent-guard" ]; then
    # Local installation from cloned repository
    cp ./bin/agent-guard "${INSTALL_DIR}/agent-guard"
    cp ./config/security_policy.yaml "${CONFIG_DIR}/security_policy.yaml"
else
    # Remote installation via curl
    echo "Fetching agent-guard from GitHub..."
    curl -fsSL "https://raw.githubusercontent.com/${REPO}/main/bin/agent-guard" -o "${INSTALL_DIR}/agent-guard"
    if [ ! -f "${CONFIG_DIR}/security_policy.yaml" ]; then
        curl -fsSL "https://raw.githubusercontent.com/${REPO}/main/config/security_policy.yaml" -o "${CONFIG_DIR}/security_policy.yaml"
    fi
fi

chmod +x "${INSTALL_DIR}/agent-guard"

# 4. Auto-configure hooks across all installed AI coding assistants
"${INSTALL_DIR}/agent-guard" init --all

# 5. Verify PATH
case ":$PATH:" in
    *":${INSTALL_DIR}:"*) ;;
    *)
        echo ""
        echo "Notice: ${INSTALL_DIR} is not in your PATH."
        echo "Add it to your ~/.zshrc or ~/.bashrc:"
        echo "  export PATH=\"\${HOME}/.local/bin:\$PATH\""
        ;;
esac

echo ""
echo "=== Installation Complete! ==="
echo "Binary : ${INSTALL_DIR}/agent-guard"
echo "Policy : ${CONFIG_DIR}/security_policy.yaml"
echo ""
echo "Test your security gate with:"
echo "  agent-guard check \"mktemp -d\""
echo "  agent-guard check \"docker run -d redis\""
echo "  agent-guard policy show"
