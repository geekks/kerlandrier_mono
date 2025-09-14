from typing import Optional, Union

import os, sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import api_utils
from script.libs.HttpRequests import patch_event
from configuration import configAPI
from script.configuration import config, oa
from script.mistral_images import postImageToImgbb, postMistralEventToOa

from db import initialize_database, DB_Connection
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from pydantic import BaseModel
from typing import List
import logging,coloredlogs

coloredlogs.install()

# Check if the database file exists and initialize it if not

if not os.path.exists(configAPI.DB_PATH):
    initialize_database(configAPI.DB_PATH)
    logging.info("Database initialized.")
db = DB_Connection(configAPI.DB_PATH)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
from api.script.libs.utils import check_image_file

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify a list of allowed origins like ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    username: str
    password: str

class Event(BaseModel):
    uid: str | int
    slug: Optional[str] = None
    keywords: List[str]

class PatchRequest(BaseModel):
    events: List[Event]

class PatchKeywordRequest(BaseModel):
    uid: str | int
    keywords: List[str]

class OaToken(BaseModel):
    success: bool
    access_token: str = None
    message: str = None

class AuthResponse(BaseModel):
    success: bool
    access_token: str = "xxxxx"
    token_type: str = "Bearer"
    
class ImageResponse(BaseModel):
    success: bool
    message: str = None
    event: dict = None

class UrlRequest(BaseModel):
    url: str

def get_token_header(authorization: str 
                        = Header(   default=None,
                                    title="Kerlandrier Token",
                                    description='Bearer token setted in headers: "Bearer TOKEN"',)
                    ):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.split(" ")[1]

def get_current_user(token: str 
                        = Depends(get_token_header)):
    payload = api_utils.verify_kl_token(token,
                            JWT_SECRET=configAPI.JWT_SECRET.get_secret_value(),
                            JWT_ALGORITHM=configAPI.JWT_ALGORITHM)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@app.get("/", status_code=404)
async def read_root():
    return {"success": False, "message": "RTFM"}

@app.post("/auth",
        summary="Get Bearer Token for Kerlandrier app",
        description="This endpoint generates a Bearer token for Kerlandrier API.\
            Requires a from manually added users in api DB.",
        response_model=AuthResponse)
async def authenticate(request: AuthRequest):
    username = request.username
    password = request.password

    # Check if the username and password are correct
    result = api_utils.get_user_by_username(db, username)
    if result is None or not api_utils.verify_password(result[1], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = result[0]
    token = api_utils.generate_kl_token(user_id,
                            JWT_SECRET=configAPI.JWT_SECRET.get_secret_value(),
                            JWT_ALGORITHM=configAPI.JWT_ALGORITHM)
    return {"success": True, "access_token": token, "token_type": "Bearer"}

@app.get("/auth/oatoken", 
        summary="Retrieve OpenAgenda Auth Token",
        description="This endpoint returns an OpenAgenda token, using the OA_SECRET_KEY on serverfor\
            Requires a manually added users in Kerlandrier API DB.",
        response_model=OaToken)
async def generates_token(current_user: dict 
                        = Depends(get_current_user)):
    logging.info( f"Token generated for user: ${current_user}")
    try:
        access_token = oa.getToken()
        if (access_token == None):
            return {"success": False, "message": "No access token"}
        else:
            return {"success": True,
                    "access_token": access_token,
                    "message": "Access token retrieved successfully"}
    except Exception as e:
        return {"success": False, "message": "Error getting OA access token"}
    

@app.patch("/event/keywords",
            summary="Update event keywords",
            description="This endpoint updates the keywords for on OA event\
                It returns the updated OA event",
            response_model=dict)
async def update_event(request: PatchKeywordRequest, current_user: dict = Depends(get_current_user)):
    try:
        access_token = oa.getToken()
        # print("access_token", access_token)
    except Exception as e:
        return {"success": False, "data": [], "message": "Erroir getting OA access token"}
    event = request
    try:
        existingKeywords = api_utils.get_event_keywords(event.uid,
                                                    api_url=config.OA_API_URL,
                                                    oa_public_key=oa.public_key)
        if existingKeywords is None or existingKeywords != event.keywords:
            patched = patch_event(
                access_token,
                event.uid,
                {
                    "data": 
                    {"keywords": 
                        {"fr": event.keywords}
                    }
                }
            )
            logging.info(f"{existingKeywords} >>>> {event.keywords}")

            return {"success": True, "data": patched, "message": "Event successfully updated"}
        else:
            logging.info("Keywords haven't changed")
            return {"success": True, "data": [], "message": "No update"}
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=400, detail=f"{e}")


@app.post("/image/upload",
        summary="Upload an image file of a poster with event",
        description="This endpoint allows authenticated users to upload an image file to be anlyze with Mistral to create an OA event.",
        response_model=ImageResponse)
async def upload_file(file: UploadFile,
                    current_user: dict = Depends(get_current_user)
                    ):

    # Save file locally. Not async
    file_path = api_utils.saveImagePost(file)
    # Send image to imgbb server to get online image
    try:
        ImgUrl = postImageToImgbb(image_path=file_path, imgbb_api_url = config.IMGBB_API_URL, imgbb_api_key = config.IMGBB_PRIVATE_API_KEY.get_secret_value() )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"infos": e} )
    # Send url and request to Mistral API
    try:
        response_mistral =api_utils.send_url_to_mistral(MISTRAL_PRIVATE_API_KEY=config.MISTRAL_PRIVATE_API_KEY.get_secret_value(),
                            url=ImgUrl)
    except Exception as e:
        raise Exception(f"Error sending Image URL to Mistral: {e}")
    try:
        OAevent = postMistralEventToOa(response_mistral,
                                    access_token=oa.getToken(),
                                    public_key=oa.public_key,
                                    locations_api_url= f"{config.OA_API_URL}/locations",
                                    image_url= ImgUrl)
        logging.info(f"OA event created: {OAevent.title.fr} at {OAevent.location.name}")
    except Exception as e:
        raise Exception(f"Error sending event on OpenAgenda: {e}")
    try:
        excerpt_response =api_utils.excerptOAEvent(OAevent)
        return excerpt_response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail={"infos": e} )
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File {file_path} deleted")


@app.post("/image/url",
        summary="Send an url link an image of a poster with event",
        description="This endpoint allows authenticated users to send the url of an image to be anlyze with Mistral to create an OA event.",
        response_model=ImageResponse)
async def upload_url(request: UrlRequest ,
                    current_user: dict = Depends(get_current_user)
                    ):
    if request.url is None:
        return {"success": False, "message": "Please provide a valid url"}
    try:
        response =api_utils.send_url_to_mistral(MISTRAL_PRIVATE_API_KEY=config.MISTRAL_PRIVATE_API_KEY.get_secret_value(),
                            access_token = oa.getToken(),
                            url=request.url,
                            OA_AGENDA_URL=config.OA_AGENDA_URL)
        if response.get("success") is False:
            raise HTTPException(status_code=400, detail=str(response.get("message")))
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=400, detail=str(f"{e}"))
