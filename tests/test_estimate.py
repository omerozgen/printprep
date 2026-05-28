from printprep.config.presets import get_material
from printprep.core import analyze, estimate_print_job
from printprep.slicer import get_slicer


def test_estimate_clean_cube_pla_in_expected_range(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    profile = get_slicer("creality").build_profile(result, "pla")
    est = estimate_print_job(result, profile, get_material("pla"))

    # A 20mm cube at 0.2 layer / 15% infill / PLA realistically lands around
    # 3-12g of filament and 10-45 min on a typical printer. We accept a wide
    # band — this is an estimate, not a slicer simulation.
    assert 3 <= est.filament_weight_g <= 15
    assert 10 <= est.print_time_min <= 60
    assert est.filament_length_mm > 0
    assert est.cost is None  # no price -> no cost


def test_estimate_with_price_returns_cost(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    profile = get_slicer("creality").build_profile(result, "pla")
    est = estimate_print_job(result, profile, get_material("pla"),
                             price_per_kg=1200.0, currency="TL")
    expected = (est.filament_weight_g / 1000.0) * 1200.0
    assert est.cost is not None
    assert abs(est.cost - round(expected, 2)) < 0.05
    assert est.currency == "TL"


def test_estimate_pla_vs_abs_weight_differs_by_density(clean_cube):
    result = analyze(clean_cube, path="clean_cube.stl")
    profile = get_slicer("creality").build_profile(result, "pla")
    pla = estimate_print_job(result, profile, get_material("pla"))
    abs_ = estimate_print_job(result, profile, get_material("abs"))
    # ABS is less dense (1.04) than PLA (1.24) so weight should be lower.
    assert abs_.filament_weight_g < pla.filament_weight_g
