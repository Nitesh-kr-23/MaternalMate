# ============================================================================
# utils/__init__.py
# ============================================================================
"""
Utility functions and helper scripts for MaternalMate

Contains:
- AI model training scripts
- Data processing utilities
- Helper functions
"""

# This file makes the 'utils' directory a Python package


# ============================================================================
# NOTES:
# ============================================================================
# 
# WHY __init__.py?
# ----------------
# In Python, any directory containing an __init__.py file is considered a
# package. This allows you to import modules from that directory.
#
# Example:
# - Without __init__.py: Cannot do "from core import models"
# - With __init__.py: Can do "from core import models"
#
# The __init__.py file can be:
# 1. Empty (just marking it as a package)
# 2. Contain initialization code
# 3. Define __all__ for package exports
# 4. Import submodules for easier access
#
# MODERN PYTHON (3.3+):
# ---------------------
# Python 3.3+ introduced "namespace packages" which don't require __init__.py,
# but Django still expects them for proper app structure.
#
# BEST PRACTICE:
# --------------
# Always include __init__.py in Django apps and project directories.
# ============================================================================