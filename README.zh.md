# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | **中文** | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | [한국어](README.ko.md) | [Français](README.fr.md)

STL 模型分析与切片机配置建议工具。

在切片前发现可能的打印问题,并获得针对您模型的切片机设置。

## 特性

- **模型分析** — 重叠几何、薄壁、反向法线、开放边/孔洞、独立实体、非流形边、自相交。
- **问题检测** — 在开始打印前识别潜在故障。
- **切片机建议** — Creality Print 和 AnycubicSlicerNext 的配置预设。
- **网格修复** — 基础修复加上通过 `pymeshfix` 的可选强力修复(带保护机制拒绝损坏的结果)。
- **100% 本地** — 模型数据不会离开您的电脑。无账户、无遥测。

## 安装

```bash
pip install printprep
```

## 快速开始

```bash
# 分析模型
printprep analyze model.stl

# 修复常见问题
printprep fix model.stl --output fixed_model.stl

# 自动定向到最佳打印姿态
printprep orient model.stl --output oriented_model.stl

# 合并独立实体为单个 (布尔并集需要: pip install -e ".[merge]")
printprep merge model.stl --output merged_model.stl

# 批量分析文件夹中的每个 STL
printprep batch ./models --json report.json

# 切片机配置建议
printprep suggest model.stl --slicer creality --material pla

# 导入您自己的切片机配置 (OrcaSlicer .json / PrusaSlicer .ini / Cura .fdm_material)
printprep suggest model.stl --slicer creality --import-profile my_filament.json

# 导出可直接载入切片机的配置文件
#   orca  -> OrcaSlicer / Creality Print / Anycubic Slicer (.json)
#   prusa -> PrusaSlicer / SuperSlicer (.ini)
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

将语言设置为中文:`export PRINTPREP_LANG=zh`

## 网页界面

3D 预览、拖放分析、修复和切片机建议 — 全部在浏览器中:

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## 桌面应用

无需浏览器 — `printprep app` 在原生窗口中打开 Web UI(macOS 用 WKWebView,Windows 用 WebView2,Linux 用 GTK WebKit)。

```bash
pip install -e ".[web,desktop]"
printprep app
```

双击启动器(所有平台):**macOS** `PrintPrep.app`、**Windows** `PrintPrep.bat`、**Linux** `./install-linux.sh`。

完全本地运行 — 模型数据不会离开您的电脑。在 3D 视图中,悬垂面为红色,薄壁为琥珀色,孔洞/开放边为洋红色,反向法线为青色背面,独立实体着色不同。

材料预设(温度、流量)来自 [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) 开源耗材库 — 详见 [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)。

## 开发

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程,[SECURITY.md](SECURITY.md) 了解安全政策,[CHANGELOG.md](CHANGELOG.md) 了解新内容。

## 支持的切片机

- Creality Print
- AnycubicSlicerNext
- 配置导出也覆盖 OrcaSlicer / PrusaSlicer / SuperSlicer 格式。

## 状态

Pre-1.0 预览版 (`0.1.x`)。API 和 CLI 可能变化。欢迎报告 bug 和提交 PR — 见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)。第三方致谢见 [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)。
