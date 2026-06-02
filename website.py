from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# =========================
# TOKEN (FIXED)
# =========================
PANDASCORE_TOKEN = os.environ.get("DRf4K_eHDya98L2VqwDslktYwSL35wTqTQDmUBLG1GQrEXl7BHs")

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

.sidebar a:hover {
    background:#222;
}

.main {
    margin-left:240px;
    padding:20px;
}

.hero {
    font-size:32px;
    font-weight:bold;
    color:#00ff99;
}
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
    <div class="hero">
        G3l0M3ll0W's Stat Pad
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