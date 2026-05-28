
from click.testing import CliRunner

from printprep.cli import main
from printprep.slicer.discover import discover_profiles


def test_discover_handles_missing_paths():
    # Custom roots that don't exist -> returns [].
    out = discover_profiles({"FakeSlicer": ["/nonexistent/path/printprep-test"]})
    assert out == []


def test_discover_finds_simulated_profiles(tmp_path):
    fil = tmp_path / "filament" / "MyPLA.json"
    fil.parent.mkdir(parents=True)
    fil.write_text("{}")
    proc = tmp_path / "process" / "0.20mm.json"
    proc.parent.mkdir()
    proc.write_text("{}")

    rows = discover_profiles({"TestSlicer": [str(tmp_path)]})
    kinds = {r["kind"] for r in rows}
    names = {r["name"] for r in rows}
    assert kinds == {"filament", "process"}
    assert "MyPLA" in names and "0.20mm" in names


def test_slicer_discover_cli_runs():
    # Just verify the command runs without crashing on the actual system
    # (output depends on what's installed; we don't assert content).
    result = CliRunner().invoke(main, ["slicer-discover"])
    assert result.exit_code == 0
