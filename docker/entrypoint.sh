#!/bin/bash
# Docker entrypoint script
# Environment variable'ları kontrol eder ve demo.py'yi çalıştırır

set -e

echo "🚀 BSM307 Multi-Objective Routing - Docker Container"
echo "=================================================="

# Environment variables kontrolü
echo "📋 Environment Variables:"
echo "   PYTHONPATH: ${PYTHONPATH:-/app}"
echo "   MPLBACKEND: ${MPLBACKEND:-Agg}"
echo "   EXPERIMENT_SEED: ${EXPERIMENT_SEED:-42}"
echo "   NUM_NODES: ${NUM_NODES:-250}"
echo "   EDGE_PROB: ${EDGE_PROB:-0.4}"
echo ""

# Python path kontrolü
if [ ! -d "/app/src" ]; then
    echo "❌ Error: /app/src directory not found!"
    exit 1
fi

# Demo script'i çalıştır
echo "▶️  Starting demo script..."
exec python demo.py "$@"

