from __future__ import annotations

# These imports are for the migrations to work as a single app "django_spire_core"

from django_spire.core.tag import models

# Must assert to stop unused import removals.

assert models
