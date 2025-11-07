# cython: language_level=3
"""
Flag diacritic operator enum.
This file makes the FlagDiacriticOperator enum importable from Python.
The actual enum definition is in flag_diacritic_operator.pxd
"""

# This file exists to make the enum defined in .pxd importable from Python.
# The enum declaration is in flag_diacritic_operator.pxd and should not be
# redeclared here to avoid Cython redeclaration errors.
