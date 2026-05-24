import numpy as np
import trimesh

from diffuser_gen import qrd


def build_diffuser(params: dict) -> trimesh.Trimesh:
    p_x = params["p_x"]
    p_y = params["p_y"]
    f_design_hz = params["f_design_hz"]
    c_m_s = params["c_m_s"]
    cell_size_mm = params["cell_size_mm"]
    wall_thickness_mm = params["wall_thickness_mm"]
    base_thickness_mm = params["base_thickness_mm"]
    min_col_height_mm = params["min_col_height_mm"]
    combine = params.get("combine", "add")

    H = qrd.height_map_2d(p_x, p_y, f_design_hz, c_m_s, min_col_height_mm, combine)
    col_size = cell_size_mm - wall_thickness_mm

    panel_w = p_x * cell_size_mm
    panel_d = p_y * cell_size_mm

    base = trimesh.creation.box(extents=(panel_w, panel_d, base_thickness_mm))
    # box is centered at origin; translate so bottom is at z=0 and corner at (0,0)
    base.apply_translation([panel_w / 2, panel_d / 2, base_thickness_mm / 2])

    meshes = [base]
    for i in range(p_x):
        for j in range(p_y):
            h = H[i, j]
            col = trimesh.creation.box(extents=(col_size, col_size, h))
            cx = (i + 0.5) * cell_size_mm
            cy = (j + 0.5) * cell_size_mm
            cz = base_thickness_mm + h / 2
            col.apply_translation([cx, cy, cz])
            meshes.append(col)

    mesh = trimesh.util.concatenate(meshes)
    mesh.process()
    return mesh
