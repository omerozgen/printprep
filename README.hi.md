# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | **हिन्दी** | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL मॉडल विश्लेषण और स्लाइसर प्रोफाइल सुझाव उपकरण।

स्लाइस करने से पहले संभावित प्रिंट समस्याओं का पता लगाएँ और अपने मॉडल के अनुसार स्लाइसर सेटिंग्स प्राप्त करें।

## विशेषताएँ

- **मॉडल विश्लेषण** — अतिव्यापी ज्यामिति, पतली दीवारें, उल्टे normals, खुले किनारे/छेद, अलग बॉडी, non-manifold किनारे, स्व-प्रतिच्छेदन।
- **समस्या पहचान** — प्रिंट शुरू करने से पहले संभावित विफलताओं की पहचान करें।
- **स्लाइसर सुझाव** — Creality Print और AnycubicSlicerNext के लिए प्रोफाइल प्रीसेट।
- **मेश मरम्मत** — बुनियादी मरम्मत के साथ-साथ `pymeshfix` के माध्यम से वैकल्पिक सघन मरम्मत (विकृत परिणामों को अस्वीकार करने वाले गार्ड के साथ)।
- **100% स्थानीय** — मॉडल डेटा कभी आपकी मशीन नहीं छोड़ता। कोई खाता नहीं, कोई टेलीमेट्री नहीं।

## स्थापना

```bash
pip install printprep
```

## त्वरित आरंभ

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # आवश्यक: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI को हिन्दी में बदलें: `export PRINTPREP_LANG=hi`

## वेब UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## डेस्कटॉप ऐप

`printprep app` वेब UI को नेटिव विंडो में खोलता है (macOS पर WKWebView, Windows पर WebView2, Linux पर GTK WebKit)।

```bash
pip install -e ".[web,desktop]"
printprep app
```

डबल-क्लिक लॉन्चर: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`।

पूरी तरह स्थानीय रूप से चलता है — आपका डेटा मशीन नहीं छोड़ता।

सामग्री प्रीसेट [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) ओपन-सोर्स फिलामेंट लाइब्रेरी से — देखें [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)।

## विकास

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

देखें [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md)।

## समर्थित स्लाइसर

- Creality Print
- AnycubicSlicerNext
- प्रोफाइल निर्यात OrcaSlicer / PrusaSlicer / SuperSlicer प्रारूपों को भी कवर करता है।

## स्थिति

Pre-1.0 पूर्वावलोकन (`0.1.x`)। API और CLI बदल सकते हैं। बग रिपोर्ट और PR स्वागत हैं।

## लाइसेंस

[MIT](LICENSE)। तीसरे-पक्ष का श्रेय [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) में।
