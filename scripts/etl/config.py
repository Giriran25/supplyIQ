from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ETLSettings(BaseSettings):
    postgres_user: str = Field("supplyiq", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("supplyiqpass", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("supplyiq", validation_alias="POSTGRES_DB")
    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")
    
    data_file_path: Path = Field(Path("data/raw/DataCoSupplyChainDataset.csv"), validation_alias="DATA_FILE_PATH")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    chunk_size: int = Field(10000, validation_alias="ETL_CHUNK_SIZE")
    batch_size: int = Field(500, validation_alias="ETL_BATCH_SIZE")
    job_name: str = Field("DATACO_FULL_LOAD", validation_alias="ETL_JOB_NAME")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = ETLSettings()
