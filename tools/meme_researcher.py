# ============================================================
# NEXUS — MEME TREND & CONTENT RESEARCH ENGINE
# Live Web Search + Gemini 3.5 for Viral Meme Formats & Competitor Insights
# ============================================================

import os
import json
import logging
from typing import Dict, Any, List

from tools.youtube_manager import _query_ai
from tools.meme_channel_db import meme_db

logger = logging.getLogger("NexusMemeResearcher")


class MemeContentResearcher:
    """
    Researches viral meme formats, trending audio concepts, and relatable
    comedy hooks specifically tailored for MemesWorld21.
    Distinguishes verified current internet trends from evergreen meme formats.
    """

    def __init__(self):
        self.profile = meme_db.get_profile()

    def _fetch_live_web_trends(self, query: str = "viral meme trends relatable comedy 2026") -> str:
        """Search DuckDuckGo for live internet meme trends."""
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=4))
                if results:
                    snippets = [f"- {r.get('title')}: {r.get('body')}" for r in results]
                    return "\n".join(snippets)
        except Exception as e:
            logger.warning(f"Live web search fallback: {e}")
        return "Recent viral themes: POV college/office struggles, expectation vs reality, awkward public moments, sleep schedule memes."

    def research_trending_memes(self, custom_theme: str = None) -> Dict[str, Any]:
        """
        Conduct deep viral research tailored for MemesWorld21.
        Returns:
        1. Verified Current Internet Trends
        2. Evergreen Relatable Meme Angles
        3. Algorithm Virality Reasoning (Why it gets views & comments)
        4. 3 Actionable Ready-to-Produce Meme Concepts
        """
        profile = meme_db.get_profile()
        theme_clause = f"Focus on this specific sub-theme: '{custom_theme}'" if custom_theme else "Search broadly across relatable young-adult and student life."

        live_context = self._fetch_live_web_trends(
            f"viral memes {custom_theme or 'relatable comedy shorts'}"
        )

        prompt = f"""
You are the Chief Creative Director for '{profile.get('channel_name', 'MemesWorld21')}'.
Channel Niche: {profile.get('niche', 'Viral Memes & Relatable Comedy')}
Target Audience: {profile.get('target_audience', 'Young adults 18-35')}
{theme_clause}

Recent Web Search Findings:
{live_context}

Provide a comprehensive Meme Research Report with:
1. 🔥 VERIFIED CURRENT TRENDING FORMATS:
   - Identify 2 formats dominating YouTube Shorts / TikTok right now (e.g. "POV:", "My honest reaction to...", "Bro really thought...")
   - Explain the specific sound design or audio punchline typically paired with it.

2. 🧠 ALGORITHM & RETENTION ANALYSIS (Why it goes viral):
   - Explain the exact viewer psychology behind these formats (e.g., looping trick, curiosity gap, triggering viewer comments like 'Tag a friend').

3. 🌲 2 EVERGREEN RELATABLE TOPICS:
   - High-performing situations that always work (sleep deprivation, exam stress, pretending to work, fake scenarios in head).

4. 💡 3 HIGH-PRIORITY ACTIONABLE MEME SHORT IDEAS:
   - For each idea, give: Title, 3-Second Opening Hook, and the Punchline Twist.

Format the response in clean, high-impact markdown for the creator HUD.
"""
        report_text = _query_ai(prompt)

        return {
            "channel_name": profile.get("channel_name", "MemesWorld21"),
            "theme": custom_theme or "Broad Viral Memes",
            "report_markdown": report_text,
            "live_context_used": live_context[:250],
        }


# Global singleton instance
meme_researcher = MemeContentResearcher()
