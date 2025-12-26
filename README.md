BSM307 Multi-Objective Routing
==============================

Çok amaçlı yönlendirme problemini GA, ACO, RL (Q-Learning) ve SA algoritmalarıyla incelemek için uçtan uca bir araştırma altyapısı. Ağ üretimi, metrik hesapları, algoritma kıyaslama, görselleştirme ve raporlama adımlarını kapsar.

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
1) Python 3.10+ kullanın.
2) Sanal ortam oluşturun ve bağımlılıkları kurun:
   ```
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3) Proje kökünü `PYTHONPATH`'a ekleyin (geliştirme kolaylığı):
   ```
   export PYTHONPATH=$(pwd)
   ```

### Docker Kurulumu (Önerilen)
1) Docker Desktop kurulumu:
   ```bash
   # Mac (Homebrew)
   brew install --cask docker
   
   # Docker Desktop'u başlat ve çalıştığını kontrol et
   docker --version
   ```

2) Docker ile çalıştır:
   ```bash
   # Development mode (volume mount ile)
   docker-compose --profile dev up
   
   # Production mode
   docker-compose --profile prod up
   
   # GUI mode (XQuartz gerekli - Mac)
   docker-compose --profile gui up
   
   # Interactive UI mode (XQuartz gerekli - Mac)
   docker-compose --profile ui up
   
   # Web server mode (FastAPI - http://localhost:8001)
   docker-compose --profile web up
   ```

3) Detaylı Docker dokümantasyonu için: `docker/README.md`

Örnek Çalışma Akışı

### Docker ile (En Kolay)
```bash
# Demo script'ini çalıştır
docker-compose --profile dev up

# Veya manuel
docker build -t bsm307-routing .
docker run --rm bsm307-routing
```

### Yerel Python ile
- Ağ oluştur: `RandomNetworkGenerator.generate()`.
- Metrikleri hesapla: `delay`, `reliability`, `resource_cost` modüllerini kullan.
- Algoritma çalıştır: `GeneticAlgorithm`, `AntColonyOptimizer`, `QLearningRouter`, `SimulatedAnnealingRouter`.
- Görselleştir: `src/ui/app.py` veya `graph_visualizer.py`.

### Demo Script
```bash
# Docker içinde
python demo.py

# Yerel olarak
python demo.py
```

Deney Talimatları
- `experiments/` altında 20 farklı (S, D, B) senaryosu üret; her algoritmayı 5 kez çalıştır.
- Sonuçları topla, ortalama/std hesapla, matplotlib/seaborn ile grafikleştir.

Rapor Yapısı
- Bölüm taslakları `docs/report/sections.md` içinde.
- Mimari diyagramlar `docs/diagrams/` altında.
- Ekran görüntüleri için `docs/diagrams/ui-screenshots/` yer tutucusu oluşturulabilir.

Ekran Görüntüsü Yer Tutucuları
- `docs/diagrams/ui-screenshots/` klasörüne PNG/JPEG ekleyin.

Katkı Rehberi / PR Checklist
- [ ] İlgili issue linki eklendi
- [ ] Testler çalıştırıldı
- [ ] Dokümantasyon/README güncellendi (gerekiyorsa)
- [ ] Logger kullanımı tutarlı

Lisans
- MIT (bkz. `LICENSE`).
