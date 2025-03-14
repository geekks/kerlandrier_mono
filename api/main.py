from typing import Optional, Union

from utils import retrieve_OA_access_token, get_event_keywords, patch_event, generate_token, verify_token, db, get_user_by_username, verify_password
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import List

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

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

def get_token_header(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.split(" ")[1]

def get_current_user(token: str = Depends(get_token_header)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@app.get("/auth")
async def authenticate(request: AuthRequest):
    username = request.username
    password = request.password

    # Check if the username and password are correct
    result = get_user_by_username(db, username)
    if result is None or not verify_password(result[1], password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = result[0]
    token = generate_token(user_id)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
async def read_root(current_user: dict = Depends(get_current_user)):
    print(current_user)
    try:
        access_token = await retrieve_OA_access_token()
        if (access_token == None):
            return {"success": False, "message": "No access token"}
        else:
            return {"success": True, "message": "Access token retrieved successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    

@app.patch("/events/keywords")
async def update_events(request: PatchRequest):
    print(request)
    try:
        access_token = await retrieve_OA_access_token()
    except Exception as e:
        return {"success": False, "message": str(e)}
    
    updated_events = []
    print(request.events)
    for event in request.events:
        print(event)
        try:
            test = await get_event_keywords(event.uid)
            if test != event.keywords:
                patched = await patch_event(access_token, event.uid, event.keywords)
                updated_events.append(patched['event']['slug'])
                print(f"{test} >>>> {event.keywords}")
            else:
                print("Keywords haven't changed")
        except Exception as e:
            print(e)
            return {"success": False, "message": str(e)}

    if len(updated_events) > 0:
        return {"success": True, "message": f"{len(updated_events)} events updated successfully", "updated_events": updated_events}
    else:
        return {"success": True, "message": "No update"}

