import logging
from typing import List

from app.database.vector_db import VectorDb, get_query_embedding_async
from app.schema.document_record import DocumentRecord

logger = logging.getLogger(__name__)


class DocumentRepository:
    def __init__(self, db: VectorDb):
        logger.info('inside def __init__(self, db: DocumentRepository)')
        self.db = db

    async def get_top_k_docs(self, query: str, k: int = 3) -> List[DocumentRecord]:
        query_emb = await get_query_embedding_async(query)
        docs: List[DocumentRecord] = await self.db.get_top_k_docs(query_emb, k)
        return docs
