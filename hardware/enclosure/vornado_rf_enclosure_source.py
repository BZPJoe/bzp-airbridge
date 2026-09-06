#!/usr/bin/env python3
"""Parametric enclosure for an ESP32-C3 Super Mini and E07-M1101D-SMA CC1101.

The generated STL files are in millimetres.  The base is printed open-side up.
The lid is already oriented outer-face down with its skirt and retention pads up.

Dependencies:
    pip install numpy trimesh manifold3d matplotlib
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import trimesh


# -------------------------- verified hardware envelope -----------------------

ESP_PCB = (22.5, 18.0, 1.6)       # L x W x nominal PCB thickness
ESP_ORIGIN = (3.4, 22.5, 17.0)    # lower-left-bottom, USB-C faces -X

CC_PCB = (28.0, 15.0, 1.2)        # L x W x PCB thickness, excludes SMA
CC_ORIGIN = (5.8, 3.0, 17.0)      # header faces -X, SMA faces +X
CC_HOLE_X_FROM_SMA_EDGE = 10.0
CC_HOLE_Y_FROM_EDGE = 3.8
CC_HOLE_DIAMETER = 3.0
CC_SMA_DIAMETER = 6.2
CC_SMA_LENGTH = 9.6

# ------------------------------- enclosure ----------------------------------

CASE_X = 36.0
CASE_Y = 43.5
BASE_H = 23.0
WALL = 2.0
FLOOR = 2.0
CORNER_R = 2.5

LID_TOP = 2.0
LID_SKIRT_DEPTH = 3.0
LID_SKIRT_WALL = 1.2
LID_CLEARANCE_PER_SIDE = 0.25
SNAP_NUB_RADIUS = 0.50
SNAP_POCKET_RADIUS = 0.68
SNAP_LENGTH = 5.0
SNAP_Z_ASSEMBLED = 19.0


def translated(mesh: trimesh.Trimesh, xyz) -> trimesh.Trimesh:
    mesh = mesh.copy()
    mesh.apply_translation(np.asarray(xyz, dtype=float))
    return mesh


def box(extents, center) -> trimesh.Trimesh:
    return trimesh.creation.box(extents=np.asarray(extents, dtype=float),
                                transform=trimesh.transformations.translation_matrix(center))


def cylinder_z(radius, height, center, sections=64) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    mesh.apply_translation(center)
    return mesh


def cylinder_x(radius, length, center, sections=64) -> trimesh.Trimesh:
    transform = trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0])
    transform[:3, 3] = center
    return trimesh.creation.cylinder(radius=radius, height=length, sections=sections,
                                     transform=transform)


def cylinder_y(radius, length, center, sections=64) -> trimesh.Trimesh:
    transform = trimesh.transformations.rotation_matrix(-math.pi / 2.0, [1, 0, 0])
    transform[:3, 3] = center
    return trimesh.creation.cylinder(radius=radius, height=length, sections=sections,
                                     transform=transform)


def union(meshes) -> trimesh.Trimesh:
    result = trimesh.boolean.union(meshes, engine="manifold")
    if result is None:
        raise RuntimeError("Boolean union failed")
    return result


def difference(mesh, cutters) -> trimesh.Trimesh:
    result = trimesh.boolean.difference([mesh, *cutters], engine="manifold")
    if result is None:
        raise RuntimeError("Boolean difference failed")
    return result


def rounded_box(extents, radius, center) -> trimesh.Trimesh:
    """Rounded XY rectangle extruded in Z."""
    sx, sy, sz = extents
    cx, cy, cz = center
    if radius <= 0:
        return box(extents, center)
    pieces = [
        box((sx - 2 * radius, sy, sz), center),
        box((sx, sy - 2 * radius, sz), center),
    ]
    for dx in (-sx / 2 + radius, sx / 2 - radius):
        for dy in (-sy / 2 + radius, sy / 2 - radius):
            pieces.append(cylinder_z(radius, sz, (cx + dx, cy + dy, cz)))
    return union(pieces)


def build_base() -> trimesh.Trimesh:
    outer = rounded_box((CASE_X, CASE_Y, BASE_H), CORNER_R,
                        (CASE_X / 2, CASE_Y / 2, BASE_H / 2))
    inner_x = CASE_X - 2 * WALL
    inner_y = CASE_Y - 2 * WALL
    inner = rounded_box((inner_x, inner_y, BASE_H - FLOOR + 2.0),
                        max(0.8, CORNER_R - WALL),
                        (CASE_X / 2, CASE_Y / 2,
                         FLOOR + (BASE_H - FLOOR + 2.0) / 2))
    shell = difference(outer, [inner])

    # Connector openings.  USB is deliberately generous for molded cable ends.
    esp_y_center = ESP_ORIGIN[1] + ESP_PCB[1] / 2
    usb_cut = box((WALL + 2.0, 12.0, 6.4),
                  (WALL / 2, esp_y_center, 19.2))

    cc_y_center = CC_ORIGIN[1] + CC_PCB[1] / 2
    cc_z_center = CC_ORIGIN[2] + CC_PCB[2] / 2
    sma_cut = cylinder_x(3.75, WALL + 2.0,
                         (CASE_X - WALL / 2, cc_y_center, cc_z_center))

    # Five vertical vents in each long wall; all are short, support-free bridges.
    vent_cuts = []
    for x in (8.0, 13.0, 18.0, 23.0, 28.0):
        vent_cuts.append(box((1.5, WALL + 2.0, 5.0), (x, WALL / 2, 13.0)))
        vent_cuts.append(box((1.5, WALL + 2.0, 5.0),
                             (x, CASE_Y - WALL / 2, 13.0)))

    # A shallow fingernail notch makes the snap lid easy to remove.
    pry_cut = box((8.0, WALL + 2.0, 2.0),
                  (CASE_X / 2, WALL / 2, BASE_H - 0.6))

    # Rounded latch pockets in the outside faces of the left and right walls.
    # Their 1.36 mm curved roofs are small enough to print upright unsupported.
    snap_pockets = [
        cylinder_y(SNAP_POCKET_RADIUS, SNAP_LENGTH + 0.8,
                   (0.0, CASE_Y / 2, SNAP_Z_ASSEMBLED)),
        cylinder_y(SNAP_POCKET_RADIUS, SNAP_LENGTH + 0.8,
                   (CASE_X, CASE_Y / 2, SNAP_Z_ASSEMBLED)),
    ]
    shell = difference(shell, [usb_cut, sma_cut, pry_cut, *vent_cuts, *snap_pockets])

    features = []

    # CC1101 posts: broad shoulders support the PCB, 2.4 mm tips locate in 3 mm holes.
    cc_sma_edge_x = CC_ORIGIN[0] + CC_PCB[0]
    hole_x = cc_sma_edge_x - CC_HOLE_X_FROM_SMA_EDGE
    for hole_y in (CC_ORIGIN[1] + CC_HOLE_Y_FROM_EDGE,
                   CC_ORIGIN[1] + CC_PCB[1] - CC_HOLE_Y_FROM_EDGE):
        shoulder_h = CC_ORIGIN[2] - FLOOR
        features.append(cylinder_z(2.5, shoulder_h,
                                   (hole_x, hole_y, FLOOR + shoulder_h / 2)))
        features.append(cylinder_z(1.2, 2.2,
                                   (hole_x, hole_y, CC_ORIGIN[2] + 1.1)))

    # ESP32 central supports leave both 2.54 mm header rows completely unobstructed.
    for support_x in (ESP_ORIGIN[0] + 6.0, ESP_ORIGIN[0] + ESP_PCB[0] - 6.0):
        for support_y in (ESP_ORIGIN[1] + 6.0, ESP_ORIGIN[1] + ESP_PCB[1] - 6.0):
            support_h = ESP_ORIGIN[2] - FLOOR
            features.append(cylinder_z(2.0, support_h,
                                       (support_x, support_y,
                                        FLOOR + support_h / 2)))

    # Low guide tabs locate the ESP32 with 0.20 mm nominal clearance per side.
    guide_top = ESP_ORIGIN[2] + 1.8
    guide_h = guide_top - FLOOR
    guide_z = FLOOR + guide_h / 2
    for gx in (ESP_ORIGIN[0] + 5.0, ESP_ORIGIN[0] + ESP_PCB[0] - 5.0):
        features.append(box((2.0, 0.8, guide_h),
                            (gx, ESP_ORIGIN[1] - 0.6, guide_z)))
        features.append(box((2.0, 0.8, guide_h),
                            (gx, ESP_ORIGIN[1] + ESP_PCB[1] + 0.6, guide_z)))
    # End guides sit outside the 9 mm-wide USB-C shell envelope.
    for gy in (ESP_ORIGIN[1] + 2.0, ESP_ORIGIN[1] + ESP_PCB[1] - 2.0):
        features.append(box((0.8, 2.0, guide_h),
                            (ESP_ORIGIN[0] - 0.6, gy, guide_z)))
        features.append(box((0.8, 2.0, guide_h),
                            (ESP_ORIGIN[0] + ESP_PCB[0] + 0.6, gy, guide_z)))

    base = union([shell, *features])
    base.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(base)
    return base


def build_lid() -> trimesh.Trimesh:
    # Print orientation: exterior face is at Z=0, skirt/bosses point upward.
    plate = rounded_box((CASE_X, CASE_Y, LID_TOP), CORNER_R,
                        (CASE_X / 2, CASE_Y / 2, LID_TOP / 2))

    inner_x = CASE_X - 2 * WALL
    inner_y = CASE_Y - 2 * WALL
    skirt_outer_x = inner_x - 2 * LID_CLEARANCE_PER_SIDE
    skirt_outer_y = inner_y - 2 * LID_CLEARANCE_PER_SIDE
    skirt_outer = rounded_box((skirt_outer_x, skirt_outer_y, LID_SKIRT_DEPTH),
                              max(0.5, CORNER_R - WALL - LID_CLEARANCE_PER_SIDE),
                              (CASE_X / 2, CASE_Y / 2,
                               LID_TOP + LID_SKIRT_DEPTH / 2))
    skirt_inner = rounded_box((skirt_outer_x - 2 * LID_SKIRT_WALL,
                               skirt_outer_y - 2 * LID_SKIRT_WALL,
                               LID_SKIRT_DEPTH + 1.0),
                              0.35,
                              (CASE_X / 2, CASE_Y / 2,
                               LID_TOP + (LID_SKIRT_DEPTH + 1.0) / 2))
    skirt = difference(skirt_outer, [skirt_inner])

    # Break the skirt around the two connector openings.
    esp_y_center = ESP_ORIGIN[1] + ESP_PCB[1] / 2
    cc_y_center = CC_ORIGIN[1] + CC_PCB[1] / 2
    # Y coordinates are mirrored in the print-ready lid because turning the lid
    # over for assembly reverses Y.  After that physical flip, these align with
    # the USB and SMA openings in the base.
    connector_reliefs = [
        box((4.0, 12.4, LID_SKIRT_DEPTH + 2.0),
            (WALL, CASE_Y - esp_y_center, LID_TOP + LID_SKIRT_DEPTH / 2)),
        box((4.0, 8.0, LID_SKIRT_DEPTH + 2.0),
            (CASE_X - WALL, CASE_Y - cc_y_center,
             LID_TOP + LID_SKIRT_DEPTH / 2)),
    ]
    skirt = difference(skirt, connector_reliefs)

    lid = union([plate, skirt])

    # External cantilever arms print vertically from the bed and flex outward as
    # the lid is installed.  Half-round inward nubs click into the base pockets.
    # The arm sides share full faces with the lid plate, so this remains one solid.
    snap_arms = [
        box((1.0, 8.0, 7.0), (-0.5, CASE_Y / 2, 3.5)),
        box((1.0, 8.0, 7.0), (CASE_X + 0.5, CASE_Y / 2, 3.5)),
    ]
    snap_nubs = [
        cylinder_y(SNAP_NUB_RADIUS, SNAP_LENGTH,
                   (0.0, CASE_Y / 2,
                    BASE_H + LID_TOP - SNAP_Z_ASSEMBLED)),
        cylinder_y(SNAP_NUB_RADIUS, SNAP_LENGTH,
                   (CASE_X, CASE_Y / 2,
                    BASE_H + LID_TOP - SNAP_Z_ASSEMBLED)),
    ]
    lid = union([lid, *snap_arms, *snap_nubs])

    # These rings only limit board lift.  The CC1101 simply drops over the base pins;
    # there are no screws, nuts, or threaded inserts anywhere in the enclosure.
    retainers = []
    cc_sma_edge_x = CC_ORIGIN[0] + CC_PCB[0]
    hole_x = cc_sma_edge_x - CC_HOLE_X_FROM_SMA_EDGE
    for hole_y in (CC_ORIGIN[1] + CC_HOLE_Y_FROM_EDGE,
                   CC_ORIGIN[1] + CC_PCB[1] - CC_HOLE_Y_FROM_EDGE):
        print_y = CASE_Y - hole_y
        outer = cylinder_z(2.25, 4.4, (hole_x, print_y, LID_TOP + 2.2))
        inner = cylinder_z(1.65, 5.0, (hole_x, print_y, LID_TOP + 2.5))
        retainers.append(difference(outer, [inner]))

    # Small insulating pads limit lift of the ESP32 without covering its antenna.
    for px in (ESP_ORIGIN[0] + 2.0, ESP_ORIGIN[0] + ESP_PCB[0] - 2.0):
        for py in (ESP_ORIGIN[1] + 1.2, ESP_ORIGIN[1] + ESP_PCB[1] - 1.2):
            retainers.append(cylinder_z(1.0, 4.0,
                                        (px, CASE_Y - py, LID_TOP + 2.0), sections=48))
    lid = union([lid, *retainers])

    # Through-vents over each board.  Longest bridge is 14 mm when printed as oriented.
    vent_cuts = []
    for y in (5.5, 8.0, 10.5, 13.0, 15.5):
        vent_cuts.append(box((14.0, 1.5, LID_TOP + 2.0),
                             (17.0, CASE_Y - y, LID_TOP / 2)))
    for y in (25.0, 28.0, 31.0, 34.0, 37.0):
        vent_cuts.append(box((14.0, 1.5, LID_TOP + 2.0),
                             (16.5, CASE_Y - y, LID_TOP / 2)))
    lid = difference(lid, vent_cuts)
    lid.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(lid)
    return lid


def hardware_proxies():
    """Non-printing reference meshes used only in the preview."""
    cc = box(CC_PCB,
             (CC_ORIGIN[0] + CC_PCB[0] / 2,
              CC_ORIGIN[1] + CC_PCB[1] / 2,
              CC_ORIGIN[2] + CC_PCB[2] / 2))
    cc.visual.face_colors = [40, 100, 180, 255]
    sma = cylinder_x(CC_SMA_DIAMETER / 2, CC_SMA_LENGTH,
                     (CC_ORIGIN[0] + CC_PCB[0] + CC_SMA_LENGTH / 2,
                      CC_ORIGIN[1] + CC_PCB[1] / 2,
                      CC_ORIGIN[2] + CC_PCB[2] / 2))
    sma.visual.face_colors = [205, 160, 35, 255]
    esp = box(ESP_PCB,
              (ESP_ORIGIN[0] + ESP_PCB[0] / 2,
               ESP_ORIGIN[1] + ESP_PCB[1] / 2,
               ESP_ORIGIN[2] + ESP_PCB[2] / 2))
    esp.visual.face_colors = [45, 120, 70, 255]
    usb = box((3.0, 9.0, 3.4),
              (ESP_ORIGIN[0] - 1.5,
               ESP_ORIGIN[1] + ESP_PCB[1] / 2,
               ESP_ORIGIN[2] + ESP_PCB[2] + 1.7))
    usb.visual.face_colors = [150, 150, 155, 255]
    return cc, sma, esp, usb


def collision_proxies():
    """Hardware envelopes with the CC1101 mounting holes removed."""
    cc, sma, esp, usb = hardware_proxies()
    cc_sma_edge_x = CC_ORIGIN[0] + CC_PCB[0]
    hole_x = cc_sma_edge_x - CC_HOLE_X_FROM_SMA_EDGE
    hole_cuts = [
        cylinder_z(CC_HOLE_DIAMETER / 2, CC_PCB[2] + 2.0,
                   (hole_x, hole_y, CC_ORIGIN[2] + CC_PCB[2] / 2))
        for hole_y in (CC_ORIGIN[1] + CC_HOLE_Y_FROM_EDGE,
                       CC_ORIGIN[1] + CC_PCB[1] - CC_HOLE_Y_FROM_EDGE)
    ]
    cc = difference(cc, hole_cuts)
    return {
        "cc1101_pcb": cc,
        "sma_barrel": sma,
        "esp32_pcb": esp,
        "usb_c_shell": usb,
    }


def lid_to_assembly(lid: trimesh.Trimesh) -> trimesh.Trimesh:
    """Flip the print-ready lid and place it on the base."""
    result = lid.copy()
    transform = trimesh.transformations.rotation_matrix(
        math.pi, [1, 0, 0], point=[CASE_X / 2, CASE_Y / 2, 0])
    transform[:3, 3] += [0, 0, BASE_H + LID_TOP]
    result.apply_transform(transform)
    return result


def collision_volume(a: trimesh.Trimesh, b: trimesh.Trimesh) -> float:
    intersection = trimesh.boolean.intersection([a, b], engine="manifold")
    if intersection is None or len(intersection.faces) == 0:
        return 0.0
    return abs(float(intersection.volume))


def export_preview(base, lid, out_path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    def add_mesh(ax, mesh, color, alpha=1.0):
        tris = mesh.triangles
        collection = Poly3DCollection(tris, linewidths=0.03, edgecolors=(0, 0, 0, 0.12))
        collection.set_facecolor((*color, alpha))
        ax.add_collection3d(collection)

    fig = plt.figure(figsize=(10, 7), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, base, (0.72, 0.75, 0.78), 0.38)
    cc, sma, esp, usb = hardware_proxies()
    add_mesh(ax, cc, (0.08, 0.25, 0.72), 0.95)
    add_mesh(ax, sma, (0.86, 0.62, 0.10), 0.95)
    add_mesh(ax, esp, (0.08, 0.55, 0.23), 0.95)
    add_mesh(ax, usb, (0.62, 0.64, 0.67), 0.95)

    # Exploded lid, displayed in assembly orientation directly above the base.
    lid_view = lid_to_assembly(lid)
    lid_view.apply_translation([0, 0, 11.0])
    add_mesh(ax, lid_view, (0.88, 0.88, 0.90), 0.75)

    ax.set_xlim(-3, 47)
    ax.set_ylim(-3, 47)
    ax.set_zlim(0, 39)
    ax.set_box_aspect((50, 50, 39))
    ax.view_init(elev=27, azim=-56)
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")
    ax.set_title("ESP32-C3 controller + CC1101/SMA radio — exploded enclosure")
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(facecolor=(0.08, 0.55, 0.23), label="SATUY ESP32-C3 controller"),
        Patch(facecolor=(0.08, 0.25, 0.72), label="AOICRIE CC1101 radio PCB"),
        Patch(facecolor=(0.86, 0.62, 0.10), label="SMA antenna connector"),
    ], loc="upper left", framealpha=0.92)
    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def validate(name: str, mesh: trimesh.Trimesh) -> dict:
    mesh.remove_unreferenced_vertices()
    return {
        "name": name,
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "body_count": int(len(mesh.split(only_watertight=False))),
        "triangles": int(len(mesh.faces)),
        "bounds_mm": np.round(mesh.bounds, 3).tolist(),
        "extents_mm": np.round(mesh.extents, 3).tolist(),
        "volume_mm3": round(float(mesh.volume), 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    base = build_base()
    lid = build_lid()
    base_path = args.output_dir / "vornado_rf_enclosure_base.stl"
    lid_path = args.output_dir / "vornado_rf_enclosure_lid.stl"
    preview_path = args.output_dir / "vornado_rf_enclosure_preview.png"
    report_path = args.output_dir / "mesh_validation.txt"

    base.export(base_path, file_type="stl")
    lid.export(lid_path, file_type="stl")
    export_preview(base, lid, preview_path)

    reports = [validate("base", base), validate("lid", lid)]
    lid_assembled = lid_to_assembly(lid)
    fit_checks = {
        "base_to_lid_overlap_mm3": collision_volume(base, lid_assembled),
    }
    for proxy_name, proxy in collision_proxies().items():
        fit_checks[f"base_to_{proxy_name}_overlap_mm3"] = collision_volume(base, proxy)
        fit_checks[f"lid_to_{proxy_name}_overlap_mm3"] = collision_volume(lid_assembled,
                                                                           proxy)
    lines = []
    for report in reports:
        lines.append(report["name"].upper())
        lines.extend(f"  {key}: {value}" for key, value in report.items() if key != "name")
        lines.append("")
    lines.append("ASSEMBLY FIT CHECKS")
    lines.extend(f"  {key}: {value:.6f}" for key, value in fit_checks.items())
    lines.append("")
    lines.append("DESIGN CLEARANCES")
    lines.append(f"  under_board_wiring_height_mm: {ESP_ORIGIN[2] - FLOOR:.2f}")
    lines.append(f"  lid_clearance_per_side_mm: {LID_CLEARANCE_PER_SIDE:.2f}")
    lines.append(f"  snap_pocket_radial_clearance_mm: "
                 f"{SNAP_POCKET_RADIUS - SNAP_NUB_RADIUS:.2f}")
    lines.append("  snap_arm_dimensions_mm: 8.0 wide x 5.0 free length x 1.0 thick")
    lines.append(f"  cc1101_sma_radial_clearance_mm: {(7.5 - CC_SMA_DIAMETER) / 2:.2f}")
    lines.append("  usb_c_opening_mm: 12.0 x 6.4")
    lines.append("  enclosure_fasteners: none (two flexible snap latches)")
    lines.append("  board_fasteners: none (drop-on locating pins/guides)")
    lines.append("  slicer_support_material_required: no")
    lines.append("")
    mesh_ok = all(r["watertight"] and r["winding_consistent"] and r["is_volume"]
                  and r["body_count"] == 1 for r in reports)
    fit_ok = all(value <= 0.001 for value in fit_checks.values())
    all_ok = mesh_ok and fit_ok
    lines.append(f"ALL_CHECKS_PASS: {all_ok}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if not all_ok:
        raise SystemExit("Mesh validation failed; see mesh_validation.txt")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
