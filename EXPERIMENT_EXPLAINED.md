# 📊 Experiment'ler Nedir? - BSM307

Bu dokümanda experiment'lerin ne olduğu, nasıl çalıştığını ve nasıl kullanılacağı açıklanmaktadır.

---

## 🎯 Experiment Nedir?

**Experiment**, projenin kalbi olan sistematik test sürecidir. PDF gereksinimlerine göre:

1. **20 farklı senaryo** üretilir
2. Her senaryo için **5 tekrar** çalıştırılır
3. Her tekrarda **GA ve ACO** algoritmaları test edilir
4. Sonuçlar **JSON ve CSV** formatında kaydedilir

**Toplam experiment sayısı:** 20 senaryo × 5 tekrar × 2 algoritma = **200 experiment**

---

## 📋 Senaryo Nedir?

Her **senaryo**, bir (S, D, B) kombinasyonudur:
- **S (Source)**: Başlangıç düğümü (0-249 arası)
- **D (Destination)**: Hedef düğümü (0-249 arası)
- **B (Bandwidth)**: İstenen bant genişliği (100-1000 Mbps arası)

**Örnek Senaryo:**
```
Senaryo 1: S=5, D=42, B=350.5 Mbps
Senaryo 2: S=12, D=88, B=721.3 Mbps
...
Senaryo 20: S=199, D=23, B=450.0 Mbps
```

---

## 🔄 Tekrar (Repetition) Nedir?

Aynı senaryo **5 kez** çalıştırılır çünkü:
- Algoritmalar rastgele (stochastic) olduğu için her çalıştırmada farklı sonuçlar üretebilir
- 5 tekrar ile **ortalama** ve **standart sapma** hesaplanabilir
- Daha **güvenilir** istatistiksel sonuçlar elde edilir

**Örnek:**
```
Senaryo 1, Tekrar 1: GA → Path bulundu, Cost=4.5
Senaryo 1, Tekrar 2: GA → Path bulundu, Cost=4.3
Senaryo 1, Tekrar 3: GA → Path bulundu, Cost=4.7
Senaryo 1, Tekrar 4: GA → Path bulundu, Cost=4.4
Senaryo 1, Tekrar 5: GA → Path bulundu, Cost=4.6
Ortalama Cost = 4.5
```

---

## 📊 Experiment Akışı

```
1. Graph Oluştur (250 düğüm, 0.4 edge probability)
   ↓
2. 20 Senaryo Üret (S, D, B kombinasyonları)
   ↓
3. Her Senaryo İçin:
   ├─ Tekrar 1:
   │  ├─ GA çalıştır → Sonuç kaydet
   │  └─ ACO çalıştır → Sonuç kaydet
   ├─ Tekrar 2:
   │  ├─ GA çalıştır → Sonuç kaydet
   │  └─ ACO çalıştır → Sonuç kaydet
   ├─ ...
   └─ Tekrar 5:
      ├─ GA çalıştır → Sonuç kaydet
      └─ ACO çalıştır → Sonuç kaydet
   ↓
4. Tüm Sonuçları JSON'a Kaydet
   ↓
5. İstatistiksel Analiz Yap (Ortalama, Std, vb.)
   ↓
6. CSV Özet Oluştur
```

---

## 📁 Experiment Dosyaları

### 1. `experiments/experiment_runner.py`

**Ne yapar:**
- Experiment'leri çalıştırır
- Sonuçları toplar
- JSON formatında kaydeder

**Ana Sınıflar:**
- `ExperimentRunner`: Experiment'leri yönetir
- `ExperimentResult`: Tek bir experiment sonucu

**Metodlar:**
- `run_single_experiment()`: Tek bir experiment çalıştırır
- `run_scenario()`: Bir senaryo için tüm tekrarları çalıştırır
- `run_all_scenarios()`: Tüm senaryoları çalıştırır

### 2. `experiments/scenario_generator.py`

**Ne yapar:**
- 20 farklı (S, D, B) senaryosu üretir
- Senaryoların geçerli olduğunu kontrol eder (path var mı?)

**Kullanım:**
```python
from experiments.scenario_generator import generate_scenarios_for_experiment

scenarios = generate_scenarios_for_experiment(
    graph=graph,
    num_scenarios=20,
    seed=42
)
# Returns: [(S1, D1, B1), (S2, D2, B2), ...]
```

### 3. `experiments/run_experiments.py`

**Ne yapar:**
- Ana experiment script'i
- Graph oluşturur
- Senaryoları üretir
- Experiment'leri çalıştırır
- Sonuçları kaydeder

**Kullanım:**
```bash
# Tam experiment (20 senaryo, 5 tekrar)
python experiments/run_experiments.py

# Hızlı test (2 senaryo, 1 tekrar)
python experiments/run_experiments.py --num-scenarios 2 --repetitions 1
```

### 4. `experiments/result_analyzer.py`

**Ne yapar:**
- JSON sonuçlarını analiz eder
- İstatistiksel özet çıkarır (ortalama, std, min, max)
- CSV formatında özet oluşturur

---

## 🚀 Experiment'leri Çalıştırma

### Yöntem 1: Komut Satırı

```bash
# Tam experiment (20-30 dakika sürer)
python experiments/run_experiments.py

# Veya kolay script
python run_experiment.py --full
```

### Yöntem 2: UI'dan

```bash
# UI'yi başlat
python run_ui.py

# UI'de:
# 1. Senaryolar: 20
# 2. Tekrarlar: 5
# 3. "Deneyi Çalıştır" butonuna tıkla
```

### Yöntem 3: Docker

```bash
# Docker ile
docker-compose --profile experiment-full up
```

---

## 📊 Sonuç Dosyaları

Experiment'ler bittikten sonra `experiments/results/` klasörüne kaydedilir:

### JSON Dosyası

**Örnek:** `results_20250126_123456.json`

```json
[
  {
    "scenario_id": 1,
    "repetition": 0,
    "algorithm": "GA",
    "source": 5,
    "target": 42,
    "bandwidth": 350.5,
    "path": [5, 12, 23, 42],
    "path_length": 4,
    "total_delay": 25.5,
    "reliability_cost": 0.05,
    "resource_cost": 3.2,
    "weighted_cost": 4.5,
    "runtime_seconds": 0.25,
    "success": true,
    "error_message": ""
  },
  ...
]
```

### CSV Özet Dosyası

**Örnek:** `summary_20250126_123456.csv`

```csv
scenario_id,algorithm,mean_cost,std_cost,mean_delay,mean_reliability,mean_resource,success_rate
1,GA,4.5,0.2,25.5,0.05,3.2,1.0
1,ACO,4.3,0.15,24.8,0.04,3.1,1.0
...
```

---

## 📈 Experiment Sonuçlarını Analiz Etme

### Python ile

```python
from experiments.result_analyzer import ResultAnalyzer
import json

# Sonuçları yükle
with open('experiments/results/results_20250126_123456.json', 'r') as f:
    results_data = json.load(f)

# Analiz et
analyzer = ResultAnalyzer(results_data)
analyzer.print_summary_report()

# CSV'ye çıkar
analyzer.export_to_csv('summary.csv')
```

### CSV ile (Excel/Google Sheets)

```bash
# CSV dosyasını aç
open experiments/results/summary_20250126_123456.csv

# Veya
cat experiments/results/summary_20250126_123456.csv
```

---

## ✅ Experiment Durumu

**Durum:** ✅ **TAMAMEN İMPLEMENT EDİLDİ**

Tüm experiment bileşenleri çalışır durumda:
- ✅ Scenario generator
- ✅ Experiment runner
- ✅ Sonuç kaydetme (JSON)
- ✅ Sonuç analizi
- ✅ CSV export
- ✅ UI entegrasyonu

---

## 🧪 Hızlı Test

Experiment'lerin çalışıp çalışmadığını test etmek için:

```bash
# Küçük test (2 senaryo, 1 tekrar, ~1 dakika)
python experiments/run_experiments.py --num-scenarios 2 --repetitions 1

# Sonuçları kontrol et
ls -lh experiments/results/
cat experiments/results/results_*.json | head -50
```

---

## 📝 PDF Gereksinimleri

**Zorunlu:**
- ✅ 20 farklı (S, D, B) senaryosu
- ✅ Her senaryo için 5 tekrar
- ✅ GA ve ACO algoritmaları
- ✅ Metrikler: delay, reliability, resource cost, weighted sum
- ✅ Sonuç toplama ve analiz

**Tüm gereksinimler karşılanmış!** ✅

---

## 🔍 Sorun Giderme

### Experiment çalışmıyor

```bash
# Test et
python experiments/experiment_runner.py

# Logları kontrol et
python experiments/run_experiments.py --num-scenarios 1 --repetitions 1
```

### Sonuçlar kaydedilmiyor

```bash
# Klasör var mı kontrol et
ls -la experiments/results/

# Manuel oluştur
mkdir -p experiments/results
```

### Çok uzun sürüyor

```bash
# Hızlı test (2 senaryo, 1 tekrar)
python experiments/run_experiments.py --num-scenarios 2 --repetitions 1

# Tam experiment (~20-30 dakika)
python experiments/run_experiments.py  # 20 senaryo, 5 tekrar
```

---

**Sorularınız için:**
- `EXPERIMENT_GUIDE.md` - Detaylı kullanım kılavuzu
- `PROJECT_ANALYSIS.md` - Teknik detaylar

