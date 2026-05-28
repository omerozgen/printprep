# PrintPrep

[English](README.md) | [Türkçe](README.tr.md) | [中文](README.zh.md) | [Español](README.es.md) | [العربية](README.ar.md) | [हिन्दी](README.hi.md) | [বাংলা](README.bn.md) | [Português](README.pt.md) | [Русский](README.ru.md) | [日本語](README.ja.md) | [ਪੰਜਾਬੀ](README.pa.md) | [Deutsch](README.de.md) | [Basa Jawa](README.jv.md) | **한국어** | [Français](README.fr.md)

STL 모델 분석 및 슬라이서 프로필 제안 도구.

슬라이싱 전에 잠재적 출력 문제를 찾고, 모델에 맞춘 슬라이서 설정을 받으세요.

## 기능

- **모델 분석** — 겹치는 지오메트리, 얇은 벽, 뒤집힌 법선, 열린 모서리/구멍, 분리된 바디, 비다양체 모서리, 자기교차.
- **문제 감지** — 출력 시작 전에 잠재적 실패를 식별.
- **슬라이서 제안** — Creality Print와 AnycubicSlicerNext용 프로필 프리셋.
- **메시 수리** — 기본 수리와 `pymeshfix`를 통한 선택적 강력 수리(손상된 결과 거부 보호 장치 포함).
- **100% 로컬** — 모델 데이터가 기계를 떠나지 않습니다. 계정 없음, 텔레메트리 없음.

## 설치

```bash
pip install printprep
```

## 빠른 시작

```bash
printprep analyze model.stl
printprep fix model.stl --output fixed_model.stl
printprep orient model.stl --output oriented_model.stl
printprep merge model.stl --output merged_model.stl   # 필요: pip install -e ".[merge]"
printprep batch ./models --json report.json
printprep suggest model.stl --slicer creality --material pla
printprep suggest model.stl --slicer creality --import-profile my_filament.json
printprep suggest model.stl --slicer anycubic --material petg --export orca --out-dir ./profiles
```

CLI를 한국어로 전환: `export PRINTPREP_LANG=ko`

## 웹 UI

```bash
pip install -e ".[web]"
printprep serve           # http://127.0.0.1:8000
```

## 데스크탑 앱

`printprep app`은 웹 UI를 네이티브 창에서 엽니다(macOS는 WKWebView, Windows는 WebView2, Linux는 GTK WebKit).

```bash
pip install -e ".[web,desktop]"
printprep app
```

더블클릭 런처: **macOS** `PrintPrep.app`, **Windows** `PrintPrep.bat`, **Linux** `./install-linux.sh`.

완전 로컬에서 실행 — 데이터가 기계를 떠나지 않습니다.

재료 프리셋은 [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) 오픈소스 필라멘트 라이브러리에서 가져옵니다 — [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) 참조.

## 개발

```bash
git clone https://github.com/omerozgen/printprep.git
cd printprep
python -m venv venv && source venv/bin/activate
pip install -e ".[dev,web]"
pytest
node --test tests/js/geometry-utils.test.mjs
```

[CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), [CHANGELOG.md](CHANGELOG.md) 참조.

## 지원 슬라이서

- Creality Print
- AnycubicSlicerNext
- 프로필 내보내기는 OrcaSlicer / PrusaSlicer / SuperSlicer 형식도 커버합니다.

## 상태

Pre-1.0 프리뷰 (`0.1.x`). API와 CLI는 변경될 수 있습니다. 버그 보고와 PR 환영.

## 라이선스

[MIT](LICENSE). 서드파티 귀속은 [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).
