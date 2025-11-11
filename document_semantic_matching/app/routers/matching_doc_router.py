import logging
from typing import List

from fastapi import APIRouter,  Depends

from app.database.document_repository import DocumentRepository
from app.database.vector_db import VectorDb, get_db
from app.schema.document_record import DocumentRecord, SearchRequest, PassageRequest, ClassificationResult
from app.service.llm_classifier import ClassifyLLMService
from app.service.document_service import DocumentService

logger = logging.getLogger(__name__)
doc_router = APIRouter(prefix="/docs", tags=["docs"])
llm = ClassifyLLMService()


def get_document_service(db: VectorDb = Depends(get_db)) -> DocumentService:
    logger.info('inside get_document_service')
    return DocumentService(DocumentRepository(db))


@doc_router.post("/search", status_code=200, response_model=List[DocumentRecord])
async def search_docs(req: SearchRequest, svc: DocumentService = Depends(get_document_service)) -> List[DocumentRecord]:
    """
    Retrieve items by category with an optional limit.
    """
    logger.info(f'received req: query -> {req.search_term.strip()}, limit -> {req.limit}')
    docs: List[DocumentRecord] = await svc.get_matching_docs(req.search_term.strip(), req.limit)
    return docs


@doc_router.post("/classify", status_code=200, response_model=ClassificationResult)
async def classify_doc(req: PassageRequest) -> ClassificationResult:
    logger.info(f'received req: query -> {req.passage.strip()}')
    docs: ClassificationResult = llm.classify(req.passage.strip())
    return ClassificationResult(result=docs.sorted_result)
