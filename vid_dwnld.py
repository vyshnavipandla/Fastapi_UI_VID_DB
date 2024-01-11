from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
import uvicorn
app = FastAPI()
@app.get("/download-video/{video_name}")
async def download_video(video_name: str):
    video_path = f"uploaded_videos/{video_name}"  
    if os.path.exists(video_path):
        return FileResponse(path=video_path, media_type="video/mp4", filename=video_name)
    else:
        return {"error": "Video not found"}
if __name__=="__main__":
    uvicorn.run(app)
