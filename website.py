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

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 20px;
}

.card {
    display: block;
    padding: 18px;
    background: #151515;
    border-radius: 12px;
    border: 1px solid #222;
    color: white;
    text-decoration: none;
    transition: 0.2s;
}

.card:hover {
    transform: scale(1.05);
    border-color: #00ff99;
    box-shadow: 0 0 12px rgba(0,255,153,0.2);
    153,0.2);
}

.title {
    font-size: 18px;
    font-weight: bold;
}

.desc {
    font-size: 13px;
    color: #aaa;
    margin-top: 6px;
}

.tag {
    margin-top: 10px;
    display: inline-block;
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 5px;
    background: #00ff99;
    color: black;
    font-weight: bold;
}
</style>
</head>

<body>

<div class="sidebar">
    <h2>Stat Pad</h2>
    <a href="/">Home</a>
    <a href="/live-dashboard">🔴 Live Dashboard</a>
    <a href="/lol">LoL</a>
    <a href="/cs2">CS2</a>
    <a href="/valorant">Valorant</a>
    <a href="/dota">Dota 2</a>
</div>

<div class="main">

    <div class="hero">
        G3l0M3ll0W's Stat Pad
    </div>

    <div class="subtext">
        Live esports tracker
    </div>

<div class="grid">

    <a href="https://hltv.org/" class="card" target="_blank">
        🎮 CS2 (HLTV)
        <p>Pro CS2 matches & stats</p>
    </a>

    <a href="https://www.vlr.gg/" class="card" target="_blank">
        ⚡ Valorant (VLR.gg)
        <p>VCT / Masters / Champions</p>
    </a>

    <a href="https://andydanger.github.io/live-lol-esports/#/" class="card" target="_blank">
        🎮 League of Legends
        <p>Live LoL esports tracker</p>
    </a>

    <a href="https://cyberscore.live/en/matches/" class="card" target="_blank">
    🧠 Dota 2 (CyberScore)
    <p>Stats & match tracking</p>
</a>

</div>

</body>
</html>
"""

def render_live_dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Live Esports Dashboard</title>

<style>
body {
    margin:0;
    font-family:Arial;
    background:#0a0a0a;
    color:white;
}

.header {
    padding:20px;
    font-size:28px;
    font-weight:bold;
    color:#00ff99;
}

.container {
    display:grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap:15px;
    padding:20px;
}

.card {
    background:#151515;
    border:1px solid #222;
    border-radius:12px;
    padding:15px;
}

.live {
    color:red;
    font-weight:bold;
    animation:pulse 1.2s infinite;
}

@keyframes pulse {
    0% {opacity:1;}
    50% {opacity:0.4;}
    100% {opacity:1;}
}

.match {
    padding:10px;
    border-bottom:1px solid #222;
}

.small {
    color:#aaa;
    font-size:12px;
}
</style>
</head>

<body>

<div class="header">🔴 LIVE ESPORTS DASHBOARD</div>

<div class="container">

    <div class="card">
        <div class="live">CS2 LIVE</div>
        <div id="cs2">Loading...</div>
    </div>

    <div class="card">
        <div class="live">Valorant LIVE</div>
        <div id="valorant">Loading...</div>
    </div>

    <div class="card">
        <div class="live">League of Legends LIVE</div>
        <div id="lol">Loading...</div>
    </div>

    <div class="card">
        <div class="live">Dota 2 LIVE</div>
        <div id="dota">Loading...</div>
    </div>

</div>

<script>
async function loadLive() {
    const res = await fetch("/live_counts");
    const counts = await res.json();

    document.getElementById("cs2").innerHTML =
        counts.cs2 > 0 ? "🔥 " + counts.cs2 + " live matches" : "No live matches";

    document.getElementById("valorant").innerHTML =
        counts.valorant > 0 ? "🔥 " + counts.valorant + " live matches" : "No live matches";

    document.getElementById("lol").innerHTML =
        counts.lol > 0 ? "🔥 " + counts.lol + " live matches" : "No live matches";

    document.getElementById("dota").innerHTML =
        counts.dota > 0 ? "🔥 " + counts.dota + " live matches" : "No live matches";
}

loadLive();
setInterval(loadLive, 15000);
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

@app.route("/live-dashboard")
def live_dashboard():
    return render_live_dashboard()

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