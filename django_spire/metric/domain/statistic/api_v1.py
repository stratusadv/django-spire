from __future__ import annotations

from ninja import Router

router = Router()


@router.get("multiply")
def multiply(request, a: int, b: int):
    return {"result": a * b}
