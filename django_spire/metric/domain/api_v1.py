from __future__ import annotations

from ninja import Router

from django_spire.metric.domain.statistic.api_v1 import router as statistic_router

router = Router()

router.add_router('statistic', statistic_router)
