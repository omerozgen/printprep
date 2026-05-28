# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | **ਪੰਜਾਬੀ** | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL ਮਾਡਲ ਵਿਸ਼ਲੇਸ਼ਣ ਅਤੇ ਸਲਾਈਸਰ ਪ੍ਰੋਫਾਈਲ ਸਲਾਹ ਟੂਲ।

ਸਲਾਈਸਿੰਗ ਤੋਂ ਪਹਿਲਾਂ ਸੰਭਾਵੀ ਪ੍ਰਿੰਟ ਸਮੱਸਿਆਵਾਂ ਨੂੰ ਪਛਾਣੋ, ਅਤੇ ਆਪਣੇ ਮਾਡਲ ਅਨੁਸਾਰ ਸਲਾਈਸਰ ਸੈਟਿੰਗਾਂ ਪ੍ਰਾਪਤ ਕਰੋ।

## ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ

- **ਮਾਡਲ ਵਿਸ਼ਲੇਸ਼ਣ** — ਓਵਰਲੈਪਿੰਗ ਜਿਓਮੈਟਰੀ, ਪਤਲੀਆਂ ਕੰਧਾਂ, ਉਲਟੇ normals, ਖੁੱਲ੍ਹੇ ਕਿਨਾਰੇ/ਛੇਕ, ਵੱਖਰੇ ਬਾਡੀਜ਼, non-manifold ਕਿਨਾਰੇ, ਸਵੈ-ਪ੍ਰਤੀਛੇਦਨ।
- **ਸਮੱਸਿਆ ਖੋਜ** — ਪ੍ਰਿੰਟ ਸ਼ੁਰੂ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਸੰਭਾਵੀ ਅਸਫਲਤਾਵਾਂ ਪਛਾਣੋ।
- **ਸਲਾਈਸਰ ਸਲਾਹ** — Creality Print ਅਤੇ AnycubicSlicerNext ਲਈ ਪ੍ਰੋਫਾਈਲ ਪ੍ਰੀਸੈਟ।
- **mesh ਮੁਰੰਮਤ** — ਮੁੱਢਲੀ ਮੁਰੰਮਤ ਨਾਲ `pymeshfix` ਰਾਹੀਂ ਵਿਕਲਪਿਕ ਸਖ਼ਤ ਮੁਰੰਮਤ (ਖਰਾਬ ਨਤੀਜਿਆਂ ਨੂੰ ਰੱਦ ਕਰਨ ਵਾਲੇ ਗਾਰਡ ਨਾਲ)।
- **100% ਸਥਾਨਕ** — ਮਾਡਲ ਡਾਟਾ ਕਦੇ ਤੁਹਾਡੀ ਮਸ਼ੀਨ ਨਹੀਂ ਛੱਡਦਾ। ਕੋਈ ਖਾਤਾ ਨਹੀਂ, ਕੋਈ ਟੈਲੀਮੈਟਰੀ ਨਹੀਂ।

## ਇੰਸਟਾਲੇਸ਼ਨ

```bash
pip install printprep
```

## ਤੇਜ਼ ਸ਼ੁਰੂਆਤ

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # ਲੋੜ: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI ਨੂੰ ਪੰਜਾਬੀ ਵਿੱਚ ਬਦਲੋ: `export PRINTPREP_LANG=pa`

## ਵੈੱਬ UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## ਡੈਸਕਟਾਪ ਐਪ

`printprep app` ਵੈੱਬ UI ਨੂੰ ਨੇਟਿਵ ਵਿੰਡੋ ਵਿੱਚ ਖੋਲ੍ਹਦਾ ਹੈ (macOS ਉੱਤੇ WKWebView, Windows ਉੱਤੇ WebView2, Linux ਉੱਤੇ GTK WebKit)।

```bash
pip install -e ".[web,desktop]"
printprep app
```

ਡਬਲ-ਕਲਿੱਕ ਲਾਂਚਰ: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`।

ਪੂਰੀ ਤਰ੍ਹਾਂ ਸਥਾਨਕ ਚੱਲਦਾ — ਤੁਹਾਡਾ ਡਾਟਾ ਮਸ਼ੀਨ ਨਹੀਂ ਛੱਡਦਾ।

ਸਮੱਗਰੀ ਪ੍ਰੀਸੈਟ [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) ਓਪਨ-ਸੋਰਸ filament ਲਾਈਬ੍ਰੇਰੀ ਤੋਂ — ਵੇਖੋ [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)।

## ਵਿਕਾਸ

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

ਵੇਖੋ [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md)।

## ਸਮਰਥਿਤ ਸਲਾਈਸਰ

- Creality Print
- AnycubicSlicerNext
- ਪ੍ਰੋਫਾਈਲ ਨਿਰਯਾਤ OrcaSlicer / PrusaSlicer / SuperSlicer ਫਾਰਮੈਟਾਂ ਨੂੰ ਵੀ ਕਵਰ ਕਰਦਾ ਹੈ।

## ਸਥਿਤੀ

Pre-1.0 ਪ੍ਰੀਵਿਊ (`0.1.x`)। API ਅਤੇ CLI ਬਦਲ ਸਕਦੇ ਹਨ। bug ਰਿਪੋਰਟਾਂ ਅਤੇ PR ਜੀ ਆਇਆਂ ਨੂੰ।

## ਲਾਈਸੈਂਸ

[MIT](LICENSE)। ਥਰਡ-ਪਾਰਟੀ attributions [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) ਵਿੱਚ।
