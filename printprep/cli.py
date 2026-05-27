"""PrintPrep command-line interface."""

import os
import sys

import click
from rich.console import Console
from rich.table import Table

from printprep import PrintPrepError, __version__
from printprep.config.presets import MATERIAL_PRESETS
from printprep.core import analyze, load_mesh, repair_mesh, suggest_orientation
from printprep.slicer import (
    EXPORT_FORMATS,
    SLICER_NAMES,
    export_profile,
    get_slicer,
    parse_material_profile,
)

console = Console()
err_console = Console(stderr=True, style="bold red")


def _yn(value: bool) -> str:
    return "[green]Yes[/green]" if value else "[red]No[/red]"


@click.group(help="STL model analysis and slicer setting recommendations.")
@click.version_option(__version__, prog_name="printprep")
def main():
    pass


@main.command(name="analyze", help="Analyze a model and report geometry, problems and overhangs.")
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
    table.add_row(
        "Min wall (est.)",
        f"{result.min_wall_mm:.2f} mm" if result.min_wall_mm is not None else "n/a",
    )
    console.print(table)

    if result.issues:
        console.print("\n[bold yellow]Issues found:[/bold yellow]")
        for issue in result.issues:
            console.print(f"  [yellow]⚠[/yellow] {issue}")
    else:
        console.print("\n[bold green]No issues found — ready for slicing.[/bold green]")


@main.command(help="Repair common mesh problems and write a fixed STL.")
@click.argument("path", type=click.Path())
@click.option("--output", "-o", required=True, type=click.Path(),
              help="Where to write the repaired STL.")
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
        err_console.print(f"Could not write '{output}': {exc}")
        sys.exit(1)

    console.print("[bold]Applied fixes:[/bold]")
    console.print(f"  ✓ Merged {report.merged_vertices} duplicate vertices")
    console.print(f"  ✓ Removed {report.removed_degenerate} degenerate faces")
    console.print(f"  ✓ Removed {report.removed_duplicate} duplicate faces")
    console.print(f"  ✓ Holes filled: {report.holes_filled}")
    console.print(
        f"\nWatertight: {report.watertight_before} → {report.watertight_after}  |  "
        f"Volume: {report.volume_after / 1000:.2f} cm³"
    )
    console.print(f"Output: [cyan]{output}[/cyan]")
    if report.watertight_after:
        console.print("[bold green]Status: READY FOR SLICING[/bold green]")
    else:
        console.print("[bold yellow]Status: still not watertight — manual repair may be needed.[/bold yellow]")


@main.command(help="Suggest slicer settings as a JSON profile.")
@click.argument("path", type=click.Path())
@click.option("--slicer", type=click.Choice(SLICER_NAMES), default="creality",
              show_default=True, help="Target slicer.")
@click.option("--material", type=click.Choice(sorted(MATERIAL_PRESETS)), default="pla",
              show_default=True, help="Filament material (ignored if --import-profile is given).")
@click.option("--import-profile", "import_profile", type=click.Path(),
              help="Use a material profile exported from your slicer (.json/.ini/.fdm_material).")
@click.option("--export", "export_fmt", type=click.Choice(EXPORT_FORMATS),
              help="Write slicer-importable profile files instead of printing JSON.")
@click.option("--out-dir", "out_dir", type=click.Path(), default=".",
              show_default=True, help="Directory for --export output files.")
def suggest(path, slicer, material, import_profile, export_fmt, out_dir):
    try:
        mesh = load_mesh(path)
    except PrintPrepError as exc:
        err_console.print(str(exc))
        sys.exit(1)

    result = analyze(mesh, path=path)
    generator = get_slicer(slicer)
    if import_profile:
        try:
            with open(import_profile, encoding="utf-8") as fh:
                preset = parse_material_profile(fh.read(), import_profile)
        except (OSError, PrintPrepError) as exc:
            err_console.print(f"Profile import failed: {exc}")
            sys.exit(1)
        profile = generator.build_profile_from_preset(result, preset)
    else:
        profile = generator.build_profile(result, material)

    if export_fmt:
        files = export_profile(profile, export_fmt)
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


@main.command(help="Suggest the best print orientation and write a rotated STL.")
@click.argument("path", type=click.Path())
@click.option("--output", "-o", required=True, type=click.Path(),
              help="Where to write the re-oriented STL.")
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
        err_console.print(f"Could not write '{output}': {exc}")
        sys.exit(1)

    rx, ry, rz = report.euler_deg
    console.print("[bold]Orientation suggestion:[/bold]")
    console.print(f"  Rotation (XYZ euler): {rx}°, {ry}°, {rz}°")
    console.print(
        f"  Overhang area: {report.overhang_before * 100:.1f}% → {report.overhang_after * 100:.1f}%"
    )
    if report.improved:
        console.print("[bold green]Found a better orientation.[/bold green]")
    else:
        console.print("[yellow]Current orientation is already optimal — no rotation applied.[/yellow]")
    console.print(f"Output: [cyan]{output}[/cyan]")


@main.command(help="Launch the local web interface (browser UI).")
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind.")
@click.option("--port", default=8000, show_default=True, type=int, help="Port to bind.")
def serve(host, port):
    try:
        import uvicorn
    except ImportError:
        err_console.print(
            "Web interface needs extra packages. Install with:\n"
            "  pip install -e \".[web]\""
        )
        sys.exit(1)

    console.print(f"PrintPrep web UI → [cyan]http://{host}:{port}[/cyan]  (Ctrl+C to stop)")
    uvicorn.run("printprep.web.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
