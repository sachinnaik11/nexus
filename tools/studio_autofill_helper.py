import os
import json
import time
import webbrowser
import pyperclip

REVAMPS_PATH = r"C:\Users\sachin naik\.gemini\antigravity\brain\1ab01de3-ed57-47ad-a57b-9d3c77f937d5\scratch\viral_revamps.json"

def get_revamp_packages():
    if os.path.exists(REVAMPS_PATH):
        with open(REVAMPS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def open_video_in_studio(video_id: str, copy_title: bool = True):
    packages = get_revamp_packages()
    target = None
    for p in packages:
        if p.get("id") == video_id:
            target = p
            break
    
    if not target and packages:
        target = packages[0]

    if not target:
        return "No revamp packages found."

    url = f"https://studio.youtube.com/video/{target['id']}/edit"
    if copy_title:
        payload = f"{target['viral_title']}\n\n{target['retention_description']}"
        pyperclip.copy(target["viral_title"])
        webbrowser.open(url)
        return (
            f"Opened YouTube Studio for video '{target['id']}'.\n"
            f"Viral Title copied to clipboard: '{target['viral_title']}'\n"
            f"Press Ctrl+V in the title box, then Save!"
        )
    return f"Opened {url}"

if __name__ == "__main__":
    packages = get_revamp_packages()
    print(f"Loaded {len(packages)} viral packages.")
    for p in packages:
        print(f"[{p['id']}] {p['viral_title']}")
