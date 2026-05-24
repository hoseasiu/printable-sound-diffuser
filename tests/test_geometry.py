import numpy as np
import pytest
import trimesh

from diffuser_gen.geometry import build_diffuser
from diffuser_gen.qrd import height_map_2d

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


@pytest.fixture
def default_mesh():
    return build_diffuser(DEFAULT_PARAMS)


@pytest.fixture
def default_H():
    p = DEFAULT_PARAMS
    return height_map_2d(
        p["p_x"], p["p_y"], p["f_design_hz"], p["c_m_s"], p["min_col_height_mm"], p["combine"]
    )


def test_build_diffuser_returns_mesh(default_mesh):
    assert isinstance(default_mesh, trimesh.Trimesh)


def test_panel_extents(default_mesh):
    p = DEFAULT_PARAMS
    expected_w = p["p_x"] * p["cell_size_mm"]
    expected_d = p["p_y"] * p["cell_size_mm"]
    extents = default_mesh.bounding_box.extents
    assert abs(extents[0] - expected_w) < 1e-6
    assert abs(extents[1] - expected_d) < 1e-6


def test_panel_height(default_mesh, default_H):
    p = DEFAULT_PARAMS
    expected_height = p["base_thickness_mm"] + default_H.max()
    actual_height = default_mesh.bounding_box.extents[2]
    assert abs(actual_height - expected_height) < 1e-6


def test_volume_floor(default_mesh, default_H):
    p = DEFAULT_PARAMS
    panel_area = p["p_x"] * p["cell_size_mm"] * p["p_y"] * p["cell_size_mm"]
    col_size = p["cell_size_mm"] - p["wall_thickness_mm"]
    col_area = col_size * col_size
    n_cols = p["p_x"] * p["p_y"]
    floor_vol = (
        p["base_thickness_mm"] * panel_area
        + p["min_col_height_mm"] * col_area * n_cols
    )
    assert default_mesh.volume >= floor_vol - 1e-3


def test_column_center_position():
    params = {
        "p_x": 5,
        "p_y": 5,
        "f_design_hz": 1000.0,
        "c_m_s": 343.0,
        "cell_size_mm": 20.0,
        "wall_thickness_mm": 2.0,
        "base_thickness_mm": 4.0,
        "min_col_height_mm": 3.0,
        "combine": "add",
    }
    H = height_map_2d(
        params["p_x"], params["p_y"],
        params["f_design_hz"], params["c_m_s"],
        params["min_col_height_mm"], params["combine"],
    )
    cell = params["cell_size_mm"]
    base = params["base_thickness_mm"]
    # Check column (0, 0): center x, y and z
    expected_cx = 0.5 * cell
    expected_cy = 0.5 * cell
    expected_cz = base + H[0, 0] / 2
    # Build mesh and verify the bounding-box center of the (0,0) column
    # by constructing it in isolation
    col_size = cell - params["wall_thickness_mm"]
    col = trimesh.creation.box(extents=(col_size, col_size, H[0, 0]))
    col.apply_translation([expected_cx, expected_cy, expected_cz])
    center = col.bounding_box.centroid
    assert abs(center[0] - expected_cx) < 1e-6
    assert abs(center[1] - expected_cy) < 1e-6
    assert abs(center[2] - expected_cz) < 1e-6
