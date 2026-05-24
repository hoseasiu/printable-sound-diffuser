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


def build_diffuser_manifold(params: dict) -> trimesh.Trimesh:
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
    half_wall = wall_thickness_mm / 2.0
    base = float(base_thickness_mm)
    W = float(p_x * cell_size_mm)
    D = float(p_y * cell_size_mm)

    # Grid of x/y breakpoints: outer edges + left/right of each column.
    # xs has 2*p_x+2 values; band bx covers [xs[bx], xs[bx+1]].
    # bx odd → column interior; bx even → moat. Same for y.
    xs = np.empty(2 * p_x + 2)
    xs[0] = 0.0
    xs[2 * p_x + 1] = W
    for i in range(p_x):
        xs[2 * i + 1] = i * cell_size_mm + half_wall
        xs[2 * i + 2] = (i + 1) * cell_size_mm - half_wall

    ys = np.empty(2 * p_y + 2)
    ys[0] = 0.0
    ys[2 * p_y + 1] = D
    for j in range(p_y):
        ys[2 * j + 1] = j * cell_size_mm + half_wall
        ys[2 * j + 2] = (j + 1) * cell_size_mm - half_wall

    verts: list = []
    tris: list = []

    def quad(v0, v1, v2, v3):
        k = len(verts)
        verts.extend([v0, v1, v2, v3])
        tris.extend([[k, k + 1, k + 2], [k, k + 2, k + 3]])

    # Horizontal quad, normal +z
    def top_quad(x0, y0, x1, y1, z):
        quad([x0, y0, z], [x1, y0, z], [x1, y1, z], [x0, y1, z])

    # Horizontal quad, normal -z
    def bot_quad(x0, y0, x1, y1, z):
        quad([x0, y0, z], [x0, y1, z], [x1, y1, z], [x1, y0, z])

    # Vertical quads — normal direction matches sign in name
    def left_quad(x, y0, y1, z0, z1):   # normal -x
        quad([x, y0, z0], [x, y0, z1], [x, y1, z1], [x, y1, z0])

    def right_quad(x, y0, y1, z0, z1):  # normal +x
        quad([x, y0, z0], [x, y1, z0], [x, y1, z1], [x, y0, z1])

    def front_quad(y, x0, x1, z0, z1):  # normal -y
        quad([x0, y, z0], [x1, y, z0], [x1, y, z1], [x0, y, z1])

    def back_quad(y, x0, x1, z0, z1):   # normal +y
        quad([x0, y, z0], [x0, y, z1], [x1, y, z1], [x1, y, z0])

    # Bottom face: segmented to share edges with the outer walls
    for bx in range(2 * p_x + 1):
        for by in range(2 * p_y + 1):
            bot_quad(xs[bx], ys[by], xs[bx + 1], ys[by + 1], 0.0)

    # Outer perimeter walls: segmented to share edges with both the bottom
    # face and the moat top tiles
    for by in range(2 * p_y + 1):
        left_quad(0.0, ys[by], ys[by + 1], 0.0, base)
        right_quad(W, ys[by], ys[by + 1], 0.0, base)
    for bx in range(2 * p_x + 1):
        front_quad(0.0, xs[bx], xs[bx + 1], 0.0, base)
        back_quad(D, xs[bx], xs[bx + 1], 0.0, base)

    # Top surface: moat at z=base; column interiors at z=base+H[i,j]
    for bx in range(2 * p_x + 1):
        for by in range(2 * p_y + 1):
            x0, x1 = xs[bx], xs[bx + 1]
            y0, y1 = ys[by], ys[by + 1]
            if bx % 2 == 1 and by % 2 == 1:
                i, j = bx // 2, by // 2
                top_quad(x0, y0, x1, y1, base + float(H[i, j]))
            else:
                top_quad(x0, y0, x1, y1, base)

    # Column side walls: vertical faces from z=base to z=base+H[i,j]
    for i in range(p_x):
        for j in range(p_y):
            x0 = xs[2 * i + 1]
            x1 = xs[2 * i + 2]
            y0 = ys[2 * j + 1]
            y1 = ys[2 * j + 2]
            h = float(H[i, j])
            left_quad(x0, y0, y1, base, base + h)
            right_quad(x1, y0, y1, base, base + h)
            front_quad(y0, x0, x1, base, base + h)
            back_quad(y1, x0, x1, base, base + h)

    mesh = trimesh.Trimesh(
        vertices=np.array(verts, dtype=np.float64),
        faces=np.array(tris, dtype=np.int32),
        process=False,
    )
    mesh.merge_vertices()
    return mesh
