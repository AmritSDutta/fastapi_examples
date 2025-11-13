from fastapi import APIRouter

from app.routers import matching_doc_router

router = APIRouter()
router.include_router(matching_doc_router.doc_router)
