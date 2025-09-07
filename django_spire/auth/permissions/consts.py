from __future__ import annotations

from typing_extensions import Literal

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser

PERMISSIONS_LEVEL_CHOICES = (
    (0, 'None'),
    (1, 'View'),
    (2, 'Add'),
    (3, 'Change'),
    (4, 'Delete'),
)


VALID_PERMISSION_LEVELS = Literal[0, 1, 2, 3, 4]


# PERMISSION_MODELS_DICT = {
#     'group': {
#         'model': AuthGroup,
#         'is_proxy_model': True
#     },
#     'user': {
#         'model': AuthUser,
#         'is_proxy_model': True
#     }
# }
