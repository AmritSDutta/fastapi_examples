import asyncio
from typing import List
from urllib.parse import urlparse

import asyncpg
import logging
import numpy as np

from app.config.Settings import get_settings
from app.database.custom_embedding import get_gemini_embedding
from app.schema.document_record import DocumentRecord

logger = logging.getLogger(__name__)
EMBED_DIM = get_settings().EMBED_DIM
DB_DSN = get_settings().DB_DSN  # "postgres://user:password@localhost/wine_review_gemini"
logging.info(f'effective DB_DSN, debug step for docker based run : {DB_DSN}')


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

    async def init(self, retries: int = 3, backoff: float = 1.0):
        if self._pool:
            return

            # --- Normalize DSN ---
        dsn = self._dsn.replace("+asyncpg", "") if self._dsn else self._dsn

        # --- Extract host for DNS check ---
        parsed = urlparse(dsn)
        host = parsed.hostname or "localhost"

        # --- Retry loop ---
        for attempt in range(1, retries + 1):
            try:
                # DNS check (ensures Docker name resolves before asyncpg connects)
                loop = asyncio.get_running_loop()
                await loop.getaddrinfo(host, parsed.port or 5432)
                self._pool = await asyncpg.create_pool(dsn=dsn)
                logger.info("DB initialized successfully on attempt %d", attempt)
                return
            except Exception as e:
                logger.warning("DB init failed (attempt %d/%d): %s", attempt, retries, e)
                await asyncio.sleep(backoff)
                backoff *= 2

        raise RuntimeError(f"Could not initialize DB pool after {retries} attempts")

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
          FROM {get_settings().TABLE_NAME}
          ORDER BY embedding <=> $1::vector
          LIMIT $2
        """
        logging.info(f'query: {sql}')
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
