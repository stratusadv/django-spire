from django_spire.contrib.rest import RestSchema
from test_project.apps.rest.rest.schemaset import PirateRestSchemaSet


class PirateRestSchema(RestSchema):
    """Schema for DummyJSON User API (mapped as Pirates)."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    objects = PirateRestSchemaSet.as_manager()
