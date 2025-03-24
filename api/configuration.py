from typing import Literal
import os
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

# Chemin absolu vers le .env à la racine du projet
# dir_file_path = os.path.dirname(os.path.abspath(__file__))
# print(os.pardir)
# env_path= os.path.join(dir_file_path,os.pardir, '.env' ) 

class Configuration(BaseSettings):
    # Common
    environment: Literal[ "dev", "preprod", "prod"] = Field(description="Execution environment", default="prod")

    # Open Agenda
    OA_PUBLIC_KEY: str = Field(description="Open Agenda public key")
    OA_SECRET_KEY: SecretStr = Field(description="Open Agenda secret key")
    ACCESS_TOKEN_URL: str = Field(description="Open Agenda access token URL", default="https://api.openagenda.com/v2/requestAccessToken")
    AGENDA_UID: str = Field(description="Kerlandrier Open Agenda UID", default="44891982")
    TBD_LOCATION_UID: str = Field(description="Open Agenda ToBeDefined location UID", default="11634941")
    KAL_LOCATION_UID: str = Field(description="Open Agenda KAL location UID", default="52856698")
    OA_BASE_URL: str = Field(description="Open Agenda base URL", default="https://api.openagenda.com/v2/")

    # Fast Api
    JWT_SECRET: SecretStr = Field(description="JWT secret key")

config = Configuration(_env_file=".env")
