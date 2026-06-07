"""Reserved seam for deterministic routing (Principle 1).

The architecture is model-driven: the model decides what to call and when.
The single allowed exception is logic that must be deterministic because it is
legally or operationally required (for example a mandated disclosure that must
fire verbatim, or a hard scheduling constraint). Such logic goes here, behind
an explicit, reviewable boundary, and nowhere else.

This package is intentionally empty for now. Keeping it empty is a feature: it
makes any future determinism a deliberate, visible decision.
"""
