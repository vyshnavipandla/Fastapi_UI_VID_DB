import os
import sqlite3
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
conn = sqlite3.connect("videos.db")
video_folder = "E:/VS_mtt/static/uploaded_videos"
os.makedirs(video_folder, exist_ok=True)

class Video:
    def __init__(self, id, videoname):
        self.id = id
        self.videoname = videoname

def get_next_video_id(cursor):
    cursor.execute("SELECT MAX(id) FROM vid_tab")
    max_id = cursor.fetchone()[0]
    return max_id + 1 if max_id else 1

def update_video_order(cursor):
    cursor.execute("""
        UPDATE vid_tab
        SET id = rowid
    """)
    conn.commit()

@app.get("/upload")
async def upload_page(request: Request):
    cursor = conn.cursor()
    cursor.execute("SELECT id, videoname FROM vid_tab ORDER BY id")
    videos_data = cursor.fetchall()
    videos = [Video(id, videoname) for id, videoname in videos_data]
    return templates.TemplateResponse("vid_upload.html", {"request": request, "videos": videos})

@app.post("/upload")
async def upload_video(request: Request, videoname: str = Form(...), video: UploadFile = File(...)):
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM vid_tab WHERE videoname = ?", (videoname,))
        existing_video = cursor.fetchone()
        if existing_video:
            #raise HTTPException(status_code=409, detail="Video name already exists. Please choose a different name.")
            return templates.TemplateResponse("vid_upload.html", {"request": request,"message": "video name alreday exists. please choose a different name."})

        extension = os.path.splitext(video.filename)[1]
        video_id = get_next_video_id(cursor)
        new_video_name = f"{video_id}{extension}"
        video_path = os.path.join(video_folder, new_video_name)
        cursor.execute("INSERT INTO vid_tab (id, videoname, videopath) VALUES (?, ?, ?)", (video_id, videoname, video_path))
        conn.commit()
        with open(video_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)
        update_video_order(cursor)
        cursor.execute("SELECT id, videoname FROM vid_tab ORDER BY id")
        videos_data = cursor.fetchall()
        videos = [Video(id, videoname) for id, videoname in videos_data]
        return templates.TemplateResponse("vid_upload.html", {"request": request, "videos": videos, "message": "Video uploaded successfully"})
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        cursor.close()

@app.post("/delete/{video_id}")
async def delete_video(request: Request, video_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT videopath FROM vid_tab WHERE id = ?", (video_id,))
        video_path = cursor.fetchone()[0] 
        cursor.execute("DELETE FROM vid_tab WHERE id = ?", (video_id,))
        conn.commit()
        os.remove(video_path) 
        update_video_order(cursor)
        return RedirectResponse("/upload", status_code=303)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error deleting video: {e}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Video file not found")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Error deleting video file: {e}")
    finally:
        cursor.close()
