import os
import trimesh


def export(mesh: trimesh.Trimesh, output: str, fmt: str) -> str:
    for ext in (".stl", ".3mf"):
        if output.endswith(ext):
            output = output[: -len(ext)]

    if fmt == "stl":
        path = output + ".stl"
        data = mesh.export(file_type="stl")
        with open(path, "wb") as f:
            f.write(data)
        return path
    elif fmt == "3mf":
        path = output + ".3mf"
        data = mesh.export(file_type="3mf")
        with open(path, "wb") as f:
            f.write(data)
        return path
    else:
        raise ValueError(f"Unknown format: {fmt!r}. Expected 'stl' or '3mf'.")
