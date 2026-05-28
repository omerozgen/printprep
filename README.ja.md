# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | **日本語** | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL モデル解析とスライサープロファイル提案ツール。

スライス前に印刷の問題を発見し、モデルに合わせたスライサー設定を取得します。

## 特徴

- **モデル解析** — 重なるジオメトリ、薄い壁、反転法線、開いたエッジ/穴、分離ボディ、非多様体エッジ、自己交差。
- **問題検出** — 印刷開始前に潜在的な失敗を特定。
- **スライサー提案** — Creality Print と AnycubicSlicerNext のプロファイルプリセット。
- **メッシュ修復** — 基本修復に加え、`pymeshfix` 経由のオプション強力修復(損傷した結果を拒否するガード付き)。
- **100% ローカル** — モデルデータはマシンを離れません。アカウント不要、テレメトリ無し。

## インストール

```bash
pip install printprep
```

## クイックスタート

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # 必要: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI を日本語に切り替え: `export PRINTPREP_LANG=ja`

## Web UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## デスクトップアプリ

`printprep app` は Web UI をネイティブウィンドウで開きます(macOS は WKWebView、Windows は WebView2、Linux は GTK WebKit)。

```bash
pip install -e ".[web,desktop]"
printprep app
```

ダブルクリックランチャー: **macOS** `PrintPrep.app`、**Windows** `PrintPrep.bat`、**Linux** `./install-linux.sh`。

完全ローカル動作 — データはマシンを離れません。

材料プリセットは [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) オープンソースフィラメントライブラリから — [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) 参照。

## 開発

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

[CONTRIBUTING.md](CONTRIBUTING.md)、[SECURITY.md](SECURITY.md)、[CHANGELOG.md](CHANGELOG.md) 参照。

## 対応スライサー

- Creality Print
- AnycubicSlicerNext
- プロファイルエクスポートは OrcaSlicer / PrusaSlicer / SuperSlicer 形式もカバー。

## ステータス

Pre-1.0 プレビュー (`0.1.x`)。API と CLI は変更される可能性あり。バグ報告と PR 歓迎。

## ライセンス

[MIT](LICENSE)。サードパーティ帰属は [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)。
