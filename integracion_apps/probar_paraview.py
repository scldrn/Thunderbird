"""Read a computed OpenFOAM benchmark and save a reproducible ParaView scene.

Run with the installed application's pvpython, outside the macOS sandbox.
This checks integration, not the aerodynamics of the vehicle.
"""
from pathlib import Path
import json

from paraview.simple import (
    OpenFOAMReader, GetAnimationScene, GetActiveViewOrCreate, Show,
    ColorBy, GetColorTransferFunction, GetScalarBar, Text, Render,
    SaveScreenshot, SaveState, GetParaViewVersion,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "paraview"
OUT.mkdir(exist_ok=True)
CASE = ROOT / "ejecucion/G0/poiseuille_80_outer50_dt_half"
marker = CASE / "benchmark.foam"
marker.touch()
reader = OpenFOAMReader(FileName=str(marker))
reader.MeshRegions = ["internalMesh"]
reader.CellArrays = ["U", "p"]
reader.UpdatePipelineInformation()
times = list(reader.TimestepValues)
assert times and abs(times[-1] - 4.0) < 1e-10, times
scene = GetAnimationScene()
scene.UpdateAnimationUsingDataTimeSteps()
scene.AnimationTime = 4.0
reader.UpdatePipeline(4.0)
info = reader.GetDataInformation()
cells = info.GetNumberOfCells()
assert cells == 80, cells
velocity_range = reader.CellData["U"].GetRange(-1)
assert 0 < velocity_range[0] < velocity_range[1] < 25, velocity_range

view = GetActiveViewOrCreate("RenderView")
view.ViewSize = [1600, 1000]
view.UseColorPaletteForBackground = 0
view.Background = [0.035, 0.045, 0.065]
display = Show(reader, view)
display.Representation = "Surface With Edges"
display.EdgeColor = [0.15, 0.17, 0.20]
ColorBy(display, ("CELLS", "U", "Magnitude"))
lut = GetColorTransferFunction("U")
lut.RescaleTransferFunction(0, velocity_range[1])
display.SetScalarBarVisibility(view, True)
bar = GetScalarBar(lut, view)
bar.Title = "|U|"
bar.ComponentTitle = "m/s"
bar.TitleColor = [0.92, 0.94, 0.96]
bar.LabelColor = [0.92, 0.94, 0.96]

view.CameraPosition = [0, 0.5, 3]
view.CameraFocalPoint = [0, 0.5, 0]
view.CameraViewUp = [0, 1, 0]
view.CameraParallelProjection = 1
view.CameraParallelScale = 0.63
title = Text()
title.Text = "PARAVIEW 6.2 | OpenFOAM 13\nPoiseuille transient - 80 cells - t = 4 s"
text_display = Show(title, view)
text_display.FontSize = 18
text_display.Color = [0.92, 0.94, 0.96]
text_display.WindowLocation = "Upper Left Corner"
note = Text()
note.Text = "INTEGRATION TEST / ANALYTIC BENCHMARK\nNot a vehicle flight simulation"
note_display = Show(note, view)
note_display.FontSize = 15
note_display.Color = [0.75, 0.80, 0.85]
note_display.WindowLocation = "Lower Left Corner"
Render(view)
SaveScreenshot(str(OUT / "prueba_cfd.png"), view, ImageResolution=[1600, 1000])
SaveState(str(OUT / "benchmark_poiseuille.pvsm"))
report = {
    "paraview_version": str(GetParaViewVersion()),
    "case": str(CASE), "time_s": 4.0, "cells": cells,
    "velocity_magnitude_range_m_s": list(velocity_range),
    "reader": "OpenFOAMReader", "read_test": "passed",
    "screenshot": str(OUT / "prueba_cfd.png"),
    "state": str(OUT / "benchmark_poiseuille.pvsm"),
    "physical_vehicle_validation": False,
}
(OUT / "PRUEBA.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
