"""
prompts.py — All prompt templates for the quiz generation pipeline.

Prompts are kept in one place so they're easy to:
- Find and improve
- A/B test different versions
- Version control separately from logic

PROMPT ENGINEERING NOTES:
- Be extremely specific about output format
- Show an example, don't just describe
- Explicitly state what NOT to do
- Use numbered constraints — models follow lists well
"""


QUIZ_GENERATION_PROMPT = """You are an expert educator and quiz designer with 20 years of experience creating assessments for university students.

Your task is to generate multiple-choice quiz questions based on the following video transcript.

## TRANSCRIPT:
{transcript}

## VIDEO TITLE (if available):
{video_title}

## YOUR TASK:
Generate exactly {num_easy} easy questions, {num_medium} medium questions, and {num_hard} hard questions.

## DIFFICULTY DEFINITIONS:
- EASY: Tests basic recall of facts explicitly stated in the transcript. Anyone who watched the video should answer correctly.
- MEDIUM: Tests understanding and ability to connect two or more concepts from the transcript.
- HARD: Tests deep analysis, inference, or application of concepts. Requires understanding the "why" not just the "what".

## STRICT RULES:
1. Every question MUST be answerable from the transcript content only. Do not use outside knowledge.
2. All 4 options must be plausible. Wrong options (distractors) should be believable, not obviously silly.
3. Never ask about timestamps, video duration, or "at minute X the speaker says...".
4. The correct_answer field must exactly match one of the 4 options word-for-word.
5. Explanations must reference the transcript content specifically.
6. Questions must be varied — do not ask similar things twice.
7. Do not number the options. Just write the text.

## REQUIRED OUTPUT FORMAT:
Return ONLY a valid JSON object. No explanation before or after. No markdown code blocks. No backticks.

The JSON must follow this exact structure:
{{
  "questions": [
    {{
      "question_text": "Write the question here as a complete sentence ending with ?",
      "options": [
        "First option text",
        "Second option text", 
        "Third option text",
        "Fourth option text"
      ],
      "correct_answer": "The exact text of the correct option",
      "difficulty": "easy",
      "explanation": "Explain why this answer is correct, referencing the transcript content."
    }}
  ]
}}

## EXAMPLE OF ONE GOOD QUESTION:
{{
  "question_text": "What is the primary reason the speaker recommends practicing a skill for 20 hours?",
  "options": [
    "To reach professional mastery in the field",
    "To overcome the initial frustration barrier and become competent enough to enjoy the activity",
    "To impress potential employers with the skill",
    "To qualify for advanced certification programs"
  ],
  "correct_answer": "To overcome the initial frustration barrier and become competent enough to enjoy the activity",
  "difficulty": "medium",
  "explanation": "The speaker explains that the first 20 hours of practice are about getting past the frustration of being a beginner, not about achieving mastery. The goal is to become good enough to actually enjoy the skill."
}}

Now generate the questions. Remember: return ONLY the JSON object, nothing else.
"""


RETRY_PROMPT = """Your previous response was not valid JSON or did not follow the required format.

Please try again. Return ONLY a valid JSON object with this exact structure:
{{
  "questions": [
    {{
      "question_text": "...",
      "options": ["...", "...", "...", "..."],
      "correct_answer": "...",
      "difficulty": "easy|medium|hard",
      "explanation": "..."
    }}
  ]
}}

Generate {num_easy} easy, {num_medium} medium, and {num_hard} hard questions from this transcript:

{transcript}

Return ONLY the JSON. No other text.
"""


CONNECTION_TEST_PROMPT = """Reply with exactly the word: CONNECTED"""