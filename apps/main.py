from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv

# Load API keys from your .env file
load_dotenv()

app = FastAPI(
    title="Pi-SocialMedia-Poster",
    description="Self-hosted FastAPI social media cross-poster for Raspberry Pi",
    version="1.0.0"
)

# --- Data Models ---
class PostContent(BaseModel):
    message: str
    image_url: Optional[str] = None
    platforms: List[str]  # e.g., ["twitter", "linkedin", "mastodon"]

class PostResponse(BaseModel):
    platform: str
    status: str
    post_id: Optional[str] = None
    error: Optional[str] = None

# --- Mock Platform Posting Functions ---
# (We will flesh these out with the actual API logic next)

async def post_to_twitter(content: PostContent) -> PostResponse:
    # TODO: Add Tweepy / X API v2 logic here
    return PostResponse(platform="twitter", status="success", post_id="mock_id_123")

async def post_to_linkedin(content: PostContent) -> PostResponse:
    # TODO: Add LinkedIn API logic here
    return PostResponse(platform="linkedin", status="success", post_id="mock_id_456")

# --- Routes ---
@app.get("/")
async def health_check():
    return {"status": "online", "message": "Pi-SocialMedia-Poster is ready."}

@app.post("/api/post", response_model=List[PostResponse])
async def create_cross_post(content: PostContent):
    results = []
    
    for platform in content.platforms:
        platform_lower = platform.lower()
        
        try:
            if platform_lower == "twitter":
                res = await post_to_twitter(content)
                results.append(res)
            elif platform_lower == "linkedin":
                res = await post_to_linkedin(content)
                results.append(res)
            # Add more platforms here as we build them out
            else:
                results.append(PostResponse(
                    platform=platform, 
                    status="failed", 
                    error="Platform not supported or disabled."
                ))
        except Exception as e:
            results.append(PostResponse(
                platform=platform, 
                status="failed", 
                error=str(e)
            ))
            
    return results

if __name__ == "__main__":
    # Runs the server on port 8000, accessible across your local network
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
