"""
Zero2JSON Subject Nodes
Specialized nodes for generating FLUX2-JSON subject components
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# SUBJECT DESCRIPTION NODE
# ============================================================================

class Z2J_SubjectDescription(Zero2JSONBaseNode):
    """
    Generate detailed subject descriptions for FLUX2_SubjectCreator.

    Outputs text suitable for the 'description' field of subjects,
    including physical characteristics, materials, textures, and details.
    """

    PROFILE_PREFIX = "subject_description_"
    DEFAULT_PROFILE = "subject_description_default.json"
    NODE_DISPLAY_NAME = "Z2J Subject Description"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        # Add subject-specific inputs
        base["optional"]["subject_type"] = (
            ["any", "person", "character", "object", "creature", "vehicle", "architecture"],
            {"default": "any", "tooltip": "Filter generation by subject type"}
        )
        return base

    CATEGORY = "Zero2JSON/Subject"
    DESCRIPTION = "Generate detailed subject descriptions using ZeroPrompt methodology"


# ============================================================================
# SUBJECT POSITION NODE
# ============================================================================

class Z2J_SubjectPosition(Zero2JSONBaseNode):
    """
    Generate spatial positioning descriptions for subjects.

    Outputs text suitable for the 'position' field, combining
    horizontal, vertical, and depth positioning.
    """

    PROFILE_PREFIX = "subject_position_"
    DEFAULT_PROFILE = "subject_position_default.json"
    NODE_DISPLAY_NAME = "Z2J Subject Position"

    CATEGORY = "Zero2JSON/Subject"
    DESCRIPTION = "Generate subject position descriptions using ZeroPrompt methodology"


# ============================================================================
# SUBJECT ACTION NODE
# ============================================================================

class Z2J_SubjectAction(Zero2JSONBaseNode):
    """
    Generate dynamic action descriptions for subjects.

    Outputs text suitable for the 'action' field, describing
    movement, activity, and dynamic states.
    """

    PROFILE_PREFIX = "subject_action_"
    DEFAULT_PROFILE = "subject_action_default.json"
    NODE_DISPLAY_NAME = "Z2J Subject Action"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["action_intensity"] = (
            ["any", "subtle", "moderate", "dynamic", "extreme"],
            {"default": "any", "tooltip": "Control action intensity level"}
        )
        return base

    CATEGORY = "Zero2JSON/Subject"
    DESCRIPTION = "Generate subject action descriptions using ZeroPrompt methodology"


# ============================================================================
# SUBJECT POSE NODE
# ============================================================================

class Z2J_SubjectPose(Zero2JSONBaseNode):
    """
    Generate static pose descriptions for subjects.

    Outputs text suitable for the 'pose' field, describing
    body position, stance, and static configurations.
    """

    PROFILE_PREFIX = "subject_pose_"
    DEFAULT_PROFILE = "subject_pose_default.json"
    NODE_DISPLAY_NAME = "Z2J Subject Pose"

    CATEGORY = "Zero2JSON/Subject"
    DESCRIPTION = "Generate subject pose descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_SubjectDescription": Z2J_SubjectDescription,
    "Z2J_SubjectPosition": Z2J_SubjectPosition,
    "Z2J_SubjectAction": Z2J_SubjectAction,
    "Z2J_SubjectPose": Z2J_SubjectPose,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_SubjectDescription": "🎯 Z2J Subject Description",
    "Z2J_SubjectPosition": "📍 Z2J Subject Position",
    "Z2J_SubjectAction": "🏃 Z2J Subject Action",
    "Z2J_SubjectPose": "🧘 Z2J Subject Pose",
}
