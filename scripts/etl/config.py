from pathlib import Path
from pydantic import BaseSettings, Field


class ETLSettings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    data_file_path: Path = Field(Path("data/raw/DataCoSupplyChainDataset.csv"), env="DATA_FILE_PATH")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    chunk_size: int = Field(10000, env="ETL_CHUNK_SIZE")
    batch_size: int = Field(5000, env="ETL_BATCH_SIZE")
    job_name: str = Field("DATACO_FULL_LOAD", env="ETL_JOB_NAME")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = ETLSettings()
