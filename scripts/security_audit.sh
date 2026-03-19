#!/bin/bash
# Dependency security audit
set -e
echo "=== Running pip-audit ==="
pip-audit
echo ""
echo "=== Audit complete ==="
