# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | **العربية** | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

أداة لتحليل نماذج STL واقتراح ملفات تعريف الشرائح.

اكتشف مشكلات الطباعة المحتملة قبل التقطيع، واحصل على إعدادات شريحة مُكيَّفة لنموذجك.

## الميزات

- **تحليل النموذج** — هندسة متداخلة، جدران رفيعة، normals معكوسة، حواف مفتوحة/ثقوب، أجسام منفصلة، حواف غير متشعبة، تقاطعات ذاتية.
- **اكتشاف المشكلات** — حدد الأعطال المحتملة قبل بدء الطباعة.
- **اقتراحات الشريحة** — إعدادات ملف تعريف مسبق لـ Creality Print و AnycubicSlicerNext.
- **إصلاح الشبكة** — إصلاح أساسي بالإضافة إلى تصعيد قوي اختياري عبر `pymeshfix` مع حارس يرفض النتائج التالفة.
- **محلي 100%** — بيانات النموذج لا تغادر جهازك أبداً. بدون حسابات، بدون تتبع.

## التثبيت

```bash
pip install printprep
```

## البدء السريع

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # يتطلب: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

تبديل CLI إلى العربية: `export PRINTPREP_LANG=ar`

## واجهة الويب

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## تطبيق سطح المكتب

`printprep app` يفتح واجهة الويب في نافذة أصلية (WKWebView على macOS، WebView2 على Windows، GTK WebKit على Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

مُشغِّلات النقر المزدوج: **macOS** `PrintPrep.app`، **Windows** `PrintPrep.bat`، **Linux** `./install-linux.sh`.

يعمل بالكامل محلياً — بياناتك لا تغادر الجهاز أبداً.

إعدادات المواد المسبقة مأخوذة من مكتبة الفتائل مفتوحة المصدر [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — انظر [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## التطوير

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

انظر [CONTRIBUTING.md](CONTRIBUTING.md)، [SECURITY.md](SECURITY.md)، [CHANGELOG.md](CHANGELOG.md).

## الشرائح المدعومة

- Creality Print
- AnycubicSlicerNext
- تصدير ملف التعريف يغطي أيضاً صيغ OrcaSlicer / PrusaSlicer / SuperSlicer.

## الحالة

معاينة ما قبل 1.0 (`0.1.x`). قد تتغير واجهات API و CLI. تقارير الأخطاء و PRs مرحب بها.

## الترخيص

[MIT](LICENSE). إسناد الطرف الثالث في [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
