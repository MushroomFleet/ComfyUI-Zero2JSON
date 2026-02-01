"""
Zero2JSON Lighting Nodes
Specialized nodes for generating FLUX2-JSON lighting descriptions
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# LIGHTING NODE
# ============================================================================

class Z2J_Lighting(Zero2JSONBaseNode):
    """
    Generate lighting setup descriptions for the lighting field.

    Outputs text describing light sources, quality, direction,
    color temperature, and overall illumination setup.
    """

    PROFILE_PREFIX = "lighting_"
    DEFAULT_PROFILE = "lighting_default.json"
    NODE_DISPLAY_NAME = "Z2J Lighting"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["lighting_type"] = (
            ["any", "natural", "studio", "dramatic", "ambient", "neon", "candlelight"],
            {"default": "any", "tooltip": "Filter by lighting type"}
        )
        base["optional"]["lighting_mood"] = (
            ["any", "bright", "dark", "moody", "soft", "harsh", "romantic"],
            {"default": "any", "tooltip": "Lighting mood hint"}
        )
        return base

    CATEGORY = "Zero2JSON/Lighting"
    DESCRIPTION = "Generate lighting descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_Lighting": Z2J_Lighting,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_Lighting": "💡 Z2J Lighting",
}
