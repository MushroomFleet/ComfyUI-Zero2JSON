"""
Zero2JSON Scene Nodes
Specialized nodes for generating FLUX2-JSON scene and environment components
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# SCENE NODE
# ============================================================================

class Z2J_Scene(Zero2JSONBaseNode):
    """
    Generate scene/environment descriptions for FLUX2_SceneBuilder.

    Outputs text suitable for the 'scene' field, including
    location, atmosphere, and environmental context.
    """

    PROFILE_PREFIX = "scene_"
    DEFAULT_PROFILE = "scene_default.json"
    NODE_DISPLAY_NAME = "Z2J Scene"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["scene_category"] = (
            ["any", "interior", "exterior", "studio", "natural", "urban", "fantasy", "scifi"],
            {"default": "any", "tooltip": "Filter by scene category"}
        )
        base["optional"]["time_hint"] = (
            ["any", "day", "night", "dawn", "dusk", "golden_hour", "blue_hour"],
            {"default": "any", "tooltip": "Time of day context hint"}
        )
        return base

    CATEGORY = "Zero2JSON/Scene"
    DESCRIPTION = "Generate scene descriptions using ZeroPrompt methodology"


# ============================================================================
# BACKGROUND NODE
# ============================================================================

class Z2J_Background(Zero2JSONBaseNode):
    """
    Generate background descriptions for the background field.

    Outputs text describing the backdrop, distant elements,
    and environmental details behind the main subjects.
    """

    PROFILE_PREFIX = "background_"
    DEFAULT_PROFILE = "background_default.json"
    NODE_DISPLAY_NAME = "Z2J Background"

    CATEGORY = "Zero2JSON/Scene"
    DESCRIPTION = "Generate background descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_Scene": Z2J_Scene,
    "Z2J_Background": Z2J_Background,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_Scene": "🌍 Z2J Scene",
    "Z2J_Background": "🖼️ Z2J Background",
}
