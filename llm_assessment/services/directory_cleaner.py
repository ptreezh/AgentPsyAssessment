"""
Directory Cleaner Service
Handles automatic cleanup of empty directories for robust assessment execution.
"""

import os
from typing import List


class DirectoryCleaner:
    """Manages automatic cleanup of empty directories"""
    
    def __init__(self, base_dirs: List[str] = None):
        """
        Initialize directory cleaner.
        
        Args:
            base_dirs: List of base directories to clean. If None, uses current directory.
        """
        self.base_dirs = base_dirs or [os.getcwd()]
    
    def cleanup_empty_dirs(self, dry_run: bool = False) -> List[str]:
        """
        Clean up empty directories recursively.
        
        Args:
            dry_run: If True, only report what would be deleted without actually deleting
            
        Returns:
            List of directories that were deleted (or would be deleted in dry run)
        """
        deleted_dirs = []
        
        for base_dir in self.base_dirs:
            # Walk directory tree bottom-up to ensure we clean nested empty directories
            for root, dirs, files in os.walk(base_dir, topdown=False):
                # Check if directory is empty (no files and no subdirectories)
                if not dirs and not files:
                    # Skip protected directories
                    if self._is_protected_dir(root):
                        continue
                    
                    if dry_run:
                        print(f"[DRY RUN] Would delete empty directory: {root}")
                        deleted_dirs.append(root)
                    else:
                        try:
                            os.rmdir(root)
                            print(f"Deleted empty directory: {root}")
                            deleted_dirs.append(root)
                        except OSError as e:
                            # Directory not empty or permission denied
                            print(f"Failed to delete directory {root}: {e}")
        
        return deleted_dirs
    
    def _is_protected_dir(self, directory: str) -> bool:
        """
        Check if a directory is protected from cleanup.
        
        Args:
            directory: Directory path to check
            
        Returns:
            True if directory is protected, False otherwise
        """
        protected_names = {'.git', '__pycache__', '.pytest_cache', '.vscode', '.idea'}
        dir_name = os.path.basename(directory)
        return dir_name in protected_names


# Example usage:
# cleaner = DirectoryCleaner(["results", "logs"])
# 
# # Dry run to see what would be deleted
# would_delete = cleaner.cleanup_empty_dirs(dry_run=True)
# print(f"Would delete {len(would_delete)} directories")
# 
# # Actual cleanup
# deleted = cleaner.cleanup_empty_dirs()
# print(f"Deleted {len(deleted)} directories")