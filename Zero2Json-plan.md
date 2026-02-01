# Zero2JSON Implementation Plan

## TINS (The Implementation Navigator System)

---

## Executive Summary

Zero2JSON is a symbiotic integration layer that augments the ComfyUI-FLUX2-JSON system with ZeroPrompt's position-as-seed procedural text generation. Each FLUX2-JSON input field receives a parallel ZeroPrompt node designed to generate contextually appropriate text using dedicated JSON profiles.

**Core Philosophy:** Not replace, but augment and extend - providing unparalleled precision in multi-dimensional orchestration of procedural prompt inputs with guardrails in the form of user curation.

---

## Part 1: Architecture Overview

### 1.1 System Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ZERO2JSON SHADOW NODES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ Z2J_Subject      │    │ Z2J_Subject      │    │ Z2J_Scene        │      │
│  │ (zeroprompt)     │    │ (zeroprompt)     │    │ (zeroprompt)     │      │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘      │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │ FLUX2_Subject    │    │ FLUX2_Subject    │    │ FLUX2_Scene      │      │
│  │ Creator          │    │ Creator          │    │ Builder          │      │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘      │
│           │                       │                       │                 │
└───────────┼───────────────────────┼───────────────────────┼─────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │   FLUX2_Subject     │
                         │      Array          │
                         └──────────┬──────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
┌───────────┼───────────────────────┼───────────────────────┼───────────────┐
│           ▼                       ▼                       ▼               │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    │
│  │ Z2J_Style        │    │ Z2J_Lighting     │    │ Z2J_Camera       │    │
│  │ (zeroprompt)     │    │ (zeroprompt)     │    │ (zeroprompt)     │    │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    │
│           │                       │                       │               │
│           ▼                       ▼                       ▼               │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    │
│  │ FLUX2_Style      │    │   (STRING)       │    │ FLUX2_Camera     │    │
│  │ Selector         │    │   lighting       │    │     Rig          │    │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    │
│           │                       │                       │               │
└───────────┼───────────────────────┼───────────────────────┼───────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  FLUX2_Prompt       │
                         │    Assembler        │
                         │   (Final JSON)      │
                         └─────────────────────┘
```

### 1.2 Node Mapping

| FLUX2-JSON Field | Zero2JSON Shadow Node | Profile JSON |
|------------------|----------------------|--------------|
| subject.description | Z2J_SubjectDescription | `subject_description.json` |
| subject.position | Z2J_SubjectPosition | `subject_position.json` |
| subject.action | Z2J_SubjectAction | `subject_action.json` |
| subject.pose | Z2J_SubjectPose | `subject_pose.json` |
| scene | Z2J_Scene | `scene.json` |
| style | Z2J_Style | `style.json` |
| lighting | Z2J_Lighting | `lighting.json` |
| mood | Z2J_Mood | `mood.json` |
| background | Z2J_Background | `background.json` |
| composition | Z2J_Composition | `composition.json` |
| camera.angle | Z2J_CameraAngle | `camera_angle.json` |
| camera.distance | Z2J_CameraDistance | `camera_distance.json` |
| camera.depth_of_field | Z2J_CameraDoF | `camera_dof.json` |
| camera.focus | Z2J_CameraFocus | `camera_focus.json` |

---

## Part 2: Core Implementation

### 2.1 Base Classes

#### File: `nodes/base.py`

```python
"""
Zero2JSON Base Classes
Position-as-seed procedural text generation for FLUX2-JSON integration
"""

import json
import struct
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import xxhash

# ============================================================================
# CONSTANTS
# ============================================================================

PROFILES_DIR = Path(__file__).parent.parent / "profiles"

# ============================================================================
# CORE HASH FUNCTIONS (Position-as-Seed Methodology)
# ============================================================================

def prompt_hash(seed: int, *coords: int) -> int:
    """
    Pure O(1) hash from seed + arbitrary coordinate tuple.
    Uses xxhash32 for speed and cross-platform determinism.

    The coordinate system allows infinite unique hashes:
    - seed: World seed (global randomization)
    - coords: Position coordinates (prompt_idx, component_idx, etc.)

    Returns: Deterministic 32-bit integer
    """
    h = xxhash.xxh32(seed=seed & 0xFFFFFFFF)
    h.update(struct.pack('<' + 'i' * len(coords), *coords))
    return h.intdigest()


def hash_to_index(h: int, pool_size: int) -> int:
    """Map hash to valid index in any pool."""
    return h % pool_size


# ============================================================================
# PROFILE MANAGEMENT
# ============================================================================

def get_profiles_dir() -> Path:
    """Get the profiles directory path, creating if needed."""
    if not PROFILES_DIR.exists():
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    return PROFILES_DIR


def discover_profiles(prefix: str = "") -> List[str]:
    """
    Discover all available JSON profiles, optionally filtered by prefix.

    Args:
        prefix: Optional prefix to filter profiles (e.g., "subject_")

    Returns:
        List of profile filenames (without path)
    """
    profiles_dir = get_profiles_dir()

    if not profiles_dir.exists():
        return ["default.json"]

    pattern = f"{prefix}*.json" if prefix else "*.json"
    profiles = sorted([
        f.name for f in profiles_dir.glob(pattern)
        if f.is_file()
    ])

    # Ensure default is first if it exists and matches prefix
    default_name = f"{prefix}default.json" if prefix else "default.json"
    if default_name in profiles:
        profiles.remove(default_name)
        profiles.insert(0, default_name)

    return profiles if profiles else ["default.json"]


def load_profile(profile_name: str) -> Dict:
    """
    Load and validate a JSON profile.

    Args:
        profile_name: Filename of the profile (e.g., "subject_description.json")

    Returns:
        Validated profile dictionary

    Raises:
        FileNotFoundError: If profile doesn't exist
        ValueError: If profile is missing required fields
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / profile_name

    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_name}")

    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)

    # Validate required fields
    if 'templates' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'templates' field")
    if 'pools' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'pools' field")

    return profile


def calculate_combinations(profile: Dict) -> int:
    """Calculate total unique combinations for a profile."""
    total = len(profile.get('templates', []))
    for pool in profile.get('pools', {}).values():
        total *= len(pool)
    return total


# ============================================================================
# PROMPT GENERATION
# ============================================================================

def generate_prompt(seed: int, prompt_idx: int, profile: Dict) -> str:
    """
    Generate a deterministic prompt from seed + index using profile vocabulary.

    Algorithm:
    1. Select template using coordinate 0
    2. For each pool (i), select component using coordinate i+1
    3. Format template with selected components

    Args:
        seed: World seed for global randomization
        prompt_idx: Position in infinite prompt space
        profile: Loaded profile dictionary with templates and pools

    Returns:
        Generated prompt string
    """
    templates = profile['templates']
    pools = profile['pools']

    # Step 1: Select template
    template_hash = prompt_hash(seed, prompt_idx, 0)
    template = templates[hash_to_index(template_hash, len(templates))]

    # Step 2: Generate each component
    components = {}
    for i, (key, pool) in enumerate(pools.items()):
        component_hash = prompt_hash(seed, prompt_idx, i + 1)
        components[key] = pool[hash_to_index(component_hash, len(pool))]

    # Step 3: Format template with components
    try:
        return template.format(**components)
    except KeyError:
        # Graceful fallback if template references non-existent pool
        for key in pools.keys():
            template = template.replace(f"{{{key}}}", components.get(key, f"[{key}]"))
        return template


# ============================================================================
# BASE NODE CLASS
# ============================================================================

class Zero2JSONBaseNode:
    """
    Base class for all Zero2JSON nodes.
    Provides common functionality for profile-based zeroprompt generation.
    """

    # Class-level profile cache
    _profile_cache: Dict[str, Dict] = {}

    # Node metadata (override in subclasses)
    PROFILE_PREFIX = ""  # e.g., "subject_", "camera_"
    DEFAULT_PROFILE = "default.json"
    NODE_DISPLAY_NAME = "Zero2JSON Base"

    @classmethod
    def INPUT_TYPES(cls):
        """Define input types for ComfyUI."""
        profiles = discover_profiles(cls.PROFILE_PREFIX)

        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "World seed for deterministic generation"
                }),
                "prompt_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "Position in infinite prompt space"
                }),
            },
            "optional": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else cls.DEFAULT_PROFILE,
                    "tooltip": "Select vocabulary profile"
                }),
                "prefix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to prepend to generated prompt"
                }),
                "suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to append to generated prompt"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = "Zero2JSON"

    def generate(
        self,
        seed: int,
        prompt_index: int,
        profile: str = None,
        prefix: str = "",
        suffix: str = ""
    ) -> Tuple[str]:
        """
        Generate procedural text using position-as-seed methodology.

        Args:
            seed: World seed
            prompt_index: Position in prompt space
            profile: Profile filename to use
            prefix: Optional prefix text
            suffix: Optional suffix text

        Returns:
            Tuple containing generated text string
        """
        # Use default profile if none specified
        if profile is None:
            profile = self.DEFAULT_PROFILE

        # Load profile (with caching)
        if profile not in self._profile_cache:
            try:
                self._profile_cache[profile] = load_profile(profile)
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                return (f"[Error loading profile '{profile}': {str(e)}]",)

        profile_data = self._profile_cache[profile]

        # Generate prompt
        prompt = generate_prompt(seed, prompt_index, profile_data)

        # Apply prefix/suffix
        if prefix or suffix:
            prompt = f"{prefix}{prompt}{suffix}"

        return (prompt,)

    @classmethod
    def IS_CHANGED(cls, seed: int, prompt_index: int, profile: str = None,
                   prefix: str = "", suffix: str = ""):
        """Ensure node updates when inputs change."""
        profile_str = profile or cls.DEFAULT_PROFILE
        profile_hash = xxhash.xxh32(profile_str.encode()).intdigest()
        return prompt_hash(seed ^ profile_hash, prompt_index, 0)
```

### 2.2 Specialized Node Implementations

#### File: `nodes/subject_nodes.py`

```python
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
```

#### File: `nodes/scene_nodes.py`

```python
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
```

#### File: `nodes/style_nodes.py`

```python
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
```

#### File: `nodes/lighting_nodes.py`

```python
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
```

#### File: `nodes/camera_nodes.py`

```python
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
```

#### File: `nodes/composition_nodes.py`

```python
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
```

#### File: `nodes/utility_nodes.py`

```python
"""
Zero2JSON Utility Nodes
Profile information and management utilities
"""

from typing import Tuple
from .base import (
    Zero2JSONBaseNode,
    discover_profiles,
    load_profile,
    calculate_combinations,
    get_profiles_dir,
    prompt_hash
)
import xxhash

# ============================================================================
# PROFILE INFO NODE
# ============================================================================

class Z2J_ProfileInfo(Zero2JSONBaseNode):
    """
    Display statistics and information about a Zero2JSON profile.

    Useful for debugging and understanding profile capabilities.
    """

    NODE_DISPLAY_NAME = "Z2J Profile Info"

    @classmethod
    def INPUT_TYPES(cls):
        profiles = discover_profiles()
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default.json",
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("info", "total_combinations")
    FUNCTION = "get_info"
    CATEGORY = "Zero2JSON/Utility"
    DESCRIPTION = "Display profile statistics and information"

    def get_info(self, profile: str) -> Tuple[str, int]:
        """Get profile information as formatted string."""
        try:
            profile_data = load_profile(profile)
        except Exception as e:
            return (f"Error loading profile: {e}", 0)

        lines = [
            f"Profile: {profile_data.get('name', profile)}",
            f"Description: {profile_data.get('description', 'N/A')}",
            f"Version: {profile_data.get('version', 'N/A')}",
            "",
            "Pool Sizes:",
        ]

        for pool_name, pool_items in profile_data.get('pools', {}).items():
            lines.append(f"  {pool_name}: {len(pool_items)} entries")

        lines.append(f"  templates: {len(profile_data.get('templates', []))} variations")
        lines.append("")

        total = calculate_combinations(profile_data)
        lines.append(f"Total unique prompts: {total:,}")
        lines.append(f"Scientific notation: {total:.2e}")

        return ("\n".join(lines), total)

    @classmethod
    def IS_CHANGED(cls, profile: str):
        """Check if profile file has changed."""
        profile_path = get_profiles_dir() / profile
        if profile_path.exists():
            return profile_path.stat().st_mtime
        return 0


# ============================================================================
# BATCH GENERATOR NODE
# ============================================================================

class Z2J_BatchGenerator(Zero2JSONBaseNode):
    """
    Generate multiple prompts in sequence for batch processing.

    Useful for creating variations or exploring prompt space.
    """

    NODE_DISPLAY_NAME = "Z2J Batch Generator"

    @classmethod
    def INPUT_TYPES(cls):
        profiles = discover_profiles()
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
                "count": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Number of prompts to generate"
                }),
            },
            "optional": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default.json",
                }),
                "separator": ("STRING", {
                    "default": "\n---\n",
                    "multiline": False,
                    "tooltip": "Separator between prompts"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("batch_text", "prompts_list")
    FUNCTION = "generate_batch"
    CATEGORY = "Zero2JSON/Utility"
    DESCRIPTION = "Generate multiple prompts in sequence"

    def generate_batch(
        self,
        seed: int,
        start_index: int,
        count: int,
        profile: str = "default.json",
        separator: str = "\n---\n"
    ) -> Tuple[str, str]:
        """Generate multiple prompts."""
        from .base import generate_prompt, load_profile

        try:
            profile_data = load_profile(profile)
        except Exception as e:
            return (f"Error: {e}", "[]")

        prompts = []
        for i in range(count):
            prompt = generate_prompt(seed, start_index + i, profile_data)
            prompts.append(prompt)

        batch_text = separator.join(prompts)
        prompts_list = "\n".join([f"[{i}] {p}" for i, p in enumerate(prompts)])

        return (batch_text, prompts_list)

    @classmethod
    def IS_CHANGED(cls, seed: int, start_index: int, count: int,
                   profile: str = "default.json", separator: str = "\n---\n"):
        profile_hash = xxhash.xxh32(profile.encode()).intdigest()
        return prompt_hash(seed ^ profile_hash, start_index, count)


# ============================================================================
# SEED MIXER NODE
# ============================================================================

class Z2J_SeedMixer(Zero2JSONBaseNode):
    """
    Combine multiple seeds into a single deterministic seed.

    Useful for creating compound seeds from multiple sources.
    """

    NODE_DISPLAY_NAME = "Z2J Seed Mixer"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed_1": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
            },
            "optional": {
                "seed_2": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
                "seed_3": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
                "seed_4": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                }),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("mixed_seed",)
    FUNCTION = "mix_seeds"
    CATEGORY = "Zero2JSON/Utility"
    DESCRIPTION = "Combine multiple seeds into one"

    def mix_seeds(
        self,
        seed_1: int,
        seed_2: int = 0,
        seed_3: int = 0,
        seed_4: int = 0
    ) -> Tuple[int]:
        """Mix seeds using xxhash."""
        h = xxhash.xxh32()
        h.update(seed_1.to_bytes(4, 'little'))
        h.update(seed_2.to_bytes(4, 'little'))
        h.update(seed_3.to_bytes(4, 'little'))
        h.update(seed_4.to_bytes(4, 'little'))
        return (h.intdigest(),)

    @classmethod
    def IS_CHANGED(cls, seed_1: int, seed_2: int = 0, seed_3: int = 0, seed_4: int = 0):
        h = xxhash.xxh32()
        h.update(seed_1.to_bytes(4, 'little'))
        h.update(seed_2.to_bytes(4, 'little'))
        return h.intdigest()


# ============================================================================
# NODE REGISTRATION
# ============================================================================

NODE_CLASS_MAPPINGS = {
    "Z2J_ProfileInfo": Z2J_ProfileInfo,
    "Z2J_BatchGenerator": Z2J_BatchGenerator,
    "Z2J_SeedMixer": Z2J_SeedMixer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Z2J_ProfileInfo": "ℹ️ Z2J Profile Info",
    "Z2J_BatchGenerator": "📦 Z2J Batch Generator",
    "Z2J_SeedMixer": "🔀 Z2J Seed Mixer",
}
```

### 2.3 Main Registration File

#### File: `__init__.py`

```python
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
```

---

## Part 3: Profile JSON Specifications

### 3.1 Profile Schema

All profiles follow this structure:

```json
{
  "name": "Profile Display Name",
  "description": "Human-readable description of profile purpose",
  "version": "1.0.0",

  "templates": [
    "Template strings with {pool_name} placeholders",
    "Multiple templates provide variation"
  ],

  "pools": {
    "pool_name_1": ["item1", "item2", "item3"],
    "pool_name_2": ["item1", "item2", "item3"]
  }
}
```

### 3.2 Profile Implementations

#### File: `profiles/subject_description_default.json`

```json
{
  "name": "Subject Description Default",
  "description": "Comprehensive subject descriptions for photography and illustration",
  "version": "1.0.0",

  "templates": [
    "{subject_type} with {detail_1}, {detail_2}, {texture}",
    "{adjective} {subject_type}, {detail_1} and {detail_2}, {texture}",
    "{subject_type} featuring {detail_1}, {texture}, {quality}",
    "{adjective} {subject_type} with {texture} and {detail_2}",
    "{subject_type}, {detail_1}, {detail_2}, with {texture} {quality}"
  ],

  "pools": {
    "subject_type": [
      "a young woman", "a middle-aged man", "an elderly person",
      "a child", "a teenager", "a professional",
      "a ceramic vase", "a wooden sculpture", "a glass bottle",
      "a leather bag", "a metal watch", "a vintage camera",
      "a sports car", "a motorcycle", "a bicycle",
      "a majestic dragon", "a phoenix", "a mystical creature",
      "a robot", "an android", "a cyborg",
      "a medieval knight", "a samurai warrior", "a viking",
      "a detective", "an astronaut", "a scientist"
    ],
    "adjective": [
      "elegant", "rugged", "minimalist", "ornate", "weathered",
      "pristine", "vintage", "modern", "classic", "futuristic",
      "delicate", "robust", "sleek", "textured", "polished"
    ],
    "detail_1": [
      "intricate patterns", "fine craftsmanship", "subtle imperfections",
      "visible wear marks", "polished surfaces", "matte finish",
      "hand-painted details", "laser-etched markings", "natural grain",
      "geometric shapes", "organic curves", "sharp edges"
    ],
    "detail_2": [
      "reflective highlights", "soft shadows", "color gradients",
      "metallic accents", "wooden inlays", "fabric textures",
      "leather stitching", "glass elements", "stone components",
      "chrome details", "brass fixtures", "copper patina"
    ],
    "texture": [
      "smooth matte surface", "rough natural texture", "glossy finish",
      "brushed metal appearance", "soft fabric feel", "worn leather look",
      "polished stone surface", "frosted glass effect", "velvet softness",
      "gritty sandpaper texture", "silk-like smoothness", "coarse weave"
    ],
    "quality": [
      "exceptional detail", "museum quality", "artisan crafted",
      "mass-produced precision", "handmade character", "industrial finish",
      "boutique quality", "professional grade", "studio quality"
    ]
  }
}
```

#### File: `profiles/subject_position_default.json`

```json
{
  "name": "Subject Position Default",
  "description": "Spatial positioning descriptions for subject placement",
  "version": "1.0.0",

  "templates": [
    "{horizontal} of frame, {vertical}, {depth}",
    "positioned {horizontal}, {vertical} section, in the {depth}",
    "{depth}, {horizontal}, {vertical}",
    "{vertical}, {horizontal}, occupying the {depth}"
  ],

  "pools": {
    "horizontal": [
      "far left", "left side", "left of center",
      "center", "dead center", "centered",
      "right of center", "right side", "far right",
      "off-center left", "off-center right", "slightly left",
      "slightly right", "extreme left edge", "extreme right edge"
    ],
    "vertical": [
      "top", "upper third", "upper section",
      "middle", "center vertical", "eye level",
      "lower third", "bottom section", "bottom",
      "above center", "below center", "ground level"
    ],
    "depth": [
      "foreground", "immediate foreground", "front plane",
      "midground", "middle distance", "central plane",
      "background", "distant background", "far plane",
      "between foreground and midground", "between midground and background"
    ]
  }
}
```

#### File: `profiles/subject_action_default.json`

```json
{
  "name": "Subject Action Default",
  "description": "Dynamic action descriptions for subjects in motion",
  "version": "1.0.0",

  "templates": [
    "{verb} {direction}, {modifier}",
    "{modifier} {verb} {direction}",
    "{verb} with {quality}, {direction}",
    "{direction}, {verb} {modifier}"
  ],

  "pools": {
    "verb": [
      "walking", "running", "sprinting", "jogging",
      "standing", "sitting", "crouching", "kneeling",
      "jumping", "leaping", "falling", "diving",
      "reaching", "grasping", "pointing", "gesturing",
      "turning", "spinning", "twisting", "pivoting",
      "climbing", "descending", "ascending", "floating"
    ],
    "direction": [
      "toward the camera", "away from the camera",
      "to the left", "to the right",
      "upward", "downward", "diagonally",
      "across the frame", "through the scene",
      "into the light", "into shadow"
    ],
    "modifier": [
      "with purpose", "hesitantly", "confidently",
      "gracefully", "awkwardly", "smoothly",
      "rapidly", "slowly", "deliberately",
      "casually", "intensely", "playfully"
    ],
    "quality": [
      "fluid motion", "sharp movement", "gentle pace",
      "explosive energy", "controlled power", "relaxed ease",
      "urgent speed", "measured steps", "natural rhythm"
    ]
  }
}
```

#### File: `profiles/subject_pose_default.json`

```json
{
  "name": "Subject Pose Default",
  "description": "Static pose descriptions for subject positioning",
  "version": "1.0.0",

  "templates": [
    "{body_position}, {arm_position}, {expression}",
    "{body_position} with {arm_position}, {head_position}",
    "{expression}, {body_position}, {arm_position}",
    "{head_position}, {body_position}, {expression}"
  ],

  "pools": {
    "body_position": [
      "standing upright", "standing relaxed", "standing at attention",
      "sitting comfortably", "sitting formally", "sitting casually",
      "leaning against wall", "leaning forward", "leaning back",
      "crouching low", "kneeling down", "lying prone"
    ],
    "arm_position": [
      "arms at sides", "arms crossed", "arms behind back",
      "one hand on hip", "hands in pockets", "arms outstretched",
      "hands clasped", "arms raised", "one arm extended",
      "hands folded", "arms akimbo", "hands together"
    ],
    "head_position": [
      "head tilted slightly", "chin raised", "chin lowered",
      "looking straight ahead", "profile view", "three-quarter view",
      "head turned left", "head turned right", "looking down",
      "looking up", "eyes closed", "gazing into distance"
    ],
    "expression": [
      "neutral expression", "subtle smile", "serious demeanor",
      "contemplative look", "confident stance", "relaxed appearance",
      "focused intensity", "gentle warmth", "mysterious air",
      "commanding presence", "approachable manner", "stoic composure"
    ]
  }
}
```

#### File: `profiles/scene_default.json`

```json
{
  "name": "Scene Default",
  "description": "Comprehensive scene and environment descriptions",
  "version": "1.0.0",

  "templates": [
    "{location}, {time_context}, {weather_atmosphere}",
    "{location} during {time_context}, {ambient_detail}",
    "{weather_atmosphere} {location}, {ambient_detail}",
    "{location} with {ambient_detail}, {time_context}"
  ],

  "pools": {
    "location": [
      "professional photography studio", "white seamless backdrop studio",
      "modern minimalist interior", "cozy living room", "industrial loft",
      "busy city street", "quiet suburban neighborhood", "urban rooftop",
      "dense forest clearing", "sandy beach shoreline", "mountain peak",
      "ancient temple ruins", "medieval castle courtyard", "futuristic cityscape",
      "underwater coral reef", "alien planet surface", "space station interior"
    ],
    "time_context": [
      "morning golden hour", "bright midday sun", "afternoon warmth",
      "golden hour sunset", "blue hour twilight", "deep night darkness",
      "overcast daylight", "stormy afternoon", "misty dawn",
      "starlit night", "moonlit evening", "artificial lighting"
    ],
    "weather_atmosphere": [
      "clear skies", "partly cloudy", "overcast gray",
      "light rain falling", "heavy downpour", "gentle snow",
      "thick fog", "morning mist", "dust in the air",
      "humid tropical", "dry desert heat", "crisp autumn air"
    ],
    "ambient_detail": [
      "dappled light through leaves", "reflections on wet surfaces",
      "dust particles in light beams", "steam rising from ground",
      "wind-blown debris", "falling leaves", "fireflies glowing",
      "neon signs reflecting", "car headlights streaking", "candlelight flickering"
    ]
  }
}
```

#### File: `profiles/style_default.json`

```json
{
  "name": "Style Default",
  "description": "Artistic and photographic style descriptions",
  "version": "1.0.0",

  "templates": [
    "{medium} style, {technique}, {quality}",
    "{aesthetic} {medium}, {technique}",
    "{technique} with {aesthetic} approach, {quality}",
    "{quality} {medium}, {aesthetic}, {technique}"
  ],

  "pools": {
    "medium": [
      "photography", "digital photography", "film photography",
      "oil painting", "watercolor", "acrylic painting",
      "digital illustration", "concept art", "3D rendering",
      "pencil sketch", "charcoal drawing", "ink illustration",
      "mixed media", "collage art", "vector graphics"
    ],
    "technique": [
      "high contrast processing", "soft diffused look", "sharp detail emphasis",
      "selective focus technique", "long exposure blur", "HDR processing",
      "cross-processing effect", "desaturated palette", "vibrant saturation",
      "film grain texture", "lens flare effects", "motion blur"
    ],
    "aesthetic": [
      "minimalist", "maximalist", "vintage", "modern",
      "retro", "futuristic", "classical", "contemporary",
      "romantic", "gritty", "ethereal", "raw",
      "polished", "organic", "geometric", "surreal"
    ],
    "quality": [
      "professional grade", "commercial quality", "editorial standard",
      "fine art caliber", "gallery worthy", "museum quality",
      "publication ready", "award-winning caliber", "masterpiece level"
    ]
  }
}
```

#### File: `profiles/lighting_default.json`

```json
{
  "name": "Lighting Default",
  "description": "Comprehensive lighting setup descriptions",
  "version": "1.0.0",

  "templates": [
    "{source} providing {quality}, {direction}, {color_temp}",
    "{quality} {source}, {direction}, creating {mood}",
    "{direction} {source} with {quality}, {color_temp}",
    "{mood} atmosphere from {source}, {quality}, {direction}"
  ],

  "pools": {
    "source": [
      "natural sunlight", "overcast skylight", "window light",
      "studio strobe", "continuous LED", "softbox lighting",
      "ring light", "beauty dish", "umbrella diffusion",
      "practical lamps", "neon signs", "candlelight",
      "firelight", "moonlight", "mixed ambient sources"
    ],
    "quality": [
      "soft diffused light", "hard directional light", "dappled light",
      "even flat lighting", "dramatic contrast", "gentle gradients",
      "specular highlights", "broad soft shadows", "deep dark shadows",
      "rim lighting effect", "fill light balance", "key light dominance"
    ],
    "direction": [
      "from above", "from below", "from the side",
      "three-quarter front", "backlit silhouette", "front lit flat",
      "split lighting", "Rembrandt lighting", "butterfly lighting",
      "loop lighting", "broad lighting", "short lighting"
    ],
    "color_temp": [
      "warm golden tones", "cool blue cast", "neutral daylight",
      "tungsten orange warmth", "fluorescent green tint", "mixed color temperatures",
      "sunset warm palette", "shade blue coolness", "candlelight amber"
    ],
    "mood": [
      "mysterious", "cheerful", "dramatic",
      "romantic", "clinical", "cozy",
      "ethereal", "intense", "peaceful"
    ]
  }
}
```

#### File: `profiles/mood_default.json`

```json
{
  "name": "Mood Default",
  "description": "Emotional atmosphere and mood descriptions",
  "version": "1.0.0",

  "templates": [
    "{emotion} atmosphere, {intensity}, {descriptor}",
    "{intensity} {emotion} mood with {descriptor}",
    "{descriptor}, creating {emotion} {intensity} feeling",
    "{emotion} and {secondary_emotion}, {descriptor}"
  ],

  "pools": {
    "emotion": [
      "serene", "peaceful", "calm", "tranquil",
      "joyful", "cheerful", "playful", "whimsical",
      "dramatic", "intense", "powerful", "bold",
      "melancholic", "somber", "wistful", "nostalgic",
      "mysterious", "enigmatic", "ethereal", "dreamlike",
      "tense", "suspenseful", "ominous", "foreboding"
    ],
    "secondary_emotion": [
      "hopeful", "longing", "contemplative", "reflective",
      "energetic", "dynamic", "restless", "anticipatory",
      "intimate", "vulnerable", "raw", "authentic"
    ],
    "intensity": [
      "subtly", "gently", "softly",
      "moderately", "noticeably", "clearly",
      "strongly", "intensely", "overwhelmingly",
      "quietly", "loudly", "profoundly"
    ],
    "descriptor": [
      "permeating every element", "underlying the composition",
      "evident in the lighting", "reflected in the colors",
      "expressed through texture", "conveyed by the subjects",
      "enhanced by the setting", "amplified by contrast",
      "suggested by negative space", "reinforced by symmetry"
    ]
  }
}
```

#### File: `profiles/background_default.json`

```json
{
  "name": "Background Default",
  "description": "Background and backdrop descriptions",
  "version": "1.0.0",

  "templates": [
    "{surface} with {detail}, {blur_quality}",
    "{blur_quality} {surface}, {detail}",
    "{surface} featuring {detail}, rendered {blur_quality}",
    "{detail} on {surface}, {blur_quality}"
  ],

  "pools": {
    "surface": [
      "seamless white backdrop", "gray gradient background", "black void",
      "textured wall", "brick surface", "concrete backdrop",
      "wooden panels", "fabric drape", "paper backdrop",
      "natural foliage", "urban architecture", "sky gradient",
      "bokeh light pattern", "abstract shapes", "geometric pattern"
    ],
    "detail": [
      "subtle texture variation", "visible grain pattern", "smooth gradient",
      "shadow play", "light leaks", "color spots",
      "dust particles", "lens artifacts", "reflection points",
      "organic shapes", "architectural lines", "natural elements"
    ],
    "blur_quality": [
      "crisp and sharp throughout", "slightly soft focus",
      "moderately blurred", "heavily defocused",
      "creamy bokeh effect", "busy bokeh pattern",
      "gradual focus falloff", "abrupt focus transition",
      "painterly soft blur", "cinematic shallow depth"
    ]
  }
}
```

#### File: `profiles/composition_default.json`

```json
{
  "name": "Composition Default",
  "description": "Visual composition and arrangement descriptions",
  "version": "1.0.0",

  "templates": [
    "{rule} with {element}, creating {effect}",
    "{element} following {rule}, {effect}",
    "{effect} achieved through {rule} and {element}",
    "{rule}, {element}, resulting in {effect}"
  ],

  "pools": {
    "rule": [
      "rule of thirds placement", "golden ratio composition", "centered symmetry",
      "diagonal composition", "triangular arrangement", "S-curve flow",
      "L-shaped framing", "frame within frame", "leading lines",
      "radial composition", "grid alignment", "asymmetrical balance"
    ],
    "element": [
      "strong foreground interest", "layered depth planes", "negative space emphasis",
      "pattern repetition", "contrast of scale", "color blocking",
      "texture juxtaposition", "shape relationships", "tonal gradients",
      "visual weight distribution", "directional flow", "focal point hierarchy"
    ],
    "effect": [
      "visual harmony", "dynamic tension", "stable balance",
      "dramatic impact", "subtle elegance", "bold statement",
      "quiet contemplation", "energetic movement", "peaceful stillness",
      "narrative depth", "emotional resonance", "aesthetic pleasure"
    ]
  }
}
```

#### File: `profiles/camera_angle_default.json`

```json
{
  "name": "Camera Angle Default",
  "description": "Camera angle and perspective descriptions",
  "version": "1.0.0",

  "templates": [
    "{vertical_angle} with {horizontal_angle}, {movement}",
    "{horizontal_angle} {vertical_angle}, {perspective}",
    "{movement} {vertical_angle}, {perspective}",
    "{perspective} from {vertical_angle}, {horizontal_angle}"
  ],

  "pools": {
    "vertical_angle": [
      "eye level shot", "slightly elevated angle", "high angle looking down",
      "low angle looking up", "bird's eye view", "worm's eye view",
      "overhead shot", "ground level perspective", "aerial view"
    ],
    "horizontal_angle": [
      "straight on front view", "three-quarter angle", "profile side view",
      "rear three-quarter", "over the shoulder", "point of view shot"
    ],
    "movement": [
      "static locked position", "subtle drift", "smooth tracking",
      "handheld documentary feel", "crane movement", "dolly push",
      "orbit around subject", "tilt reveal", "pan across scene"
    ],
    "perspective": [
      "natural perspective", "forced perspective", "extreme foreshortening",
      "telephoto compression", "wide angle distortion", "fisheye curvature",
      "tilt-shift miniature effect", "anamorphic stretch", "standard rectilinear"
    ]
  }
}
```

#### File: `profiles/camera_distance_default.json`

```json
{
  "name": "Camera Distance Default",
  "description": "Camera distance and shot framing descriptions",
  "version": "1.0.0",

  "templates": [
    "{shot_type}, {framing}",
    "{framing} {shot_type}",
    "{shot_type} with {detail}",
    "{detail}, {shot_type}"
  ],

  "pools": {
    "shot_type": [
      "extreme close-up", "close-up shot", "medium close-up",
      "medium shot", "medium full shot", "full shot",
      "wide shot", "extreme wide shot", "establishing shot"
    ],
    "framing": [
      "tight framing", "loose framing", "balanced framing",
      "off-center framing", "headroom heavy", "lead room emphasized",
      "cropped composition", "full frame utilization", "negative space heavy"
    ],
    "detail": [
      "capturing fine details", "showing full context", "emphasizing scale",
      "isolating the subject", "relating to environment", "creating intimacy",
      "establishing geography", "revealing relationships", "focusing on expression"
    ]
  }
}
```

#### File: `profiles/camera_dof_default.json`

```json
{
  "name": "Camera Depth of Field Default",
  "description": "Depth of field and focus plane descriptions",
  "version": "1.0.0",

  "templates": [
    "{dof_type} with {bokeh}, {transition}",
    "{bokeh} {dof_type}, {plane_description}",
    "{plane_description}, {dof_type}, {bokeh}",
    "{transition} {dof_type} creating {bokeh}"
  ],

  "pools": {
    "dof_type": [
      "extremely shallow depth of field", "shallow depth of field",
      "moderate depth of field", "deep depth of field",
      "infinite depth of field", "selective focus",
      "split focus", "rack focus transition", "zone focus"
    ],
    "bokeh": [
      "creamy smooth bokeh", "busy nervous bokeh", "circular bokeh shapes",
      "hexagonal bokeh pattern", "swirly bokeh effect", "soap bubble bokeh",
      "cat's eye bokeh", "harsh bokeh edges", "soft feathered bokeh"
    ],
    "transition": [
      "gradual falloff", "abrupt focus edge", "smooth gradient",
      "stepped focus planes", "continuous sharpness change", "dramatic separation"
    ],
    "plane_description": [
      "single plane in focus", "multiple planes sharp", "foreground soft background sharp",
      "subject isolated from background", "everything acceptably sharp",
      "thin slice of focus", "deep zone of sharpness", "selective critical focus"
    ]
  }
}
```

#### File: `profiles/camera_focus_default.json`

```json
{
  "name": "Camera Focus Default",
  "description": "Focus target and attention descriptions",
  "version": "1.0.0",

  "templates": [
    "{focus_target}, {sharpness}, {attention}",
    "{sharpness} on {focus_target}, {attention}",
    "{attention} with {focus_target} {sharpness}",
    "{focus_target} rendered {sharpness}, {attention}"
  ],

  "pools": {
    "focus_target": [
      "sharp focus on eyes", "focus on face", "focus on hands",
      "focus on main subject", "focus on foreground element", "focus on background detail",
      "focus on product", "focus on texture", "focus on reflection",
      "focus on edge detail", "focus on center of interest", "focus on action point"
    ],
    "sharpness": [
      "tack sharp", "critically sharp", "acceptably sharp",
      "slightly soft", "intentionally soft", "razor sharp",
      "pin sharp", "dreamy soft", "clinical sharpness"
    ],
    "attention": [
      "drawing the eye immediately", "guiding viewer attention",
      "creating focal hierarchy", "establishing visual priority",
      "emphasizing the subject", "directing the gaze",
      "anchoring the composition", "highlighting key elements"
    ]
  }
}
```

---

## Part 4: Directory Structure

```
ComfyUI-Zero2JSON/
├── __init__.py                           # Main registration file
├── requirements.txt                      # Python dependencies
├── README.md                            # Documentation
├── Zero2Json-plan.md                    # This implementation plan
│
├── nodes/
│   ├── __init__.py                      # Nodes package init
│   ├── base.py                          # Base classes and utilities
│   ├── subject_nodes.py                 # Subject-related nodes
│   ├── scene_nodes.py                   # Scene and background nodes
│   ├── style_nodes.py                   # Style and mood nodes
│   ├── lighting_nodes.py                # Lighting nodes
│   ├── camera_nodes.py                  # Camera-related nodes
│   ├── composition_nodes.py             # Composition nodes
│   └── utility_nodes.py                 # Utility and debug nodes
│
└── profiles/
    ├── subject_description_default.json
    ├── subject_position_default.json
    ├── subject_action_default.json
    ├── subject_pose_default.json
    ├── scene_default.json
    ├── style_default.json
    ├── lighting_default.json
    ├── mood_default.json
    ├── background_default.json
    ├── composition_default.json
    ├── camera_angle_default.json
    ├── camera_distance_default.json
    ├── camera_dof_default.json
    └── camera_focus_default.json
```

---

## Part 5: Requirements

#### File: `requirements.txt`

```
xxhash>=3.0.0
```

---

## Part 6: Node Summary

### Complete Node List (14 Generation Nodes + 3 Utility Nodes)

| Node ID | Display Name | Category | Output Type | Profile |
|---------|--------------|----------|-------------|---------|
| Z2J_SubjectDescription | 🎯 Z2J Subject Description | Zero2JSON/Subject | STRING | subject_description_*.json |
| Z2J_SubjectPosition | 📍 Z2J Subject Position | Zero2JSON/Subject | STRING | subject_position_*.json |
| Z2J_SubjectAction | 🏃 Z2J Subject Action | Zero2JSON/Subject | STRING | subject_action_*.json |
| Z2J_SubjectPose | 🧘 Z2J Subject Pose | Zero2JSON/Subject | STRING | subject_pose_*.json |
| Z2J_Scene | 🌍 Z2J Scene | Zero2JSON/Scene | STRING | scene_*.json |
| Z2J_Background | 🖼️ Z2J Background | Zero2JSON/Scene | STRING | background_*.json |
| Z2J_Style | 🎨 Z2J Style | Zero2JSON/Style | STRING | style_*.json |
| Z2J_Mood | 😊 Z2J Mood | Zero2JSON/Style | STRING | mood_*.json |
| Z2J_Lighting | 💡 Z2J Lighting | Zero2JSON/Lighting | STRING | lighting_*.json |
| Z2J_Composition | 📐 Z2J Composition | Zero2JSON/Composition | STRING | composition_*.json |
| Z2J_CameraAngle | 📐 Z2J Camera Angle | Zero2JSON/Camera | STRING | camera_angle_*.json |
| Z2J_CameraDistance | 📏 Z2J Camera Distance | Zero2JSON/Camera | STRING | camera_distance_*.json |
| Z2J_CameraDoF | 🔍 Z2J Camera DoF | Zero2JSON/Camera | STRING | camera_dof_*.json |
| Z2J_CameraFocus | 🎯 Z2J Camera Focus | Zero2JSON/Camera | STRING | camera_focus_*.json |
| Z2J_ProfileInfo | ℹ️ Z2J Profile Info | Zero2JSON/Utility | STRING, INT | Any profile |
| Z2J_BatchGenerator | 📦 Z2J Batch Generator | Zero2JSON/Utility | STRING, STRING | Any profile |
| Z2J_SeedMixer | 🔀 Z2J Seed Mixer | Zero2JSON/Utility | INT | N/A |

---

## Part 7: Integration Workflow Example

### Typical Zero2JSON + FLUX2-JSON Workflow

```
[Z2J_SubjectDescription] ─────────────────────┐
   seed: 42                                   │
   prompt_index: 0                            │
   profile: subject_description_default.json  │
                                              ▼
                                    ┌─────────────────────┐
[Z2J_SubjectPosition] ─────────────►│  FLUX2_Subject      │
   seed: 42                         │     Creator         │
   prompt_index: 0                  │                     │
                                    │ description ◄───────┤
[Z2J_SubjectAction] ───────────────►│ position ◄──────────┤
   seed: 42                         │ action ◄────────────┤
   prompt_index: 0                  │ pose ◄──────────────┤
                                    └──────────┬──────────┘
[Z2J_SubjectPose] ─────────────────────────────┘
   seed: 42                                    │
   prompt_index: 0                             │
                                               ▼
                                    ┌─────────────────��───┐
                                    │  FLUX2_Subject      │
                                    │     Array           │
                                    └──────────┬──────────┘
                                               │
[Z2J_Scene] ──────────────────────────────────┐│
   seed: 42                                   ││
   prompt_index: 0                            ││
                                              ▼▼
[Z2J_Style] ─────────────────────────────────►┌─────────────────────┐
   seed: 42                                   │  FLUX2_Prompt       │
   prompt_index: 0                            │    Assembler        │
                                              │                     │
[Z2J_Lighting] ──────────────────────────────►│ subjects ◄──────────┤
   seed: 42                                   │ scene ◄─────────────┤
   prompt_index: 0                            │ style ◄─────────────┤
                                              │ lighting ◄──────────┤
[Z2J_Mood] ──────────────────────────────────►│ mood ◄──────────────┤
   seed: 42                                   │ background ◄────────┤
   prompt_index: 0                            │ composition ◄───────┤
                                              │ camera ◄────────────┤
[Z2J_Background] ────────────────────────────►└─────────────────────┘
   seed: 42                                             │
   prompt_index: 0                                      │
                                                        ▼
[Z2J_Composition] ─────────────────────────────  Final JSON Output
   seed: 42
   prompt_index: 0

[Z2J_CameraAngle] ────────────────────────────┐
   seed: 42                                   │
   prompt_index: 0                            │
                                              ▼
                                    ┌─────────────────────┐
[Z2J_CameraDoF] ───────────────────►│  FLUX2_Camera       │
   seed: 42                         │      Rig            │
   prompt_index: 0                  └──────────┬──────────┘
                                               │
[Z2J_CameraFocus] ─────────────────────────────┘
   seed: 42
   prompt_index: 0
```

---

## Part 8: Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `/ComfyUI-Zero2JSON/` directory structure
- [ ] Implement `nodes/base.py` with core hash functions
- [ ] Create `__init__.py` with node registration
- [ ] Add `requirements.txt`

### Phase 2: Subject Nodes
- [ ] Implement `nodes/subject_nodes.py`
- [ ] Create `profiles/subject_description_default.json`
- [ ] Create `profiles/subject_position_default.json`
- [ ] Create `profiles/subject_action_default.json`
- [ ] Create `profiles/subject_pose_default.json`

### Phase 3: Scene & Style Nodes
- [ ] Implement `nodes/scene_nodes.py`
- [ ] Implement `nodes/style_nodes.py`
- [ ] Create `profiles/scene_default.json`
- [ ] Create `profiles/background_default.json`
- [ ] Create `profiles/style_default.json`
- [ ] Create `profiles/mood_default.json`

### Phase 4: Lighting & Camera Nodes
- [ ] Implement `nodes/lighting_nodes.py`
- [ ] Implement `nodes/camera_nodes.py`
- [ ] Create `profiles/lighting_default.json`
- [ ] Create `profiles/camera_angle_default.json`
- [ ] Create `profiles/camera_distance_default.json`
- [ ] Create `profiles/camera_dof_default.json`
- [ ] Create `profiles/camera_focus_default.json`

### Phase 5: Composition & Utility Nodes
- [ ] Implement `nodes/composition_nodes.py`
- [ ] Implement `nodes/utility_nodes.py`
- [ ] Create `profiles/composition_default.json`

### Phase 6: Testing & Documentation
- [ ] Test all nodes in ComfyUI
- [ ] Verify FLUX2-JSON integration
- [ ] Create example workflows
- [ ] Write README.md documentation

---

## Part 9: Mathematical Foundation

### Position-as-Seed Hash Formula

```
prompt = generate(seed, prompt_index, profile)

Where:
  - seed ∈ [0, 2³²) = World randomization
  - prompt_index ∈ [0, 2³²) = Position in infinite space
  - profile = JSON vocabulary definition

Internal computation:
  template_hash = xxhash32(seed, prompt_index, 0)
  template = templates[template_hash % len(templates)]

  For each pool i:
    component_hash = xxhash32(seed, prompt_index, i + 1)
    components[pool_name] = pool[component_hash % len(pool)]

  output = template.format(**components)

Total combinations = len(templates) × Π(len(pool_i))
```

### Determinism Guarantee

For any fixed (seed, prompt_index, profile):
- Same hash values are always computed
- Same template is always selected
- Same components are always chosen
- Same output is always generated

This holds across:
- Different machines
- Different Python versions (3.7+)
- Different operating systems
- Different times of execution

---

## Conclusion

Zero2JSON provides a complete framework for augmenting FLUX2-JSON with ZeroPrompt's position-as-seed procedural text generation. The 17 specialized nodes cover every text input field in the FLUX2-JSON system, each with dedicated JSON profiles allowing domain-specific vocabulary curation.

Key benefits:
1. **Deterministic**: Same seed + index always produces same output
2. **Infinite**: Trillions of unique combinations per profile
3. **Customizable**: JSON profiles allow vocabulary tuning without code changes
4. **Modular**: Each node operates independently with its own profile
5. **Symbiotic**: Augments rather than replaces FLUX2-JSON functionality

The user maintains full control through:
- Seed selection (global randomization)
- Prompt index navigation (position in infinite space)
- Profile selection (vocabulary domain)
- Prefix/suffix modification (fine-tuning)
- Direct override (use manual input instead)
