# 🐳 Docker Kullanım Kılavuzu - BSM307

Bu kılavuz projeyi Docker ile nasıl çalıştıracağınızı gösterir.

---

## 📋 İçindekiler

1. [Docker Kurulumu](#1-docker-kurulumu)
2. [Hızlı Başlangıç](#2-hızlı-başlangıç)
3. [Docker Modları](#3-docker-modları)
4. [Experiment Çalıştırma](#4-experiment-çalıştırma)
5. [Sorun Giderme](#5-sorun-giderme)

---

## 1. Docker Kurulumu

### Mac için

```bash
# Homebrew ile
brew install --cask docker

# Docker Desktop'u başlat
open -a Docker
```

### Linux için

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Docker'ı başlat
sudo systemctl start docker
sudo systemctl enable docker
```

### Docker Kurulumunu Kontrol Et

```bash
docker --version
docker-compose --version
```

---

## 2. Hızlı Başlangıç

### İlk Çalıştırma

```bash
# Proje klasörüne git
cd /Users/hamidkarimli/BSM307-MultiObjective-Routing

# Docker image'i build et
docker-compose build

# Hızlı test çalıştır (demo)
docker-compose --profile dev up
```

---

## 3. Docker Modları

### 3.1. Development Mode (Dev)

**Kullanım:** Geliştirme ve test için

```bash
docker-compose --profile dev up
```

**Özellikler:**
- Volume mount ile hot reload
- Demo script çalıştırır
- Headless mode (GUI yok)
- Interactive terminal (stdin/tty)

**Durdurma:**
```bash
Ctrl+C  # veya başka terminal'den
docker-compose --profile dev down
```

### 3.2. Production Mode (Prod)

**Kullanım:** Production build

```bash
docker-compose --profile prod up
```

**Özellikler:**
- Optimized build
- Demo script çalıştırır
- Headless mode

### 3.3. GUI Mode (GUI)

**Kullanım:** GUI ile demo

**Ön Gereksinimler (Mac):**
```bash
# XQuartz kurulumu gerekli
brew install --cask xquartz

# XQuartz'ı başlat
open -a XQuartz

# X11 forwarding izni
xhost +localhost
```

**Çalıştırma:**
```bash
docker-compose --profile gui up
```

### 3.4. UI Mode (UI)

**Kullanım:** Interactive matplotlib UI

**Ön Gereksinimler:** GUI mode ile aynı (XQuartz)

```bash
docker-compose --profile ui up
```

**Not:** UI mode XQuartz gerektirir. Mac'te daha kolay, Linux'ta X11 forwarding gerekli.

### 3.5. Web Mode (Web)

**Kullanım:** FastAPI web server

```bash
docker-compose --profile web up
```

**Tarayıcıda aç:**
```
http://localhost:8001
```

**Durdurma:**
```bash
docker-compose --profile web down
```

---

## 4. Experiment Çalıştırma

### 4.1. Hızlı Test (Quick Experiment)

**Kullanım:** 2 senaryo, 1 tekrar (test için)

```bash
docker-compose --profile experiment-quick up
```

**Ne yapar:**
- 2 senaryo üretir
- Her senaryo için 1 tekrar
- GA ve ACO algoritmalarını test eder
- Sonuçları `experiments/results/` klasörüne kaydeder

### 4.2. Tam Experiment (Full Experiment)

**Kullanım:** 20 senaryo, 5 tekrar (PDF gereksinimleri)

```bash
docker-compose --profile experiment-full up
```

**Ne yapar:**
- 20 farklı senaryo üretir
- Her senaryo için 5 tekrar
- Toplam 200 experiment (20 × 5 × 2 algoritma)
- Sonuçları JSON ve CSV olarak kaydeder
- **Süre:** ~20-30 dakika

### 4.3. Özelleştirilmiş Experiment (Custom)

**Kullanım:** Özel parametrelerle experiment

```bash
# Önce container'ı build et
docker-compose build routing-experiment

# Özel komutla çalıştır
docker-compose run --rm routing-experiment \
  python experiments/run_experiments.py \
  --num-scenarios 5 \
  --repetitions 2 \
  --algorithms GA

# Veya interactive mode
docker-compose --profile experiment run --rm routing-experiment bash
# Sonra container içinde:
python experiments/run_experiments.py --num-scenarios 5 --repetitions 2
```

### 4.4. Sonuçları Kontrol Etme

Experiment'ler bittikten sonra sonuçlar host'ta erişilebilir:

```bash
# Sonuçları listele
ls -lh experiments/results/

# JSON sonuçları görüntüle
cat experiments/results/results_*.json | head -50

# CSV özetini görüntüle
cat experiments/results/summary_*.csv
```

**Not:** `experiments/results/` klasörü Docker volume olarak mount edilir, bu yüzden sonuçlar container durdurulduktan sonra da kalır.

---

## 5. Sorun Giderme

### 5.1. Build Hatası

```bash
# Cache olmadan yeniden build
docker-compose build --no-cache

# Veya sadece belirli service
docker-compose build --no-cache routing-experiment-full
```

### 5.2. Permission Hatası

```bash
# Container'ın dosya yazma izinlerini kontrol et
docker-compose run --rm routing-experiment-full ls -la experiments/results/

# Host'ta klasör izinlerini kontrol et
ls -la experiments/results/
chmod -R 755 experiments/results/
```

### 5.3. XQuartz/GUI Sorunları

```bash
# XQuartz çalışıyor mu kontrol et
ps aux | grep XQuartz

# X11 forwarding izni
xhost +localhost

# GUI modu test et
docker-compose --profile gui up
```

### 5.4. Container Çalışmıyor

```bash
# Container loglarını kontrol et
docker-compose logs routing-experiment-full

# Veya belirli service
docker-compose --profile experiment-full logs -f
```

### 5.5. Volume Mount Sorunu

```bash
# Container içine gir ve kontrol et
docker-compose run --rm routing-experiment-full bash
# Container içinde:
ls -la /app
ls -la /app/experiments/results/
```

### 5.6. Port Çakışması (Web Mode)

```bash
# Port 8001 kullanımda mı kontrol et
lsof -i :8001

# Veya farklı port kullan
docker-compose --profile web up
# docker-compose.yml'de port numarasını değiştir: "8002:8000"
```

---

## 6. Örnek Kullanım Senaryoları

### Senaryo 1: Hızlı Test

```bash
# Development mode ile demo
docker-compose --profile dev up

# Hızlı experiment test
docker-compose --profile experiment-quick up
```

### Senaryo 2: Tam Experiment

```bash
# Background'da çalıştır (logları dosyaya kaydet)
docker-compose --profile experiment-full up > experiment.log 2>&1 &

# Process ID'yi kaydet
echo $! > experiment.pid

# Logları izle
tail -f experiment.log

# Durdur
kill $(cat experiment.pid)
```

### Senaryo 3: Web UI ile Experiment

```bash
# Web server'ı başlat
docker-compose --profile web up -d

# Tarayıcıda aç: http://localhost:8001
# Web UI'den experiment çalıştır

# Durdur
docker-compose --profile web down
```

### Senaryo 4: Özel Experiment

```bash
# Interactive mode
docker-compose --profile experiment run --rm routing-experiment bash

# Container içinde:
python experiments/run_experiments.py \
  --num-scenarios 10 \
  --repetitions 3 \
  --algorithms GA ACO \
  --output-dir /app/experiments/results

# Çıkış
exit
```

---

## 7. Docker Komutları Özeti

### Build

```bash
# Tüm servisleri build et
docker-compose build

# Belirli service'i build et
docker-compose build routing-experiment-full

# Cache olmadan build
docker-compose build --no-cache
```

### Çalıştırma

```bash
# Development mode
docker-compose --profile dev up

# Experiment (quick)
docker-compose --profile experiment-quick up

# Experiment (full)
docker-compose --profile experiment-full up

# Web server
docker-compose --profile web up
```

### Durdurma

```bash
# Tüm servisleri durdur
docker-compose down

# Belirli profile'ı durdur
docker-compose --profile experiment-full down
```

### Temizleme

```bash
# Container'ları ve network'leri temizle
docker-compose down

# Volume'ları da temizle (dikkat: sonuçlar silinir!)
docker-compose down -v

# Image'leri temizle
docker-compose down --rmi all
```

### Loglar

```bash
# Logları görüntüle
docker-compose logs

# Belirli service logları
docker-compose logs routing-experiment-full

# Live log takibi
docker-compose logs -f routing-experiment-full
```

---

## 8. Docker vs Yerel Çalıştırma

### Docker Kullan (Önerilen)

**Avantajlar:**
- ✅ Tutarlı ortam (her yerde aynı)
- ✅ Bağımlılık yönetimi kolay
- ✅ Isolation (sistem kirlenmez)
- ✅ Production'a hazır

**Ne zaman:**
- Experiment çalıştırırken
- Production build test ederken
- Bağımlılık sorunları varsa

### Yerel Python Kullan

**Avantajlar:**
- ✅ Hızlı development
- ✅ Debug kolay
- ✅ GUI kullanımı kolay

**Ne zaman:**
- UI ile test ederken
- Hızlı kod değişiklikleri yaparken
- Debug ederken

---

## 9. Cache Temizleme

### Hızlı Cache Temizleme

```bash
# Container'ları durdur ve yeniden build (cache olmadan)
docker-compose down
docker-compose build --no-cache
docker-compose --profile ui up
```

### Python Cache Sorunu İçin

```bash
# Container içinde cache temizle
docker-compose exec routing-ui bash
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
exit

# Container'ı yeniden başlat
docker-compose restart routing-ui
```

**Detaylı cache temizleme kılavuzu:** `DOCKER_CACHE_CLEAN.md`

## 10. Önerilen Workflow

### Development

```bash
# Yerel Python ile UI test
python run_ui.py

# Docker ile experiment test
docker-compose --profile experiment-quick up
```

### Testing

```bash
# Yerel Python ile unit test
python test_aco.py
python test_ga.py

# Docker ile integration test
docker-compose --profile experiment-quick up
```

### Production/Submission

```bash
# Docker ile tam experiment
docker-compose --profile experiment-full up

# Sonuçları kontrol et
ls -lh experiments/results/
```

---

**Sorularınız için:**
- `QUICK_START.md` - Yerel Python kullanımı
- `EXPERIMENT_GUIDE.md` - Detaylı experiment kılavuzu
- `PROJECT_ANALYSIS.md` - Teknik detaylar

