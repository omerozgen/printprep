"""Bin-packing: arrange multiple STLs on a printer bed.

Uses First-Fit-Decreasing-Height (FFDH) shelf packing on the XY footprint of
each part. Items are placed left-to-right on horizontal shelves; a new shelf
opens when the current one is full vertically; a new bed opens when a part
doesn't fit on any shelf of any existing bed. Optional 90° rotation lets the
packer choose the better orientation per part.

This is the standard "good enough" heuristic — not optimal, but deterministic
and fast. For 3D printing it lines up parts the same way a slicer's auto-arrange
would, with a small inter-part gap for cooling/adhesion.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Placement:
    item_id: str
    x: float          # bottom-left X of the placed part on the bed
    y: float          # bottom-left Y
    width: float      # XY footprint width AFTER any rotation
    depth: float      # XY footprint depth AFTER any rotation
    rotated: bool     # True if rotated 90° about Z


@dataclass
class Shelf:
    y: float
    height: float
    cursor_x: float = 0.0
    items: List[Placement] = field(default_factory=list)


@dataclass
class Bed:
    width: float
    depth: float
    shelves: List[Shelf] = field(default_factory=list)
    items: List[Placement] = field(default_factory=list)

    def top_used(self) -> float:
        return max((s.y + s.height for s in self.shelves), default=0.0)


@dataclass
class PackResult:
    bed_size: Tuple[float, float]
    padding: float
    beds: List[Bed]
    unplaced: List[Tuple[str, float, float]] = field(default_factory=list)

    @property
    def bed_count(self) -> int:
        return len(self.beds)


def _fits(width: float, height: float, bed_w: float, bed_d: float) -> bool:
    return width <= bed_w + 1e-9 and height <= bed_d + 1e-9


def _orientations(w: float, d: float, allow_rotate: bool):
    """Yield (w, d, rotated) candidates, larger-side-first to favour the upright fit."""
    if allow_rotate and abs(w - d) > 1e-9:
        if w >= d:
            yield w, d, False
            yield d, w, True
        else:
            yield d, w, True
            yield w, d, False
    else:
        yield w, d, False


def _try_place(bed: Bed, item_id: str, w: float, d: float, padding: float,
               allow_rotate: bool) -> Optional[Placement]:
    """Try to place an item on existing shelves, or open a new one."""
    for orient_w, orient_d, rotated in _orientations(w, d, allow_rotate):
        ow = orient_w + padding
        od = orient_d + padding
        # Try every open shelf first.
        for shelf in bed.shelves:
            if od <= shelf.height + 1e-9 and shelf.cursor_x + ow <= bed.width + 1e-9:
                place = Placement(item_id, shelf.cursor_x, shelf.y, orient_w, orient_d, rotated)
                shelf.cursor_x += ow
                shelf.items.append(place)
                bed.items.append(place)
                return place
        # Open a new shelf above the topmost one.
        top = bed.top_used()
        if top + od <= bed.depth + 1e-9 and ow <= bed.width + 1e-9:
            shelf = Shelf(y=top, height=od, cursor_x=ow)
            place = Placement(item_id, 0.0, top, orient_w, orient_d, rotated)
            shelf.items.append(place)
            bed.shelves.append(shelf)
            bed.items.append(place)
            return place
    return None


def pack(items: List[Tuple[str, float, float]], bed_size: Tuple[float, float] = (420.0, 420.0),
         padding: float = 5.0, allow_rotate: bool = True) -> PackResult:
    """Pack 2D-footprint items into beds.

    `items` is a list of `(id, width_mm, depth_mm)`. Returns a PackResult with
    one or more Beds; each Placement gives bottom-left (x, y) on the bed.
    Items that don't fit on a fresh bed (too large) go into `unplaced`.
    """
    bed_w, bed_d = bed_size
    sorted_items = sorted(items, key=lambda t: -max(t[1], t[2]))
    beds: List[Bed] = []
    unplaced: List[Tuple[str, float, float]] = []

    for item_id, w, d in sorted_items:
        if not _fits(min(w, d) + padding, max(w, d) + padding, bed_w, bed_d):
            unplaced.append((item_id, w, d))
            continue

        placed = False
        for bed in beds:
            if _try_place(bed, item_id, w, d, padding, allow_rotate) is not None:
                placed = True
                break
        if not placed:
            new_bed = Bed(width=bed_w, depth=bed_d)
            if _try_place(new_bed, item_id, w, d, padding, allow_rotate) is not None:
                beds.append(new_bed)
            else:
                unplaced.append((item_id, w, d))

    return PackResult(bed_size=bed_size, padding=padding, beds=beds, unplaced=unplaced)
