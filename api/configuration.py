from typing import Literal
import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

# Chemin absolu vers le .env du dosseir "script"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path= os.path.join(SCRIPT_DIR, '.env' ) 

class Configuration(BaseSettings):
    # Common
    ENV_DEV: Literal[ "dev", "preprod", "prod"] = Field(description="Execution environment", default="prod")

    # OA Fast API auth
    JWT_SECRET: SecretStr = Field(description="JWT secret key")
    JWT_ALGORITHM: str = Field(description="JWT algorithm", default="HS256")
    DB_PATH:str = Field(description="relative path of the database auth.db", default="db/auth.db")

    model_config = {
        "env_file": env_path,
        "env_file_encoding" : 'utf-8'
        }
configAPI = Configuration()
