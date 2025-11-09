import asyncio
from typing import List
import asyncpg
import logging
import numpy as np
from app.database.custom_embedding import get_gemini_embedding
from app.schema.document_record import DocumentRecord

logger = logging.getLogger(__name__)
TABLE_NAME = "wines_3"
EMBED_DIM = 256
DB_DSN = "postgres://user:password@localhost/wine_review_gemini"


async def get_query_embedding_async(text: str) -> List[float]:
    # wrap sync embedding call in a thread to avoid blocking event loop
    emb = await asyncio.to_thread(get_gemini_embedding, text, 'retrieval_query', EMBED_DIM)
    # ensure return is plain list of floats
    return list(np.asarray(emb).astype(float))


class VectorDb:
    def __init__(self, dsn: str):
        logger.info('inside def __init__(self, dsn: str)')
        self._dsn = dsn
        self._pool: asyncpg.Pool | None = None

    async def init(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(dsn=self._dsn)
            logger.info('db initialized')

    async def close(self):
        if self._pool:
            await self._pool.close()

    async def fetch(self, query: str, *args):
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def get_top_k_docs(self, query_emb: List[float], k: int = 3) -> List[DocumentRecord]:
        arr_literal = self._vector_literal(query_emb)
        sql = f"""
          SELECT title, description
          FROM {TABLE_NAME}
          ORDER BY embedding <=> $1::vector
          LIMIT $2
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, arr_literal, k)
        return [DocumentRecord(name=r['title'], description=r['description']) for r in rows]

    def _vector_literal(self, arr: List[float]) -> str:
        # pgvector expects a literal like '[1,2,3]'
        return "[" + ",".join(map(str, arr)) + "]"


db = VectorDb(DB_DSN)


async def get_db() -> VectorDb:
    logger.info('get_db()')
    return db
