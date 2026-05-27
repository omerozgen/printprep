from printprep.slicer.anycubic import AnycubicSlicer
from printprep.slicer.base import BaseSlicer, SlicerProfile
from printprep.slicer.creality import CrealitySlicer
from printprep.slicer.export_profile import EXPORT_FORMATS, export_profile
from printprep.slicer.profile_import import parse_material_profile

_SLICERS = {
    CrealitySlicer.name: CrealitySlicer,
    AnycubicSlicer.name: AnycubicSlicer,
}

SLICER_NAMES = tuple(_SLICERS)


def get_slicer(name: str) -> BaseSlicer:
    key = name.lower()
    if key not in _SLICERS:
        valid = ", ".join(SLICER_NAMES)
        raise KeyError(f"Unknown slicer '{name}'. Available: {valid}")
    return _SLICERS[key]()


__all__ = ["BaseSlicer", "SlicerProfile", "CrealitySlicer", "AnycubicSlicer",
           "get_slicer", "SLICER_NAMES", "parse_material_profile",
           "export_profile", "EXPORT_FORMATS"]
