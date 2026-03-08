from __future__ import annotations

from ninja import Router

router = Router()


@router.get("/add")
def add(request, a: int, b: int):
    return {"result": a + b}
