from typing import Optional, Union

import os
from pprint import pprint
from .api_utils import  get_event_keywords, generate_kl_token, verify_kl_token, db, get_user_by_username, verify_password
from api.script.libs.HttpRequests import patch_event
from api.script.configuration import config, oa
from api.script.mistral_images import getMistralImageEvent, postImageToImgbb, postMistralEventToOa, mistralEvent
from api.script.libs.oa_types import OpenAgendaEvent

from api.db import initialize_database, db_path
from fastapi import FastAPI, Depends, HTTPException, Header, File, UploadFile
from pydantic import BaseModel
from typing import List

# Check if the database file exists and initialize it if not

if not os.path.exists(db_path):
    initialize_database(db_path)
    print("Database initialized.")

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
from api.script.libs.oa_types import OpenAgendaEvent

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
    payload = verify_kl_token(token)
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
    print(request)
    username = request.username
    password = request.password

    # Check if the username and password are correct
    result = get_user_by_username(db, username)
    if result is None or not verify_password(result[1], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = result[0]
    token = generate_kl_token(user_id)
    return {"success": True, "access_token": token, "token_type": "Bearer"}

@app.get("/auth/oatoken", 
        summary="Retrieve OpenAgenda Auth Token",
        description="This endpoint returns an OpenAgenda token, using the OA_SECRET_KEY on serverfor\
            Requires a manually added users in Kerlandrier API DB.",
        response_model=OaToken)
async def generates_token(current_user: dict 
                        = Depends(get_current_user)):
    print(current_user)
    try:
        access_token = oa.access_token
        if (access_token == None):
            return {"success": False, "message": "No access token"}
        else:
            return {"success": True,
                    "access_token": access_token,
                    "message": "Access token retrieved successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    

@app.patch("/event/keywords",
            summary="Update event keywords",
            description="This endpoint updates the keywords for on OA event\
                It returns the updated OA event",
            response_model=dict)
async def update_event(request: PatchKeywordRequest, current_user: dict = Depends(get_current_user)):
    try:
        access_token = oa.access_token
        print("access_token", access_token)
    except Exception as e:
        return {"success": False, "data": [], "message": str(e)}
    event = request
    try:
        existingKeywords = await get_event_keywords(event.uid)
        if existingKeywords is None or existingKeywords != event.keywords:
            patched = await patch_event(access_token, event.uid, event.keywords)
            print(f"{existingKeywords} >>>> {event.keywords}")
            return {"success": True, "data": patched, "message": "Event successfully updated"}
        else:
            print("Keywords haven't changed")
            return {"success": True, "data": [], "message": "No update"}
    except Exception as e:
        print(e)
        return {"success": False, "data": [], "message": str(e)}

@app.post("/upload/image/",
        summary="Upload an image file of a poster with event",
        description="This endpoint allows authenticated users to upload an image file to be anlyze with Mistral to create an OA event.",
        response_model=dict)
async def upload_file(file: UploadFile, current_user: dict = Depends(get_current_user)):
    # Define the directory to save the uploaded file
    try:
        upload_dir = "images"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the uploaded file to the directory
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error while saving image file"}

    try:
        image_url = postImageToImgbb(image_path=file_path, imgbb_api_url = config.IMGBB_API_URL, imgbb_api_key = config.IMGBB_PRIVATE_API_KEY.get_secret_value() )
        response_mistral:mistralEvent = getMistralImageEvent(config.MISTRAL_PRIVATE_API_KEY.get_secret_value(), image_path=file_path)
        print("Mistral answer:")
        pprint(response_mistral.model_dump(mode='json'))
        OAevent:OpenAgendaEvent = postMistralEventToOa(response_mistral, access_token=oa.access_token, image_url= image_url)
        if OAevent.uid:
            event_url= f"https://openagenda.com/fr/{config.AGENDA_SLUG}/events/{OAevent.slug}"
            print(f"OA event created: {OAevent.title.fr} at {OAevent.location.name}")
            return {"success": True, "message": "File uploaded successfully", "OAeventURL": event_url, "OAeventName": OAevent.title.fr}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error generating event from image file"}

