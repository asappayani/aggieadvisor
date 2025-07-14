#!/usr/bin/env python3
"""
simple_rmp.py – look up a prof, pick the right one, see their RMP numbers.

• Updated: July 2025 – now also prints the professor’s department.
• Reqs   : pip install requests
"""

import requests, textwrap

# ---------------------------------------------------------------------------
API     = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "Authorization": "Basic dGVzdDp0ZXN0",          # mandatory Basic-auth
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
      edges { node { id name city state } }
    }
  }
}
"""

# ---------- GraphQL: teacher search --------------------------------------
TEACHER_QUERY = """
query ($text: String!, $sid: ID!) {
  newSearch {
    teachers(query: { text: $text, schoolID: $sid }) {
      edges {
        node {
          id
          legacyId
          firstName
          lastName
          department        # department is valid on Teacher
          avgRating
          avgDifficulty
          numRatings
        }
      }
    }
  }
}
"""

# ---------- GraphQL helper ------------------------------------------------
def gql(doc: str, variables: dict) -> dict:
    r = requests.post(API, headers=HEADERS,
                      json={"query": doc, "variables": variables},
                      timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]

# ---------- interactive school picker ------------------------------------
def pick_school() -> str:
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

# ---------- choose-a-prof helper -----------------------------------------
def choose_prof(edges):
    """Show all hits and let the user pick one."""
    for i, e in enumerate(edges, 1):
        n   = e["node"]
        who = f"{n['firstName']} {n['lastName']}"
        dept = n.get("department") or "?"
        extra = f" [{dept}] ({n['numRatings']} ratings, {n['avgRating'] or '–'}/5)"
        print(f"{i}. {who}{extra}")
    while True:
        try:
            idx = int(input(f"Choose 1-{len(edges)} (0 = cancel): "))
        except ValueError:
            print("  – enter a number –"); continue
        if idx == 0:
            return None
        if 1 <= idx <= len(edges):
            return edges[idx-1]["node"]
        print("  – out of range –")

# ---------- professor look-up --------------------------------------------
def prof_stats(name: str, school_id: str):
    edges = gql(TEACHER_QUERY,
                {"text": name, "sid": school_id})["newSearch"]["teachers"]["edges"]
    if not edges:
        return None

    node = edges[0]["node"] if len(edges) == 1 else choose_prof(edges)
    if node is None:                      # user cancelled
        return "cancelled"

    return {
        "display":    f"{node['firstName']} {node['lastName']}",
        "department": node.get("department"),
        "rating":     node["avgRating"],
        "difficulty": node["avgDifficulty"],
        "count":      node["numRatings"],
        "link":       f"https://www.ratemyprofessors.com/professor/{node['legacyId']}",
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
        if info is None:
            print("  ✗  No RMP entry found.\n"); continue
        if info == "cancelled":
            print("  – cancelled –\n"); continue

        print(textwrap.dedent(f"""\
            ▸ {info['display']}  [{info['department'] or '–'}]
              rating      : {info['rating'] or '–'} / 5
              difficulty  : {info['difficulty'] or '–'} / 5
              # of ratings: {info['count']}
              link        : {info['link']}
        """))

if __name__ == "__main__":
    main()
