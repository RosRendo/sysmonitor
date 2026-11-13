#!/usr/bin/env bash
# ==============================================================================
# SysMonitor Environment Preflight Check
# ==============================================================================
set -euo pipefail

echo "======================================"
echo " SysMonitor Preflight Environment Check"
echo "======================================"

# 1. Verify Linux Kernel
if [[ "$(uname -s)" != "Linux" ]]; then
    echo "[-] ERROR: SysMonitor requires a Linux environment (got: $(uname -s))."
    echo "    Please run inside WSL2, a Linux VM, or a Linux container."
    exit 1
fi
echo "[+] Operating System: Linux ($(uname -r))"

# 2. Verify /proc accessibility
if [[ -d "/proc" && -r "/proc/stat" && -r "/proc/meminfo" ]]; then
    echo "[+] /proc filesystem: Accessible and readable"
else
    echo "[-] ERROR: Cannot read /proc/stat or /proc/meminfo."
    exit 1
fi

# 3. Verify Python 3
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version)
    echo "[+] Python runtime: $PY_VER"
else
    echo "[-] ERROR: python3 is not installed or not in PATH."
    exit 1
fi

# 4. Verify Git
if command -v git &>/dev/null; then
    echo "[+] Git: Installed ($(git --version))"
else
    echo "[!] WARNING: git is not installed (recommended for version control)."
fi

echo "======================================"
echo " Environment is READY for SysMonitor!"
echo "======================================"

