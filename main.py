from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return url

@app.post("/api/extract-video")
async def extract_and_summarize(req: VideoRequest):
    try:
        video_id = extract_video_id(req.url)
        
        # YouTube Transcript ဆွဲယူခြင်း
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'my'])
        full_text = " ".join([item['text'] for item in transcript_list])
        
        # Gemini AI ဖြင့် မြန်မာ Movie Recap Script ဖန်တီးခြင်း
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Summarize this video transcript into an engaging Myanmar voiceover recap script. Keep it concise, dramatic, and naturally spoken in Myanmar language:\n\n{full_text}"
        response = model.generate_content(prompt)
        
        return {
            "status": "success",
            "video_id": video_id,
            "direct_video_url": f"https://www.youtube.com/embed/{video_id}?autoplay=1",
            "myanmar_script": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

