# BSM307 - Experiment ve UI Kullanım Kılavuzu

Bu kılavuz, projeyi nasıl çalıştıracağınızı ve experiment'leri nasıl yöneteceğinizi açıklar.

---

## 📋 İçindekiler

1. [Proje Kurulumu](#1-proje-kurulumu)
2. [Projeyi Kaydetme](#2-projeyi-kaydetme)
3. [Experiment Çalıştırma](#3-experiment-çalıştırma)
4. [UI Kullanımı](#4-ui-kullanımı)
5. [Experiment UI Entegrasyonu](#5-experiment-ui-entegrasyonu)

---

## 1. Proje Kurulumu

### 1.1. Gereksinimler

- Python 3.10 veya üzeri
- pip (Python package manager)
- Git (opsiyonel, kaynak kodu çekmek için)

### 1.2. Bağımlılıkları Yükleme

```bash
# Proje klasörüne git
cd /Users/hamidkarimli/BSM307-MultiObjective-Routing

# Sanal ortam oluştur (önerilen)
python3 -m venv .venv

# Sanal ortamı aktif et
source .venv/bin/activate  # Mac/Linux
# veya
.venv\Scripts\activate  # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 1.3. PYTHONPATH Ayarı (Geliştirme için)

```bash
# Mac/Linux
export PYTHONPATH=$(pwd)

# Windows (PowerShell)
$env:PYTHONPATH = $PWD
```

---

## 2. Projeyi Kaydetme

### 2.1. Git ile Kaydetme (Önerilen)

```bash
# Git repository'yi başlat (eğer yoksa)
git init

# Tüm dosyaları ekle
git add .

# Commit yap
git commit -m "BSM307 project: ACO penalty fix and experiment setup"

# Remote repository ekle (GitHub, GitLab, vb.)
git remote add origin <your-repository-url>

# Push yap
git push -u origin main
```

### 2.2. Manuel Kaydetme

Dosyalarınız zaten kaydedilmiş durumda. Yaptığınız değişiklikler otomatik olarak kaydediliyor.

**Önemli Dosyalar:**
- `src/algorithms/aco/ant_colony.py` - ACO algoritması (penalty hatası düzeltildi ✅)
- `experiments/run_experiments.py` - Experiment runner
- `experiments/scenario_generator.py` - Senaryo üretici
- `src/ui/app.py` - UI uygulaması

---

## 3. Experiment Çalıştırma

### 3.1. Hızlı Test (2 senaryo, 1 tekrar)

```bash
cd /Users/hamidkarimli/BSM307-MultiObjective-Routing
python experiments/run_experiments.py --num-scenarios 2 --repetitions 1
```

### 3.2. Tam Experiment (PDF Gereksinimleri)

```bash
# 20 senaryo, her biri için 5 tekrar
python experiments/run_experiments.py

# Veya açıkça belirt:
python experiments/run_experiments.py --num-scenarios 20 --repetitions 5
```

### 3.3. Özelleştirilmiş Experiment

```bash
# Sadece GA algoritması
python experiments/run_experiments.py --algorithms GA

# Özel output dizini
python experiments/run_experiments.py --output-dir ./my_results

# Analiz olmadan (sadece sonuçları kaydet)
python experiments/run_experiments.py --skip-analysis
```

### 3.4. Experiment Sonuçları

Sonuçlar `experiments/results/` klasörüne kaydedilir:

- **JSON dosyası**: `results_YYYYMMDD_HHMMSS.json` - Tüm detaylı sonuçlar
- **CSV dosyası**: `summary_YYYYMMDD_HHMMSS.csv` - Özet istatistikler

**Örnek çıktı:**
```
experiments/results/
  ├── results_20250126_123456.json
  └── summary_20250126_123456.csv
```

### 3.5. Sonuçları Analiz Etme

```python
# Python script ile
from experiments.result_analyzer import ResultAnalyzer
import json

# Sonuçları yükle
with open('experiments/results/results_20250126_123456.json', 'r') as f:
    results_data = json.load(f)

# ResultAnalyzer kullan (gerekirse ExperimentResult objelerine çevir)
analyzer = ResultAnalyzer(results_data)
analyzer.print_summary_report()
```

---

## 4. UI Kullanımı

### 4.1. UI'yi Başlatma

```bash
# Yerel olarak (GUI gerekli)
python run_ui.py

# Veya
python -c "from src.ui.app import run_app; run_app()"
```

### 4.2. UI Özellikleri

**Kontroller:**
- **Source/Target**: Başlangıç ve hedef düğümler (text box)
- **Bandwidth**: İstenen bandwidth değeri (Mbps)
- **Algorithm**: GA veya ACO seçimi
- **Weight Sliders**: Delay, Reliability, Resource ağırlıkları
- **Calculate Path**: Path hesaplama butonu

**Görselleştirme:**
- Network grafiği (spring layout)
- Bulunan path (kırmızı çizgi ile vurgulanır)
- Source (yeşil), Target (mavi)
- Metrikler (delay, cost, vb.)

### 4.3. UI ile Tek Test

1. UI'yi başlat: `python run_ui.py`
2. Source, Target, Bandwidth değerlerini gir
3. Algoritma seç (GA veya ACO)
4. Weight'leri ayarla (slider'lar)
5. "Calculate Path" butonuna tıkla
6. Sonuçları görselleştir

---

## 5. Experiment UI Entegrasyonu

Mevcut UI tek tek path hesaplama için tasarlanmış. Eğer UI'den experiment başlatmak isterseniz, aşağıdaki seçenekler var:

### 5.1. Seçenek A: Yeni Experiment UI Butonu Ekle

UI'ye experiment başlatma butonu ekleyebiliriz. Bu şekilde UI içinden experiment çalıştırabilirsiniz.

**Özellikler:**
- UI'de "Run Experiment" butonu
- Senaryo sayısı ve tekrar sayısı input'ları
- Progress bar (experiment sırasında)
- Sonuçları UI'de gösterme

**İsterseniz bu özelliği ekleyebilirim.**

### 5.2. Seçenek B: Ayrı Experiment Launcher Script

Basit bir script ile experiment'i UI olmadan çalıştırabilirsiniz (şu an mevcut).

### 5.3. Seçenek C: Web UI (Mevcut)

FastAPI web server ile experiment çalıştırabilirsiniz:

```bash
python run_web.py
# Veya
docker-compose --profile web up
```

Sonra tarayıcıda: `http://localhost:8001`

---

## 6. Hızlı Başlangıç Özeti

### İlk Çalıştırma

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. PYTHONPATH ayarla
export PYTHONPATH=$(pwd)

# 3. Küçük test çalıştır
python experiments/run_experiments.py --num-scenarios 2 --repetitions 1

# 4. UI'yi dene (GUI gerekli)
python run_ui.py
```

### Tam Experiment

```bash
# Tam experiment (20 senaryo, 5 tekrar)
python experiments/run_experiments.py

# Sonuçları kontrol et
ls -lh experiments/results/
```

### Projeyi Kaydet

```bash
# Git ile
git add .
git commit -m "BSM307: Penalty fix and experiment setup"
git push
```

---

## 7. Sorun Giderme

### 7.1. Import Hataları

```bash
# PYTHONPATH ayarlandığından emin ol
export PYTHONPATH=$(pwd)

# Veya direkt Python modülü olarak çalıştır
python -m experiments.run_experiments
```

### 7.2. UI Açılmıyor

```bash
# Backend kontrolü
python -c "import matplotlib; print(matplotlib.get_backend())"

# TkAgg backend gerekli
export MPLBACKEND=TkAgg
python run_ui.py
```

### 7.3. Experiment Hataları

```bash
# Log seviyesini artır
export LOG_LEVEL=DEBUG

# Test ACO'yu
python test_aco.py

# Test GA'yı
python test_ga.py
```

---

## 8. Sonraki Adımlar

1. ✅ **Penalty hatası düzeltildi** - ACO artık çalışıyor
2. 🔄 **Experiment çalıştır** - `python experiments/run_experiments.py`
3. 📊 **Sonuçları analiz et** - JSON ve CSV dosyalarını incele
4. 📈 **Grafikler oluştur** - `experiments/generate_report.py` (gerekirse)
5. 📝 **Rapor yaz** - `docs/report/sections.md` dosyasını doldur

---

**Sorularınız için:** `PROJECT_ANALYSIS.md` dosyasına bakın.

