# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | **Français**

Outil d'analyse de modèles STL et de suggestion de profil de slicer.

Repérez les problèmes d'impression probables avant de slicer, et obtenez des réglages de slicer adaptés à votre modèle.

## Caractéristiques

- **Analyse de modèle** — géométrie chevauchante, parois fines, normales inversées, arêtes ouvertes/trous, corps séparés, arêtes non-manifold, auto-intersections.
- **Détection des problèmes** — identifie les défaillances potentielles avant de lancer l'impression.
- **Suggestions de slicer** — préréglages de profil pour Creality Print et AnycubicSlicerNext.
- **Réparation de maillage** — réparation de base plus escalade agressive optionnelle via `pymeshfix` avec garde-fou rejetant les résultats abîmés.
- **100% local** — les données du modèle ne quittent jamais votre machine. Pas de compte, pas de télémétrie.

## Installation

```bash
pip install printprep
```

## Démarrage rapide

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # nécessite: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

Passer le CLI en français : `export PRINTPREP_LANG=fr`

## Interface Web

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Application bureau

`printprep app` ouvre l'UI web dans une fenêtre native (WKWebView sur macOS, WebView2 sur Windows, GTK WebKit sur Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Lanceurs double-clic : **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Fonctionne entièrement localement — vos données ne quittent jamais la machine.

Les préréglages de matériaux proviennent de la bibliothèque de filaments open-source [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — voir [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Développement

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

Voir [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Slicers pris en charge

- Creality Print
- AnycubicSlicerNext
- L'export de profil couvre aussi les formats OrcaSlicer / PrusaSlicer / SuperSlicer.

## État

Aperçu pré-1.0 (`0.1.x`). Les API et le CLI peuvent changer. Les rapports de bugs et PR sont les bienvenus.

## Licence

[MIT](LICENSE). Attributions tierces dans [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
