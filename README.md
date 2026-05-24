# Printable Sound Diffuser

Generate a 3D-printable 2D skyline QRD (Quadratic Residue Diffuser) acoustic panel as an STL or 3MF file. Given a design frequency and a pair of prime numbers, the tool computes the well-depth sequence, combines two 1D patterns into a 2D heightmap, and emits a watertight mesh sized for FDM or resin printing.

<!-- screenshot / render here -->

## Quickstart

```
pip install -e .[dev,3mf,preview]
python generate.py --p-x 7 --p-y 7 --f-design 1000 --output panel
```

This writes `panel.stl` to the current directory and prints a summary to stdout.

## Example

```
$ python generate.py --p-x 7 --p-y 7 --f-design 1000 --output panel
Panel size:     210.0 x 210.0 mm
Total height:   207.0 mm
Max well depth: 196.0 mm
f_design:       1000 Hz  (lower bound)
f_high:         6236 Hz  (well-width upper cutoff)
Column size:    27.5 mm
Warnings:
  ! tall columns may be fragile
Saved: panel.stl
```

The panel diffuses frequencies in the band **1000 – 6236 Hz**. The warning flags that 196 mm columns may need infill or internal supports; raise `--f-design` to reduce well depth.

## All flags

| Flag | Default | Description |
|---|---|---|
| `--p-x` | 7 | QRD prime, x-axis |
| `--p-y` | 7 | QRD prime, y-axis |
| `--f-design` | 1000.0 | Design (lower-bound) frequency, Hz |
| `--c` | 343.0 | Speed of sound, m/s |
| `--cell-size` | 30.0 | Cell outer size, mm |
| `--wall-thickness` | 2.5 | Gap between adjacent columns, mm |
| `--base-thickness` | 6.0 | Base plate thickness, mm |
| `--min-col-height` | 5.0 | Minimum column height, mm |
| `--combine` | `add` | 2D combination mode: `add` or `multiply` |
| `--manifold` | flag | Use single watertight heightfield mesh |
| `--format` | `stl` | Output format: `stl` or `3mf` |
| `--output` | `diffuser` | Output filename (extension replaced automatically) |
| `--preview` | flag | Open interactive 3D viewer before export (requires `pip install -e .[preview]`) |

## How it works

### QRD sequence

A QRD of order *p* (a prime number) assigns well depth to each column via:

```
s[n] = (n * n) mod p    for n = 0, 1, ..., p-1
```

The sequence `s` is then scaled to physical depths:

```
unit_mm = c / (2 * p * f_design) * 1000
depth[n] = s[n] * unit_mm
```

where `c` is the speed of sound (m/s) and `f_design` is the lowest frequency the panel should diffuse.

### 2D additive combination

Two independent 1D sequences (one per axis) are combined by addition:

```
total_depth[i, j] = depth_x[i] + depth_y[j]
```

Column height is the inverse of total depth so that the deepest well corresponds to the shortest column:

```
H[i, j] = (max_total_depth - total_depth[i, j]) + min_col_height
```

This doubles the maximum panel thickness compared to a single 1D QRD with the same prime. Use `--combine multiply` to keep depth bounded to `max(depth_x, depth_y)` at the cost of a less acoustically rigorous pattern.

### Mesh construction

The default builder (`build_diffuser`) concatenates a base plate with one rectangular prism per cell and calls `mesh.process()` so slicers can handle the result directly.

The `--manifold` builder (`build_diffuser_manifold`) constructs a single watertight mesh from the heightmap — bottom face, triangulated top surface (cell tops at full height, inter-column gaps at base level), and side walls. Use this path for resin slicers or boolean operations downstream.

## Printing notes

- **Orientation:** print with the base plate on the bed. No supports needed for the default builder; the columns are vertical and self-supporting as long as their height-to-width ratio is reasonable.
- **Infill:** 15–20 % gyroid is a good default. Tall, narrow columns may benefit from 30 %+ or a stronger pattern.
- **Layer height:** 0.2 mm is fine for most panels. Columns narrower than ~8 mm may warrant 0.15 mm.
- **Material:** PLA works well for wall panels. PETG or ABS if thermal stability matters (e.g., near windows).

## Future work

A single QRD panel is periodic, which can produce grating lobes — coherent re-reflections at specific angles. For more uniform diffusion across a wall, arrange panels with different primes (e.g., p = 5, 7, 11) in a modulated, aperiodic array.
