# BSM307 Multi-Objective Routing

**2025-2026 GÜZ DÖNEMİ - BSM307 BİLGİSAYAR AĞLARI TEa
AM PROJESİ**

Çok amaçlı yönlendirme problemini GA (Genetik Algoritma), ACO (Karınca Kolonisi Optimizasyonu)algoritmalarıyla incelemek için uçtan uca bir araştırma altyapısı. Ağ üretimi, metrik hesapları, algoritma kıyaslama, görselleştirme ve raporlama adımlarını kapsar.

Öne Çıkanlar
- 250 düğümlü Erdos–Renyi rastgele grafik üreticisi; düğüm/bağ özellikleri.
- Metrikler: toplam gecikme, güvenilirlik maliyeti (−log R), kaynak maliyeti, ağırlıklı skor.
- Algoritmalar: GA, ACO, Q-Learning, Simulated Annealing iskeletleri.
- UI: networkx + matplotlib ile S-D seçimi, ağırlık slider’ları ve sonuç çizimi.
- Deneyler: Çoklu senaryo üretimi, tekrar koşuları, performans grafikleri.

Sistem Mimarisi
- `src/network`: Topoloji üretimi, düğüm ve bağlantı modelleri.
- `src/metrics`: Gecikme, güvenilirlik ve kaynak maliyeti hesapları.
- `src/algorithms`: GA/ACO/RL/SA çekirdekleri ve operatörleri.
- `src/routing`: Yol geçerlilik ve kısıt kontrolleri.
- `src/ui`: Grafik görselleştirme ve kullanıcı girdileri.
- `src/utils`: Logger, rastgele tohumlama, grafik yardımcıları.
- `experiments`: Senaryo üretimi ve sonuç toplama betikleri.
- `tests`: Birim testleri (metrikler, üretici, operatörler vb.).

Kurulum

### Yerel Kurulum

1. **Python 3.10+** kullanın.

2. **Sanal ortam oluşturun ve bağımlılıkları kurun:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Proje kökünü `PYTHONPATH`'a ekleyin:**
   ```bash
   export PYTHONPATH=$(pwd)
   ```

### Docker Kurulumu (Önerilen)

1. **Docker Desktop kurulumu:**
   ```bash
   # Mac (Homebrew)
   brew install --cask docker
   
   # Docker Desktop'u başlat ve çalıştığını kontrol et
   docker --version
   ```

2. **Docker ile çalıştır:**
   ```bash
   # Web UI (FastAPI - http://localhost:8001)
   docker-compose --profile web up
   
  
   
   # Experiment çalıştırma (20 senaryo × 5 tekrar)
   docker-compose --profile experiment-full up
   ```

3. **Detaylı Docker dokümantasyonu için:** `DOCKER_GUIDE.md`

---

## 📖 Kullanım

### Web UI (Önerilen)

```bash
# Docker ile
docker-compose --profile web up

# Yerel olarak
python run_web.py
```

Web UI'ya erişim: **http://localhost:8001** (Docker) veya **http://localhost:8000** (yerel)

**Özellikler:**
- Kaynak ve hedef düğüm seçimi
- Bandwidth ayarı (100-1000 Mbps)
- Ağırlık slider'ları (Gecikme, Güvenilirlik, Kaynak)
- Algoritma seçimi (GA, ACO)
- Sonuç görselleştirme
- Experiment UI (20 senaryo testi)

### Matplotlib UI

```bash
# Docker ile (XQuartz gerekli - Mac)
docker-compose --profile ui up

# Yerel olarak
python src/ui/app.py
```

### Experiment Çalıştırma

```bash
# Docker ile (20 senaryo × 5 tekrar)
docker-compose --profile experiment-full up

# Yerel olarak
python experiments/experiment_runner.py

# Sonuçlar: experiments/results/
```

### Demo Script

```bash
# Docker içinde
python demo.py

# Yerel olarak
python demo.py
```

---

## 🔧 Karşılaşılan Sorunlar ve Çözümler

### 1. ACO Bandwidth Sorunu (Düzeltildi ✅)

**Problem:** 900+ Mbps bandwidth değerleri için ACO path bulamıyordu.

**Sebep:** 
- `_select_next_node()` metodunda fallback mekanizması yetersiz bandwidth'li edge'leri seçiyordu
- `construct_solution()` metodunda bandwidth kontrolü yapılmadan shortest path döndürülüyordu

**Çözüm:**
- Fallback mekanizması kaldırıldı - sadece yeterli bandwidth'e sahip edge'ler seçiliyor
- Shortest path fallback'inde bandwidth kontrolü eklendi
- Daha agresif loglama eklendi

**Dosya:** `src/algorithms/aco/ant_colony.py`

### 2. `name 'penalty' is not defined` Hatası (Düzeltildi ✅)

**Problem:** ACO algoritmasında `penalty` değişkeni tanımsızdı.

**Sebep:** `_path_cost()` metodunda `return cost + penalty` kullanılıyordu ama `penalty` tanımlanmamıştı.

**Çözüm:** `return cost + penalty` → `return cost` olarak değiştirildi. `weighted_sum()` fonksiyonu zaten toplam maliyeti hesaplıyor.

**Dosya:** `src/algorithms/aco/ant_colony.py` (satır 249)

### 3. UI Bandwidth Validasyonu (Doğru ✅)

**Durum:** ✅ Doğru
- HTML input: `min="100" max="1000"`
- Backend validation: `if bandwidth < 100 or bandwidth > 1000:`
- PDF gereksinimine uygun: [100-1000 Mbps]

---

## 📊 Deney Talimatları

### Senaryo Üretimi

20 farklı (Source, Destination, Bandwidth) senaryosu otomatik olarak üretilir:
- Source: Rastgele düğüm (0-249)
- Destination: Rastgele düğüm (0-249, Source ≠ Destination)
- Bandwidth: [100-1000 Mbps] arası rastgele

### Tekrar ve Analiz

Her senaryo için:
- **5 tekrar** çalıştırılır
- **Ortalama, standart sapma, en iyi-en kötü** değerler hesaplanır
- **Çalışma süresi** loglanır
- Sonuçlar JSON formatında kaydedilir: `experiments/results/`

### Sonuç Analizi

```bash
python experiments/result_analyzer.py
```

---

## 👥 Grup Bilgileri

 
**Bölüm:** BTBS

### Grup Üyeleri

1. **Hamid Karimli**
   
2. **Haydar Bayramov**

---

## 📝 Proje Sunumu İçin Hazırlık

### Görev Dağılımı
- **Hamid Karimli:** Ağ modeli, metrikler, GA, path validation, experiment runner, Docker
- **Haydar Bayramov:** ACO testleri, dokümantasyon, UI görselleştirme

### Öğrenim Süreci
- **NetworkX:** Graf manipülasyonu ve görselleştirme
- **FastAPI:** Web API geliştirme
- **Docker:** Containerization ve deployment
- **Meta-heuristic Algoritmalar:** GA ve ACO teorisi ve pratik uygulama
- **Multi-objective Optimization:** Ağırlıklı toplam yaklaşımı

### Karşılaşılan Zorluklar ve Çözümler
1. **ACO Bandwidth Sorunu:** Agresif bandwidth filtresi ile çözüldü
2. **Penalty Hatası:** Gereksiz penalty değişkeni kaldırıldı
3. **Docker GUI:** XQuartz entegrasyonu ile Mac'te çözüldü
4. **Experiment UI:** FastAPI route'ları ile web tabanlı çözüm

### Sistem Mimarisi ve İşleyiş
- **Frontend:** HTML/CSS/JavaScript (Cytoscape.js)
- **Backend:** FastAPI (Python)
- **Algoritmalar:** GA, ACO (Python)
- **Görselleştirme:** NetworkX, Matplotlib, Cytoscape.js
- **Deployment:** Docker, Docker Compose

### Algoritma Tasarımı
- **GA:** Crossover (tek/iki nokta), Mutation (swap/insertion), Selection (tournament/roulette)
- **ACO:** Pheromone model, Heuristic value, Path construction, Bandwidth filtering

### Uygulama Demosu
- Web UI üzerinden canlı demo
- Experiment UI ile 20 senaryo testi
- Algoritma karşılaştırması (GA vs ACO)

---

## 📚 Dokümantasyon

- **`DOCKER_GUIDE.md`:** Docker kurulumu ve kullanımı
- **`DOCKER_CACHE_CLEAN.md`:** Docker cache temizleme
- **`QUICK_START.md`:** Hızlı başlangıç rehberi
- **`EXPERIMENT_GUIDE.md`:** Deney çalıştırma rehberi
- **`EXPERIMENT_EXPLAINED.md`:** Deney kavramları açıklaması
- **`PROJECT_STATUS.md`:** Detaylı proje durumu
- **`PROJECT_COMPLETION.md`:** Proje tamamlanma durumu
- **`ISSUES.md`:** Kalan görevler (issue formatında)

---

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest tests/

# Belirli bir test dosyası
pytest tests/test_metrics.py
```

---

## 📄 Lisans

MIT (bkz. `LICENSE`)

---


