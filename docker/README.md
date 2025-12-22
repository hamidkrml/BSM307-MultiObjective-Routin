# Docker Setup - BSM307 Multi-Objective Routing

## Mac Kurulumu

### 1. Docker Desktop Kurulumu

```bash
# Homebrew ile (önerilen)
brew install --cask docker

# Veya manuel:
# https://www.docker.com/products/docker-desktop/ adresinden indir
```

### 2. Docker Desktop'u Başlat
- Applications klasöründen Docker Desktop'u aç
- İlk açılışta kurulum tamamlanana kadar bekle
- Menü çubuğunda Docker ikonunun yeşil olduğunu kontrol et

### 3. Docker'ın Çalıştığını Kontrol Et
```bash
docker --version
docker-compose --version
```

### 4. XQuartz Kurulumu (GUI için - opsiyonel)
```bash
brew install --cask xquartz

# XQuartz'ı başlat ve ayarlar:
# Preferences → Security → "Allow connections from network clients" ✓
```

## Kullanım

### Development Mode (Volume Mount ile)
```bash
# Build ve run
docker-compose --profile dev up

# Veya sadece build
docker-compose --profile dev build

# Arka planda çalıştır
docker-compose --profile dev up -d

# Logları görüntüle
docker-compose --profile dev logs -f

# Durdur
docker-compose --profile dev down
```

### Production Mode
```bash
docker-compose --profile prod up
```

### GUI Mode (XQuartz gerekli)
```bash
# XQuartz'ı başlat ve network connections'ı aktif et
xhost +localhost

# GUI mode'da çalıştır
docker-compose --profile gui up
```

### Manuel Docker Komutları
```bash
# Build
docker build -t bsm307-routing .

# Run (headless)
docker run --rm bsm307-routing

# Run (GUI - XQuartz gerekli)
docker run --rm \
  -e DISPLAY=host.docker.internal:0 \
  -e MPLBACKEND=TkAgg \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --network host \
  bsm307-routing

# Run with custom environment variables
docker run --rm \
  -e EXPERIMENT_SEED=123 \
  -e NUM_NODES=100 \
  -e EDGE_PROB=0.5 \
  bsm307-routing
```

## Environment Variables

- `MPLBACKEND`: Matplotlib backend (Agg, TkAgg, Qt5Agg)
- `EXPERIMENT_SEED`: Random seed (default: 42)
- `NUM_NODES`: Düğüm sayısı (default: 250)
- `EDGE_PROB`: Edge probability (default: 0.4)
- `PYTHONPATH`: Python path (default: /app)

## Troubleshooting

### Matplotlib GUI çalışmıyor
- XQuartz'ın çalıştığından emin ol
- `xhost +localhost` komutunu çalıştır
- `DISPLAY=host.docker.internal:0` environment variable'ını kontrol et

### Volume mount çalışmıyor
- Docker Desktop → Settings → Resources → File Sharing
- Proje klasörünün paylaşıldığından emin ol

### Permission denied
- Docker Desktop → Settings → Resources → Advanced
- File sharing permissions'ı kontrol et

