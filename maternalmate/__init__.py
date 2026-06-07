# ============================================================================
# maternalmate/__init__.py
# ============================================================================
"""
MaternalMate - AI-Based Maternal Care Monitoring System

This package contains the main Django project configuration.
"""

# This file can be empty, but it's required to make Python treat
# the directory as a package.

# You can optionally add version information:
__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'


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