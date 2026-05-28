import json

from click.testing import CliRunner

from printprep.cli import main
from printprep.core import pack


def test_three_small_parts_fit_one_bed():
    items = [("a.stl", 30, 30), ("b.stl", 40, 40), ("c.stl", 25, 25)]
    result = pack(items, bed_size=(100, 100), padding=5)
    assert result.bed_count == 1
    assert {p.item_id for p in result.beds[0].items} == {"a.stl", "b.stl", "c.stl"}
    assert result.unplaced == []


def test_overflow_spans_multiple_beds():
    items = [("big1.stl", 60, 60), ("big2.stl", 60, 60), ("big3.stl", 60, 60)]
    result = pack(items, bed_size=(100, 100), padding=5)
    # 60+5=65 -> one shelf fits one big part; height 65 -> second shelf 65+65=130 > 100.
    # So each big part needs its own bed.
    assert result.bed_count == 3
    assert result.unplaced == []


def test_oversize_goes_to_unplaced():
    items = [("ok.stl", 50, 50), ("huge.stl", 500, 500)]
    result = pack(items, bed_size=(100, 100), padding=5)
    assert result.bed_count == 1
    assert [u[0] for u in result.unplaced] == ["huge.stl"]


def test_rotation_helps_fit():
    # A 90x10 part fits on a 100x20 bed only by rotating to 10x90? No, 10x90 doesn't fit
    # in 20mm depth either. Try a 90x30 on a 50x100 bed -> needs rotation to 30x90.
    items = [("strip.stl", 90, 30)]
    rotated = pack(items, bed_size=(50, 100), padding=5, allow_rotate=True)
    not_rotated = pack(items, bed_size=(50, 100), padding=5, allow_rotate=False)
    assert rotated.bed_count == 1 and rotated.beds[0].items[0].rotated is True
    assert not_rotated.unplaced  # without rotation it doesn't fit


def test_pack_cli_writes_combined_stl(tmp_path, clean_cube, broken_cube):
    clean_cube.export(str(tmp_path / "a.stl"))
    broken_cube.export(str(tmp_path / "b.stl"))
    out_dir = tmp_path / "out"

    result = CliRunner().invoke(
        main, ["pack", str(tmp_path), "--bed", "100x100", "--out-dir", str(out_dir)]
    )
    assert result.exit_code == 0, result.output
    assert (out_dir / "packed_bed1.stl").exists()
    layout = json.loads((out_dir / "layout.json").read_text())
    assert layout["bed_size_mm"] == [100, 100]
    assert len(layout["beds"]) >= 1
