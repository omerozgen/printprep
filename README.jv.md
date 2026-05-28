# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | **Basa Jawa** | [한국어](README.ko.md) | [Français](README.fr.md)

Alat analisis model STL lan saran profil slicer.

Goleki masalah cetak sing mungkin sadurunge slicing, lan entuk setelan slicer sing cocog karo model panjenengan.

## Fitur

- **Analisis model** — geometri tumpang tindih, tembok tipis, normals kuwalik, pinggir mbukak/bolongan, awak kapisah, pinggir non-manifold, swa-tabrakan.
- **Deteksi masalah** — kenali kegagalan potensial sadurunge wiwitan cetak.
- **Saran slicer** — preset profil kanggo Creality Print lan AnycubicSlicerNext.
- **Ndandani mesh** — ndandani dhasar plus eskalasi agresif opsional liwat `pymeshfix` kanthi jaga sing nolak asil rusak.
- **100% lokal** — data model ora tau ninggalake komputer. Ora butuh akun, ora ana telemetri.

## Instalasi

```bash
pip install printprep
```

## Mulai cepet

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # mbutuhake: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

Ganti CLI menyang Basa Jawa: `export PRINTPREP_LANG=jv`

## Web UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Aplikasi desktop

`printprep app` mbukak web UI ing jendela asli (WKWebView ing macOS, WebView2 ing Windows, GTK WebKit ing Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Peluncur klik-loro: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Mlaku kabeh lokal — data ora tau ninggalake mesin.

Preset materi saka pustaka filamen open-source [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — pirsani [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Pangembangan

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

Pirsani [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Slicer sing didukung

- Creality Print
- AnycubicSlicerNext
- Ekspor profil uga nyakup format OrcaSlicer / PrusaSlicer / SuperSlicer.

## Status

Pratinjau Pre-1.0 (`0.1.x`). API lan CLI bisa owah. Laporan bug lan PR ditampa.

## Lisensi

[MIT](LICENSE). Atribusi pihak katelu ing [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
