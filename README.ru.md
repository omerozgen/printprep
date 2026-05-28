# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | **Русский** | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

Инструмент анализа моделей STL и предложения профилей слайсера.

Обнаруживайте вероятные проблемы печати до слайсинга и получайте настройки слайсера, адаптированные к вашей модели.

## Возможности

- **Анализ модели** — пересекающаяся геометрия, тонкие стенки, обратные нормали, открытые рёбра/отверстия, отдельные тела, не-многообразные рёбра, самопересечения.
- **Обнаружение проблем** — выявляйте потенциальные сбои до начала печати.
- **Предложения слайсера** — предустановки профилей для Creality Print и AnycubicSlicerNext.
- **Ремонт меша** — базовый ремонт плюс опциональная агрессивная эскалация через `pymeshfix` с защитой, отклоняющей искажённые результаты.
- **100% локально** — данные модели не покидают ваш компьютер. Без аккаунтов, без телеметрии.

## Установка

```bash
pip install printprep
```

## Быстрый старт

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # требует: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

Переключить CLI на русский: `export PRINTPREP_LANG=ru`

## Веб-интерфейс

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Десктоп-приложение

`printprep app` открывает веб-UI в нативном окне (WKWebView на macOS, WebView2 на Windows, GTK WebKit на Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Двойной клик: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Полностью локально — данные не покидают ваш компьютер.

Предустановки материалов взяты из open-source библиотеки филаментов [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — см. [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Разработка

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

См. [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Поддерживаемые слайсеры

- Creality Print
- AnycubicSlicerNext
- Экспорт профиля также покрывает форматы OrcaSlicer / PrusaSlicer / SuperSlicer.

## Статус

Предварительная версия Pre-1.0 (`0.1.x`). API и CLI могут меняться. Приветствуются баг-репорты и PR.

## Лицензия

[MIT](LICENSE). Атрибуции третьих сторон в [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
