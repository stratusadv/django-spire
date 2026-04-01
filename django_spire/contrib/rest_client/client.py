from django.core.exceptions import ImproperlyConfigured

T = TypeVar('T')


class BaseRestClient:
    rest_schema_class: type[T]
    base_url: str

    def __init__(
            self,
    ):
        # Configure Auth
        self.base_url = base_url

    def __init_subclass__(cls, **kwargs):
        required_attributes = ['base_url']

        for attribute in required_attributes:
            if getattr(cls, attribute, None) is None:
                message = f'{attribute} is required'
                raise ImproperlyConfigured(message)

    def build_headers(self):
        pass

    def get(url_path) -> T:
        # Retry logic
        # Custom or Handleable Exceptions
        return requests.get(url_path)

    def post(url_path) -> T:
        return requests.post(url_path)

