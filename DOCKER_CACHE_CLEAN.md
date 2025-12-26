# 🧹 Docker Cache Temizleme Kılavuzu

Docker kullanırken cache temizleme için farklı yöntemler:

---

## 1. Python Cache Temizleme (Container İçinde)

### Çalışan Container'da

```bash
# Container içine gir
docker-compose exec routing-ui bash

# Veya container ismini kontrol et
docker ps
docker exec -it <container-name> bash

# Container içinde cache temizle
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Çıkış
exit
```

### Container Yeniden Başlatma (Önerilen)

```bash
# Container'ları durdur
docker-compose down

# Container'ları yeniden başlat
docker-compose --profile ui up
```

---

## 2. Docker Image Cache Temizleme

### Build Cache Olmadan Yeniden Build

```bash
# Mevcut image'i cache olmadan yeniden build et
docker-compose build --no-cache

# Veya belirli bir service için
docker-compose build --no-cache routing-ui
```

### Tüm Build Cache'i Temizle

```bash
# Docker build cache'ini temizle
docker builder prune

# Tüm kullanılmayan cache'leri temizle (dikkatli!)
docker builder prune -a
```

---

## 3. Docker Image ve Container Temizleme

### Kullanılmayan Container'ları Temizle

```bash
# Durdurulmuş container'ları temizle
docker container prune

# Tüm container'ları durdur ve temizle
docker-compose down
docker container prune -f
```

### Image'leri Temizle

```bash
# Kullanılmayan image'leri listele
docker images

# Kullanılmayan image'leri temizle
docker image prune

# Tüm kullanılmayan image'leri temizle (dikkatli!)
docker image prune -a
```

### Volume'ları Temizle

```bash
# Kullanılmayan volume'ları temizle
docker volume prune

# Volume'ları da temizle (dikkat: sonuçlar silinir!)
docker-compose down -v
```

---

## 4. Tam Temizlik (Nükleer Seçenek)

### Her Şeyi Temizle

```bash
# ⚠️ DİKKAT: Tüm kullanılmayan Docker kaynaklarını temizler

# Container'ları durdur
docker-compose down

# Tüm kullanılmayan kaynakları temizle
docker system prune -a --volumes

# Veya adım adım:
docker container prune -f
docker image prune -a -f
docker volume prune -f
docker network prune -f
docker builder prune -a -f
```

---

## 5. Sadece Proje İçin Temizlik

### Proje Container'larını Temizle

```bash
# Proje container'larını durdur ve temizle
docker-compose down

# Proje image'lerini temizle
docker-compose down --rmi all

# Volume'ları da temizle (sonuçlar silinir!)
docker-compose down -v --rmi all
```

### Yeniden Build Et

```bash
# Temiz başlangıç
docker-compose build --no-cache

# Çalıştır
docker-compose --profile ui up
```

---

## 6. Hızlı Temizlik (Önerilen)

UI cache sorunları için en hızlı çözüm:

```bash
# 1. Container'ları durdur
docker-compose down

# 2. Image'i cache olmadan yeniden build
docker-compose build --no-cache routing-ui

# 3. Yeniden başlat
docker-compose --profile ui up
```

---

## 7. Python Cache Sorunu İçin Özel

### Container İçinde Manuel Temizleme

```bash
# Container'ı çalıştır (background)
docker-compose --profile ui up -d

# Container'a gir
docker-compose exec routing-ui bash

# Cache temizle
cd /app
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Çıkış
exit

# Container'ı yeniden başlat
docker-compose restart routing-ui
```

### Dockerfile'a Cache Temizleme Ekle (Kalıcı Çözüm)

`.dockerignore` dosyasına şunları ekleyebilirsiniz:
```
__pycache__/
*.py[cod]
*$py.class
*.pyo
```

---

## 8. Disk Alanı Kontrolü

### Kullanılan Alanı Görüntüle

```bash
# Docker disk kullanımı
docker system df

# Detaylı bilgi
docker system df -v
```

### Sadece Kullanılmayanları Temizle

```bash
# Sadece kullanılmayan kaynakları temizle (güvenli)
docker system prune

# Volume'lar hariç (sonuçlar korunur)
docker system prune --volumes=false
```

---

## 📋 Hızlı Referans

### UI Cache Sorunu İçin

```bash
docker-compose down
docker-compose build --no-cache
docker-compose --profile ui up
```

### Tam Temizlik (Dikkatli!)

```bash
docker-compose down -v --rmi all
docker system prune -a --volumes
docker-compose build --no-cache
```

### Sadece Container Yeniden Başlatma

```bash
docker-compose restart routing-ui
```

---

## ⚠️ Dikkat Edilmesi Gerekenler

1. **`docker system prune -a`**: Tüm kullanılmayan image'leri siler, dikkatli kullanın!
2. **`docker-compose down -v`**: Volume'ları da siler, `experiments/results/` klasörü silinebilir!
3. **`--no-cache`**: Build çok uzun sürer, sadece gerekliyse kullanın

---

## ✅ Önerilen Workflow

**Normal kullanım için:**
```bash
docker-compose down
docker-compose --profile ui up
```

**Cache sorunu varsa:**
```bash
docker-compose down
docker-compose build --no-cache routing-ui
docker-compose --profile ui up
```

**Tam temizlik (ara sıra):**
```bash
docker-compose down -v
docker system prune
docker-compose build
docker-compose --profile ui up
```

