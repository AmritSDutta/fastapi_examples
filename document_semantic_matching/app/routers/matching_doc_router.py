import logging
from typing import List

from fastapi import APIRouter, Query, Depends

from app.database.document_repository import DocumentRepository
from app.database.vector_db import VectorDb, get_db
from app.schema.document_record import DocumentRecord
from app.service.document_service import DocumentService

logger = logging.getLogger(__name__)
doc_router = APIRouter(prefix="/docs", tags=["docs"])


def get_document_service(db: VectorDb = Depends(get_db)) -> DocumentService:
    logger.info('inside get_document_service')
    return DocumentService(DocumentRepository(db))


def get_matching_docs(search_term, limit):
    pass


@doc_router.get("/search", status_code=200, response_model=List[DocumentRecord])
async def search_docs(search_term: str = Query(..., description="search query"),
                      limit: int = Query(3, ge=1, le=10, description="Number of docs to return"),
                      svc: DocumentService = Depends(get_document_service)) -> List[DocumentRecord]:
    """
    Retrieve items by category with an optional limit.
    """
    docs: List[DocumentRecord] = await svc.get_matching_docs(search_term, limit)
    return docs
