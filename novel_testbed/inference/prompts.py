"""
Prompt templates for LLM-based contract inference.
"""

from __future__ import annotations

from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """
    You are a narrative analyst that outputs ONLY valid JSON.
    Do not include commentary, markdown, or extra keys.
    """
).strip()


def build_module_prompt(*, novel_title: str, chapter: str, module_title: str, module_text: str) -> str:
    """
    Build the user prompt for a module inference request.

    :param novel_title: Title of the novel.
    :param chapter: Chapter name.
    :param module_title: Module title.
    :param module_text: Full module body text.
    :return: Prompt string.
    """
    return dedent(
        f"""
        Novel: {novel_title}
        Chapter: {chapter}
        Module: {module_title}

        TASK
        Infer the module's narrative intent and reader-state outcome.

        OUTPUT JSON SCHEMA (exact keys only):
        {{
          "expected_changes": ["..."],
          "post_state": {{
            "genre": "string|null",
            "power_balance": "string|null",
            "emotional_tone": "string|null",
            "dominant_fantasy_id": "string|null",
            "threat_level": number|null,
            "agency_level": number|null
          }},
          "confidence": number,
          "notes": {{}}
        }}

        RULES
        - expected_changes must be a list of short strings (3-8 words each).
        - threat_level and agency_level are 0..1 if present.
        - confidence is 0..1.
        - If uncertain, use null fields and lower confidence.
        - Output ONLY JSON.

        MODULE TEXT
        {module_text}
        """
    ).strip()