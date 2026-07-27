import json
import re
from typing import Any

from app.config import get_settings

settings = get_settings()


def _client():
    if not settings.openai_api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def _extract_json(text: str) -> Any:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)
        if match:
            return json.loads(match.group(0))
        raise


def chat_json(system: str, user: str, temperature: float = 0.7) -> Any | None:
    client = _client()
    if client is None:
        return None
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json(content)


FALLBACK_BANK: dict[str, list[dict[str, Any]]] = {
    "DSA": [
        {
            "prompt": "Given an unsorted array of integers, describe an efficient approach to find two numbers that sum to a target value. Discuss time and space complexity trade-offs.",
            "hints": ["Consider hashing", "Two-pointer after sort"],
            "expected_topics": ["hash map", "two pointers", "complexity"],
        },
        {
            "prompt": "Explain how you would detect a cycle in a linked list and return the node where the cycle begins.",
            "hints": ["Floyd's algorithm", "Reset one pointer after meeting"],
            "expected_topics": ["fast-slow pointers", "cycle detection"],
        },
        {
            "prompt": "Design an algorithm to find the longest substring without repeating characters. Walk through an example.",
            "hints": ["Sliding window", "Track last seen indices"],
            "expected_topics": ["sliding window", "hash map"],
        },
        {
            "prompt": "How would you implement a min-heap from scratch, and when would you choose it over a sorted array?",
            "hints": ["Sift up/down", "O(log n) insert"],
            "expected_topics": ["heap", "priority queue"],
        },
        {
            "prompt": "Given a binary tree, explain how to serialize and deserialize it so structure is preserved.",
            "hints": ["Preorder with null markers", "BFS levels"],
            "expected_topics": ["tree traversal", "serialization"],
        },
    ],
    "System Design": [
        {
            "prompt": "Design a URL shortener like bit.ly. Cover API design, data model, hashing strategy, and scaling reads.",
            "hints": ["Base62 encoding", "Cache hot URLs", "Redirect analytics"],
            "expected_topics": ["hashing", "caching", "databases", "CDN"],
        },
        {
            "prompt": "Design a real-time chat system supporting 1:1 and group conversations. Discuss delivery guarantees and presence.",
            "hints": ["WebSockets", "message queues", "fan-out"],
            "expected_topics": ["websockets", "pubsub", "consistency"],
        },
        {
            "prompt": "How would you design a rate limiter for a public API used by millions of clients?",
            "hints": ["Token bucket", "Redis counters", "distributed clocks"],
            "expected_topics": ["rate limiting", "redis", "distributed systems"],
        },
        {
            "prompt": "Design a news feed system similar to Twitter. Discuss timeline generation strategies and ranking.",
            "hints": ["Push vs pull", "fan-out on write", "caching"],
            "expected_topics": ["feeds", "caching", "ranking"],
        },
        {
            "prompt": "Design an online collaborative document editor (Google Docs-like). Focus on conflict resolution.",
            "hints": ["OT vs CRDT", "websockets", "version vectors"],
            "expected_topics": ["CRDT", "consistency", "realtime"],
        },
    ],
    "HR": [
        {
            "prompt": "Tell me about a time you faced a significant technical disagreement with a teammate. How did you resolve it?",
            "hints": ["STAR method", "Focus on collaboration"],
            "expected_topics": ["conflict resolution", "communication"],
        },
        {
            "prompt": "Describe a project you owned end-to-end. What was the hardest trade-off you made?",
            "hints": ["Ownership", "Measurable impact"],
            "expected_topics": ["ownership", "decision making"],
        },
        {
            "prompt": "How do you prioritize work when everything feels urgent? Give a concrete example.",
            "hints": ["Impact vs effort", "Stakeholder alignment"],
            "expected_topics": ["prioritization", "time management"],
        },
        {
            "prompt": "What motivates you in a software engineering role, and why this company/role specifically?",
            "hints": ["Align with role", "Genuine curiosity"],
            "expected_topics": ["motivation", "role fit"],
        },
        {
            "prompt": "Tell me about a failure or mistake. What did you learn and what changed afterward?",
            "hints": ["Accountability", "Growth mindset"],
            "expected_topics": ["learning", "resilience"],
        },
    ],
}


def _fallback_questions(domain: str, count: int, role: str, difficulty: str) -> list[dict[str, Any]]:
    domains = ["DSA", "System Design", "HR"] if domain == "Mixed" else [domain]
    pool: list[dict[str, Any]] = []
    for d in domains:
        for item in FALLBACK_BANK.get(d, []):
            pool.append({**item, "domain": d})
    # Mild difficulty flavoring
    for q in pool:
        if difficulty == "Hard":
            q["prompt"] = q["prompt"] + f" Tailor your answer for a senior {role}."
        elif difficulty == "Easy":
            q["prompt"] = q["prompt"] + " Keep the explanation beginner-friendly with an example."
    return pool[:count] if len(pool) >= count else (pool * ((count // max(len(pool), 1)) + 1))[:count]


def generate_questions(
    role: str,
    domain: str,
    difficulty: str,
    count: int,
    company_style: str | None = None,
    experience_level: str | None = None,
) -> list[dict[str, Any]]:
    system = (
        "You are an expert technical interviewer. Return JSON with key 'questions' as an array. "
        "Each question object must include: domain, prompt, hints (array of strings), expected_topics (array)."
    )
    user = (
        f"Generate {count} interview questions for role '{role}'. "
        f"Domain focus: {domain}. Difficulty: {difficulty}. "
        f"Company style: {company_style or 'general tech'}. "
        f"Candidate experience: {experience_level or 'mid-level'}. "
        "For Mixed domain, diversify across DSA, System Design, and HR. "
        "Questions should be realistic, specific, and interview-ready."
    )
    data = chat_json(system, user)
    if not data or "questions" not in data:
        return _fallback_questions(domain, count, role, difficulty)

    questions = []
    for item in data["questions"][:count]:
        questions.append(
            {
                "domain": item.get("domain") or (domain if domain != "Mixed" else "DSA"),
                "prompt": item.get("prompt", "Describe your approach to this problem."),
                "hints": item.get("hints") or [],
                "expected_topics": item.get("expected_topics") or [],
            }
        )
    while len(questions) < count:
        questions.extend(_fallback_questions(domain, count - len(questions), role, difficulty))
    return questions[:count]


def evaluate_answer(
    question: str,
    answer: str,
    domain: str,
    role: str,
    expected_topics: list[str] | None = None,
) -> dict[str, Any]:
    system = (
        "You are a rigorous but constructive interview coach. Return JSON with keys: "
        "score (0-100 number), feedback (string), strengths (string array), "
        "improvements (string array), follow_up (string), "
        "clarity (0-100), technical_depth (0-100), structure (0-100), communication (0-100)."
    )
    user = (
        f"Role: {role}\nDomain: {domain}\nQuestion: {question}\n"
        f"Expected topics: {', '.join(expected_topics or [])}\n"
        f"Candidate answer:\n{answer}\n"
        "Score fairly. Reward structure (STAR for HR, complexity for DSA, trade-offs for System Design)."
    )
    data = chat_json(system, user, temperature=0.4)
    if data:
        return {
            "score": float(data.get("score", 70)),
            "feedback": data.get("feedback", "Solid attempt with room to deepen specifics."),
            "strengths": data.get("strengths") or ["Clear communication"],
            "improvements": data.get("improvements") or ["Add more concrete examples"],
            "follow_up": data.get("follow_up"),
            "dimensions": {
                "clarity": float(data.get("clarity", 70)),
                "technical_depth": float(data.get("technical_depth", 70)),
                "structure": float(data.get("structure", 70)),
                "communication": float(data.get("communication", 70)),
            },
        }
    return _heuristic_evaluate(answer, expected_topics or [])


def _heuristic_evaluate(answer: str, expected_topics: list[str]) -> dict[str, Any]:
    words = len(answer.split())
    lower = answer.lower()
    topic_hits = sum(1 for t in expected_topics if t.lower() in lower)
    topic_ratio = topic_hits / max(len(expected_topics), 1)

    length_score = 40 if words < 40 else 60 if words < 90 else 75 if words < 220 else 70
    structure_bonus = 8 if any(k in lower for k in ("first", "then", "because", "trade-off", "for example")) else 0
    score = min(95.0, length_score + topic_ratio * 25 + structure_bonus)

    strengths = []
    improvements = []
    if words >= 80:
        strengths.append("Provided a sufficiently detailed response")
    else:
        improvements.append("Expand your answer with more concrete steps and examples")
    if topic_hits:
        strengths.append("Touched on relevant technical topics")
    else:
        improvements.append("Cover core expected concepts more explicitly")
    if structure_bonus:
        strengths.append("Used a structured explanation")
    else:
        improvements.append("Organize the answer into clear steps or sections")

    return {
        "score": round(score, 1),
        "feedback": (
            "Your answer shows foundational understanding. "
            "Strengthen it with clearer structure, complexity analysis or trade-offs, and concrete examples."
        ),
        "strengths": strengths or ["Attempted the question thoughtfully"],
        "improvements": improvements or ["Add measurable impact and edge cases"],
        "follow_up": "Can you walk through an edge case or failure mode for your approach?",
        "dimensions": {
            "clarity": min(90.0, 55 + words / 10),
            "technical_depth": min(90.0, 50 + topic_ratio * 40),
            "structure": 70.0 if structure_bonus else 55.0,
            "communication": min(88.0, 58 + words / 12),
        },
    }


def summarize_session(
    role: str,
    domain: str,
    answers: list[dict[str, Any]],
) -> dict[str, Any]:
    system = (
        "You are a career coach summarizing a mock interview. Return JSON with keys: "
        "summary (string), strengths (string array), improvements (string array), "
        "recommendations (string array of actionable practice tips), "
        "score_breakdown (object with domain keys mapping to average scores)."
    )
    user = f"Role: {role}. Domain focus: {domain}. Answers JSON:\n{json.dumps(answers)[:8000]}"
    data = chat_json(system, user, temperature=0.5)
    if data:
        return {
            "summary": data.get("summary", "Interview completed. Review per-question feedback below."),
            "strengths": data.get("strengths") or [],
            "improvements": data.get("improvements") or [],
            "recommendations": data.get("recommendations") or [],
            "score_breakdown": data.get("score_breakdown") or {},
        }

    scores = [a.get("score") or 0 for a in answers]
    avg = sum(scores) / max(len(scores), 1)
    by_domain: dict[str, list[float]] = {}
    for a in answers:
        by_domain.setdefault(a.get("domain", "General"), []).append(float(a.get("score") or 0))
    breakdown = {k: round(sum(v) / len(v), 1) for k, v in by_domain.items()}
    weakest = min(breakdown, key=breakdown.get) if breakdown else domain

    return {
        "summary": (
            f"You completed a {domain} mock interview for {role} with an average score of {avg:.0f}/100. "
            f"Focus next practice cycles on {weakest}."
        ),
        "strengths": list({s for a in answers for s in (a.get("strengths") or [])})[:5]
        or ["Consistent engagement across questions"],
        "improvements": list({s for a in answers for s in (a.get("improvements") or [])})[:5]
        or ["Deepen technical specifics and edge-case handling"],
        "recommendations": [
            f"Schedule a focused {weakest} drill session this week",
            "Re-answer your lowest-scoring question using STAR or complexity-first structure",
            "Practice one voice interview to improve spoken clarity under time pressure",
            "Review system trade-offs or algorithm patterns for 30 minutes daily",
        ],
        "score_breakdown": breakdown,
    }
