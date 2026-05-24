import numpy as np
import pytest

from diffuser_gen.feasibility import validate, summary, print_summary


DEFAULT_PARAMS = {
    "p_x": 7,
    "p_y": 7,
    "f_design_hz": 1000.0,
    "c_m_s": 343.0,
    "cell_size_mm": 30.0,
    "wall_thickness_mm": 2.5,
    "base_thickness_mm": 6.0,
    "min_col_height_mm": 5.0,
    "combine": "add",
}


def test_validate_rejects_nonprime_p():
    for bad in (1, 4, 6, 9):
        with pytest.raises(ValueError):
            validate({**DEFAULT_PARAMS, "p_x": bad})
        with pytest.raises(ValueError):
            validate({**DEFAULT_PARAMS, "p_y": bad})


def test_validate_rejects_wall_thicker_than_cell():
    with pytest.raises(ValueError):
        validate({**DEFAULT_PARAMS, "wall_thickness_mm": 30.0})
    with pytest.raises(ValueError):
        validate({**DEFAULT_PARAMS, "wall_thickness_mm": 31.0})


def test_summary_includes_f_high():
    H = np.full((7, 7), 10.0)
    result = summary(DEFAULT_PARAMS, H)
    assert "f_high_hz" in result
    col_size = DEFAULT_PARAMS["cell_size_mm"] - DEFAULT_PARAMS["wall_thickness_mm"]
    expected = DEFAULT_PARAMS["c_m_s"] / (2 * col_size * 1e-3)
    assert abs(result["f_high_hz"] - expected) < 1.0


def test_summary_warns_on_small_well_width():
    # col_size = 10 - 3 = 7 mm < 8 mm threshold
    params = {**DEFAULT_PARAMS, "cell_size_mm": 10.0, "wall_thickness_mm": 3.0}
    H = np.full((7, 7), 10.0)
    result = summary(params, H)
    assert any("nozzle" in w or "FDM" in w for w in result["warnings"])


def test_summary_required_keys():
    H = np.full((7, 7), 10.0)
    result = summary(DEFAULT_PARAMS, H)
    required = {
        "panel_w_mm", "panel_d_mm", "total_height_mm", "max_well_depth_mm",
        "f_design_hz", "f_high_hz", "col_size_mm", "warnings",
    }
    assert required.issubset(result.keys())
