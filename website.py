from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# =========================
# TOKENS
# =========================

PANDASCORE_TOKEN = os.environ.get("PANDASCORE_TOKEN")

# =========================
# API CALLS
# =========================

def headers():
    return {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

def get_lol_matches():
    return requests.get(
        "https://api.pandascore.co/lol/matches/upcoming",
        headers=headers()
    ).json()

def get_cs2_matches():
    return requests.get(
        "https://api.pandascore.co/csgo/matches/upcoming",
        headers=headers()
    ).json()

def get_valorant_matches():
    return requests.get(
        "https://api.pandascore.co/valorant/matches/upcoming",
        headers=headers()
    ).json()

def get_dota_matches():
    return requests.get(
        "https://api.pandascore.co/dota2/matches/upcoming",
        headers=headers()
    ).json()

# =========================
# FORMAT MATCH
# =========================

def format_match(match):
    if not isinstance(match, dict):
        return None

    opp = match.get("opponents") or []

    team1 = "TBD"
    team2 = "TBD"

    if len(opp) > 0:
        team1 = opp[0].get("opponent", {}).get("name", "TBD")
    if len(opp) > 1:
        team2 = opp[1].get("opponent", {}).get("name", "TBD")

    return {
        "id": match.get("id"),
        "team1": team1,
        "team2": team2,
        "time": match.get("scheduled_at", "TBD"),
        "league": match.get("league", {}).get("name", "Unknown"),
        "status": (match.get("status") or "UPCOMING").upper(),
        "url": f"https://www.google.com/search?q={team1}+vs+{team2}+esports"
    }

# =========================
# HTML TEMPLATE
# =========================

def render_matches(title, endpoint):
    return f"""
<!DOCTYPE html>
<html>
<head>
<title>{title}</title>
<style>
body {{
    margin:0;
    background:#0a0a0a;
    color:white;
    font-family:Arial;
}}
.container {{
    padding:20px;
}}
.match {{
    background:#1a1a1a;
    padding:12px;
    margin:10px 0;
    border-radius:8px;
    display:block;
    text-decoration:none;
    color:white;
}}
.match:hover {{
    background:#222;
}}
</style>
</head>

<body>
<div class="container">
    <h1>{title}</h1>
    <div id="matches">Loading...</div>
</div>

<script>
async function load() {{
    const res = await fetch("{endpoint}");
    const data = await res.json();

    document.getElementById("matches").innerHTML =
        data.map(m => `
            <a class="match" href="${{m.url}}" target="_blank">
                <b>${{m.team1}} vs ${{m.team2}}</b><br>
                <small>${{m.league}} • ${{m.time}}</small>
            </a>
        `).join("");
}}

load();
setInterval(load, 20000);
</script>

</body>
</html>
"""

# =========================
# ROUTES
# =========================

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Stat Pad</title>
<style>
body {
    margin:0;
    background:#0a0a0a;
    color:white;
    font-family:Arial;
}

.sidebar {
    width:220px;
    height:100vh;
    background:#111;
    position:fixed;
    padding:20px;
}

.sidebar a {
    display:block;
    color:white;
    padding:10px;
    text-decoration:none;
}

.main {
    margin-left:240px;
    padding:30px;
}

.card {
    background:#1a1a1a;
    padding:15px;
    margin:10px;
    border-radius:10px;
    display:inline-block;
}
</style>
</head>

<body>

<div class="sidebar">
    <h2>Stat Pad</h2>
    <a href="/">Home</a>
    <a href="/lol">LoL</a>
    <a href="/cs2">CS2</a>
    <a href="/valorant">Valorant</a>
    <a href="/dota">Dota 2</a>
</div>

<div class="main">
    <h1>G3l0M3ll0W Stat Pad</h1>

    <div class="card"><a href="/lol">League of Legends</a></div>
    <div class="card"><a href="/cs2">CS2</a></div>
    <div class="card"><a href="/valorant">Valorant</a></div>
    <div class="card"><a href="/dota">Dota 2</a></div>
</div>

</body>
</html>
"""

@app.route("/lol")
def lol_page():
    return render_matches("League of Legends", "/tier1/lol")

@app.route("/cs2")
def cs2_page():
    return render_matches("CS2", "/tier1/cs2")

@app.route("/valorant")
def valorant_page():
    return render_matches("Valorant", "/tier1/valorant")

@app.route("/dota")
def dota_page():
    return render_matches("Dota 2", "/tier1/dota")

# =========================
# JSON ENDPOINTS
# =========================

@app.route("/tier1/lol")
def tier1_lol():
    return jsonify([format_match(m) for m in get_lol_matches() if format_match(m)])

@app.route("/tier1/cs2")
def tier1_cs2():
    return jsonify([format_match(m) for m in get_cs2_matches() if format_match(m)])

@app.route("/tier1/valorant")
def tier1_valorant():
    return jsonify([format_match(m) for m in get_valorant_matches() if format_match(m)])

@app.route("/tier1/dota")
def tier1_dota():
    return jsonify([format_match(m) for m in get_dota_matches() if format_match(m)])

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)