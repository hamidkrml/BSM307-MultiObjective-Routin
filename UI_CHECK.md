# UI Kontrol Listesi

Dosya: `src/ui/app.py`

## Buton Kontrolü

Buton satır 201-204'te tanımlanmış:
```python
# Experiment UI butonu (ayrı UI'ye geçiş)
ax_exp_ui = plt.axes([0.76, 0.05, 0.15, 0.04])
self.button_exp_ui = Button(ax_exp_ui, "Experiment UI'ye Git", color="lightcyan")
self.button_exp_ui.on_clicked(self.open_experiment_ui)
```

## Türkçe Çeviriler Kontrolü

✅ Başlık: "BSM307 Çok Amaçlı Yönlendirme - Etkileşimli Arayüz"
✅ Kaynak: "Kaynak: "
✅ Hedef: "Hedef: "
✅ Bant Genişliği: "Bant Genişliği (Mbps): "
✅ Algoritma: "Algoritma (GA/ACO): "
✅ Gecikme Ağırlığı: "Gecikme Ağırlığı"
✅ Güvenilirlik Ağırlığı: "Güvenilirlik Ağırlığı"
✅ Kaynak Ağırlığı: "Kaynak Ağırlığı"
✅ Yol Hesapla: "Yol Hesapla"
✅ Senaryolar: "Senaryolar: "
✅ Tekrarlar: "Tekrarlar: "
✅ Deneyi Çalıştır: "Deneyi Çalıştır"
✅ Experiment UI'ye Git: "Experiment UI'ye Git"

## Sorun Giderme

Eğer buton görünmüyorsa:
1. UI'yi kapatıp yeniden başlatın
2. Python cache'ini temizleyin: `find . -name "*.pyc" -delete`
3. Dosyayı kaydedip tekrar çalıştırın

