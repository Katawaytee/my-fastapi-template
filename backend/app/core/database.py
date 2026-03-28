import logging

from sqlalchemy import MetaData, Table, create_engine
from app.settings import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = config.DB_URL


class DBManager:
    def __init__(self, table_name: str, data_model_class) -> None:
        self.db_engine = create_engine(
            DB_URL,
            pool_size=20,
            max_overflow=0,
            pool_recycle=3600,
        )
        self.meta = MetaData()
        self.table_name = table_name
        self.data_model_class = data_model_class
        self._table = None
        logger.info(f"[init] {table_name}")

    @property
    def table(self) -> Table:
        if self._table is None:
            try:
                self._table = Table(
                    self.table_name,
                    self.meta,
                    autoload_with=self.db_engine,
                )
            except Exception as e:
                logger.error(
                    f" [reflect_table] error reflecting table {self.table_name} | {e}"
                )
                raise

        return self._table
