import json

from click.testing import CliRunner

from printprep.cli import main


def test_batch_analyzes_folder(tmp_path, clean_cube, broken_cube):
    clean_cube.export(str(tmp_path / "a.stl"))
    broken_cube.export(str(tmp_path / "b.stl"))
    out_json = tmp_path / "report.json"

    result = CliRunner().invoke(main, ["batch", str(tmp_path), "--json", str(out_json)])

    assert result.exit_code == 0
    assert "2/2 analyzed" in result.output
    assert out_json.exists()
    data = json.loads(out_json.read_text())
    assert len(data) == 2
    assert all("dimensions_mm" in row for row in data)


def test_batch_empty_dir_errors(tmp_path):
    result = CliRunner().invoke(main, ["batch", str(tmp_path)])
    assert result.exit_code == 1
    assert "No files" in result.output
