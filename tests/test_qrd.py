import pytest
import numpy as np
from diffuser_gen.qrd import qrd_sequence, well_depths_mm, height_map_2d


def test_qrd_sequence_p7():
    assert qrd_sequence(7).tolist() == [0, 1, 4, 2, 2, 4, 1]


def test_qrd_sequence_p11_range():
    seq = qrd_sequence(11)
    assert len(seq) == 11
    assert seq.min() >= 0
    assert seq.max() <= 10


def test_qrd_rejects_nonprime():
    for p in (1, 4, 6, 9):
        with pytest.raises(ValueError):
            qrd_sequence(p)


def test_well_depths_scaling():
    seq = qrd_sequence(7)
    depths_base = well_depths_mm(seq, 1000.0, 343.0)
    depths_double = well_depths_mm(seq, 2000.0, 343.0)
    assert np.isclose(depths_double.max(), depths_base.max() / 2)


def test_height_map_shape():
    H = height_map_2d(7, 11, 1000.0, 343.0, 5.0)
    assert H.shape == (7, 11)


def test_height_map_min():
    H = height_map_2d(7, 7, 1000.0, 343.0, 5.0)
    assert np.isclose(H.min(), 5.0)


def test_height_map_combine_modes():
    seq = qrd_sequence(7)
    depths = well_depths_mm(seq, 1000.0, 343.0)
    H_add = height_map_2d(7, 7, 1000.0, 343.0, 5.0, combine="add")
    H_mul = height_map_2d(7, 7, 1000.0, 343.0, 5.0, combine="multiply")

    assert H_add.shape == (7, 7)
    assert H_mul.shape == (7, 7)
    assert np.isclose(H_add.max() - 5.0, 2 * depths.max())
    assert H_mul.min() >= 5.0
