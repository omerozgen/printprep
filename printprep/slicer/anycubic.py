"""AnycubicSlicerNext profile generator."""

from printprep.slicer.base import BaseSlicer


class AnycubicSlicer(BaseSlicer):
    name = "anycubic"
    support_style = "tree_auto"
