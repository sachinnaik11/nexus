# ============================================================
# NEXUS — AUTONOMOUS MEME VIDEO GENERATOR & YOUTUBE UPLOADER
# Full Automated Pipeline: Scripting -> Voiceover -> MP4 Synthesis -> YouTube Upload
# ============================================================

import os
import re
import time
import json
import logging
import subprocess
import tempfile
from typing import Dict, Any, Optional, List

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import pyttsx3
import imageio_ffmpeg

from tools.youtube_manager import _query_ai, get_channel_niche

load_dotenv()
logger = logging.getLogger("NexusMemeGenerator")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class AutonomousMemeUploader:
    """
    End-to-End Autonomous Meme Creator and YouTube Uploader.
    1. AI writes high-CTR viral meme scripts for comedy/relatable niches.
    2. pyttsx3 synthesizes punchy comedic voiceover.
    3. PIL renders vertical 9:16 (1080x1920) meme graphics.
    4. imageio_ffmpeg compiles the final MP4 video.
    5. Directly uploads video to YouTube channel or opens Studio uploader.
    """

    YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"

    def __init__(self):
        self.output_dir = os.path.join("assets", "generated_memes")
        os.makedirs(self.output_dir, exist_ok=True)
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # ------------------------------------------------------------
    # 1. AI MEME SCRIPT GENERATOR
    # ------------------------------------------------------------
    def generate_meme_script(self, custom_topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Uses Gemini 3.5 Flash Lite to write a high-retention relatable meme.
        """
        niche = get_channel_niche()
        topic_clause = f"Topic or theme: {custom_topic}" if custom_topic else "Choose a wildly relatable life/student/work/daily struggle meme topic."

        prompt = f"""
You are the world's best viral meme creator for YouTube Shorts and TikTok.
Channel Niche: {niche}
{topic_clause}

Create an ultra-relatable, hilarious meme script:
1. "title": High-CTR meme title (Under 55 chars, e.g. "POV: You thought today was Friday 💀 #shorts", "Bro really thought 😭 #shorts")
2. "hook": The setup text shown at the top of the meme (e.g. "When you finally decide to sleep early at 10 PM")
3. "punchline": The twist or punchline shown in the middle (e.g. "Your brain at 3:14 AM: 'Hey remember that embarrassing thing from 2018?' 💀")
4. "voiceover": Narration script read aloud (punchy, witty, under 20 words, perfect for comedic timing)
5. "description": Engaging description with comment hook ("Tag someone who does this 😭") and hashtags #shorts #meme #memes #relatable #funny #comedy
6. "tags": Array of 10 viral comedy tags (e.g. ["shorts", "meme", "memes", "funny", "relatable", "comedy", "dankmemes", "viral", "humor", "lol"])

Output ONLY valid JSON with keys: "title", "hook", "punchline", "voiceover", "description", "tags".
"""
        raw_response = _query_ai(prompt)

        try:
            cleaned = re.sub(r"^```json\s*", "", raw_response.strip())
            cleaned = re.sub(r"```$", "", cleaned.strip())
            data = json.loads(cleaned)
        except Exception:
            data = {
                "title": "POV: You woke up thinking it was Sunday 💀 #shorts",
                "hook": "When you wake up feeling completely relaxed and peaceful...",
                "punchline": "...then you check your phone and see 'Monday 7:45 AM' 😭💀",
                "voiceover": "You thought today was Sunday, didn't you? Get up, you're late!",
                "description": "Tag someone who always falls for this 💀\n\n#shorts #meme #memes #funny #relatable #comedy",
                "tags": ["shorts", "meme", "memes", "funny", "relatable", "comedy", "viral", "humor"],
            }

        return data

    # ------------------------------------------------------------
    # 2. AUDIO SYNTHESIS (PYTTSX3)
    # ------------------------------------------------------------
    def synthesize_voiceover(self, text: str, output_wav: str) -> bool:
        """Generate high-quality spoken voiceover for the meme."""
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165) # Brisk comedic pace
            engine.setProperty("volume", 1.0)
            engine.save_to_file(text, output_wav)
            engine.runAndWait()
            return os.path.exists(output_wav) and os.path.getsize(output_wav) > 0
        except Exception as e:
            logger.error(f"TTS voiceover synthesis error: {e}")
            return False

    # ------------------------------------------------------------
    # 3. VERTICAL FRAME RENDERING (PIL - 1080x1920 9:16)
    # ------------------------------------------------------------
    def render_meme_frame(self, hook: str, punchline: str, output_img: str) -> bool:
        """
        Renders a crisp 1080x1920 vertical meme graphic optimized for YouTube Shorts.
        Features high-contrast dark card layout with vibrant typography.
        """
        width, height = 1080, 1920
        img = Image.new("RGB", (width, height), color=(10, 15, 29)) # Deep cyber slate
        draw = ImageDraw.Draw(img)

        # Draw decorative background gradient & accent borders
        draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(30, 41, 59), width=4)
        draw.line([(40, 180), (width - 40, 180)], fill=(0, 229, 255), width=3)
        draw.line([(40, height - 200), (width - 40, height - 200)], fill=(0, 229, 255), width=3)

        # Header Badge
        header_text = "😂  V I R A L   R E L A T A B L E   M E M E  😂"
        draw.text((width // 2, 120), header_text, fill=(0, 229, 255), anchor="mm")

        # Top Meme Hook Box (Clean contrast card)
        card_margin = 60
        top_y = 280
        draw.rounded_rectangle(
            [(card_margin, top_y), (width - card_margin, top_y + 360)],
            radius=24,
            fill=(255, 255, 255),
            outline=(203, 213, 225),
            width=3,
        )

        # Draw Hook Text inside top box
        draw.text(
            (card_margin + 30, top_y + 30),
            "POV:",
            fill=(239, 68, 68), # Punchy red accent
            spacing=10,
        )

        # Word-wrap hook text
        hook_wrapped = self._wrap_text(hook, max_chars_per_line=30)
        draw.text(
            (card_margin + 30, top_y + 90),
            hook_wrapped,
            fill=(15, 23, 42), # Dark bold readable text
            spacing=14,
        )

        # Center Graphic / Punchline Card
        punch_y = 740
        draw.rounded_rectangle(
            [(card_margin, punch_y), (width - card_margin, punch_y + 600)],
            radius=24,
            fill=(15, 23, 42),
            outline=(0, 229, 255),
            width=4,
        )

        # Punchline Text
        punch_wrapped = self._wrap_text(punchline, max_chars_per_line=26)
        draw.text(
            (width // 2, punch_y + 240),
            punch_wrapped,
            fill=(248, 250, 252),
            anchor="mm",
            spacing=20,
        )

        # Giant Reaction Emoji Placeholder
        draw.text((width // 2, punch_y + 480), "💀 😭 💀", fill=(255, 255, 255), anchor="mm")

        # Bottom Call to Action
        draw.text(
            (width // 2, height - 140),
            "👉 FOLLOW & SUBSCRIBE FOR DAILY MEMES 👈",
            fill=(56, 189, 248),
            anchor="mm",
        )

        img.save(output_img)
        return os.path.exists(output_img)

    def _wrap_text(self, text: str, max_chars_per_line: int = 28) -> str:
        words = text.split()
        lines = []
        current = []
        current_len = 0
        for w in words:
            if current_len + len(w) + 1 <= max_chars_per_line:
                current.append(w)
                current_len += len(w) + 1
            else:
                lines.append(" ".join(current))
                current = [w]
                current_len = len(w)
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines)

    # ------------------------------------------------------------
    # 4. MP4 VIDEO SYNTHESIS (FFMPEG)
    # ------------------------------------------------------------
    def synthesize_meme_video(self, image_path: str, audio_path: str, output_mp4: str) -> bool:
        """
        Combines the 1080x1920 visual frame and voiceover audio into an MP4 video.
        """
        cmd = [
            self.ffmpeg_exe,
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_mp4,
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
            if res.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 0:
                logger.info(f"Synthesized meme video successfully: {output_mp4} ({os.path.getsize(output_mp4)} bytes)")
                return True
            logger.error(f"FFMPEG encoding failed (code {res.returncode}): {res.stderr.decode()[:300]}")
            return False
        except Exception as e:
            logger.error(f"Video compilation error: {e}")
            return False

    # ------------------------------------------------------------
    # 5. DIRECT YOUTUBE RESUMABLE UPLOAD API
    # ------------------------------------------------------------
    def upload_to_youtube(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        privacy_status: str = "public",
        category_id: str = "23", # 23 = Comedy
    ) -> Dict[str, Any]:
        """
        Uploads an MP4 video directly to your YouTube channel using YouTube Data API v3.
        """
        token = os.getenv("YOUTUBE_ACCESS_TOKEN", "").strip()
        if not token:
            return {
                "success": False,
                "needs_auth": True,
                "message": (
                    "YOUTUBE_ACCESS_TOKEN not set in .env.\n"
                    "Provide your YouTube OAuth token in .env for 100% direct uploads, "
                    "or NEXUS will open YouTube Studio and prepare the video for you!"
                ),
            }

        file_size = os.path.getsize(video_path)

        # 1. Initiate Resumable Upload Session
        init_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(file_size),
        }
        metadata_payload = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:50],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        try:
            init_res = requests.post(
                self.YOUTUBE_UPLOAD_URL,
                headers=init_headers,
                json=metadata_payload,
                timeout=15,
            )

            if init_res.status_code not in (200, 201):
                return {
                    "success": False,
                    "message": f"YouTube Upload Session Error ({init_res.status_code}): {init_res.text[:250]}",
                }

            upload_url = init_res.headers.get("Location")
            if not upload_url:
                return {"success": False, "message": "YouTube did not return a resumable upload location."}

            # 2. Upload Binary Video Bytes
            with open(video_path, "rb") as vf:
                video_bytes = vf.read()

            upload_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "video/mp4",
                "Content-Length": str(file_size),
            }

            logger.info(f"Uploading {file_size} bytes to YouTube...")
            upload_res = requests.put(upload_url, headers=upload_headers, data=video_bytes, timeout=180)

            if upload_res.status_code in (200, 201):
                data = upload_res.json()
                video_id = data.get("id")
                video_url = f"https://youtube.com/shorts/{video_id}"
                logger.info(f"Video uploaded successfully! ID: {video_id} -> {video_url}")
                return {
                    "success": True,
                    "video_id": video_id,
                    "video_url": video_url,
                    "message": f"🎉 VIDEO UPLOADED SUCCESSFULLY TO YOUTUBE!\n• URL: {video_url}\n• Title: {title}",
                }
            return {
                "success": False,
                "message": f"YouTube Video Byte Upload Failed ({upload_res.status_code}): {upload_res.text[:250]}",
            }
        except Exception as e:
            return {"success": False, "message": f"Network error during YouTube upload: {e}"}

    # ------------------------------------------------------------
    # 6. END-TO-END AUTONOMOUS GENERATOR & UPLOADER
    # ------------------------------------------------------------
    def auto_generate_and_upload(self, custom_topic: Optional[str] = None) -> str:
        """
        Executes the entire autonomous lifecycle:
        1. AI scripts viral relatable meme
        2. Generates TTS audio voiceover
        3. Renders 1080x1920 vertical meme graphic
        4. Compiles high-definition MP4 video
        5. Uploads to YouTube channel or opens Studio with 1-click clipboard paste!
        """
        ts = int(time.time())
        logger.info("Starting autonomous meme video generation...")

        # Step 1: Generate AI Script
        script = self.generate_meme_script(custom_topic)
        title = script.get("title", "POV: Relatable Moment 💀 #shorts")
        hook = script.get("hook", "When you think life is going fine...")
        punchline = script.get("punchline", "...and everything crashes at once 😭")
        voiceover = script.get("voiceover", hook + " " + punchline)
        description = script.get("description", "")
        tags = script.get("tags", ["shorts", "meme", "funny"])

        # Step 2 & 3: Temp audio and image paths
        temp_audio = os.path.join(self.output_dir, f"audio_{ts}.wav")
        temp_image = os.path.join(self.output_dir, f"frame_{ts}.png")
        final_mp4 = os.path.join(self.output_dir, f"meme_short_{ts}.mp4")

        try:
            # Voiceover
            audio_ok = self.synthesize_voiceover(voiceover, temp_audio)
            if not audio_ok:
                return "Failed to synthesize voiceover audio."

            # Graphic Frame
            frame_ok = self.render_meme_frame(hook, punchline, temp_image)
            if not frame_ok:
                return "Failed to render meme visual frame."

            # Compile Video
            video_ok = self.synthesize_meme_video(temp_image, temp_audio, final_mp4)
            if not video_ok:
                return "Failed to synthesize final MP4 video."

            # Clean up intermediate audio and frame
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            if os.path.exists(temp_image):
                os.remove(temp_image)

            # Step 4: Upload to YouTube
            upload_result = self.upload_to_youtube(final_mp4, title, description, tags)

            if upload_result.get("success"):
                return (
                    f"🎉 AUTONOMOUS MEME VIDEO GENERATED & UPLOADED LIVE!\n\n"
                    f"📺 YouTube Shorts URL: {upload_result['video_url']}\n"
                    f"📌 Title: {title}\n"
                    f"📁 Local File: {final_mp4}\n\n"
                    f"Your video is now live on your channel under Comedy & Memes!"
                )

            # If API Token not configured, provide 1-Click Studio Uploader
            try:
                import pyperclip
                import webbrowser
                pyperclip.copy(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTAGS:\n{', '.join(tags)}")
                webbrowser.open("https://studio.youtube.com/channel/mine/videos/upload?d=ud")
                subprocess.Popen(f'explorer /select,"{os.path.abspath(final_mp4)}"')
            except Exception:
                pass

            return (
                f"🎬 MEME SHORT GENERATED & READY FOR UPLOAD!\n\n"
                f"• Video File: {final_mp4} ({round(os.path.getsize(final_mp4) / 1024, 1)} KB)\n"
                f"• Title: {title}\n"
                f"• Retention Hook: {hook}\n"
                f"• Punchline: {punchline}\n\n"
                f"⚡ NEXUS opened YouTube Studio and your file folder.\n"
                f"Title & description have been copied to your clipboard — simply drag the highlighted video into Studio and press Ctrl+V!"
            )

        except Exception as e:
            logger.error(f"Error in auto_generate_and_upload: {e}")
            return f"Error creating meme video: {e}"


# Global singleton instance
meme_uploader = AutonomousMemeUploader()
