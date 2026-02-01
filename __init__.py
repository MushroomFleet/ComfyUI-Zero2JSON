"""
Zero2JSON - ZeroPrompt Integration for FLUX2-JSON
Position-as-seed procedural text generation for structured prompt building

This package provides shadow nodes that augment FLUX2-JSON inputs
with deterministic, profile-based procedural text generation.
"""

# Import all node modules
from .nodes.subject_nodes import (
    NODE_CLASS_MAPPINGS as SUBJECT_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as SUBJECT_DISPLAY_MAPPINGS,
)
from .nodes.scene_nodes import (
    NODE_CLASS_MAPPINGS as SCENE_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as SCENE_DISPLAY_MAPPINGS,
)
from .nodes.style_nodes import (
    NODE_CLASS_MAPPINGS as STYLE_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as STYLE_DISPLAY_MAPPINGS,
)
from .nodes.lighting_nodes import (
    NODE_CLASS_MAPPINGS as LIGHTING_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as LIGHTING_DISPLAY_MAPPINGS,
)
from .nodes.camera_nodes import (
    NODE_CLASS_MAPPINGS as CAMERA_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as CAMERA_DISPLAY_MAPPINGS,
)
from .nodes.composition_nodes import (
    NODE_CLASS_MAPPINGS as COMPOSITION_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as COMPOSITION_DISPLAY_MAPPINGS,
)
from .nodes.utility_nodes import (
    NODE_CLASS_MAPPINGS as UTILITY_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as UTILITY_DISPLAY_MAPPINGS,
)

# Merge all mappings
NODE_CLASS_MAPPINGS = {
    **SUBJECT_MAPPINGS,
    **SCENE_MAPPINGS,
    **STYLE_MAPPINGS,
    **LIGHTING_MAPPINGS,
    **CAMERA_MAPPINGS,
    **COMPOSITION_MAPPINGS,
    **UTILITY_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **SUBJECT_DISPLAY_MAPPINGS,
    **SCENE_DISPLAY_MAPPINGS,
    **STYLE_DISPLAY_MAPPINGS,
    **LIGHTING_DISPLAY_MAPPINGS,
    **CAMERA_DISPLAY_MAPPINGS,
    **COMPOSITION_DISPLAY_MAPPINGS,
    **UTILITY_DISPLAY_MAPPINGS,
}

# Package metadata
__version__ = "1.0.0"
__author__ = "Zero2JSON Team"
__description__ = "ZeroPrompt Integration for FLUX2-JSON - Procedural Prompt Generation"

# Exported symbols
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
