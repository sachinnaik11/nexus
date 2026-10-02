# ============================================================
# NEXUS — FULL MEME VIDEO PRODUCTION SUITE
# Hook, Scene-by-Scene Storyboard, CapCut Editing Guide, Metadata & Checklist
# ============================================================

import os
import re
import json
import logging
from typing import Dict, Any, Optional

from tools.youtube_manager import _query_ai
from tools.meme_channel_db import meme_db
from tools.meme_generator import meme_uploader

logger = logging.getLogger("NexusMemeProduction")


class MemeProductionSuite:
    """
    Takes any meme idea (or topic) and generates an exhaustive, professional
    production blueprint tailored for MemesWorld21.
    """

    def generate_full_production_package(
        self,
        concept_or_idea_title: str,
        idea_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates a complete 7-part production package:
        1. 3-Second Visual Retention Hook
        2. Scene-by-Scene Storyboard (0-3s, 3-7s, 7-11s, 11-15s)
        3. CapCut / Editor Notes (sound effects, cuts, font styling)
        4. Three High-CTR Titles with psychology breakdown
        5. Retention-Optimized Description & Tags
        6. Thumbnail / Cover Frame Concept
        7. Pre-Upload Checklist
        """
        profile = meme_db.get_profile()
        channel_name = profile.get("channel_name", "MemesWorld21")
        target_audience = profile.get("target_audience", "Young adults (18-35)")

        notes_clause = f"Additional Creator Notes: {idea_notes}" if idea_notes else ""

        prompt = f"""
You are the Executive Producer for YouTube Meme Channel '{channel_name}'.
Channel Focus: {profile.get('niche', 'Viral Memes & Relatable Comedy')}
Target Audience: {target_audience}

Meme Concept to Produce:
"{concept_or_idea_title}"
{notes_clause}

Generate an exhaustive, ready-to-shoot YouTube Shorts production package:

### 1. 🪝 3-SECOND RETENTION HOOK
- Visual Opening (Exact frame description):
- On-Screen Big Text:
- Opening Audio/Voiceover Hook:

### 2. 🎬 SCENE-BY-SCENE STORYBOARD (15s Total)
- [00:00 - 00:03] Scene 1 (The Hook): Action + On-screen text
- [00:03 - 00:07] Scene 2 (The Setup / Expectation): Action + Dialogue
- [00:07 - 00:11] Scene 3 (The Twist / Reality Check): Action + Reaction
- [00:11 - 00:15] Scene 4 (Punchline & Loop Trigger): Climax + End frame that smoothly loops back to start

### 3. ✂️ CAPCUT / VIDEO EDITOR DIRECTIVE
- Pacing & Jump Cuts (Timestamp cues):
- Sound Effects (SFX) Cues: (e.g., Vine boom, record scratch, dramatic silence, sad violin)
- Text Styling: (e.g. Classic meme font Arial Bold/Impact with black drop shadow, colored key words)
- Music Tone: (Trending background meme track suggestion)

### 4. 📌 THREE HIGH-CTR TITLE OPTIONS
1. Curiosity Hook: Title + [Why it clicks]
2. POV / Relatable Hook: Title + [Why it clicks]
3. Punchline / Reaction Hook: Title + [Why it clicks]

### 5. 📝 DESCRIPTION & VIRAL TAGS
- 2-Line Description with Comment Trigger:
- Hashtags: #shorts #meme #memes #relatable #funny #comedy
- Top 10 Algorithm Search Tags:

### 6. 🖼️ THUMBNAIL / FIRST-FRAME BRIEF
- The exact freeze-frame description for the Shorts thumbnail:

### 7. ✅ PRE-UPLOAD QUALITY CHECKLIST
- 4 critical checks before hitting publish:
"""
        response_text = _query_ai(prompt)

        return {
            "concept": concept_or_idea_title,
            "channel_name": channel_name,
            "production_package": response_text,
        }

    def render_video_for_concept(self, concept_title: str) -> str:
        """
        Directly renders a 1080x1920 MP4 video with voiceover using meme_uploader.
        """
        return meme_uploader.auto_generate_and_upload(concept_title)


# Global singleton instance
meme_production = MemeProductionSuite()
