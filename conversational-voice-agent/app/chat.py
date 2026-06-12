import os
import subprocess
import sys
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from livekit import api
from dotenv import load_dotenv

# Load workspace environment variables
load_dotenv()

app = FastAPI(title="Unified Voice Agent Bridge")

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
    raise ValueError("Missing critical LiveKit configurations inside your local .env file.")

class TokenRequest(BaseModel):
    room_name: str
    identity: str

@app.post("/api/get-token")
async def get_token(request: TokenRequest):
    """Generates the secure gateway token required for the UI client."""
    try:
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(request.identity) \
            .with_name(request.identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=request.room_name,
            ))
        
        return {
            "token": token.to_jwt(),
            "server_url": LIVEKIT_URL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Reads and serves the index.html user interface layout dynamically."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "index.html")
    try:
        with open(html_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"index.html layout target not found at: {html_path}")

# SYSTEM STARTUP AUTOMATION LAYER
@app.on_event("startup")
async def launch_agent_worker():
    """
    Automatically intercept runtime startup to spin up 'main.py' 
    in a non-blocking background process execution thread.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(current_dir, "main3.py")
    
    if not os.path.exists(main_py_path):
        print(f"\n[CRITICAL ERROR] 'main.py' could not be found at: {main_py_path}")
        return

    print("\n========================================================")
    print("[SYSTEM] Launching target voice worker 'main.py dev'...")
    print("========================================================\n")
    
    # Executing using current python platform path matrix configuration
    subprocess.Popen(
        [sys.executable, main_py_path, "dev"],
        stdout=sys.stdout, 
        stderr=sys.stderr
    )
    
    # Safe system timing buffer to allow your pipeline instances to link up to LiveKit cloud
    time.sleep(2)
    print("\n[SYSTEM] LiveKit background pipeline linked and active.\n")

if __name__ == "__main__":
    import uvicorn
    # reload=False is mandatory here. If set to True, uvicorn file-watchers will clone 
    # multiple duplicate instances of main.py whenever you save a file, breaking port mappings.
    uvicorn.run("chat.py:app", host="0.0.0.0", port=8000, reload=False)