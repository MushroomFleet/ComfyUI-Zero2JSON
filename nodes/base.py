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
        suffix: str = "",
        **kwargs  # Accept additional subclass-specific inputs
    ) -> Tuple[str]:
        """
        Generate procedural text using position-as-seed methodology.

        Args:
            seed: World seed
            prompt_index: Position in prompt space
            profile: Profile filename to use
            prefix: Optional prefix text
            suffix: Optional suffix text
            **kwargs: Additional subclass-specific inputs (ignored by base)

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
                   prefix: str = "", suffix: str = "", **kwargs):
        """Ensure node updates when inputs change."""
        profile_str = profile or cls.DEFAULT_PROFILE
        profile_hash = xxhash.xxh32(profile_str.encode()).intdigest()
        return prompt_hash(seed ^ profile_hash, prompt_index, 0)
