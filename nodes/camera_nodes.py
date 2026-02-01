"""
Zero2JSON Camera Nodes
Specialized nodes for generating FLUX2-JSON camera component descriptions
"""

from .base import Zero2JSONBaseNode, discover_profiles

# ============================================================================
# CAMERA ANGLE NODE
# ============================================================================

class Z2J_CameraAngle(Zero2JSONBaseNode):
    """
    Generate camera angle descriptions for FLUX2_CameraRig.

    Outputs text suitable for the 'angle' field, describing
    camera positioning, tilt, and perspective.
    """

    PROFILE_PREFIX = "camera_angle_"
    DEFAULT_PROFILE = "camera_angle_default.json"
    NODE_DISPLAY_NAME = "Z2J Camera Angle"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["angle_type"] = (
            ["any", "eye_level", "high", "low", "birds_eye", "worms_eye", "dutch"],
            {"default": "any", "tooltip": "Filter by angle type"}
        )
        return base

    CATEGORY = "Zero2JSON/Camera"
    DESCRIPTION = "Generate camera angle descriptions using ZeroPrompt methodology"


# ============================================================================
# CAMERA DISTANCE NODE
# ============================================================================

class Z2J_CameraDistance(Zero2JSONBaseNode):
    """
    Generate camera distance/shot descriptions.

    Outputs text suitable for custom_distance field, describing
    shot framing and subject-to-camera relationship.
    """

    PROFILE_PREFIX = "camera_distance_"
    DEFAULT_PROFILE = "camera_distance_default.json"
    NODE_DISPLAY_NAME = "Z2J Camera Distance"

    CATEGORY = "Zero2JSON/Camera"
    DESCRIPTION = "Generate camera distance descriptions using ZeroPrompt methodology"


# ============================================================================
# CAMERA DEPTH OF FIELD NODE
# ============================================================================

class Z2J_CameraDoF(Zero2JSONBaseNode):
    """
    Generate depth of field descriptions for FLUX2_CameraRig.

    Outputs text suitable for the 'depth_of_field' field,
    describing focus planes, bokeh, and sharpness distribution.
    """

    PROFILE_PREFIX = "camera_dof_"
    DEFAULT_PROFILE = "camera_dof_default.json"
    NODE_DISPLAY_NAME = "Z2J Camera DoF"

    @classmethod
    def INPUT_TYPES(cls):
        base = super().INPUT_TYPES()
        base["optional"]["dof_style"] = (
            ["any", "shallow", "moderate", "deep", "bokeh_heavy", "everything_sharp"],
            {"default": "any", "tooltip": "Depth of field style hint"}
        )
        return base

    CATEGORY = "Zero2JSON/Camera"
    DESCRIPTION = "Generate depth of field descriptions using ZeroPrompt methodology"


# ============================================================================
# CAMERA FOCUS NODE
# ============================================================================

class Z2J_CameraFocus(Zero2JSONBaseNode):
    """
    Generate focus target descriptions for FLUX2_CameraRig.

    Outputs text suitable for the 'focus' field, describing
    what elements are sharp and where attention is drawn.
    """

    PROFILE_PREFIX = "camera_focus_"
    DEFAULT_PROFILE = "camera_focus_default.json"
    NODE_DISPLAY_NAME = "Z2J Camera Focus"

    CATEGORY = "Zero2JSON/Camera"
    DESCRIPTION = "Generate focus descriptions using ZeroPrompt methodology"


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_CameraAngle": Z2J_CameraAngle,
    "Z2J_CameraDistance": Z2J_CameraDistance,
    "Z2J_CameraDoF": Z2J_CameraDoF,
    "Z2J_CameraFocus": Z2J_CameraFocus,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_CameraAngle": "📐 Z2J Camera Angle",
    "Z2J_CameraDistance": "📏 Z2J Camera Distance",
    "Z2J_CameraDoF": "🔍 Z2J Camera DoF",
    "Z2J_CameraFocus": "🎯 Z2J Camera Focus",
}
