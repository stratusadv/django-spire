from typing import Literal

from django_spire.permission.models import PortalGroup
from django_spire.permission.models import PortalUser
from django_spire.cookbook.models import Cookbook


PERMISSIONS_LEVEL_CHOICES = (
    (0, 'None'),
    (1, 'View'),
    (2, 'Add'),
    (3, 'Change'),
    (4, 'Delete'),
)


VALID_PERMISSION_LEVELS = Literal[0, 1, 2, 3, 4]


PERMISSION_MODELS_DICT = {
    'group': {
        'model': PortalGroup,
        'is_proxy_model': True
    },
    'user': {
        'model': PortalUser,
        'is_proxy_model': True
    },
    'cookbook': {
        'model': Cookbook,
        'is_proxy_model': False
    },
}
