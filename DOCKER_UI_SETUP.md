# 🖥️ Docker'da UI Kullanımı - BSM307

Docker container'ında matplotlib UI'yi görmek için X11 forwarding kurulumu gerekiyor.

---

## ⚠️ Önemli Not

**Docker'da UI görüntülemek Mac'te biraz karmaşık.** 

**Önerilen Yöntem:**
- ✅ **Yerel Python ile UI çalıştır** (en kolay): `python run_ui.py`
- ✅ **Web UI kullan** (önerilen): `docker-compose --profile web up`
- ⚠️ **XQuartz ile Docker UI** (gelişmiş kullanıcılar için)

---

## 🖥️ Seçenek 1: Yerel Python ile UI (En Kolay - ÖNERİLEN)

```bash
# Direkt yerel Python ile çalıştır (Docker yok)
python run_ui.py
```

**Avantajlar:**
- ✅ Hiçbir ekstra kurulum gerekmez
- ✅ GUI doğrudan çalışır
- ✅ Hızlı ve kolay

---

## 🌐 Seçenek 2: Web UI (ÖNERİLEN - Docker ile)

Web tabanlı UI Docker'da sorunsuz çalışır:

```bash
# Web server'ı başlat
docker-compose --profile web up

# Tarayıcıda aç
open http://localhost:8001
```

**Avantajlar:**
- ✅ Docker'da sorunsuz çalışır
- ✅ XQuartz gerekmez
- ✅ Her platformda çalışır (Mac, Linux, Windows)
- ✅ Modern web arayüzü

---

## 🖼️ Seçenek 3: XQuartz ile Docker UI (Gelişmiş)

Mac'te Docker container'ında matplotlib GUI görmek için XQuartz gerekli.

### Adım 1: XQuartz Kurulumu

```bash
# Homebrew ile kur
brew install --cask xquartz

# XQuartz'ı başlat
open -a XQuartz
```

### Adım 2: XQuartz Ayarları

1. **XQuartz'ı aç:** Applications → Utilities → XQuartz
2. **Preferences'a git:** XQuartz → Preferences
3. **Security sekmesi:**
   - ✅ "Allow connections from network clients" işaretle
4. **XQuartz'ı kapat ve yeniden başlat**

### Adım 3: X11 Forwarding İzni

```bash
# X11 forwarding'e izin ver
xhost +localhost

# Kontrol et (herhangi bir hata yoksa OK)
echo $DISPLAY  # Boş olabilir, sorun değil
```

### Adım 4: Docker UI'yi Başlat

```bash
# UI mode'u başlat
docker-compose --profile ui up
```

**Eğer çalışmazsa:**

```bash
# DISPLAY environment variable'ını kontrol et
export DISPLAY=host.docker.internal:0

# Tekrar dene
docker-compose --profile ui up
```

### Sorun Giderme

**Problem: UI görünmüyor**

```bash
# 1. XQuartz çalışıyor mu kontrol et
ps aux | grep -i xquartz

# 2. X11 forwarding izni var mı
xhost

# 3. DISPLAY variable'ı kontrol et (container içinde)
docker-compose run --rm routing-ui env | grep DISPLAY

# 4. Manuel test
docker-compose run --rm routing-ui python -c "import matplotlib; print(matplotlib.get_backend())"
# Çıktı: TkAgg olmalı
```

**Problem: "cannot connect to X server"**

```bash
# XQuartz'ı yeniden başlat
killall XQuartz
open -a XQuartz

# İzinleri tekrar ver
xhost +localhost

# Docker'ı yeniden başlat
docker-compose --profile ui up
```

**Problem: "No display name and no $DISPLAY environment variable"**

```bash
# DISPLAY variable'ını ayarla
export DISPLAY=host.docker.internal:0

# Docker-compose.yml'de zaten var ama kontrol et:
docker-compose config | grep DISPLAY
```

---

## 📊 Karşılaştırma

| Yöntem | Kolaylık | Docker | Platform | Önerilen |
|--------|----------|--------|----------|----------|
| **Yerel Python** | ⭐⭐⭐⭐⭐ | ❌ | Mac/Linux/Windows | ✅ En kolay |
| **Web UI** | ⭐⭐⭐⭐ | ✅ | Mac/Linux/Windows | ✅ Önerilen (Docker) |
| **XQuartz UI** | ⭐⭐ | ✅ | Sadece Mac/Linux | ⚠️ Gelişmiş |

---

## 🎯 Önerilen Workflow

### Development (UI Test)

```bash
# Yerel Python ile (en kolay)
python run_ui.py
```

### Docker Test (Experiment)

```bash
# Docker ile experiment (UI gerekmez)
docker-compose --profile experiment-quick up
```

### Production (Web UI)

```bash
# Web UI (Docker, her platformda çalışır)
docker-compose --profile web up
# Tarayıcı: http://localhost:8001
```

---

## 🔍 UI'nin Çalışıp Çalışmadığını Kontrol

### Yerel Python

```bash
python run_ui.py
# Bir pencere açılmalı ✅
```

### Web UI

```bash
docker-compose --profile web up
# Tarayıcıda http://localhost:8001 açılmalı ✅
```

### XQuartz UI

```bash
# Önce XQuartz kontrolü
ps aux | grep XQuartz  # Çalışıyor olmalı
xhost  # localhost listede olmalı

# Docker UI başlat
docker-compose --profile ui up
# Matplotlib penceresi açılmalı ✅
```

---

## 💡 Tavsiyeler

1. **İlk defa UI kullanıyorsanız:** Yerel Python ile başlayın (`python run_ui.py`)
2. **Docker kullanmak istiyorsanız:** Web UI kullanın (`docker-compose --profile web up`)
3. **XQuartz ile uğraşmak istemiyorsanız:** Web UI veya yerel Python kullanın

---

## 📝 Özet Komutlar

```bash
# ✅ EN KOLAY: Yerel Python UI
python run_ui.py

# ✅ ÖNERİLEN: Web UI (Docker)
docker-compose --profile web up
# Tarayıcı: http://localhost:8001

# ⚠️ GELİŞMİŞ: XQuartz UI (Docker, Mac)
xhost +localhost
docker-compose --profile ui up
```

---

**Sorularınız için:**
- `DOCKER_GUIDE.md` - Genel Docker kılavuzu
- `QUICK_START.md` - Hızlı başlangıç
- `EXPERIMENT_GUIDE.md` - Experiment detayları

