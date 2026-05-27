"""Default thresholds and tunable constants for analysis and suggestions."""

# Analysis thresholds
OVERHANG_THRESHOLD_DEG = 45.0  # surfaces tilting more than this from vertical need support
MIN_WALL_MM = 1.2  # walls thinner than this are flagged
MAX_RAY_SAMPLES = 2000  # cap ray casts for thin-wall estimate (perf)
THIN_WALL_SEED = 0  # fixed RNG seed -> deterministic thin-wall estimate

# Hardware assumptions
NOZZLE_DIAMETER_MM = 0.4
LINE_WIDTH_MM = 0.42  # typical extrusion width at a 0.4mm nozzle

# Recommended print speed is derived from the material's max volumetric flow
# (speed = flow / (layer_height * line_width)), then clamped to a sane range.
MIN_PRINT_SPEED_MMS = 20
MAX_PRINT_SPEED_MMS = 150

# Slicer suggestion defaults
DEFAULT_LAYER_HEIGHT_MM = 0.2
DEFAULT_INFILL_PCT = 15
DEFAULT_WALL_COUNT = 2

# Brim heuristic: enable a brim when the model is tall & narrow (tip-over / adhesion risk)
BRIM_ASPECT_RATIO = 3.0  # height / min(footprint dimension)
BRIM_MIN_FOOTPRINT_MM = 20.0  # footprints smaller than this also get a brim
