from django_spire.contrib.session.base_session import BaseSession


class ShoppingCartSession(BaseSession):
    json_serializable = True
    session_key = 'shopping_cart'

    _seconds_till_timeout: int = 60 * 30
