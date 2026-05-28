# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | **বাংলা** | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL মডেল বিশ্লেষণ ও স্লাইসার প্রোফাইল পরামর্শ টুল।

স্লাইসিংয়ের আগে সম্ভাব্য মুদ্রণ সমস্যা শনাক্ত করুন এবং আপনার মডেল অনুযায়ী স্লাইসার সেটিংস পান।

## বৈশিষ্ট্য

- **মডেল বিশ্লেষণ** — অতিব্যাপ্ত জ্যামিতি, পাতলা দেয়াল, উল্টানো normals, খোলা প্রান্ত/ছিদ্র, পৃথক বডি, non-manifold প্রান্ত, স্ব-ছেদ।
- **সমস্যা সনাক্তকরণ** — মুদ্রণ শুরু করার আগে সম্ভাব্য ব্যর্থতা চিহ্নিত করুন।
- **স্লাইসার পরামর্শ** — Creality Print এবং AnycubicSlicerNext-এর জন্য প্রোফাইল প্রিসেট।
- **মেশ মেরামত** — মৌলিক মেরামতের পাশাপাশি `pymeshfix`-এর মাধ্যমে ঐচ্ছিক সক্রিয় মেরামত (বিকৃত ফলাফল প্রত্যাখ্যানকারী রক্ষাকারী সহ)।
- **১০০% স্থানীয়** — মডেল ডেটা কখনো আপনার মেশিন ছাড়ে না। কোনো অ্যাকাউন্ট নেই, কোনো টেলিমেট্রি নেই।

## ইনস্টলেশন

```bash
pip install printprep
```

## দ্রুত শুরু

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # প্রয়োজন: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI বাংলায় স্যুইচ: `export PRINTPREP_LANG=bn`

## ওয়েব UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## ডেস্কটপ অ্যাপ

`printprep app` ওয়েব UI-কে একটি নেটিভ উইন্ডোতে খোলে (macOS-এ WKWebView, Windows-এ WebView2, Linux-এ GTK WebKit)।

```bash
pip install -e ".[web,desktop]"
printprep app
```

ডাবল-ক্লিক লঞ্চার: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`।

সম্পূর্ণ স্থানীয়ভাবে চলে — আপনার ডেটা মেশিন ছাড়ে না।

উপাদান প্রিসেট [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) ওপেন-সোর্স ফিলামেন্ট লাইব্রেরি থেকে — দেখুন [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)।

## উন্নয়ন

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

দেখুন [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md)।

## সমর্থিত স্লাইসার

- Creality Print
- AnycubicSlicerNext
- প্রোফাইল রপ্তানি OrcaSlicer / PrusaSlicer / SuperSlicer ফরম্যাটও কভার করে।

## অবস্থা

Pre-1.0 প্রিভিউ (`0.1.x`)। API এবং CLI পরিবর্তিত হতে পারে। বাগ রিপোর্ট এবং PR স্বাগত।

## লাইসেন্স

[MIT](LICENSE)। তৃতীয়-পক্ষের গুণাবলী [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)-এ।
