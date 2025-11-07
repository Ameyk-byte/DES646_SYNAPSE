import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path("Data")
DATA_DIR.mkdir(exist_ok=True)
USER_PROFILE_PATH = DATA_DIR / "user_profile.json"
RESOURCES_PATH = DATA_DIR / "learning_resources.json"

#Data model
@dataclass
class UserProfile:
    user_id: str
    goals: List[str]
    level: str 
    interests: List[str]
    history: List[Dict]  # [{timestamp, input, recommendations[..]}]

DEFAULT_PROFILE = UserProfile(
    user_id="default",
    goals=[],
    level="beginner",
    interests=[],
    history=[]
)

#Utilities
def _load_profile() -> UserProfile:
    if USER_PROFILE_PATH.exists():
        return UserProfile(**json.loads(USER_PROFILE_PATH.read_text()))
    return DEFAULT_PROFILE

def _save_profile(profile: UserProfile) -> None:
    USER_PROFILE_PATH.write_text(json.dumps(asdict(profile), indent=2))

def _load_resources() -> List[Dict]:
    """
    Each resource is:
    {
      "id": "py-basic-1",
      "title": "Python Basics – FreeCodeCamp",
      "topic": "python",
      "level": "beginner",
      "type": "video|article|course|exercise",
      "duration_min": 90,
      "tags": ["syntax","variables"],
      "url": "https://.."
    }
    """
    if RESOURCES_PATH.exists():
        return json.loads(RESOURCES_PATH.read_text())
    # Seed with a tiny starter set; extend this file later.
    seed = [
        {
            "id":"py-basic-1","title":"Python Basics – FreeCodeCamp",
            "topic":"python","level":"beginner","type":"video","duration_min":240,
            "tags":["syntax","variables","loops","functions"],
            "url":"https://www.youtube.com/watch?v=rfscVS0vtbw"
        },
        {
            "id":"py-int-1","title":"Intermediate Python",
            "topic":"python","level":"intermediate","type":"article","duration_min":60,
            "tags":["oop","iterators","generators"],"url":"https://realpython.com/"
        },
        {
            "id":"ml-basic-1","title":"Intro to Machine Learning (KNN/Linear)",
            "topic":"ml","level":"beginner","type":"course","duration_min":180,
            "tags":["supervised","features"],"url":"https://www.kaggle.com/learn/intro-to-machine-learning"
        },
        {
            "id":"bioinfo-basic-1","title":"Bioinformatics for Beginners",
            "topic":"bioinformatics","level":"beginner","type":"course","duration_min":180,
            "tags":["sequence","alignment","genes"],"url":"https://www.edx.org/"
        },
        {
            "id":"scanpy-1","title":"Scanpy Tutorial",
            "topic":"single-cell","level":"intermediate","type":"article","duration_min":90,
            "tags":["scanpy","anndata","umap"],"url":"https://scanpy.readthedocs.io/"
        },
    ]
    RESOURCES_PATH.write_text(json.dumps(seed, indent=2))
    return seed

def _tfidf_rank(query: str, docs: List[Dict], fields=("title","tags","topic")) -> List[Tuple[float, Dict]]:
    corpus = []
    for d in docs:
        text = " ".join([
            d.get("title",""),
            " ".join(d.get("tags", [])),
            d.get("topic",""),
            d.get("level","")
        ]).lower()
        corpus.append(text)
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(corpus + [query.lower()])
    sims = cosine_similarity(X[-1], X[:-1]).ravel()
    ranked = sorted(list(zip(sims, docs)), key=lambda x: x[0], reverse=True)
    return ranked

def _filter_by_level(docs: List[Dict], level: str) -> List[Dict]:
    # allow neighbor levels too, but prioritize exact
    order = {"beginner":0, "intermediate":1, "advanced":2}
    lvl = order.get(level, 0)
    return [d for d in docs if abs(order.get(d.get("level","beginner"),0) - lvl) <= 1]

def _make_study_plan(recs: List[Dict], hours_per_week: int = 5) -> List[Dict]:
    """
    Make a simple weekly plan using durations.
    """
    plan, bucket = [], 0
    week, wk_items = 1, []
    limit = hours_per_week * 60
    for r in recs:
        dur = r.get("duration_min", 60)
        if bucket + dur <= limit:
            wk_items.append(r)
            bucket += dur
        else:
            plan.append({"week": week, "items": wk_items})
            week += 1
            wk_items = [r]
            bucket = dur
    if wk_items:
        plan.append({"week": week, "items": wk_items})
    return plan

#Public API 
def update_profile(user_input: str, level: str = None, goals: List[str] = None, interests: List[str] = None) -> Dict:
    prof = _load_profile()
    if level: prof.level = level
    if goals: prof.goals = list(set([*prof.goals, *goals]))
    if interests: prof.interests = list(set([*prof.interests, *interests]))
    _save_profile(prof)
    return asdict(prof)

def recommend(user_query: str, k: int = 6, hours_per_week: int = 5) -> Dict:
    """
    Core recommendation call used by router.
    Steps:
      1) Load profile + resources
      2) Rank by TF-IDF relevance to query + interests/goals
      3) Filter by level proximity
      4) Return top-k + a simple weekly study plan
    """
    profile = _load_profile()
    resources = _load_resources()

    # Build a compound query using user text
    context_bits = []
    if profile.goals: context_bits.append("goals: " + ", ".join(profile.goals))
    if profile.interests: context_bits.append("interests: " + ", ".join(profile.interests))
    context_bits.append(f"level: {profile.level}")
    compound_query = f"{user_query}. {' '.join(context_bits)}"

    # Level-aware filter, then TF-IDF ranking
    level_filtered = _filter_by_level(resources, profile.level)
    ranked = _tfidf_rank(compound_query, level_filtered)
    top = [d for _, d in ranked[:k]]


    plan = _make_study_plan(top, hours_per_week=hours_per_week)

   
    profile.history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "input": user_query,
        "recommendations": [t["id"] for t in top]
    })
    _save_profile(profile)

    return {
        "profile": asdict(profile),
        "query": user_query,
        "recommendations": top,
        "weekly_plan": plan
    }

def run(user_input: str) -> Tuple[str, Dict]:
    """
    Adapter used by Main.py.
    Accepts free-form commands:
      - 'set level intermediate'
      - 'add goals: machine learning, bioinformatics'
      - 'add interests: python, single-cell'
      - 'recommend resources for <topic>'
    Returns: (text_response, payload_json)
    """
    ui = user_input.strip().lower()

    if ui.startswith("set level "):
        level = ui.split("set level ",1)[1].strip()
        prof = update_profile(user_input, level=level)
        return f"Level updated to '{level}'.", {"profile": prof}

    if ui.startswith("add goals:"):
        items = [x.strip() for x in ui.split("add goals:",1)[1].split(",") if x.strip()]
        prof = update_profile(user_input, goals=items)
        return f"Added goals: {', '.join(items)}.", {"profile": prof}

    if ui.startswith("add interests:"):
        items = [x.strip() for x in ui.split("add interests:",1)[1].split(",") if x.strip()]
        prof = update_profile(user_input, interests=items)
        return f"Added interests: {', '.join(items)}.", {"profile": prof}

    # default: treat as a recommendation request
    result = recommend(user_input, k=8, hours_per_week=6)
    lines = ["Here are personalized recommendations:\n"]
    for i, r in enumerate(result["recommendations"], 1):
        lines.append(f"{i}. {r['title']}  [{r['type']} • {r['level']} • ~{r['duration_min']} min]")
    lines.append("\nWeekly plan:")
    for wk in result["weekly_plan"]:
        bullets = "\n   - " + "\n   - ".join([f"{it['title']} ({it['type']}, ~{it['duration_min']} min)" for it in wk["items"]])
        lines.append(f"  Week {wk['week']}:{bullets}")
    return "\n".join(lines), result
