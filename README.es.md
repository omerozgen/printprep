# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | **Español** | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

Herramienta de análisis de modelos STL y sugerencia de perfiles de slicer.

Detecta posibles problemas de impresión antes de cortar, y obtén ajustes de slicer adaptados a tu modelo.

## Características

- **Análisis de modelo** — geometría superpuesta, paredes finas, normales invertidas, bordes abiertos/agujeros, cuerpos separados, bordes no-manifold, autointersecciones.
- **Detección de problemas** — identifica posibles fallos antes de empezar la impresión.
- **Sugerencias de slicer** — predefinidos de perfil para Creality Print y AnycubicSlicerNext.
- **Reparación de malla** — reparación básica más escalada opcional vía `pymeshfix` con protección que rechaza resultados dañados.
- **100% local** — los datos del modelo nunca salen de tu máquina. Sin cuentas, sin telemetría.

## Instalación

```bash
pip install printprep
```

## Inicio rápido

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # requiere: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

Cambiar idioma del CLI a español: `export PRINTPREP_LANG=es`

## UI Web

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Aplicación de escritorio

`printprep app` abre la UI web en una ventana nativa (WKWebView en macOS, WebView2 en Windows, GTK WebKit en Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Lanzadores doble-clic: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Funciona totalmente local — tus datos nunca salen de la máquina.

Los preajustes de material vienen de la biblioteca de filamentos open-source [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — ver [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Desarrollo

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Slicers soportados

- Creality Print
- AnycubicSlicerNext
- Exportar perfil también cubre formatos OrcaSlicer / PrusaSlicer / SuperSlicer.

## Estado

Vista previa pre-1.0 (`0.1.x`). Las APIs y el CLI pueden cambiar. Reportes de bugs y PRs son bienvenidos.

## Licencia

[MIT](LICENSE). Atribuciones de terceros en [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
