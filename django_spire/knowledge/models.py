from __future__ import annotations

# These imports are for the migrations to work as a single app "django_spire_knowledge"

from django_spire.knowledge.entry import models as entry_models # noqa
from django_spire.knowledge.entry.version import models as entry_version_models # noqa
from django_spire.knowledge.entry.version.block import models as entry_version_block_models # noqa
from django_spire.knowledge.collection import models as collection_models # noqa
