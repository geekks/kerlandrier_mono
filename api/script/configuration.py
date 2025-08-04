from typing import Literal
import os,sys
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

# Chemin absolu vers le .env du dosseir "script"
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path= os.path.join(SCRIPT_DIR, '.env' ) 

from .libs.oa_types import OA_Connection

class Configuration(BaseSettings):
    # Common
    ENV_DEV: Literal[ "dev", "preprod", "prod"] = Field(description="Execution environment", default="prod")

    # Emails
    SENDER_EMAIL: str = Field(description="Mail account used to send email")
    SENDER_EMAIL_PASSWORD: SecretStr = Field(description="Mail account password used to send email")
    RECEIVER_EMAIL: str = Field(description="Email account used to receive email")
    MAIL_SERVER_PORT: int = Field(description="Mail server port", default=465)
    SMTP_SERVER:str = Field(description="Mail server", default="ssl0.ovh.net")
    
    # Open Agenda
    OA_PUBLIC_KEY: str = Field(description="Open Agenda public key")
    OA_SECRET_KEY: SecretStr = Field(description="Open Agenda secret key")
    OA_ACCESS_TOKEN_URL: str = Field(description="Open Agenda access token URL", default="https://api.openagenda.com/v2/requestAccessToken")
    AGENDA_UID: str = Field(description="Kerlandrier Open Agenda UID", default="44891982")
    TBD_LOCATION_UID: str = Field(description="Open Agenda ToBeDefined location UID", default="11634941")
    KAL_LOCATION_UID: str = Field(description="Open Agenda KAL location UID", default="52856698")
    AGENDA_SLUG: str = Field(description="Kerlandrier Open Agenda slug", default="kerlandrier")
    
    @property
    def OA_AGENDA_URL(self):
        return f"https://openagenda.com/fr/{self.AGENDA_SLUG}"
    
    @property
    def OA_API_URL(self):
        return f"https://api.openagenda.com/v2/agendas/{self.AGENDA_UID}"
    
    # Facebook events ICS URL
    ICS_PRIVATE_URL_KLR_FB: SecretStr = Field(description="Kerlandrier Facebook events ICS URL")

    # Ateliers KAL ICS URL
    URL_AGENDA_ATELIERS_KAL: str = Field(description="KAL Ateliers ICS URL", default="https://cloud.konkarlab.bzh/remote.php/dav/public-calendars/JixPor4dk7xqRAja/?export")
    KAL_LOCATION_UID: str = Field(description="KAL location UID", default="52856698")
    
    # API Key mistral for image analysis
    MISTRAL_PRIVATE_API_KEY: SecretStr = Field(description="Mistral API key for image analysis")
    IMGBB_API_URL: str = Field(description="Temp web image upload service URL", default="https://api.imgbb.com/1/upload")
    IMGBB_PRIVATE_API_KEY: SecretStr = Field(description="Temp web image upload service API token")
    
    # Scraping
    HEADLESS_PLAYWRIGHT: bool = Field(description="Headless mode for Playwright", default=True)
    model_config = {
        "extra" : "allow"
    }
    
config = Configuration(_env_file=env_path)

oa = OA_Connection(
    agenda_uid=config.AGENDA_UID,
    oa_api_url=config.OA_API_URL,
    access_token_url=config.OA_ACCESS_TOKEN_URL,
    tbd_location_uid=config.TBD_LOCATION_UID,
    public_key=config.OA_PUBLIC_KEY,
    secret_key=config.OA_SECRET_KEY.get_secret_value(),
)

