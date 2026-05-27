# PrintPrep - 3D Baskı Model Analiz & Slicer Öneri Sistemi

## Proje Özeti

**PrintPrep**, STL formatındaki 3D baskı modellerini analiz eden, potansiyel baskı sorunlarını tespit eden ve modelin özelliklerine göre uygun slicer ayarlarını öneren açık kaynaklı bir araçtır.

### Hedef Kitle
- Kişisel 3D baskı kullanıcıları
- Maker topluluğu
- İleride: açık kaynak katkıcıları ve ticari kullanıcılar

---

## Problem Tanımı

3D baskı sürecinde iki kritik sorun var:

1. **Model Kalitesi Sorunları**
   - Overlapping geometry (çakışan yüzeyler)
   - Non-manifold edges ( açık meshler, delikler)
   - Inverted normals ( ters yüzey normalleri)
   - Thin walls ( çok ince duvarlar - baskı için uygunsuz)
   - Self-intersections ( kendi kendisiyle kesişen yüzeyler)
   - Holes in mesh (mesh içinde delikler)
   - Non-watertight models ( su sızdırmaz olmayan meshler)

2. **Slicer Ayar Belirsizliği**
   - Hangi model için hangi infill oranı uygun?
   - Destek gereksinimi ne olmalı?
   - Katman yüksekliği ne olmalı?
   - Filament sıcaklıkları ne olmalı?
   - Overhang açıları için hangi ayarlar gerekli?

---

## Hedef Özellikler

### 1. Model Analizi Modülü
- [ ] **Mesh Validasyonu**
  - Watertight (kapalı mesh) kontrolü
  - Manifold durumu kontrolü
  - Normal yön kontrolü
  - Orientation (hangi yüzün aşağı/içeri) tespiti

- [ ] **Geometri Analizi**
  - Volume hesaplama (cm³)
  - Surface area hesaplama (cm²)
  - Bounding box boyutları
  - En kalın ve en ince kesit ölçümü
  - Thin wall tespiti (configurable threshold)

- [ ] **Sorun Tespiti**
  - Overlapping triangles
  - Degenerate triangles (sıfır alanlı üçgenler)
  - Self-intersecting faces
  - Sharp edges / overhang angles
  - Hole detection
  - Connected component analizi

- [ ] **Otomatik Düzeltme Önerileri**
  - Repair commands (fix normals, fill holes, merge vertices)
  - Simplification önerileri (very complex modeller için)
  - Orientation önerileri (en iyi baskı pozisyonu)

### 2. Slicer Ayar Öneri Modülü

#### Model Bazlı Öneriler
| Parametre | Analiz Bazlı Kriter |
|-----------|---------------------|
| Infill % | Modelin iç dolgu yoğunluğu gereksinimi |
| Layer Height | Model detay seviyesi + baskı hızı dengesi |
| Support | Overhang açısı > 45° ise gerekli |
| Brim | Model taban alanı ve aderans gereksinimi |
| Wall Count | Model duvar kalınlığı gereksinimi |

#### Slicera Özel Çıktı
- [ ] **Creality Print** profil ayarları (JSON/config export)
- [ ] **AnycubicSlicerNext** profil ayarları (JSON/config export)

Her slicer için ayrı:
- Material preset (PLA, PETG, ABS, TPU vb.)
- Temperature settings
- Speed settings
- Retraction settings

### 3. Model Onarım Araçları
- [ ] Normal düzeltme
- [ ] Hole filling (delik kapatma)
- [ ] Vertex merging (birleşik olmayan vertexleri birleştirme)
- [ ] Watertightify (mesh'i su geçirmez hale getirme)
- [ ] Decimation (gereksiz geometri azaltma)
- [ ] Export with embedded metadata (analiz sonuçları ile birlikte)

### 4. Kullanıcı Arayüzü Seçenekleri

#### CLI (Komut Satırı) - Birincil Hedef
```
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep suggest model.stl --slicer creality
```

#### Web Arayüzü (İkincil - v2)
- File upload
- Interactive 3D preview
- Sonuçların görsel gösterimi
- Batch processing

#### Desktop App (v2-3)
- Electron veya Tauri tabanlı
- Offline çalışma
- Local file system erişimi

---

## Teknoloji Stack

### Core (Python)
| Kütüphane | Kullanım Amacı |
|-----------|----------------|
| `numpy` | Numerik hesaplamalar |
| `scipy` | Geometrik analiz algoritmaları |
| `trimesh` | Mesh okuma, analiz, basit onarım |
| `skimage` | Görüntü işleme (mesh'den 2D kesitler için) |
| `networkx` | Graph analizi (connected components) |

### Mesh Processing (Advanced)
| Kütüphane | Kullanım Amacı |
|-----------|----------------|
| `pyCGAL` veya `cgal-bindings` | Advanced mesh repair, boolean operations |
| `open3d` | 3D görselleştirme ve advanced ICP |

### CLI & Config
| Kütüphane | Kullanım Amacı |
|-----------|----------------|
| `click` veya `argparse` | CLI interface |
| `pydantic` | Config validation |
| `rich` | CLI'da güzel output |

### Testing
| Kütüphane | Kullanım Amacı |
|-----------|----------------|
| `pytest` | Unit testing |
| `pytest-cov` | Coverage reporting |

---

## Proje Yapısı

```
stl-project/
├── PRINTPREP.md                 # Bu dosya - detaylı proje planı
├── README.md                    # Kullanıcıya açıklama
├── LICENSE                     # MIT/Apache
├── setup.py                    # Package setup
├── pyproject.toml              # Modern Python package config
├── requirements.txt            # Dependency list
├── requirements-dev.txt        # Development dependencies
│
├── printprep/                  # Main package
│   ├── __init__.py
│   ├── cli.py                  # CLI entry point
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── mesh.py             # Mesh loading and basic operations
│   │   ├── analyzer.py         # Geometry analysis
│   │   ├── validator.py         # Problem detection
│   │   └── repair.py            # Fix/repair operations
│   │
│   ├── slicer/                 # Slicer-specific output
│   │   ├── __init__.py
│   │   ├── base.py              # Base profile generator
│   │   ├── creality.py          # Creality Print profiles
│   │   └── anycubic.py          # AnycubicSlicerNext profiles
│   │
│   ├── config/                  # Configuration
│   │   ├── __init__.py
│   │   ├── defaults.py          # Default thresholds
│   │   └── presets.py           # Material presets
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── geometry.py          # Geometry helper functions
│       └── export.py            # Export functions
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_validator.py
│   └── test_repair.py
│
├── examples/                    # Example models and usage
│   └── sample_workflow.py
│
└── docs/                        # Documentation
    ├── installation.md
    ├── usage.md
    └── api.md
```

---

## Mimari Kararlar

### Neden Python?
1. **Erişilebilirlik** - En geniş kitleye ulaşılabilir
2. **Mesh kütüphaneleri** - `trimesh`, `pyCGAL`, `open3d` Python'da en olgun
3. **Açık kaynak uyumu** - Katkıcı bulması kolay
4. **Prototipleme** - Hızlı geliştirme döngüsü

### Neden trimesh?
- STL okuma/yazma (native)
- Basic repair operations
- Visualization
- Cross-platform
- MIT lisans

### Mimari Prensipler
1. **Modüler** - Her modül bağımsız test edilebilir
2. **Extendable** - Yeni slicer desteği kolayca eklenebilir
3. **CLI-first** - Tüm fonksiyonalite CLI'dan erişilebilir olmalı
4. **Fail-fast** - Analiz hataları kullanıcıya anlaşılır mesajlarla raporlanmalı

---

## Geliştirme Aşamaları

### v0.1 - Proof of Concept
- [x] Proje planı
- [ ] Basic mesh loading (trimesh ile)
- [ ] Volume/surface area hesaplama
- [ ] Basic CLI skeleton

### v0.2 - Core Analysis
- [ ] Watertight check
- [ ] Normal direction check
- [ ] Basic problem detection
- [ ] CLI full implementation

### v0.3 - Slicer Integration
- [ ] Creality Print profile export
- [ ] AnycubicSlicerNext profile export
- [ ] Material presets

### v0.4 - Repair Tools
- [ ] Basic repair operations
- [ ] Interactive fix suggestions
- [ ] Export with metadata

### v1.0 - Alpha Release
- [ ] Full CLI functionality
- [ ] Test suite
- [ ] Documentation
- [ ] PyPI release

### v2.0 - Web Interface (Optional)
- [ ] Flask/FastAPI backend
- [ ] React/Vue frontend
- [ ] File upload & processing

---

## Örnek Kullanım Senaryoları

### Senaryo 1: Model Analizi
```
$ printprep analyze ./models/artifact_vase.stl

Model: artifact_vase.stl
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Volume: 124.3 cm³
Surface Area: 89.7 cm²
Dimensions: 12.4 x 8.2 x 18.7 cm

Issues Found:
⚠ Thin wall detected: 0.8mm at base (recommended: 1.2mm minimum)
⚠ Overhang detected: 67° angle near top (requires support)
⚠ Normal inconsistency: 3 faces inverted

Recommended Printer Settings (Creality Print):
├── Layer Height: 0.16mm
├── Infill: 15%
├── Supports: YES (angle > 45°)
├── Wall Count: 2
└── First Layer Temp: 210°C / 205°C
```

### Senaryo 2: Otomatik Düzeltme
```
$ printprep fix ./models/broken_mesh.stl --output fixed/

Applying fixes:
✓ Fixed 12 inverted normals
✓ Merged 34 duplicate vertices
✓ Filled 2 holes
✓ Watertightness verified

Output: fixed/broken_mesh.stl
Status: READY FOR SLICING
```

### Senaryo 3: Slicer Profile Export
```
$ printprep suggest ./models/phone_stand.stl --slicer anycubic --material petg

AnycubicSlicerNext Profile:
{
  "material": "PETG",
  "nozzle_temp": 240,
  "bed_temp": 80,
  "infill": 20,
  "layer_height": 0.16,
  "wall_count": 3,
  "support": "tree_auto",
  "retraction": "smart"
}
```

---

## TODO Listesi (İlk Sprint İçin)

### Setup
- [ ] Git init ve initial commit
- [ ] pyproject.toml oluştur
- [ ] Virtual environment setup
- [ ] Dependencies installed

### Core (v0.1-0.2)
- [ ] Mesh loading with trimesh
- [ ] Volume/surface calculator
- [ ] Dimensions extractor
- [ ] Watertight checker
- [ ] Normal analyzer
- [ ] Thin wall detector
- [ ] Overhang angle calculator

### CLI (v0.1)
- [ ] analyze command
- [ ] fix command
- [ ] suggest command

### Slicer Profiles (v0.3)
- [ ] Creality Print JSON profile generator
- [ ] AnycubicSlicerNext JSON profile generator
- [ ] PLA material preset
- [ ] PETG material preset

### Testing
- [ ] Unit tests for analyzer
- [ ] Unit tests for validator
- [ ] Integration tests

### Documentation
- [ ] README.md
- [ ] Installation guide
- [ ] Basic usage guide

---

## Kaynaklar & Referanslar

### Mesh Processing
- [trimesh documentation](https://trimsh.org/)
- [PyCGAL](https://github.com/MmgTools/pymcgol)
- [Open3D](http://www.open3d.org/docs/release/)

### 3D Printing References
- [Creality Print docs](https://www.creality.com/pages/download)
- [AnycubicSlicer](https://www.anycubic.com/pages/anycubic-slicer)
- [ slic3r Project Documentation](https://manual.slic3r.org/)

### Algorithms
- Watertight mesh detection: [Jump Flood Algorithm](https://en.wikipedia.org/wiki/Jump_Flood_Algorithm)
- Convex Hull: [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html)
- Mesh boolean: [CGAL documentation](https://doc.cgal.org/latest/Mesh_3/)

---

## Katkıda Bulunma (Gelecek Planı)

Açık kaynak yayınladığında:
1. GitHub repository setup
2. Contributing guidelines
3. Code of conduct
4. Issue templates
5. Pull request workflow
6. Release process

### Potential Contributors
- 3D printing enthusiasts
- Python developers
- Mesh processing experts
- UI/UX designers (for web version)

---

## License Seçimi

**MIT License** önerilir:
- Ticari kullanıma izin
- Modify ve private fork yapılabilir
- Minimal restristion
- Topluluk katkısı için en yaygın tercih

Alternatif: **Apache 2.0** (Google/Microsoft tercihi)

---

*Son güncelleme: 2026-05-27*
*Proje: PrintPrep v0.1*
