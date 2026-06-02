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
# HOME PAGE
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
.hero {
    font-size:36px;
    font-weight:bold;
    color:#00ff99;
}
.subtext {
    color:#aaa;
    margin-bottom:20px;
}
.card {
    display:inline-block;
    padding:15px;
    background:#1a1a1a;
    margin:10px;
    border-radius:10px;
}
</style>
</head>
<body>

<div class="sidebar">
    <h2>Stat Pad</h2>
    <a href="/">Home</a>
    <a href="/live-dashboard">Live Dashboard</a>
    <a href="/lol">LoL</a>
    <a href="/cs2">CS2</a>
    <a href="/valorant">Valorant</a>
    <a href="/dota">Dota 2</a>
</div>

<div class="main">
    <div class="hero">G3l0M3ll0W Stat Pad</div>
    <div class="subtext">Live esports tracker</div>

    <div class="card"><a href="/lol">LoL</a></div>
    <div class="card"><a href="/cs2">CS2</a></div>
    <div class="card"><a href="/valorant">Valorant</a></div>
    <div class="card"><a href="/dota">Dota 2</a></div>
</div>

</body>
</html>
"""

# =========================
# MATCH PAGES
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
.match {{
    background:#1a1a1a;
    padding:10px;
    margin:10px;
    border-radius:8px;
}}
</style>
</head>
<body>
<h1>{title}</h1>
<div id="matches">Loading...</div>

<script>
async function load() {{
    const res = await fetch("{endpoint}");
    const data = await res.json();

    document.getElementById("matches").innerHTML =
        data.map(m => `
            <div class="match">
                <a href="${{m.url}}" target="_blank" style="color:white">
                    ${{
                        m.team1
                    }} vs ${{
                        m.team2
                    }}
                </a>
                <div>${{m.league}}</div>
            </div>
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

# =========================
# LIVE DASHBOARD (FIXED)
# =========================

@app.route("/live-dashboard")
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
    const res = await fetch("/live_matches");
    const data = await res.json();

    function render(list) {
        if (!list || list.length === 0) {
            return "No live matches";
        }

        return list.map(m => `
            <div class="match">
                <a href="${m.url}" target="_blank" style="color:white;text-decoration:none;">
                    🔴 <b>${m.team1} vs ${m.team2}</b>
                </a>
                <div class="small">${m.league}</div>
            </div>
        `).join("");
    }

    document.getElementById("cs2").innerHTML = render(data.cs2);
    document.getElementById("valorant").innerHTML = render(data.valorant);
    document.getElementById("lol").innerHTML = render(data.lol);
    document.getElementById("dota").innerHTML = render(data.dota);
}

loadLive();
setInterval(loadLive, 15000);
</script>

</body>
</html>
"""

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