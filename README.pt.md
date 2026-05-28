# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | **Português** | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

Ferramenta de análise de modelos STL e sugestão de perfis de slicer.

Detecte prováveis problemas de impressão antes de fatiar, e obtenha ajustes de slicer adaptados ao seu modelo.

## Recursos

- **Análise de modelo** — geometria sobreposta, paredes finas, normais invertidas, bordas abertas/buracos, corpos separados, bordas não-manifold, autointerseções.
- **Detecção de problemas** — identifica possíveis falhas antes de iniciar a impressão.
- **Sugestões de slicer** — predefinições de perfil para Creality Print e AnycubicSlicerNext.
- **Reparo de malha** — reparo básico mais escalonamento opcional via `pymeshfix` com proteção que rejeita resultados danificados.
- **100% local** — os dados do modelo nunca saem da sua máquina. Sem contas, sem telemetria.

## Instalação

```bash
pip install printprep
```

## Início rápido

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # requer: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

Mudar CLI para português: `export PRINTPREP_LANG=pt`

## UI Web

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## Aplicativo desktop

`printprep app` abre a UI web em uma janela nativa (WKWebView no macOS, WebView2 no Windows, GTK WebKit no Linux).

```bash
pip install -e ".[web,desktop]"
printprep app
```

Lançadores de duplo-clique: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

Funciona totalmente local — seus dados nunca saem da máquina.

Predefinições de material vêm da biblioteca de filamentos open-source [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) — ver [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Desenvolvimento

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

Ver [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md).

## Slicers suportados

- Creality Print
- AnycubicSlicerNext
- Exportação de perfil também cobre formatos OrcaSlicer / PrusaSlicer / SuperSlicer.

## Status

Pré-visualização pré-1.0 (`0.1.x`). APIs e CLI podem mudar. Relatos de bugs e PRs são bem-vindos.

## Licença

[MIT](LICENSE). Atribuições de terceiros em [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
