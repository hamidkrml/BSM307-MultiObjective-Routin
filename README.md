BSM307 Multi-Objective Routing
==============================

Çok amaçlı yönlendirme problemini GA, ACO, RL (Q-Learning) ve SA algoritmalarıyla incelemek için uçtan uca bir araştırma altyapısı. Ağ üretimi, metrik hesapları, algoritma kıyaslama, görselleştirme ve raporlama adımlarını kapsar.

Öne Çıkanlar
- 250 düğümlü Erdos–Renyi rastgele grafik üreticisi; düğüm/bağ özellikleri.
- Metrikler: toplam gecikme, güvenilirlik maliyeti (−log R), kaynak maliyeti, ağırlıklı skor.
- Algoritmalar: GA, ACO, Q-Learning, Simulated Annealing iskeletleri.
- UI: networkx + matplotlib ile S-D seçimi, ağırlık slider'ları ve sonuç çizimi.
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

Örnek Çalışma Akışı
- Ağ oluştur: `RandomNetworkGenerator.generate()`.
- Metrikleri hesapla: `delay`, `reliability`, `resource_cost` modüllerini kullan.
- Algoritma çalıştır: `GeneticAlgorithm`, `AntColonyOptimizer`, `QLearningRouter`, `SimulatedAnnealingRouter`.
- Görselleştir: `src/ui/app.py` veya `graph_visualizer.py`.

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
