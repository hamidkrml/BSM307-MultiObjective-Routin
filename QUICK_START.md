# 🚀 BSM307 - Hızlı Başlangıç Kılavuzu

Bu kılavuz projeyi en hızlı şekilde çalıştırmanızı sağlar.

---

## ✅ Hızlı Kurulum

### Seçenek A: Docker (Önerilen - En Kolay)

```bash
# 1. Docker Desktop'u başlat (Mac için)
open -a Docker

# 2. Proje klasörüne git
cd /Users/hamidkarimli/BSM307-MultiObjective-Routing

# 3. Docker image'i build et
docker-compose build

# 4. Hızlı test çalıştır
docker-compose --profile experiment-quick up
```

**Detaylı Docker kılavuzu:** `DOCKER_GUIDE.md`

### Seçenek B: Yerel Python

```bash
# 1. Proje klasörüne git
cd /Users/hamidkarimli/BSM307-MultiObjective-Routing

# 2. Bağımlılıkları yükle
pip install -r requirements.txt

# 3. PYTHONPATH ayarla (geliştirme için)
export PYTHONPATH=$(pwd)
```

---

## 🎯 3 Adımda Çalıştırma

### Adım 1: Test (2 dakika)

**Docker ile:**
```bash
docker-compose --profile experiment-quick up
```

**Yerel Python ile:**
```bash
python run_experiment.py --quick
```

**Ne yapar:**
- 2 senaryo üretir
- Her senaryo için 1 tekrar çalıştırır
- GA ve ACO algoritmalarını test eder
- Sonuçları `experiments/results/` klasörüne kaydeder

### Adım 2: UI ile Tek Test (1 dakika)

**Yerel Python ile (GUI gerekli):**
```bash
python run_ui.py
```

**Docker ile (XQuartz gerekli - Mac):**
```bash
# XQuartz'ı başlat ve izin ver
xhost +localhost

# UI'yi başlat
docker-compose --profile ui up
```

**UI'de:**
1. Source, Target, Bandwidth değerlerini gir
2. Algoritma seç (GA veya ACO)
3. "Calculate Path" butonuna tıkla
4. Sonuçları görselleştir

### Adım 3: Tam Experiment (20-30 dakika)

**Docker ile:**
```bash
docker-compose --profile experiment-full up
```

**Yerel Python ile:**
```bash
python run_experiment.py --full
```

**Ne yapar:**
- 20 farklı senaryo üretir
- Her senaryo için 5 tekrar çalıştırır
- Toplam 200 experiment (20 × 5 × 2 algoritma)
- Sonuçları JSON ve CSV olarak kaydeder

---

## 📁 Projeyi Kaydetme

### Git ile (Önerilen)

```bash
# Git repository başlat (eğer yoksa)
git init

# Dosyaları ekle
git add .

# Commit yap
git commit -m "BSM307: Penalty fix, experiment setup"

# Remote ekle (GitHub/GitLab)
git remote add origin <your-repo-url>

# Push yap
git push -u origin main
```

### Manuel Kaydetme

Dosyalarınız zaten kaydedilmiş! Değişiklikler otomatik olarak kaydediliyor.

**Önemli dosyalar:**
- ✅ `src/algorithms/aco/ant_colony.py` - Penalty hatası düzeltildi
- ✅ `experiments/run_experiments.py` - Experiment runner
- ✅ `PROJECT_ANALYSIS.md` - Detaylı analiz raporu
- ✅ `EXPERIMENT_GUIDE.md` - Kullanım kılavuzu

---

## 🔧 Sorun Giderme

### Import Hatası

```bash
export PYTHONPATH=$(pwd)
python run_experiment.py --quick
```

### UI Açılmıyor

```bash
# TkAgg backend gerekli
export MPLBACKEND=TkAgg
python run_ui.py
```

### Experiment Hata Veriyor

```bash
# ACO test et
python test_aco.py

# GA test et
python test_ga.py
```

---

## 📊 Sonuçları İnceleme

Experiment'ler bittikten sonra:

```bash
# Sonuçları listele
ls -lh experiments/results/

# Sonuçları görüntüle (JSON)
cat experiments/results/results_*.json | head -50

# Özet CSV'yi görüntüle
cat experiments/results/summary_*.csv
```

---

## 📚 Daha Fazla Bilgi

- **Docker Kılavuzu**: `DOCKER_GUIDE.md` ⭐
- **Detaylı Analiz**: `PROJECT_ANALYSIS.md`
- **Experiment Kılavuzu**: `EXPERIMENT_GUIDE.md`
- **README**: `README.md`

---

## ✅ Checklist

Projeyi tamamlamak için:

- [x] Penalty hatası düzeltildi
- [ ] Hızlı test çalıştırıldı (`python run_experiment.py --quick`)
- [ ] UI test edildi (`python run_ui.py`)
- [ ] Tam experiment çalıştırıldı (`python run_experiment.py --full`)
- [ ] Sonuçlar analiz edildi
- [ ] Rapor yazıldı (`docs/report/sections.md`)

---

**Sorun mu var?** `PROJECT_ANALYSIS.md` dosyasındaki sorun giderme bölümüne bakın.

