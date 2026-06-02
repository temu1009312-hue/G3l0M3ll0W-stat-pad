from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# =========================
# TOKEN (FIXED)
# =========================

PANDASCORE_TOKEN = os.environ.get("PANDASCORE_TOKEN")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# =========================
# API CALLS
# =========================

def get_lol_matches():
    url = "https://api.pandascore.co/lol/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    return requests.get(url, headers=headers).json()

def get_cs2_matches():
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    return requests.get(url, headers=headers).json()

def get_valorant_matches():
    url = "https://api.pandascore.co/valorant/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    return requests.get(url, headers=headers).json()

def get_dota_matches():
    url = "https://api.pandascore.co/dota2/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    return requests.get(url, headers=headers).json()

# =========================
# FORMAT MATCH
# =========================

def format_match(match):
    if not isinstance(match, dict):
        return None

    opp = match.get("opponents") or []

    team1 = "TBD"
    team2 = "TBD"

    try:
        if len(opp) > 0:
            team1 = opp[0].get("opponent", {}).get("name", "TBD")
        if len(opp) > 1:
            team2 = opp[1].get("opponent", {}).get("name", "TBD")
    except:
        pass

    return {
        "id": match.get("id"),
        "team1": team1,
        "team2": team2,
        "time": match.get("scheduled_at", "TBD"),
        "league": match.get("league", {}).get("name", "Unknown"),
        "status": match.get("status", "UPCOMING").upper(),
        "url": f"https://www.google.com/search?q={team1}+vs+{team2}+esports"
    }

# =========================
# ROUTES
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

@app.route("/tier1/lol")
def tier1_lol():
    return jsonify([
    fm for fm in (format_match(m) for m in get_lol_matches())
    if fm is not None
])

@app.route("/tier1/cs2")
def tier1_cs2():
    return jsonify([
    fm for fm in (format_match(m) for m in get_cs2_matches())
    if fm is not None
])

@app.route("/tier1/valorant")
def tier1_valorant():
    return jsonify([
    fm for fm in (format_match(m) for m in get_valorant_matches())
    if fm is not None
])

@app.route("/tier1/dota")
def tier1_dota():
    return jsonify([
    fm for fm in (format_match(m) for m in get_dota_matches())
    if fm is not None
])

# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>G3l0M3ll0W Stat Pad</title>

<style>
body {
    margin: 0;
    background: radial-gradient(circle at top, #111 0%, #0a0a0a 70%);
    color: white;
    font-family: Arial;
}

/* SIDEBAR */
.sidebar {
    width: 220px;
    height: 100vh;
    background: #0f0f0f;
    position: fixed;
    padding: 20px;
    border-right: 1px solid #222;
}

.sidebar h2 {
    color: #00ff99;
}

.sidebar a {
    display: block;
    color: white;
    padding: 10px;
    text-decoration: none;
    border-radius: 6px;
}

.sidebar a:hover {
    background: #222;
}

/* MAIN */
.main {
    margin-left: 240px;
    padding: 30px;
}

/* HERO */
.hero {
    font-size: 42px;
    font-weight: bold;
    color: #00ff99;
    margin-bottom: 10px;
}

.subtext {
    color: #aaa;
    margin-bottom: 30px;
}

/* CARDS */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
}

.card {
    background: #151515;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #222;
    transition: 0.2s;
}

.card:hover {
    transform: scale(1.03);
    border-color: #00ff99;
}

.card h3 {
    margin: 0;
    color: #fff;
}

.tag {
    display: inline-block;
    padding: 3px 8px;
    font-size: 12px;
    border-radius: 5px;
    margin-top: 8px;
}

.live { background: red; }
.upcoming { background: gold; color: black; }
.finished { background: gray; }
</style>

</head>

<body>

<div class="sidebar">
    <h2>☰ Stat Pad</h2>
    <a href="/">Home</a>
    <a href="/lol">LoL</a>
    <a href="/cs2">CS2</a>
    <a href="/valorant">Valorant</a>
    <a href="/dota">Dota 2</a>
</div>

<div class="main">

    <div class="hero">G3l0M3ll0W's Stat Pad</div>
    <div class="subtext">Live esports tracker for Tier 1 matches (LoL • CS2 • Valorant • Dota 2)</div>

    <div class="grid">

        <a href="/lol" style="text-decoration:none;">
<div class="card">
    <h3>🎮 League of Legends</h3>
    <p>View live & upcoming LCK / LEC / LCS matches</p>
    <span class="tag upcoming">ENTER</span>
</div>
</a>

        <a href="/cs2" style="text-decoration:none;">
<div class="card">
    <h3>🔫 CS2</h3>
    <p>Major tournaments & pro circuit matches</p>
    <span class="tag upcoming">ENTER</span>
</div>
</a>

        <a href="/valorant" style="text-decoration:none;">
<div class="card">
    <h3>⚡ Valorant</h3>
    <p>VCT, Masters & Champions matches</p>
    <span class="tag upcoming">ENTER</span>
</div>
</a>

        <a href="/dota" style="text-decoration:none;">
<div class="card">
    <h3>🧠 Dota 2</h3>
    <p>The International & regional leagues</p>
    <span class="tag upcoming">ENTER</span>
</div>
</a>

    </div>

</div>

</body>
</html>
"""

# =========================
# RUN (RENDER FIX)
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)