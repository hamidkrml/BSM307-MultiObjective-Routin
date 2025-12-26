#!/bin/bash
# Docker helper script - Mac için kolay kullanım

set -e

MODE=${1:-dev}

case "$MODE" in
    dev)
        echo "🚀 Development mode başlatılıyor..."
        docker-compose --profile dev up
        ;;
    prod)
        echo "🚀 Production mode başlatılıyor..."
        docker-compose --profile prod up
        ;;
    gui)
        echo "🚀 GUI mode başlatılıyor..."
        echo "⚠️  XQuartz'ın çalıştığından ve 'Allow network connections' aktif olduğundan emin ol!"
        xhost +localhost 2>/dev/null || echo "⚠️  xhost komutu çalışmadı, devam ediliyor..."
        docker-compose --profile gui up
        ;;
    ui)
        echo "🚀 Interactive UI mode başlatılıyor..."
        echo "⚠️  XQuartz'ın çalıştığından ve 'Allow network connections' aktif olduğundan emin ol!"
        xhost +localhost 2>/dev/null || echo "⚠️  xhost komutu çalışmadı, devam ediliyor..."
        docker-compose --profile ui up
        ;;
    web)
        echo "🚀 Web server mode başlatılıyor..."
        echo "📋 Server http://localhost:8001 adresinde çalışacak"
        docker-compose --profile web up
        ;;
    build)
        echo "🔨 Docker image build ediliyor..."
        docker-compose build
        ;;
    clean)
        echo "🧹 Docker container'ları temizleniyor..."
        docker-compose down
        docker system prune -f
        ;;
    *)
        echo "Kullanım: ./docker/run.sh [dev|prod|gui|ui|web|build|clean]"
        echo ""
        echo "Modlar:"
        echo "  dev   - Development mode (volume mount, hot reload)"
        echo "  prod  - Production mode (optimized)"
        echo "  gui   - GUI mode (XQuartz gerekli)"
        echo "  ui    - Interactive UI mode (XQuartz gerekli)"
        echo "  web   - Web server mode (FastAPI - http://localhost:8000)"
        echo "  build - Sadece build et"
        echo "  clean - Container'ları temizle"
        exit 1
        ;;
esac

