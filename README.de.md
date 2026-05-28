# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | **Deutsch** | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL-Modellanalyse und Slicer-Profilvorschlagstool.

Erkenne wahrscheinliche Druckprobleme bevor du slicest und erhalte auf dein Modell zugeschnittene Slicer-Einstellungen.

## Funktionen

- **Modellanalyse** — überlappende Geometrie, dünne Wände, umgekehrte Normalen, offene Kanten/Löcher, separate Körper, Non-Manifold-Kanten, Selbstüberschneidungen.
- **Problemerkennung** — identifiziert potenzielle Fehler vor dem Druckstart.
- **Slicer-Vorschläge** — Profil-Voreinstellungen für Creality Print und AnycubicSlicerNext.
- **Mesh-Reparatur** — Grundreparatur plus optionale aggressive Eskalation über `pymeshfix` mit Schutzmechanismus, der zerstörte Ergebnisse ablehnt.
- **100% lokal** — Modelldaten verlassen deinen Rechner nie. Keine Konten, keine Telemetrie.

## Installation

```bash
pip install printprep
```

## Schnellstart

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # benötigt: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI auf Deutsch umstellen: `export PRINTPREP_LANG=de`

## Web-UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Desktop-Anwendung

`printprep app` öffnet die Web-UI in einem nativen Fenster (WKWebView auf macOS, WebView2 auf Windows, GTK WebKit auf Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Doppelklick-Starter: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Läuft vollständig lokal — deine Daten verlassen den Rechner nie.

Material-Voreinstellungen kommen aus der Open-Source-Filamentbibliothek [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — siehe [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Entwicklung

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

Siehe [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Unterstützte Slicer

- Creality Print
- AnycubicSlicerNext
- Profilexport deckt auch OrcaSlicer / PrusaSlicer / SuperSlicer Formate ab.

## Status

Pre-1.0 Vorschau (`0.1.x`). APIs und CLI können sich ändern. Bug-Reports und PRs willkommen.

## Lizenz

[MIT](LICENSE). Drittanbieter-Zuschreibungen in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
