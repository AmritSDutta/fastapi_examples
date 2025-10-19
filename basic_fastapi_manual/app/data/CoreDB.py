import asyncpg
import logging

logger = logging.getLogger("CoreDB")


class CoreDB:
    def __init__(self, dsn: str):
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


db = CoreDB("postgres://postgres:postgres@127.0.0.1:5432/oracle_hr")


async def get_db() -> CoreDB:
    logger.info('get_db()')
    return db
