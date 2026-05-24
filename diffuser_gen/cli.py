import argparse

from diffuser_gen import export, feasibility, geometry, qrd


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="diffuser-gen",
        description="Generate a 3D-printable 2D skyline QRD acoustic diffuser.",
    )
    parser.add_argument("--p-x", type=int, default=7, help="QRD prime, x-axis")
    parser.add_argument("--p-y", type=int, default=7, help="QRD prime, y-axis")
    parser.add_argument("--f-design", type=float, default=1000.0, help="Design frequency, Hz")
    parser.add_argument("--c", type=float, default=343.0, help="Speed of sound, m/s")
    parser.add_argument("--cell-size", type=float, default=30.0, help="Cell size, mm")
    parser.add_argument("--wall-thickness", type=float, default=2.5, help="Wall/gap thickness, mm")
    parser.add_argument("--base-thickness", type=float, default=6.0, help="Base plate thickness, mm")
    parser.add_argument("--min-col-height", type=float, default=5.0, help="Minimum column height, mm")
    parser.add_argument("--combine", choices=["add", "multiply"], default="add", help="Combination mode")
    parser.add_argument("--manifold", action="store_true", help="Use single watertight heightfield builder")
    parser.add_argument("--format", dest="fmt", choices=["stl", "3mf"], default="stl", help="Output format")
    parser.add_argument("--output", default="diffuser", help="Output filename (extension stripped/replaced)")
    parser.add_argument("--preview", action="store_true", help="Open interactive viewer before export")

    args = parser.parse_args(argv)

    params = {
        "p_x": args.p_x,
        "p_y": args.p_y,
        "f_design_hz": args.f_design,
        "c_m_s": args.c,
        "cell_size_mm": args.cell_size,
        "wall_thickness_mm": args.wall_thickness,
        "base_thickness_mm": args.base_thickness,
        "min_col_height_mm": args.min_col_height,
        "combine": args.combine,
    }

    feasibility.validate(params)

    H = qrd.height_map_2d(
        params["p_x"],
        params["p_y"],
        params["f_design_hz"],
        params["c_m_s"],
        params["min_col_height_mm"],
        params["combine"],
    )

    if args.manifold:
        mesh = geometry.build_diffuser_manifold(params)
    else:
        mesh = geometry.build_diffuser(params)

    s = feasibility.summary(params, H)
    feasibility.print_summary(s)

    if args.preview:
        mesh.show()

    path = export.export(mesh, args.output, args.fmt)
    print(f"Saved: {path}")
