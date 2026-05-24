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


def qrd_sequence(p: int) -> np.ndarray:
    if not _is_prime(p):
        raise ValueError(f"{p} is not prime")
    return np.array([(n * n) % p for n in range(p)], dtype=int)


def well_depths_mm(sequence: np.ndarray, f_design_hz: float, c_m_s: float) -> np.ndarray:
    p = len(sequence)
    unit_mm = (c_m_s / (2 * p * f_design_hz)) * 1000.0
    return sequence * unit_mm


def height_map_2d(
    p_x: int,
    p_y: int,
    f_design_hz: float,
    c_m_s: float,
    min_col_height_mm: float,
    combine: str = "add",
) -> np.ndarray:
    seq_x = qrd_sequence(p_x)
    seq_y = qrd_sequence(p_y)
    depths_x = well_depths_mm(seq_x, f_design_hz, c_m_s)
    depths_y = well_depths_mm(seq_y, f_design_hz, c_m_s)

    if combine == "add":
        total_depth = depths_x[:, np.newaxis] + depths_y[np.newaxis, :]
        max_total = total_depth.max()
        H = (max_total - total_depth) + min_col_height_mm
    elif combine == "multiply":
        max_depth_mm = max(depths_x.max(), depths_y.max())
        dx_norm = depths_x / depths_x.max()
        dy_norm = depths_y / depths_y.max()
        H = (1 - dx_norm[:, np.newaxis] * dy_norm[np.newaxis, :]) * max_depth_mm + min_col_height_mm
    else:
        raise ValueError(f"Unknown combine mode: {combine!r}")

    return H
