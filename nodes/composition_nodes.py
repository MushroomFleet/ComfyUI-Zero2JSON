"""
Zero2JSON Composition Nodes
Specialized nodes for generating FLUX2-JSON composition descriptions
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# COMPOSITION NODE
# ============================================================================

class Z2J_Composition(Zero2JSONBaseNode):
    """
    Generate composition rule descriptions for the composition field.

    Outputs text describing visual arrangement, rule of thirds,
    leading lines, framing, and compositional techniques.
    """

    PROFILE_PREFIX = "composition_"
    DEFAULT_PROFILE = "composition_default.json"
    NODE_DISPLAY_NAME = "Z2J Composition"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["composition_style"] = (
            ["any", "rule_of_thirds", "centered", "diagonal", "symmetrical", "dynamic", "minimal"],
            {"default": "any", "tooltip": "Filter by composition style"}
        )
        return base

    CATEGORY = "Zero2JSON/Composition"
    DESCRIPTION = "Generate composition descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_Composition": Z2J_Composition,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_Composition": "📐 Z2J Composition",
}
