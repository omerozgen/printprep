# PrintPrep

<p align="center">
  <img src="https://raw.githubusercontent.com/omerozgen/printprep/main/printprep/web/static/favicon.ico" alt="PrintPrep Logo" width="80" height="80" />
</p>

<p align="center">
  <b>%100 Çevrimdışı & Yerel STL Model Analizi, Otomatik Mesh Onarımı ve Dilimleyici (Slicer) Asistanı</b>
</p>

<p align="center">
  <a href="https://github.com/omerozgen/printprep/actions/workflows/ci.yml"><img src="https://github.com/omerozgen/printprep/actions/workflows/ci.yml/badge.svg" alt="CI Durumu" /></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="Lisans: MIT" /></a>
  <img src="https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue" alt="Python Sürümleri" />
  <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey" alt="Platform" />
  <img src="https://img.shields.io/badge/privacy-%25100%20yerel%20%26%20çevrimdışı-green" alt="%100 Çevrimdışı" />
</p>

---

<p align="center">
  <b>🌐 Dil Seçimi / Choose Language:</b><br>
  <a href="README.md">English</a> •
  <b>Türkçe</b> •
  <a href="README.zh.md">中文</a> •
  <a href="README.de.md">Deutsch</a> •
  <a href="README.es.md">Español</a> •
  <a href="README.fr.md">Français</a> •
  <a href="README.ja.md">日本語</a> •
  <a href="README.ko.md">한국어</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.pt.md">Português</a> •
  <a href="README.ar.md">العربية</a> •
  <a href="README.hi.md">हिन्दी</a> •
  <a href="README.bn.md">বাংলা</a> •
  <a href="README.pa.md">ਪੰਜਾਬੀ</a> •
  <a href="README.jv.md">Basa Jawa</a>
</p>

---

## 📖 Genel Bakış

**PrintPrep**, 3D baskı sürecinden önce modellerinizi uçtan uca denetleyen, onaran ve optimize eden kapsamlı bir baskı öncesi hazırlık aracıdır. Dilimleme (slicing) işleminden önce STL dosyalarınızdaki yapısal ve geometrik hataları tespit eder, delikleri kapatır, ters yüzeyleri düzeltir, modeli en az destek gerektiren açıya yatırır, birden fazla parçayı tablaya dizer ve kurulu dilimleyicinizle yazıcınızın donanım sınırlarına göre en uygun baskı ayarlarını otomatik önerir.

**🔒 %100 Yerel ve Güvenli:** Bulut bağımlılığı, telemetri, hesap oluşturma veya internet bağlantısı gerektirmez. Tüm mesh hesaplamaları ve model analizleri tamamen bilgisayarınızın kendi donanımında gerçekleşir.

---

## ✨ Temel Özellikler

### 🔍 Kapsamlı Mesh Analizi & Teşhis
- **Su Sızdırmazlık & Manifold Kontrolü:** Modelin kapalı hacim (watertight) olup olmadığını, açık kenar döngülerini (delikler) ve non-manifold kenarları denetler.
- **Işın İzlemeli Et Kalınlığı Analizi (Ray-Casting):** Model genelindeki duvar kalınlığı dağılımını (`min`, `p5`, `medyan`, `max`) ölçerek yazıcınızın basamayacağı kadar ince duvarları önceden haber verir.
- **Overhang (Askıda Kalan Yüzey) Tespiti:** Destek gerektiren aşağı bakan yüzeylerin oranını ve en dik sarkma açısını hesaplar.
- **Ters Yüzey Normalleri:** Dilimleyicilerin içini boş görmesine yol açan ters dönmüş üçgenleri (inverted normals) bulur.
- **Ayrık Gövde (Multi-body) Analizi:** Tek bir dosya içindeki birbirine bağlı olmayan bağımsız gövdeleri sayar ve listeler.
- **Kendi Kendini Kesen Yüzeyler:** Çakışan yüzeyleri işaretler (isteğe bağlı `[analyze]` paketi ile).

### 🛠️ Akıllı Model Onarımı & Boolean Birleştirme
- **Tek Komutla Onarım (`fix`):** Yinelenen köşeleri birleştirir, sıfır alanlı bozuk yüzeyleri siler, açık delikleri yamalar ve yüzey normallerini düzeltir.
- **Korumalı Agresif Onarım:** Standart onarımın yetmediği zorlu modellerde otomatik olarak `pymeshfix` motoruna geçer; model detaylarının bozulmasını önleyen akıllı bir hacim koruma kalkanına sahiptir.
- **Boolean Gövde Birleştirme (`merge`):** Parçalı gövdeleri `manifold3d` kütüphanesiyle tek ve katı bir manifold gövdeye dönüştürür.

### 🧭 Otomatik Yönlendirme & Tablaya Dizme
- **En İyi Açıya Yatırma (`orient`):** Konveks kabuk yüzey vektörlerini inceleyerek en az destek malzemesi harcayacak ve en kararlı oturacak baskı pozisyonunu bulur.
- **Çoklu Parça Paketleme (`pack`):** Klasördeki tüm STL'leri yazıcı tablasının boyutlarına göre aralarında güvenli boşluk bırakacak şekilde otomatik dizer.

### 🖨️ Yazıcı-Farkında Dilimleyici Önerileri & Maliyet Hesabı
- **Gerçek Donanım Entegrasyonu:** Kurulu dilimleyicinizden (Creality Print, OrcaSlicer, Anycubic Slicer, PrusaSlicer) nozzle çapı, tabla boyutları, hız ve geri çekme (retraction) limitlerini otomatik okur.
- **Gömülü Yazıcı Veritabanı:** Dilimleyici kurulu olmasa bile Creality, Anycubic, Bambu Lab ve Prusa gibi popüler yazıcıların hazır profillerini sunar.
- **Gerçek Zaman ve Maliyet Hesabı:** Dilimleyicinizdeki aktif filament yoğunluğu ve kg fiyatını kullanarak harcanacak filament miktarını (metre ve gram), tahmini baskı süresini ve maliyetini hesaplar.
- **Doğrudan Dışa Aktarma:** Dilimleyicinizin içine hemen aktarabileceğiniz `.json` (OrcaSlicer / Creality / Anycubic) ve `.ini` (PrusaSlicer / SuperSlicer) profil dosyaları üretir.

### 🖥️ Etkileşimli 3D Web & Masaüstü Arayüzü
- **Three.js 3D Önizleme:** Dosyayı sürükleyip bırakarak tarayıcıda görsel inceleme yapın:
  - 🔴 **Kırmızı:** Destek gerektiren sarkıntılar (overhang)
  - 🟡 **Sarı:** İnce duvarlar (< 0.8 mm)
  - 🟣 **Macenta:** Açık kenarlar ve delikler
  - 🔵 **Mavi/Camgöbeği:** Ters yüzey normalleri
  - 🌈 **Gökkuşağı Renkleri:** Birbirinden bağımsız ayrı gövdeler
- **Etkileşimli 3D Araçlar:** 2 noktalı 3D kumpas ölçüm cetveli ve modelin içini görmenizi sağlayan kesit düzlemi (clipping plane).
- **Masaüstü Uygulaması:** `pywebview` ile bağımsız native pencere olarak çalışır (`PrintPrep.app`, `PrintPrep.bat`, `PrintPrep.desktop`).

---

## 🚀 Kurulum

PyPI üzerinden doğrudan kurun:

```bash
pip install printprep
```

### İsteğe Bağlı Ek Özellik Paketleri

| Paket Adı | Kurulum Komutu | Açıklama |
| :--- | :--- | :--- |
| **Web Arayüzü** | `pip install "printprep[web]"` | FastAPI sunucusu ve Three.js 3D görselleştirici |
| **Masaüstü Uygulaması** | `pip install "printprep[web,desktop]"` | Native işletim sistemi masaüstü penceresi (`pywebview`) |
| **Agresif Onarım** | `pip install "printprep[repair]"` | İnatçı açık delikler için `pymeshfix` desteği |
| **Boolean Birleştirme**| `pip install "printprep[merge]"` | Ayrık gövdeler için `manifold3d` boolean union |
| **Kesişim Tespiti** | `pip install "printprep[analyze]"` | `pymeshlab` ile çakışan yüzey analizi (Python 3.10+) |
| **Tam Paket** | `pip install "printprep[all]"` | Tüm temel ve ek özellikleri eksiksiz kurar |

---

## ⚡ Hızlı Başlangıç (CLI)

```bash
# 1. STL modelini analiz et
printprep analyze model.stl

# 2. Delikleri, bozuk yüzeyleri ve ters normalleri onar
printprep fix model.stl --output onarilmis_model.stl

# 3. Modeli en az destek gerektirecek en ideal açıya yatır
printprep orient model.stl --output cevrilmis_model.stl

# 4. Birbirinden kopuk gövdeleri tek parça katı modele birleştir
printprep merge coklu_parca.stl --output birlesik.stl

# 5. Yazıcınıza ve malzemenize göre en iyi dilimleyici ayarlarını öner
printprep suggest model.stl --slicer creality --material pla --auto-printer

# 6. Klasördeki tüm STL'leri topluca analiz et ve JSON raporu al
printprep batch ./modeller --json rapor.json

# 7. Algılanan ve gömülü tüm 3D yazıcıları listele
printprep printer-list

# 8. Bilgisayarda kurulu slicer profil dizinlerini tara
printprep slicer-discover

# 9. Birden fazla modeli yazıcı tablasına otomatik yerleştir
printprep pack ./parcalar --bed-x 220 --bed-y 220 --output-dir ./yerlesim
```

---

## 🌐 Web Arayüzü

Yerel web arayüzünü başlatmak için:

```bash
printprep serve --host 127.0.0.1 --port 8000
```
Tarayıcınızda `http://127.0.0.1:8000` adresini açın. Modellerinizi sürükleyip bırakarak hataları renkli inceleyebilir, onarım öncesi/sonrası kıyaslaması yapabilir ve hazır profil dosyalarını indirebilirsiniz.

---

## 💻 Masaüstü Uygulaması

Tarayıcı açmadan doğrudan yerel masaüstü penceresinde çalıştırmak için:

```bash
printprep app
```

### Masaüstü Çift Tıklama Başlatıcıları

- **macOS:** `PrintPrep.app` uygulamasını çift tıklayın (veya Dock'a / Uygulamalar klasörüne ekleyin). Apple Silicon ve Rosetta uyumludur.
- **Windows:** `PrintPrep.bat` dosyasını çift tıklayın (Masaüstü kısayolu olarak kullanılabilir).
- **Linux:** `./install-linux.sh` komutunu çalıştırarak uygulama menünüze `PrintPrep.desktop` ekleyin.

---

## 🖨️ Desteklenen Dilimleyiciler

| Dilimleyici | Otomatik Tespit | Profil İçe Aktarma | Profil Dışa Aktarma |
| :--- | :---: | :---: | :---: |
| **OrcaSlicer** | ✅ Otomatik | ✅ `.json` | ✅ `.json` (Process + Filament) |
| **Creality Print (5.x / 7.x)** | ✅ Otomatik | ✅ `.json` | ✅ `.json` |
| **AnycubicSlicerNext** | ✅ Otomatik | ✅ `.json` | ✅ `.json` |
| **PrusaSlicer / SuperSlicer** | ✅ Otomatik | ✅ `.ini` | ✅ `.ini` |
| **UltiMaker Cura** | ✅ Otomatik | ✅ `.fdm_material` | — |
| **Bambu Studio** | ✅ Gömülü Özellikler | ✅ `.json` | ✅ `.json` |

---

## 🛠️ Geliştirme ve Test

```bash
# 1. Depoyu klonlayın
git clone https://github.com/omerozgen/printprep.git
cd printprep

# 2. Sanal ortamı oluşturun ve aktif edin
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Geliştirici bağımlılıklarını kurun
pip install -e ".[dev,web]"

# 4. Python testlerini çalıştırın (70 test)
pytest

# 5. JavaScript 3D geometri testlerini çalıştırın (Node 18+)
node --test tests/js/geometry-utils.test.mjs

# 6. Kod kalitesini denetleyin (Ruff)
ruff check printprep tests
```

---

## 📄 Lisans

Bu proje **MIT Lisansı** ile lisanslanmıştır — detaylar için [LICENSE](LICENSE) dosyasına bakabilirsiniz.

Üçüncü taraf açık kaynak kütüphaneler ve dilimleyici filament kütüphanesi atıfları [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) dosyasında listelenmiştir.
