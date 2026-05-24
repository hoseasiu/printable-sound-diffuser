import numpy as np


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def validate(params: dict) -> None:
    p_x = params["p_x"]
    p_y = params["p_y"]
    f_design_hz = params["f_design_hz"]
    c_m_s = params["c_m_s"]
    wall_thickness_mm = params["wall_thickness_mm"]
    cell_size_mm = params["cell_size_mm"]
    min_col_height_mm = params["min_col_height_mm"]
    base_thickness_mm = params["base_thickness_mm"]

    if not _is_prime(p_x):
        raise ValueError(f"p_x={p_x} is not prime")
    if not _is_prime(p_y):
        raise ValueError(f"p_y={p_y} is not prime")
    if f_design_hz <= 0:
        raise ValueError(f"f_design_hz must be positive, got {f_design_hz}")
    if c_m_s <= 0:
        raise ValueError(f"c_m_s must be positive, got {c_m_s}")
    if wall_thickness_mm >= cell_size_mm:
        raise ValueError(
            f"wall_thickness_mm ({wall_thickness_mm}) must be less than cell_size_mm ({cell_size_mm})"
        )
    if min_col_height_mm < 0:
        raise ValueError(f"min_col_height_mm must be >= 0, got {min_col_height_mm}")
    if base_thickness_mm <= 0:
        raise ValueError(f"base_thickness_mm must be positive, got {base_thickness_mm}")


def summary(params: dict, height_map: np.ndarray) -> dict:
    p_x = params["p_x"]
    p_y = params["p_y"]
    f_design_hz = params["f_design_hz"]
    c_m_s = params["c_m_s"]
    cell_size_mm = params["cell_size_mm"]
    wall_thickness_mm = params["wall_thickness_mm"]
    base_thickness_mm = params["base_thickness_mm"]
    min_col_height_mm = params["min_col_height_mm"]

    col_size_mm = cell_size_mm - wall_thickness_mm
    panel_w_mm = p_x * cell_size_mm
    panel_d_mm = p_y * cell_size_mm
    total_height_mm = base_thickness_mm + float(height_map.max())
    max_well_depth_mm = float(height_map.max()) - min_col_height_mm
    f_high_hz = c_m_s / (2 * col_size_mm * 1e-3)

    warnings = []
    if height_map.max() > 150:
        warnings.append("tall columns may be fragile")
    if col_size_mm < 8:
        warnings.append("well width below typical FDM nozzle resolution")
    wavelength_at_f_design_mm = (c_m_s / f_design_hz) * 1000.0
    if cell_size_mm > 0.5 * wavelength_at_f_design_mm:
        warnings.append("cells too large for design freq")

    return {
        "panel_w_mm": panel_w_mm,
        "panel_d_mm": panel_d_mm,
        "total_height_mm": total_height_mm,
        "max_well_depth_mm": max_well_depth_mm,
        "f_design_hz": f_design_hz,
        "f_high_hz": f_high_hz,
        "col_size_mm": col_size_mm,
        "warnings": warnings,
    }


def print_summary(summary_dict: dict) -> None:
    print(f"Panel size:     {summary_dict['panel_w_mm']:.1f} x {summary_dict['panel_d_mm']:.1f} mm")
    print(f"Total height:   {summary_dict['total_height_mm']:.1f} mm")
    print(f"Max well depth: {summary_dict['max_well_depth_mm']:.1f} mm")
    print(f"f_design:       {summary_dict['f_design_hz']:.0f} Hz  (lower bound)")
    print(f"f_high:         {summary_dict['f_high_hz']:.0f} Hz  (well-width upper cutoff)")
    print(f"Column size:    {summary_dict['col_size_mm']:.1f} mm")
    if summary_dict["warnings"]:
        print("Warnings:")
        for w in summary_dict["warnings"]:
            print(f"  ! {w}")
