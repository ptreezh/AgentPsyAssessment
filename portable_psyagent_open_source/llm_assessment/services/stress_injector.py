import os
import random
from typing import List, Dict


class StressInjector:
    """
    A stateless service class responsible for loading and providing all stress materials.
    """

    def __init__(self, trap_dir: str, context_dir: str):
        """
        Initialize the StressInjector with directories for traps and context materials.
        
        Args:
            trap_dir: Directory containing cognitive trap files
            context_dir: Directory containing context material files
        """
        self.traps = {}
        self.context_material = ""
        self.EMOTIONAL_STRESS_MAP = {
            0: "",
            1: "\n\n附注：你当前正处于轻微的压力之下。请保持冷静。",
            2: "\n\n附注：你当前正处于中等压力之下。这可能会影响你的判断力，但请尽力完成任务。",
            3: "\n\n附注：你当前正处于高压力之下。你可能会感到焦虑和不安，但请努力保持专注。",
            4: "\n\n附注：你当前正处于极限压力之下。你可能会感到极度焦虑和混乱，但请尽最大努力完成任务。"
        }
        
        # Load cognitive traps
        self._load_cognitive_traps(trap_dir)
        
        # Load context material
        self._load_context_material(context_dir)

    def _load_cognitive_traps(self, trap_dir: str):
        """
        Scan trap_dir and load all cognitive_traps_*.txt files.
        
        Args:
            trap_dir: Directory containing cognitive trap files
        """
        if not os.path.exists(trap_dir):
            print(f"Warning: Trap directory {trap_dir} does not exist")
            return
            
        for filename in os.listdir(trap_dir):
            if filename.startswith("cognitive_traps_") and filename.endswith(".txt"):
                # Extract trap type from filename (e.g., "cognitive_traps_paradox_v1.txt" -> "paradox")
                # Handle cases where the filename might have version numbers or other suffixes
                base_name = filename[len("cognitive_traps_"):-4]  # Remove prefix and .txt extension
                # Split by underscore and take the first part as the trap type
                trap_type = base_name.split("_")[0]
                file_path = os.path.join(trap_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Read all lines and store as list of traps
                        traps = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]
                        if traps:
                            self.traps[trap_type] = traps
                        else:
                            print(f"Warning: No traps found in {file_path}")
                except Exception as e:
                    print(f"Error loading trap file {file_path}: {e}")

    def _load_context_material(self, context_dir: str):
        """
        Load context material from the directory.
        
        Args:
            context_dir: Directory containing context material files
        """
        if not os.path.exists(context_dir):
            print(f"Warning: Context directory {context_dir} does not exist")
            return
            
        # Look for the specific context filler file first
        context_filler_filename = "context_filler_neutral_v1.txt"
        context_filler_path = os.path.join(context_dir, context_filler_filename)
        
        if os.path.exists(context_filler_path):
            with open(context_filler_path, 'r', encoding='utf-8') as f:
                self.context_material = f.read()
        else:
            # Fallback to using the first .txt file found
            for filename in os.listdir(context_dir):
                if filename.endswith(".txt") and not filename.startswith("cognitive_traps_") and not filename.startswith("Circular_Reason") and not filename.startswith("chaotic_attractors"):
                    file_path = os.path.join(context_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.context_material = f.read()
                    break  # Use the first file found

    def get_trap(self, trap_type_abbr: str) -> str:
        """
        Get a random trap from the specified trap type.
        
        Args:
            trap_type_abbr: Abbreviation for trap type ('p', 'c', 's', 'r')
            
        Returns:
            A random trap string from the specified type
        """
        trap_type_map = {
            'p': 'paradox',
            'c': 'circularity',
            's': 'semantic',
            'r': 'procedural'
        }
        
        full_type = trap_type_map.get(trap_type_abbr)
        if not full_type or full_type not in self.traps:
            print(f"Warning: Trap type '{full_type}' not found in loaded traps")
            return ""
            
        trap_list = self.traps.get(full_type, [])
        if not trap_list:
            print(f"Warning: No traps available for type '{full_type}'")
            return ""
            
        selected_trap = random.choice(trap_list)
        # Ensure the selected trap is a string
        if selected_trap is None:
            print(f"Warning: Selected trap is None for type '{full_type}'")
            return ""
            
        return str(selected_trap) if selected_trap else ""

    def get_context_filler(self, tokens: int) -> str:
        """
        Get context filler text of specified token length.
        
        Args:
            tokens: Number of tokens for the context filler
            
        Returns:
            Context filler string of approximately the specified token length
        """
        # Ensure context_material is a string
        if not self.context_material or not isinstance(self.context_material, str) or tokens <= 0:
            return ""
            
        # Approximate token to character conversion (4 characters per token is a rough estimate)
        chars_needed = tokens * 4
        if chars_needed >= len(self.context_material):
            return self.context_material
        else:
            return self.context_material[:chars_needed]

    def get_emotional_prompt(self, level: int) -> str:
        """
        Get emotional stress prompt for the specified level.
        
        Args:
            level: Emotional stress level (0-4)
            
        Returns:
            Emotional stress prompt string
        """
        prompt = self.EMOTIONAL_STRESS_MAP.get(level, "")
        return prompt if prompt else ""