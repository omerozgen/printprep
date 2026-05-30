"""PrintPrep command-line interface."""

import glob
import json as _json
import os
import sys
from dataclasses import asdict

import click
import numpy as np
from rich.console import Console
from rich.table import Table

from printprep import PrintPrepError, __version__
from printprep.config.presets import MATERIAL_PRESETS
from printprep.core import (
    analyze, estimate_from_active, estimate_print_job, load_mesh, merge_to_single,
    pack as pack_layout, repair_mesh, suggest_orientation,
)
from printprep.config.presets import get_material
from printprep.i18n import t
from printprep.slicer import (
    EXPORT_FORMATS,
    SLICER_NAMES,
    bed_fit_warning,
    export_profile,
    get_bundled,
    get_slicer,
    parse_machine_file,
    parse_material_profile,
)

console = Console()
err_console = Console(stderr=True, style="bold red")


def _yn(value: bool) -> str:
    return "[green]Yes[/green]" if value else "[red]No[/red]"


def _resolve_printer(printer: str = "", printer_profile: str = "", auto: bool = False):
    """Resolve a PrinterSpec from CLI options. Priority:

    1. --printer-profile PATH  (a slicer machine JSON; most precise)
    2. --auto-printer          (scan installed slicers; match --printer name if given)
    3. --printer NAME          (bundled database lookup)

    Returns the PrinterSpec or None. Prints a friendly note on what was used.
    """
    if printer_profile:
        spec = parse_machine_file(printer_profile)
        if spec is None:
            err_console.print(t("err_printer_profile_failed", path=printer_profile))
        return spec
    if auto:
        from printprep.slicer.discover import discover_printers
        found = discover_printers()
        if printer:
            for row in found:
                if printer.lower() in row["spec"].name.lower():
                    return row["spec"]
        if found:
            return found[0]["spec"]
        # fall through to bundled lookup if nothing detected
    if printer:
        return get_bundled(printer)
    return None


def _fmt_minutes(minutes: float) -> str:
    if minutes < 60:
        return f"{minutes:.0f} {t('minute_short_cli') or 'min'}"
    h, m = divmod(int(round(minutes)), 60)
    return f"{h} {t('hour_short_cli') or 'h'} {m} {t('minute_short_cli') or 'min'}"


@click.group(help=t("cli_group_help"))
@click.version_option(__version__, prog_name="printprep")
def main():
    pass


@main.command(name="analyze", help=t("cmd_analyze_help"))
@click.argument("path", type=click.Path())
def analyze_cmd(path):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    result = analyze(mesh, path=path)
    dx, dy, dz = result.dimensions_mm

    table = Table(title=f"Model: {path}", show_header=False, title_style="bold cyan")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Volume", f"{result.volume_mm3 / 1000:.2f} cm³")
    table.add_row("Surface area", f"{result.surface_area_mm2 / 100:.2f} cm²")
    table.add_row("Dimensions", f"{dx:.1f} × {dy:.1f} × {dz:.1f} mm")
    table.add_row("Triangles / vertices", f"{result.face_count} / {result.vertex_count}")
    table.add_row("Bodies", str(result.body_count))
    table.add_row("Watertight", _yn(result.is_watertight))
    table.add_row("Consistent normals", _yn(result.is_winding_consistent))
    table.add_row("Printable (is_volume)", _yn(result.is_volume))
    table.add_row("Degenerate faces", str(result.degenerate_faces))
    table.add_row("Duplicate faces", str(result.duplicate_faces))
    if result.overhang_face_count:
        table.add_row(
            "Overhangs",
            f"{result.overhang_face_count} faces, up to {result.steepest_overhang_deg:.0f}° "
            f"({result.overhang_area_fraction * 100:.1f}% area)",
        )
    else:
        table.add_row("Overhangs", "none")
    if result.wall_thickness:
        wt = result.wall_thickness
        table.add_row(
            "Wall thickness (min/p5/med)",
            f"{wt['min_mm']:.2f} / {wt['p5_mm']:.2f} / {wt['p50_mm']:.2f} mm",
        )
    else:
        table.add_row("Wall thickness", "n/a")
    if result.holes:
        top = result.holes[0]
        extra = f" (+{len(result.holes) - 1} smaller)" if len(result.holes) > 1 else ""
        table.add_row("Holes", f"{len(result.holes)} — largest {top['perimeter_mm']:.1f} mm perim.{extra}")
    if result.non_manifold_edges:
        table.add_row("Non-manifold edges", str(result.non_manifold_edges))
    console.print(table)

    if result.issues:
        console.print(f"\n[bold yellow]{t('msg_issues_found')}[/bold yellow]")
        for issue in result.issues:
            console.print(f"  [yellow]⚠[/yellow] {issue['text']}")
    else:
        console.print(f"\n[bold green]{t('msg_no_issues')}[/bold green]")


@main.command(help=t("cmd_fix_help"))
@click.argument("path", type=click.Path())
@click.option("--output", "-o", required=True, type=click.Path(),
              help=t("opt_fix_output"))
def fix(path, output):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    mesh, report = repair_mesh(mesh)
    try:
        mesh.export(output)
    except Exception as exc:
        err_console.print(t("err_could_not_write", path=output, err=exc))
        sys.exit(1)

    console.print(f"[bold]{t('msg_applied_fixes')}[/bold]")
    console.print(f"  ✓ {t('msg_merged_vertices', n=report.merged_vertices)}")
    console.print(f"  ✓ {t('msg_removed_degenerate', n=report.removed_degenerate)}")
    console.print(f"  ✓ {t('msg_removed_duplicate', n=report.removed_duplicate)}")
    console.print(f"  ✓ {t('msg_holes_filled', n=report.holes_filled)}")
    if report.method == "meshfix":
        console.print(f"  ✓ {t('msg_aggressive_applied')}")
    console.print(
        f"\nWatertight: {report.watertight_before} → {report.watertight_after}  |  "
        f"Volume: {report.volume_after / 1000:.2f} cm³"
    )
    console.print(t("msg_output", path=f"[cyan]{output}[/cyan]"))
    if report.watertight_after:
        console.print(f"[bold green]{t('msg_status_ready')}[/bold green]")
    else:
        console.print(
            f"[bold yellow]Status: still not watertight — {report.open_edges_after} open "
            f"edge(s) remain; manual repair may be needed.[/bold yellow]"
        )


@main.command(help=t("cmd_suggest_help"))
@click.argument("path", type=click.Path())
@click.option("--slicer", type=click.Choice(SLICER_NAMES), default="creality",
              show_default=True, help=t("opt_suggest_slicer"))
@click.option("--material", type=click.Choice(sorted(MATERIAL_PRESETS)), default="pla",
              show_default=True, help=t("opt_suggest_material"))
@click.option("--import-profile", "import_profile", type=click.Path(),
              help=t("opt_suggest_import"))
@click.option("--export", "export_fmt", type=click.Choice(EXPORT_FORMATS),
              help=t("opt_suggest_export"))
@click.option("--out-dir", "out_dir", type=click.Path(), default=".",
              show_default=True, help=t("opt_suggest_outdir"))
@click.option("--printer", default="", show_default=False,
              help=t("opt_suggest_printer"))
@click.option("--printer-profile", "printer_profile", type=click.Path(),
              help=t("opt_suggest_printer_profile"))
@click.option("--auto-printer", "auto_printer", is_flag=True,
              help=t("opt_suggest_auto_printer"))
@click.option("--price-per-kg", "price_per_kg", type=float, default=None,
              help=t("opt_suggest_price"))
@click.option("--currency", default="", help=t("opt_suggest_currency"))
def suggest(path, slicer, material, import_profile, export_fmt, out_dir, printer,
            printer_profile, auto_printer, price_per_kg, currency):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    result = analyze(mesh, path=path)
    generator = get_slicer(slicer)
    printer_spec = _resolve_printer(printer, printer_profile, auto_printer)
    if import_profile:
        try:
            with open(import_profile, encoding="utf-8") as fh:
                preset = parse_material_profile(fh.read(), import_profile)
        except (OSError, PrintPrepError) as exc:
            err_console.print(f"Profile import failed: {exc}")
            sys.exit(1)
        profile = generator.build_profile_from_preset(result, preset, printer_spec)
    else:
        preset = get_material(material)
        profile = generator.build_profile_from_preset(result, preset, printer_spec)

    if printer_spec is not None:
        console.print(t("msg_printer_used", name=printer_spec.name,
                        src=("slicer" if printer_spec.source == "slicer" else "bundled")))
        warn = bed_fit_warning(result, printer_spec)
        if warn:
            console.print(f"[bold yellow]⚠ {warn['text']}[/bold yellow]")

    # Estimate: with --auto-printer, base it on the user's REAL active slicer
    # settings (layer height, infill, speed, filament density + cost); otherwise
    # estimate the recommended profile.
    active_cfg = None
    if auto_printer:
        from printprep.slicer.discover import detect_active_config
        cfgs = [c for c in detect_active_config() if c.get("printer")]
        if printer_spec:
            active_cfg = next((c for c in cfgs if c["printer"].name == printer_spec.name), None)
        active_cfg = active_cfg or (cfgs[0] if cfgs else None)

    estimate_note = None
    if active_cfg and (active_cfg.get("process") or active_cfg.get("filament")):
        estimate, est_profile = estimate_from_active(
            result, printer=active_cfg["printer"], process=active_cfg["process"],
            filament=active_cfg["filament"], currency=currency, price_per_kg=price_per_kg)
        estimate_note = t("msg_estimate_basis", layer=est_profile.layer_height_mm,
                          infill=est_profile.infill_pct, speed=est_profile.print_speed_mms,
                          material=est_profile.material)
    else:
        estimate = estimate_print_job(result, profile, preset,
                                      price_per_kg=price_per_kg, currency=currency)

    # An explicit --printer string wins for export binding; otherwise use the
    # resolved spec's name so the preset binds to the right printer.
    export_printer = printer or (printer_spec.name if printer_spec else "")
    if export_fmt:
        files = export_profile(profile, export_fmt, printer=export_printer)
        os.makedirs(out_dir, exist_ok=True)
        console.print(f"[bold]Exported {export_fmt} profile for {profile.slicer}:[/bold]")
        for fname, text in files.items():
            dest = os.path.join(out_dir, fname)
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(text)
            console.print(f"  ✓ [cyan]{dest}[/cyan]")
        hint = ("Import into OrcaSlicer/Creality Print: drag the .json onto the app "
                "or use the preset import." if export_fmt == "orca"
                else "Import into PrusaSlicer: File > Import > Import Config.")
        console.print(f"[dim]{hint}[/dim]")
    else:
        console.print(generator.to_json(profile))

    # Always-on estimate block (clearly labelled as approximate).
    cost_line = ""
    if estimate.cost is not None:
        cur = estimate.currency or ""
        cost_line = f"  Cost            : {estimate.cost}{(' ' + cur) if cur else ''}\n"
    console.print(
        "\n[bold cyan]Print estimate (~70% accurate):[/bold cyan]\n"
        f"  Filament        : {estimate.filament_length_mm / 1000:.2f} m  "
        f"({estimate.filament_weight_g:.1f} g)\n"
        f"  Time            : ~{_fmt_minutes(estimate.print_time_min)}\n"
        + cost_line
    )
    if estimate_note:
        console.print(f"[dim]{estimate_note}[/dim]")


@main.command(help=t("cmd_orient_help"))
@click.argument("path", type=click.Path())
@click.option("--output", "-o", required=True, type=click.Path(),
              help=t("opt_orient_output"))
def orient(path, output):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    oriented, report = suggest_orientation(mesh)
    try:
        oriented.export(output)
    except Exception as exc:
        err_console.print(t("err_could_not_write", path=output, err=exc))
        sys.exit(1)

    rx, ry, rz = report.euler_deg
    console.print(f"[bold]{t('msg_orient_heading')}[/bold]")
    console.print(f"  {t('msg_orient_rotation', rx=rx, ry=ry, rz=rz)}")
    console.print(
        f"  Overhang area: {report.overhang_before * 100:.1f}% → {report.overhang_after * 100:.1f}%"
    )
    if report.improved:
        console.print(f"[bold green]{t('msg_orient_better')}[/bold green]")
    else:
        console.print(f"[yellow]{t('msg_orient_optimal')}[/yellow]")
    console.print(t("msg_output", path=f"[cyan]{output}[/cyan]"))


@main.command(help=t("cmd_merge_help"))
@click.argument("path", type=click.Path())
@click.option("--output", "-o", required=True, type=click.Path(),
              help=t("opt_merge_output"))
def merge(path, output):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    merged, report = merge_to_single(mesh)
    try:
        merged.export(output)
    except Exception as exc:
        err_console.print(t("err_could_not_write", path=output, err=exc))
        sys.exit(1)

    console.print(f"[bold]{t('msg_merge_heading')}[/bold]")
    console.print(f"  {t('msg_merge_method', method=report.method)}")
    console.print(f"  {t('msg_merge_bodies', before=report.bodies_before, after=report.bodies_after)}")
    console.print(f"  {t('msg_merge_watertight', wt=report.watertight_after, vol=f'{report.volume_after / 1000:.2f}')}")
    console.print(f"[dim]{report.note}[/dim]")
    console.print(t("msg_output", path=f"[cyan]{output}[/cyan]"))


@main.command(name="slicer-discover", help=t("cmd_discover_help"))
def slicer_discover():
    from printprep.slicer.discover import discover_profiles
    rows = discover_profiles()
    if not rows:
        console.print(f"[yellow]{t('msg_no_profiles')}[/yellow]")
        console.print(f"[dim]{t('msg_no_profiles_hint')}[/dim]")
        return

    table = Table(title="Installed slicer profiles", title_style="bold cyan")
    table.add_column("Slicer", style="cyan")
    table.add_column("Kind")
    table.add_column("Name", overflow="fold")
    table.add_column("Path", overflow="fold", style="dim")
    for r in rows:
        table.add_row(r["slicer"], r["kind"], r["name"], r["path"])
    console.print(table)
    console.print(
        f"\n{len(rows)} profile(s). "
        "Use [cyan]printprep suggest --import-profile <path>[/cyan] to base a recommendation on one."
    )


@main.command(name="printer-list", help=t("cmd_printer_list_help"))
def printer_list():
    from printprep.slicer.discover import discover_printers
    from printprep.slicer.printer import BUNDLED_PRINTERS

    table = Table(title="Printers", title_style="bold cyan")
    table.add_column("Source", style="cyan")
    table.add_column("Name", overflow="fold")
    table.add_column("Bed (mm)", justify="right")
    table.add_column("Nozzle", justify="right")
    table.add_column("Retraction", justify="right")

    detected = discover_printers()
    for row in detected:
        s = row["spec"]
        table.add_row(f"{row['slicer']}", s.name,
                      f"{s.bed_x_mm:.0f}×{s.bed_y_mm:.0f}×{s.bed_z_mm:.0f}",
                      f"{s.nozzle_diameter_mm}",
                      f"{s.retraction_mm if s.retraction_mm is not None else '—'}")
    for s in BUNDLED_PRINTERS:
        table.add_row("bundled", s.name,
                      f"{s.bed_x_mm:.0f}×{s.bed_y_mm:.0f}×{s.bed_z_mm:.0f}",
                      f"{s.nozzle_diameter_mm}",
                      f"{s.retraction_mm if s.retraction_mm is not None else '—'}")
    console.print(table)
    if detected:
        console.print(t("msg_printers_detected", n=len(detected)))
    console.print(t("msg_printer_usage"))


@main.command(help=t("cmd_batch_help"))
@click.argument("directory", type=click.Path())
@click.option("--pattern", default="*.stl", show_default=True, help=t("opt_batch_pattern"))
@click.option("--recursive", "-r", is_flag=True, help=t("opt_batch_recursive"))
@click.option("--json", "json_out", type=click.Path(), help=t("opt_batch_json"))
def batch(directory, pattern, recursive, json_out):
    if not os.path.isdir(directory):
        err_console.print(t("err_not_a_directory", path=directory))
        sys.exit(1)

    if recursive:
        files = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    else:
        files = glob.glob(os.path.join(directory, pattern))
    files = sorted(f for f in files if os.path.isfile(f))
    if not files:
        err_console.print(t("err_no_files_matching", pattern=pattern, dir=directory))
        sys.exit(1)

    table = Table(title=f"Batch analysis — {directory}", title_style="bold cyan")
    table.add_column("File", style="cyan", overflow="fold")
    table.add_column("Size (mm)", justify="right")
    table.add_column("Vol (cm³)", justify="right")
    table.add_column("Watertight", justify="center")
    table.add_column("Bodies", justify="right")
    table.add_column("Issues", justify="right")

    results = []
    for path in files:
        name = os.path.basename(path)
        try:
            result = analyze(load_mesh(path), path=path)
        except PrintPrepError as exc:
            table.add_row(name, "[red]error[/red]", "-", "-", "-", str(exc)[:40])
            results.append({"path": path, "error": str(exc)})
            continue
        dx, dy, dz = result.dimensions_mm
        table.add_row(
            name,
            f"{dx:.0f}×{dy:.0f}×{dz:.0f}",
            f"{result.volume_mm3 / 1000:.1f}",
            "[green]Yes[/green]" if result.is_watertight else "[red]No[/red]",
            str(result.body_count),
            str(len(result.issues)),
        )
        results.append(asdict(result))

    console.print(table)
    ok = sum(1 for r in results if "error" not in r)
    console.print("\n" + t("msg_batch_analyzed", ok=ok, total=len(files)))

    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            _json.dump(results, fh, indent=2)
        console.print(t("msg_full_results", path=f"[cyan]{json_out}[/cyan]"))


@main.command(help=t("cmd_pack_help"))
@click.argument("directory", type=click.Path())
@click.option("--bed", "bed_spec", default="420x420", show_default=True,
              help=t("opt_pack_bed"))
@click.option("--padding", default=5.0, show_default=True, type=float,
              help=t("opt_pack_padding"))
@click.option("--rotate/--no-rotate", default=True, show_default=True,
              help=t("opt_pack_rotate"))
@click.option("--pattern", default="*.stl", show_default=True)
@click.option("--recursive", "-r", is_flag=True)
@click.option("--out-dir", "out_dir", type=click.Path(), default=".",
              show_default=True, help=t("opt_pack_outdir"))
def pack(directory, bed_spec, padding, rotate, pattern, recursive, out_dir):
    import trimesh
    try:
        bed_w, bed_d = (float(x) for x in bed_spec.lower().split("x", 1))
    except Exception:
        err_console.print(t("err_invalid_bed", bed=bed_spec))
        sys.exit(1)
    if not os.path.isdir(directory):
        err_console.print(t("err_not_a_directory", path=directory))
        sys.exit(1)

    if recursive:
        files = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    else:
        files = glob.glob(os.path.join(directory, pattern))
    files = sorted(f for f in files if os.path.isfile(f))
    if not files:
        err_console.print(t("err_no_files_matching", pattern=pattern, dir=directory))
        sys.exit(1)

    meshes = {}
    items = []
    for path in files:
        try:
            mesh = load_mesh(path)
        except PrintPrepError as exc:
            err_console.print(f"  skipping {os.path.basename(path)}: {exc}")
            continue
        name = os.path.basename(path)
        meshes[name] = mesh
        items.append((name, float(mesh.extents[0]), float(mesh.extents[1])))

    if not items:
        err_console.print(t("err_nothing_to_pack"))
        sys.exit(1)

    layout = pack_layout(items, bed_size=(bed_w, bed_d), padding=padding,
                         allow_rotate=rotate)
    os.makedirs(out_dir, exist_ok=True)

    table = Table(title="Bed-pack layout", title_style="bold cyan")
    table.add_column("Bed")
    table.add_column("Parts")
    table.add_column("Items", overflow="fold")
    for bi, bed in enumerate(layout.beds, start=1):
        names = ", ".join(p.item_id + (" (R)" if p.rotated else "") for p in bed.items)
        table.add_row(str(bi), str(len(bed.items)), names)
    console.print(table)
    console.print(
        f"\n[bold]{layout.bed_count}[/bold] bed(s) for {len(items)} part(s) "
        f"on {bed_w:.0f}×{bed_d:.0f} mm bed."
    )
    if layout.unplaced:
        console.print(
            f"[yellow]{len(layout.unplaced)} part(s) too large for the bed: "
            + ", ".join(u[0] for u in layout.unplaced) + "[/yellow]"
        )

    # Write one combined STL per bed: each part translated (and optionally rotated)
    # to its assigned position, with its base resting on z=0.
    layout_json = {"bed_size_mm": [bed_w, bed_d], "padding_mm": padding,
                   "beds": [], "unplaced": [u[0] for u in layout.unplaced]}
    for bi, bed in enumerate(layout.beds, start=1):
        parts = []
        for place in bed.items:
            src = meshes[place.item_id].copy()
            if place.rotated:
                R = trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1])
                src.apply_transform(R)
            mn = src.bounds[0]
            src.apply_translation([place.x - mn[0], place.y - mn[1], -mn[2]])
            parts.append(src)
        combined = trimesh.util.concatenate(parts) if len(parts) > 1 else parts[0]
        out_path = os.path.join(out_dir, f"packed_bed{bi}.stl")
        combined.export(out_path)
        console.print(f"  ✓ [cyan]{out_path}[/cyan]")
        layout_json["beds"].append({
            "bed": bi,
            "items": [
                {"name": p.item_id, "x": round(p.x, 3), "y": round(p.y, 3),
                 "w": round(p.width, 3), "d": round(p.depth, 3), "rotated": p.rotated}
                for p in bed.items
            ],
        })
    with open(os.path.join(out_dir, "layout.json"), "w", encoding="utf-8") as fh:
        _json.dump(layout_json, fh, indent=2)


@main.command(help=t("cmd_serve_help"))
@click.option("--host", default="127.0.0.1", show_default=True, help=t("opt_serve_host"))
@click.option("--port", default=8000, show_default=True, type=int, help=t("opt_serve_port"))
def serve(host, port):
    try:
        import uvicorn
    except ImportError:
        err_console.print(
            "Web interface needs extra packages. Install with:\n"
            "  pip install -e \".[web]\""
        )
        sys.exit(1)

    console.print(t("msg_web_running", url=f"[cyan]http://{host}:{port}[/cyan]"))
    uvicorn.run("printprep.web.app:app", host=host, port=port, log_level="info")


@main.command(name="app", help=t("cmd_app_help"))
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--width", default=1100, type=int, show_default=True)
@click.option("--height", default=820, type=int, show_default=True)
def app_cmd(host, port, width, height):
    try:
        import webview
        import uvicorn
    except ImportError:
        err_console.print(
            "Native window mode needs the [desktop] extra. Install with:\n"
            "  pip install -e \".[desktop]\""
        )
        sys.exit(1)

    import socket
    import threading
    import time

    # uvicorn runs in a daemon thread so closing the window kills everything.
    config = uvicorn.Config(
        "printprep.web.app:app", host=host, port=port,
        log_level="warning", access_log=False,
    )
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()

    # Wait until the port responds (or give up after a few seconds).
    deadline = time.time() + 8
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)

    webview.create_window("PrintPrep", f"http://{host}:{port}/",
                          width=width, height=height, resizable=True)
    webview.start()


if __name__ == "__main__":
    main()
