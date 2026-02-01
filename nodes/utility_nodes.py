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
