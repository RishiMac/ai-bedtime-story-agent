import os
import json
import openai
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
load_dotenv()

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

If I had two more hours, I would add a lightweight interactive feedback loop so the child
or parent could ask for changes like "make it funnier" or "make it shorter." I would also
add stronger safety checks for scary, violent, or age-inappropriate content before generation,
plus save multiple story versions so the judge could compare candidates and select the best one.
"""

MODEL_NAME = "gpt-3.5-turbo"
NUM_CANDIDATE_STORIES = 3

def call_model(prompt: str, max_tokens: int = 3000, temperature: float = 0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Please set it before running this script."
        )

    resp = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return resp.choices[0].message["content"].strip()  # type: ignore


def safe_json_loads(raw_text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and start < end:
            try:
                return json.loads(raw_text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


def safety_precheck(user_request: str) -> Dict[str, Any]:
    prompt = f"""
You are a safety classifier for a children's bedtime story generator.

Evaluate this user request:
"{user_request}"

Return ONLY valid JSON in this exact structure:
{{
  "status": "safe",
  "reason": "brief explanation",
  "safe_request": "safe rewritten version of the request if needed"
}}

Rules:
- status must be one of: "safe", "needs_softening", "unsafe"
- "safe" means the request is already appropriate for ages 5 to 10
- "needs_softening" means the idea can be rewritten into a gentle child-safe bedtime story
- "unsafe" means the request contains mature, violent, sexual, hateful, graphic, or otherwise inappropriate content
- If status is "safe", safe_request should be the original request
- If status is "needs_softening", safe_request should preserve the harmless parts while making it appropriate for ages 5 to 10
- If status is "unsafe", safe_request should be a gentle, unrelated child-safe bedtime story idea
"""

    raw = call_model(prompt, max_tokens=700, temperature=0.1)
    parsed = safe_json_loads(raw)

    if parsed is None:
        return {
            "status": "needs_softening",
            "reason": "Safety check could not be parsed, so the request was softened by default.",
            "safe_request": "A gentle bedtime story about kindness, friendship, and feeling safe at night.",
        }

    return parsed


def analyze_request(user_request: str) -> Dict[str, Any]:
    prompt = f"""
You are a bedtime story request analyzer.

Analyze this request for a children's bedtime story:
"{user_request}"

Return ONLY valid JSON with this structure:
{{
  "theme": "one short theme",
  "main_characters": ["character 1", "character 2"],
  "setting": "short setting",
  "tone": "calm/funny/adventurous/magical/etc",
  "lesson": "simple child-friendly lesson",
  "potential_risks": ["anything that may be scary, unsafe, or age-inappropriate"],
  "generation_strategy": "brief strategy for telling this story well for ages 5 to 10"
}}

Rules:
- The story must be appropriate for ages 5 to 10.
- Avoid violence, horror, adult themes, intense danger, or anything too scary.
- If the user request is vague, infer a safe and creative direction.
"""

    raw = call_model(prompt, max_tokens=800, temperature=0.1)
    parsed = safe_json_loads(raw)

    if parsed is None:
        return {
            "theme": "friendship",
            "main_characters": ["a kind child", "a helpful animal friend"],
            "setting": "a cozy neighborhood",
            "tone": "calm and magical",
            "lesson": "kindness and courage help solve problems",
            "potential_risks": [],
            "generation_strategy": "Use a gentle beginning, small problem, creative teamwork, and peaceful ending.",
        }

    return parsed


def build_story_prompt(user_request: str, analysis: Dict[str, Any], candidate_number: int) -> str:
    return f"""
You are a warm and imaginative bedtime storyteller for children ages 5 to 10.

Original user request:
"{user_request}"

Request analysis:
{json.dumps(analysis, indent=2)}

You are writing candidate story #{candidate_number}. Make this version distinct in wording, imagery, and magical details from other possible candidates.

Write a polished bedtime story that follows these requirements:

Audience:
- Ages 5 to 10
- Safe, gentle, positive, and easy to understand

Story structure:
- Clear beginning, middle, and ending
- Introduce the main character
- Create a small, non-scary problem
- Solve the problem through kindness, curiosity, teamwork, or courage
- End with a peaceful bedtime feeling

Style:
- Warm, vivid, and creative
- Use simple language
- Include light sensory details
- Add one unique imaginative or magical twist that makes the story memorable
- Give the main character a clear personality trait
- Avoid scary, violent, or mature content
- Length should be around 600 to 900 words
- Give the story a title

Include:
- A subtle lesson, not a lecture
- A cozy final paragraph that feels appropriate before sleep

Return only the story.
"""


def judge_story(user_request: str, story: str) -> Dict[str, Any]:
    prompt = f"""
You are an expert judge for children's bedtime stories.

Evaluate the story below for a child ages 5 to 10.

Original request:
"{user_request}"

Story:
\"\"\"
{story}
\"\"\"

Score the story from 1 to 10 in each category:
- age_appropriateness
- bedtime_tone
- creativity
- clarity
- request_following
- safety

Return ONLY valid JSON in this exact structure:
{{
  "age_appropriateness": 0,
  "bedtime_tone": 0,
  "creativity": 0,
  "clarity": 0,
  "request_following": 0,
  "safety": 0,
  "overall_score": 0,
  "passes": true,
  "feedback": "specific feedback for improvement"
}}

Passing rules:
- passes should be true only if overall_score is 8 or higher
- passes should be false if there is anything scary, violent, unsafe, confusing, or not appropriate for ages 5 to 10
"""

    raw = call_model(prompt, max_tokens=800, temperature=0.1)
    parsed = safe_json_loads(raw)

    if parsed is None:
        return {
            "age_appropriateness": 7,
            "bedtime_tone": 7,
            "creativity": 7,
            "clarity": 7,
            "request_following": 7,
            "safety": 7,
            "overall_score": 7,
            "passes": False,
            "feedback": "The judge response was not valid JSON, so revise the story to be clearer, safer, and more bedtime-focused.",
        }

    return parsed


def revise_story(user_request: str, story: str, judge_result: Dict[str, Any]) -> str:
    prompt = f"""
You are improving a children's bedtime story for ages 5 to 10.

Original request:
"{user_request}"

Original story:
\"\"\"
{story}
\"\"\"

Judge feedback:
{json.dumps(judge_result, indent=2)}

Revise the story so it:
- Better follows the user's request
- Is more age-appropriate
- Has a calmer bedtime tone
- Is clearer and more creative
- Avoids scary, violent, unsafe, or mature content
- Keeps a clear beginning, middle, and ending
- Ends peacefully

Return only the improved final story.
"""

    return call_model(prompt, max_tokens=3000, temperature=0.3)


def generate_candidate_stories(user_request: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = []

    for i in range(1, NUM_CANDIDATE_STORIES + 1):
        print(f"Generating candidate story {i}...")

        story_prompt = build_story_prompt(user_request, analysis, i)
        story = call_model(story_prompt, max_tokens=3000, temperature=0.7)

        print(f"Running judge for candidate story {i}...")
        judge = judge_story(user_request, story)

        candidates.append(
            {
                "candidate_number": i,
                "story": story,
                "judge": judge,
                "score": float(judge.get("overall_score", 0)),
            }
        )

    return candidates


def select_best_candidate(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    return max(candidates, key=lambda candidate: candidate["score"])


def generate_story(user_request: str) -> Dict[str, Any]:
    print("\nRunning safety pre-check...\n")
    safety = safety_precheck(user_request)

    safe_request = safety.get("safe_request", user_request)

    if safety.get("status") != "safe":
        print(f"Safety status: {safety.get('status')}")
        print(f"Safety note: {safety.get('reason')}")
        print("Using a child-safe version of the request.\n")
    else:
        print("Safety pre-check passed.\n")

    analysis = analyze_request(safe_request)

    print("Generating multiple story candidates...\n")
    candidates = generate_candidate_stories(safe_request, analysis)

    best_candidate = select_best_candidate(candidates)
    best_story = best_candidate["story"]
    best_judge = best_candidate["judge"]

    print("\nBest candidate selected.")
    print(f"Selected candidate: {best_candidate['candidate_number']}")
    print(f"Selected score: {best_candidate['score']}/10\n")

    if best_judge.get("passes", False):
        print("Judge approved the selected story.\n")
        return {
            "original_request": user_request,
            "safe_request": safe_request,
            "safety": safety,
            "analysis": analysis,
            "story": best_story,
            "judge": best_judge,
            "revised": False,
            "selected_candidate": best_candidate["candidate_number"],
            "candidate_scores": [candidate["score"] for candidate in candidates],
        }

    print("Judge requested improvements. Revising selected story...\n")

    revised_story = revise_story(safe_request, best_story, best_judge)
    second_judge = judge_story(safe_request, revised_story)

    return {
        "original_request": user_request,
        "safe_request": safe_request,
        "safety": safety,
        "analysis": analysis,
        "story": revised_story,
        "judge": second_judge,
        "revised": True,
        "selected_candidate": best_candidate["candidate_number"],
        "candidate_scores": [candidate["score"] for candidate in candidates],
    }


def print_result(result: Dict[str, Any]) -> None:
    print("\n" + "=" * 80)
    print("FINAL BEDTIME STORY")
    print("=" * 80)
    print(result["story"])

    print("\n" + "=" * 80)
    print("SYSTEM SUMMARY")
    print("=" * 80)
    print(f"Original request: {result.get('original_request', 'N/A')}")
    print(f"Safe request used: {result.get('safe_request', 'N/A')}")
    print(f"Safety status: {result['safety'].get('status', 'N/A')}")
    print(f"Theme: {result['analysis'].get('theme', 'N/A')}")
    print(f"Tone: {result['analysis'].get('tone', 'N/A')}")
    print(f"Lesson: {result['analysis'].get('lesson', 'N/A')}")
    print(f"Selected candidate: {result.get('selected_candidate', 'N/A')}")
    print(f"Candidate scores: {result.get('candidate_scores', 'N/A')}")
    print(f"Revised after judge feedback: {result['revised']}")
    print(f"Judge overall score: {result['judge'].get('overall_score', 'N/A')}/10")
    print("Evaluation criteria: age appropriateness, bedtime tone, creativity, clarity, safety")
    print(f"Judge feedback: {result['judge'].get('feedback', 'N/A')}")


def main() -> None:
    print("Hippocratic AI Bedtime Story Generator")
    print("Tell me what kind of bedtime story you want.")
    print("Example: A story about a girl named Alice and her best friend Bob, who is a cat.\n")

    user_input = input("Story request: ").strip()

    if not user_input:
        user_input = "A gentle bedtime story about a curious child and a friendly moon rabbit."

    result = generate_story(user_input)
    print_result(result)

    follow_up = input("\nWould you like to modify the story (e.g., funnier, shorter)? (y/n): ").strip().lower()

    if follow_up == "y":
        change = input("What change would you like? ")

        print("\nRefining story...\n")

        revised = revise_story(result["safe_request"], result["story"], {"feedback": change})

        print("\nUPDATED STORY:\n")
        print(revised)

if __name__ == "__main__":
    main()