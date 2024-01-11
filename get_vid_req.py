import requests
import os
url = 'http://192.168.0.130:8000/download-video'  
video_name = '1.mp4'  
download_folder = 'downloaded_videos'  
try:
    response = requests.get(f'{url}/{video_name}')
    if response.status_code == 200:
        os.makedirs(download_folder, exist_ok=True)  
        video_path = os.path.join(download_folder, video_name)
        with open(video_path, 'wb') as f:
            f.write(response.content)
        print(f"Video '{video_name}' downloaded successfully and stored in '{download_folder}' folder.")
    else:
        print("Error:", response.text)
except requests.exceptions.RequestException as e:
    print("Error sending request:", e)
