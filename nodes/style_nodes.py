"""
Zero2JSON Style Nodes
Specialized nodes for generating FLUX2-JSON style and mood components
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# STYLE NODE
# ============================================================================

class Z2J_Style(Zero2JSONBaseNode):
    """
    Generate artistic style descriptions for FLUX2_StyleSelector.

    Outputs text suitable for the 'style' field, including
    artistic medium, aesthetic approach, and rendering style.
    """

    PROFILE_PREFIX = "style_"
    DEFAULT_PROFILE = "style_default.json"
    NODE_DISPLAY_NAME = "Z2J Style"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["style_category"] = (
            ["any", "photorealistic", "artistic", "cinematic", "anime", "illustration", "vintage"],
            {"default": "any", "tooltip": "Filter by style category"}
        )
        return base

    CATEGORY = "Zero2JSON/Style"
    DESCRIPTION = "Generate style descriptions using ZeroPrompt methodology"


# ============================================================================
# MOOD NODE
# ============================================================================

class Z2J_Mood(Zero2JSONBaseNode):
    """
    Generate mood/atmosphere descriptions for the mood field.

    Outputs text describing emotional tone, atmosphere,
    and psychological feeling of the image.
    """

    PROFILE_PREFIX = "mood_"
    DEFAULT_PROFILE = "mood_default.json"
    NODE_DISPLAY_NAME = "Z2J Mood"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["mood_valence"] = (
            ["any", "positive", "negative", "neutral", "tense", "peaceful"],
            {"default": "any", "tooltip": "Emotional valence hint"}
        )
        return base

    CATEGORY = "Zero2JSON/Style"
    DESCRIPTION = "Generate mood descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_Style": Z2J_Style,
    "Z2J_Mood": Z2J_Mood,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_Style": "🎨 Z2J Style",
    "Z2J_Mood": "😊 Z2J Mood",
}
