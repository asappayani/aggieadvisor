#!/usr/bin/env python3
"""
simple_rmp.py  –  type a professor’s name, get their RateMyProfessors stats.

• Updated: July 2025 — uses the current RMP GraphQL schema (newSearch root)
• Reqs   : pip install requests
"""

import requests, textwrap

# ---------------------------------------------------------------------------
API     = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    # RMP now enforces Basic-auth (“test:test”) on all GraphQL POSTs
    "Authorization": "Basic dGVzdDp0ZXN0",
    "Content-Type":  "application/json",
    "Origin":        "https://www.ratemyprofessors.com",
    "Referer":       "https://www.ratemyprofessors.com/",
    "User-Agent":    "Mozilla/5.0 (simple-RMP-CLI)",
}

# ---------- GraphQL documents (2025 schema) -------------------------------
SCHOOL_QUERY = """
query ($text: String!) {
  newSearch {
    schools(query: { text: $text }) {
      edges {
        node { id name city state }
      }
    }
  }
}
"""

TEACHER_QUERY = """
query ($text: String!, $sid: ID!) {
  newSearch {
    teachers(query: { text: $text, schoolID: $sid }) {
      edges {
        node {
          id legacyId firstName lastName
          avgRating avgDifficulty numRatings
        }
      }
    }
  }
}
"""

# ---------- helper to fire GraphQL calls ---------------------------------
def gql(doc: str, variables: dict) -> dict:
    r = requests.post(API, headers=HEADERS,
                      json={"query": doc, "variables": variables},
                      timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]

# ---------- interactive campus picker ------------------------------------
def pick_school() -> str:
    """Prompt the user until they pick a campus; return that campus’s ID."""
    while True:
        term = input("School search (e.g. “Texas A&M”): ").strip()
        hits = gql(SCHOOL_QUERY, {"text": term})["newSearch"]["schools"]["edges"]
        if not hits:
            print("  – no matches –"); continue

        for i, e in enumerate(hits, 1):
            n = e["node"]
            print(f"{i}. {n['name']} — {n['city']}, {n['state']}")
        try:
            idx = int(input(f"Choose 1-{len(hits)}: ")) - 1
            return hits[idx]["node"]["id"]
        except (ValueError, IndexError):
            print("  – invalid choice –")

# ---------- professor look-up --------------------------------------------
def prof_stats(name: str, school_id: str):
    edges = gql(TEACHER_QUERY,
                {"text": name, "sid": school_id})["newSearch"]["teachers"]["edges"]
    if not edges:
        return None
    n = edges[0]["node"]
    return {
        "display":    f"{n['firstName']} {n['lastName']}",
        "rating":     n["avgRating"],
        "difficulty": n["avgDifficulty"],
        "count":      n["numRatings"],
        "link":       f"https://www.ratemyprofessors.com/professor/{n['legacyId']}",
    }

# ---------- CLI loop ------------------------------------------------------
def main() -> None:
    sid = pick_school()
    print("\nType professor names (blank to quit)…\n")
    while True:
        try:
            name = input("Professor: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not name:
            break

        info = prof_stats(name, sid)
        if not info:
            print("  ✗  No RMP entry found.\n"); continue

        print(textwrap.dedent(f"""\
            ▸ {info['display']}
              rating      : {info['rating'] or '–'} / 5
              difficulty  : {info['difficulty'] or '–'} / 5
              # of ratings: {info['count']}
              link        : {info['link']}
        """))

if __name__ == "__main__":
    main()
