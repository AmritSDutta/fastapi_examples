from fastapi import FastAPI, APIRouter
from .router import employee_web
router = APIRouter()
router.include_router(employee_web.router)

