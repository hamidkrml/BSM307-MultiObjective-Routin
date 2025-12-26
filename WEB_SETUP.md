# Web Server Kurulum ve Çalıştırma

## Sorun Giderme

### Container başlamıyorsa:

1. **Docker Desktop'ın çalıştığından emin ol:**
   ```bash
   docker ps
   ```

2. **Image'i build et:**
   ```bash
   docker-compose --profile web build
   ```

3. **Container'ı başlat:**
   ```bash
   docker-compose --profile web up
   ```

4. **Logları kontrol et:**
   ```bash
   docker-compose --profile web logs -f
   ```

### Port Kullanımı:

**Docker için:** Port mapping `8001:8000` şeklinde ayarlanmıştır.
- Host'tan erişim: `http://localhost:8001`
- Container içinde: `http://localhost:8000`

Eğer 8001 de kullanımda ise, `docker-compose.yml` dosyasında değiştir:
```yaml
ports:
  - "8002:8000"  # İstediğin port numarası
```

### Container çalışıyor ama bağlanamıyorsan:

1. **Container'ın çalıştığını kontrol et:**
   ```bash
   docker-compose --profile web ps
   ```

2. **Container içinde test et:**
   ```bash
   docker-compose --profile web exec routing-web curl http://localhost:8000/api/health
   ```

3. **Host'tan test et:**
   ```bash
   curl http://localhost:8001/api/health
   ```

## Hızlı Başlangıç

```bash
# 1. Build
docker-compose --profile web build

# 2. Başlat
docker-compose --profile web up

# 3. Tarayıcıda aç
open http://localhost:8001
```

## Lokal Test (Docker olmadan)

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Server'ı başlat
python run_web.py

# Tarayıcıda aç
open http://localhost:8000
```

## API Test

```bash
# Health check
curl http://localhost:8001/api/health

# Graph info
curl http://localhost:8001/api/graph/info

# Calculate path (POST)
curl -X POST http://localhost:8001/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "source": 0,
    "target": 100,
    "bandwidth": 500,
    "algorithm": "GA",
    "weights": {
      "delay": 0.4,
      "reliability": 0.3,
      "resource": 0.3
    }
  }'
```

