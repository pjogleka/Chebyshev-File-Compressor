import pytest
from compress import compress
from decompress import decompress
import numpy as np
import itertools
from read_file import read_file
from find_files import rand_files


n = 1
@pytest.mark.parametrize("file_path", rand_files(n))
def test_accuracy(tmp_path, file_path):
    x = read_file(file_path)
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    c_level = np.random.randint(1, 10)
    tol = {1:1, 2:2.5, 3:5, 4:7.5, 5:10, 6:12.5, 7:15, 8:17.5, 9:20}
    compress(file_path, c_level, out_dir=test_dir)
    decompress(f"{test_dir}/comp_{x.file_name}", out_dir=test_dir)
    y = read_file(f"{test_dir}/decomp_{x.file_name}")
    # Add 1% overhead to error tolerance to account for round off error during calculation
    assert np.allclose(y.data, x.data, rtol=(tol[c_level] + 1) * 0.01, atol=1e-6) == True


@pytest.mark.parametrize("file_path", rand_files(n))
def test_preserve(tmp_path, file_path):
    x = read_file(file_path)
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    compress(file_path, c_level=3, out_dir=test_dir)
    decompress(f"{test_dir}/comp_{x.file_name}", out_dir=test_dir)
    y = read_file(f"{test_dir}/decomp_{x.file_name}")
    with open(f"{test_dir}/comp_{x.file_name}") as comp:
        for i, line in enumerate(itertools.islice(comp, 6, 6 + np.size(x.lat_vals)*np.size(x.lon_vals))):
            if line[0] == "*":
                assert np.array_equal(x.data[i], y.data[i]) == True


@pytest.mark.parametrize("file_path", rand_files(n))
def test_coeff(tmp_path, file_path):
    x = read_file(file_path)
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    cheb_coeff_arr, cheb_approx_arr = compress(file_path, c_level=3, out_dir=test_dir, store=True)
    with open(f"{test_dir}/comp_{x.file_name}") as comp:
        for i, line in enumerate(itertools.islice(comp, 6, 6 + np.size(x.lat_vals)*np.size(x.lon_vals))):
            if line[0] != "*" and not isinstance(line[0], str):
                assert np.array_equal(cheb_coeff_arr[i], np.fromstring(line, sep=" ")) == True
            elif line[0][0] == "x":
                decomp = line.split()
                assert np.array_equal(cheb_coeff_arr[i], np.array(decomp[2:]).astype(float)) == True


@pytest.mark.parametrize("file_path", rand_files(n))
def test_approx(tmp_path, file_path):
    x = read_file(file_path)
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    cheb_coeff_arr, cheb_approx_arr = compress(file_path, c_level=3, out_dir=test_dir, store=True)
    decompress(f"{test_dir}/comp_{x.file_name}", out_dir=test_dir)
    y = read_file(f"{test_dir}/decomp_{x.file_name}")
    with open(f"{test_dir}/comp_{x.file_name}") as comp:
        for i, line in enumerate(itertools.islice(comp, 6, 6 + np.size(x.lat_vals)*np.size(x.lon_vals))):
            if line[0] != "*" and not isinstance(line[0], str):
                assert np.allclose(cheb_approx_arr[i], y.data[i], rtol=0.06, atol=1e-6) == True
            elif line[0][0] == "x":
                decomp = line.split()
                assert np.allclose(cheb_approx_arr[i], y.data[i][int(decomp[0][1:]):], rtol=0.06, atol=1e-6) == True


@pytest.mark.parametrize("file_path", rand_files(n))
def test_cutoff(tmp_path, file_path):
    x = read_file(file_path)
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    compress(file_path, c_level=3, out_dir=test_dir)
    with open(f"{test_dir}/comp_{x.file_name}") as comp:
        for i, line in enumerate(itertools.islice(comp, 6, 6 + np.size(x.lat_vals)*np.size(x.lon_vals))):
            if line[0] != "*" and not isinstance(line[0], str):
                assert np.size(np.fromstring(line, sep=" ")) <= 0.8 * np.size(x.alt_vals)
            elif line[0][0] == "x":
                decomp = line.split()
                assert np.size(decomp) - 2 <= 0.8 * np.size(x.alt_vals)