# Docker Makefile - Kolay kullanım için

.PHONY: help dev prod gui build clean test

help:
	@echo "BSM307 Docker Komutları:"
	@echo "  make dev    - Development mode başlat"
	@echo "  make prod   - Production mode başlat"
	@echo "  make gui    - GUI mode başlat (XQuartz gerekli)"
	@echo "  make ui     - Interactive UI mode başlat (XQuartz gerekli)"
	@echo "  make web    - Web server mode başlat (http://localhost:8000)"
	@echo "  make build  - Docker image build et"
	@echo "  make clean  - Container'ları temizle"
	@echo "  make test   - Demo script'i test et"

dev:
	docker-compose --profile dev up

prod:
	docker-compose --profile prod up

gui:
	@echo "⚠️  XQuartz'ın çalıştığından emin ol!"
	xhost +localhost 2>/dev/null || true
	docker-compose --profile gui up

ui:
	@echo "⚠️  XQuartz'ın çalıştığından emin ol!"
	xhost +localhost 2>/dev/null || true
	docker-compose --profile ui up

web:
	@echo "🚀 Web server başlatılıyor..."
	@echo "📋 http://localhost:8001 adresinde açılacak"
	docker-compose --profile web up

build:
	docker-compose build

clean:
	docker-compose down
	docker system prune -f

test:
	docker-compose --profile dev run --rm routing-dev python demo.py

