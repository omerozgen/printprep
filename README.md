# PrintPrep

STL model analizi ve slicer ayar önerisi aracı.

3D baskı modellerinizdeki sorunları tespit edin, slicer ayarlarınızı otomatik önerin.

## Özellikler

- **Model Analizi**: Overlapping geometry, thin walls, inverted normals tespiti
- **Sorun Tespiti**: Baskı öncesi potansiyel hataların belirlenmesi
- **Slicer Önerileri**: Creality Print ve AnycubicSlicerNext için ayar profilleri
- **Model Onarım**: Temel mesh onarım işlemleri

## Kurulum

```bash
pip install printprep
```

## Hızlı Başlangıç

```bash
# Model analizi
printprep analyze model.stl

# Sorun düzeltme
printprep fix model.stl --output fixed_model.stl

# En iyi baskı pozisyonuna yatır
printprep orient model.stl --output oriented_model.stl

# Ayrı gövdeleri tek parçaya birleştir (boolean union için: pip install -e ".[merge]")
printprep merge model.stl --output merged_model.stl

# Agresif onarım (inatçı meshler için, opsiyonel): pip install -e ".[repair]"
#   fix komutu standart onarım yetmezse otomatik olarak pymeshfix'e yükselir
#   (geometriyi bozacaksa güvenlik koruması devreye girip standart sonucu korur)

# Bir klasördeki tüm STL'leri toplu analiz et
printprep batch ./models --json report.json

# Slicer ayar önerisi
printprep suggest model.stl --slicer creality --material pla

# Kendi slicer profilini kullan (OrcaSlicer .json / PrusaSlicer .ini / Cura .fdm_material)
printprep suggest model.stl --slicer creality --import-profile my_filament.json

# Slicer'a doğrudan yüklenebilir profil dosyaları üret
#   orca  -> OrcaSlicer / Creality Print / Anycubic Slicer (.json: filament + process)
#   prusa -> PrusaSlicer / SuperSlicer (.ini)
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

## Web Arayüzü

Tarayıcıda 3D önizleme, sürükle-bırak analiz, onarım ve slicer önerisi:

```bash
pip install -e ".[web]"   # tek seferlik
printprep serve           # http://127.0.0.1:8000
```

## Masaüstü Uygulaması

Tarayıcıya gerek yok — `printprep app` web arayüzünü kendi native penceresinde açar (WKWebView/WebView2/GTK WebKit). Sunucu aynı süreçte arka planda çalışır; pencereyi kapatınca her şey kapanır.

```bash
pip install -e ".[web,desktop]"   # pywebview dahil
printprep app                     # native pencerede aç
```

Çift-tıkla başlatıcılar (tüm platformlar için):

- **macOS:** `PrintPrep.app`'i çift-tıkla (veya Dock'a sürükle / `/Applications` klasörüne kopyala)
- **Windows:** `PrintPrep.bat`'i çift-tıkla (Masaüstü kısayolu olarak da çalışır)
- **Linux:** `./install-linux.sh` çalıştır → `~/.local/share/applications/printprep.desktop` kurulur ve uygulama menüsünde **PrintPrep** olarak görünür

Tümü aynı `printprep app` komutunu çağırır. Pywebview kurulu değilse otomatik olarak `printprep serve` + varsayılan tarayıcıya düşer.

Tamamen yerel çalışır — model verisi bilgisayardan çıkmaz. 3D görünümde overhang
yüzeyleri kırmızı, ince duvarlar amber, delik/açık kenarlar macenta işaretlenir;
ayrı gövdeler farklı renklere boyanır. Modeli en iyi pozisyona yatırabilir, kendi
slicer profilini içe aktarabilir ve slicer'a doğrudan yüklenebilir profil (.zip)
dışa aktarabilirsin.

Malzeme ön ayarları (sıcaklık, akış) [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer)
açık kaynak filament kütüphanesinden alınmıştır; geometri analizi modelden hesaplanır.

## Geliştirme

```bash
# Clone
git clone https://github.com/omerozgen/printprep.git
cd printprep

# Virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Dependencies
pip install -e ".[dev]"

# Test (Python)
pytest

# Test (3D viewer geometri yardımcıları, Node 18+)
node --test tests/js/geometry-utils.test.mjs
```

## Desteklenen Slicers

- Creality Print
- AnycubicSlicerNext

## Lisans

MIT License
