import pytest
import trimesh
from diffuser_gen.export import export


@pytest.fixture
def box_mesh():
    return trimesh.creation.box(extents=(10.0, 10.0, 10.0))


def test_extension_stripping_stl_to_3mf(box_mesh, tmp_path):
    out = export(box_mesh, str(tmp_path / "panel.stl"), fmt="3mf")
    assert out.endswith(".3mf")
    assert not out.endswith(".stl.3mf")


def test_extension_stripping_3mf_to_stl(box_mesh, tmp_path):
    out = export(box_mesh, str(tmp_path / "panel.3mf"), fmt="stl")
    assert out.endswith(".stl")
    assert not out.endswith(".3mf.stl")


def test_extension_stripping_no_existing_ext(box_mesh, tmp_path):
    out = export(box_mesh, str(tmp_path / "panel"), fmt="stl")
    assert out == str(tmp_path / "panel.stl")


def test_stl_roundtrip(box_mesh, tmp_path):
    path = export(box_mesh, str(tmp_path / "panel"), fmt="stl")
    loaded = trimesh.load(path)
    assert isinstance(loaded, trimesh.Trimesh)
    assert len(loaded.faces) > 0


def test_stl_file_is_nonempty(box_mesh, tmp_path):
    import os
    path = export(box_mesh, str(tmp_path / "panel"), fmt="stl")
    assert os.path.getsize(path) > 0


def test_unknown_fmt_raises(box_mesh, tmp_path):
    with pytest.raises(ValueError, match="Unknown format"):
        export(box_mesh, str(tmp_path / "panel"), fmt="obj")


def test_returns_written_path(box_mesh, tmp_path):
    path = export(box_mesh, str(tmp_path / "out"), fmt="stl")
    import os
    assert os.path.exists(path)
