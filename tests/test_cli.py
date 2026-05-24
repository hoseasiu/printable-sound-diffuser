import os

from diffuser_gen.cli import main


def test_smoke_stl(tmp_path):
    out = str(tmp_path / "panel")
    main(["--p-x", "5", "--p-y", "5", "--output", out])
    stl = out + ".stl"
    assert os.path.exists(stl), f"Expected {stl} to exist"
    assert os.path.getsize(stl) > 0, "STL file is empty"


def test_smoke_manifold(tmp_path):
    out = str(tmp_path / "manifold_panel")
    main(["--p-x", "5", "--p-y", "5", "--manifold", "--output", out])
    stl = out + ".stl"
    assert os.path.exists(stl)
    assert os.path.getsize(stl) > 0


def test_summary_output_contains_f_design_and_f_high(tmp_path, capsys):
    out = str(tmp_path / "panel")
    main(["--p-x", "5", "--p-y", "5", "--output", out])
    captured = capsys.readouterr()
    assert "f_design" in captured.out
    assert "f_high" in captured.out


def test_output_path_printed(tmp_path, capsys):
    out = str(tmp_path / "panel")
    main(["--p-x", "5", "--p-y", "5", "--output", out])
    captured = capsys.readouterr()
    assert "panel.stl" in captured.out


def test_3mf_format(tmp_path):
    out = str(tmp_path / "panel")
    main(["--p-x", "5", "--p-y", "5", "--format", "3mf", "--output", out])
    assert os.path.exists(out + ".3mf")
    assert os.path.getsize(out + ".3mf") > 0
