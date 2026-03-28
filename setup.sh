#!/bin/bash
# Setup the image generation MCP server virtual environment.
#
# Usage:
#   bash setup.sh            # creates venv in ./venv
#   bash setup.sh /path/to   # creates venv at custom location
#
# After setup, add to .cursor/mcp.json:
#   "mcp-image-gen": {
#     "command": "<venv>/bin/python",
#     "args": ["<this-dir>/server.py"]
#   }

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="${1:-$SCRIPT_DIR/venv}"

echo "=== MCP Image Gen Server Setup ==="
echo "Directory: $SCRIPT_DIR"
echo "Venv path: $VENV_PATH"
echo ""

if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

source "$VENV_PATH/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q

echo "Installing optimum-intel from git (latest model support)..."
pip install "git+https://github.com/huggingface/optimum-intel.git" --extra-index-url https://download.pytorch.org/whl/cpu -q

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Python: $VENV_PATH/bin/python"
echo "Server: $SCRIPT_DIR/server.py"
echo ""
echo "Add to your .cursor/mcp.json:"
echo ""
echo "  \"mcp-image-gen\": {"
echo "    \"command\": \"$VENV_PATH/bin/python\","
echo "    \"args\": [\"$SCRIPT_DIR/server.py\"]"
echo "  }"
echo ""
echo "Models will download from HuggingFace on first use."
