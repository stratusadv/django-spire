from django_spire.contrib.rest import RestSchema


class PirateSchema(RestSchema):
    """Schema for DummyJSON User API (mapped as Pirates)."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    class Meta:
        base_url = 'https://dummyjson.com'
        base_path = 'users'
        results_key = 'users'
