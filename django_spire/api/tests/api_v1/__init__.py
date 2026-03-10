from ninja import Router

from django_spire.api.tests.api_v1.echo_router import echo_router

router = Router()

router.add_router('', echo_router)
