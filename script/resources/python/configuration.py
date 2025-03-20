from typing import Literal
import os
from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings

# Chemin absolu vers le .env à la racine du projet
dir_file_path = os.path.dirname(os.path.abspath(__file__))
env_path= os.path.join(dir_file_path,os.pardir, os.pardir, '.env' ) 

class Configuration(BaseSettings):
    # Common
    environment: Literal[ "dev", "preprod", "prod"] = Field(description="Execution environment", default="prod")

    # Emails
    sender_email: str = Field(description="Mail account used to send email")
    sender_email_password: SecretStr = Field(description="Mail account password used to send email")
    receiver_email: str = Field(description="Email account used to receive email")
    mail_server_port: int = Field(description="Mail server port", default=465)
    smtp_server:str = Field(description="Mail server", default="ssl0.ovh.net")
    # Scraper
    headless: bool = Field(description="Set to true to run in headless mode", default=True)

    # Open Agenda
    OA_PUBLIC_KEY: str = Field(description="Open Agenda public key")
    OA_SECRET_KEY: SecretStr = Field(description="Open Agenda secret key")
    ACCESS_TOKEN_URL: str = Field(description="Open Agenda access token URL", default="https://api.openagenda.com/v2/requestAccessToken")
    AGENDA_UID: str = Field(description="Kerlandrier Open Agenda UID", default="44891982")
    TBD_LOCATION_UID: str = Field(description="Open Agenda ToBeDefined location UID", default="11634941")
    KAL_LOCATION_UID: str = Field(description="Open Agenda KAL location UID", default="52856698")

    # Facebook events ICS URL
    ICS_PRIVATE_URL_KLR_FB: SecretStr = Field(description="Kerlandrier Facebook events ICS URL")

    # Ateliers KAL ICS URL
    URL_AGENDA_ATELIERS_KAL: str = Field(description="KAL Ateliers ICS URL", default="https://cloud.konkarlab.bzh/remote.php/dav/public-calendars/JixPor4dk7xqRAja/?export")

    # API Key mistral for image analysis
    MISTRAL_PRIVATE_API_KEY: SecretStr = Field(description="Mistral API key for image analysis")

    ## EXAMPLE: load, and compute values
    #
    # raw_filtered_cities: str | None = Field(
    #     default=None,
    #     description="Cities that must be filtered when checking events."
    #     "Values converted to lower case.",
    #     examples=["Rennes", "Paris"],
    # )

    # @computed_field
    # def filtered_cities(self) -> list[str]:
    #     return [x.lower() for x in self.raw_filtered_cities]  if self.raw_filtered_cities is not None else []

config = Configuration(_env_file=env_path)
