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
        "https://api.pandascore.co/lol/matches",
        headers=headers()
    ).json()

def get_cs2_matches():
    return requests.get(
        "https://api.pandascore.co/csgo/matches",
        headers=headers()
    ).json()

def get_valorant_matches():
    return requests.get(
        "https://api.pandascore.co/valorant/matches",
        headers=headers()
    ).json()

def get_dota_matches():
    return requests.get(
        "https://api.pandascore.co/dota2/matches",
        headers=headers()
    ).json()

# =========================
# FORMAT MATCH
# =========================

def format_match(match):
    if not isinstance(match, dict):
        return None

    opp = match.get("opponents") or []

    if len(opp) < 2:
        return None

    team1 = opp[0].get("opponent", {}).get("name")
    team2 = opp[1].get("opponent", {}).get("name")

    if not team1 or not team2:
        return None

    results = match.get("results") or []

    score1 = results[0].get("score", 0) if len(results) > 0 else 0
    score2 = results[1].get("score", 0) if len(results) > 1 else 0

    games = match.get("games") or []

    maps = []

    for i, g in enumerate(games, start=1):
        maps.append({
            "map": i,
            "status": g.get("status", "pending"),
            "winner": (
                g.get("winner", {}).get("name")
                if isinstance(g.get("winner"), dict)
                else None
            )
        })

    return {
    "id": match.get("id"),
    "team1": team1,
    "team2": team2,

    "team1_logo": opp[0]["opponent"].get("image_url"),
    "team2_logo": opp[1]["opponent"].get("image_url"),

    "time": match.get("scheduled_at", "TBD"),
    "league": match.get("league", {}).get("name", "Unknown"),
    "status": (match.get("status") or "UPCOMING").upper(),

    "score1": score1,
    "score2": score2,
    "maps": maps,

    "url": f"/match/{match.get('id')}"
}

    # =========================
    # GLOBAL MATCH SCORE
    # =========================
    results = match.get("results") or []
    score1 = results[0].get("score", 0) if len(results) > 0 else 0
    score2 = results[1].get("score", 0) if len(results) > 1 else 0

    # =========================
    # MAP / GAME TRACKING
    # =========================
    games = match.get("games") or []

    maps = []
    for i, g in enumerate(games, start=1):
        maps.append({
            "map": i,
            "status": g.get("status", "pending"),
            "winner": (
                g.get("winner", {}).get("name")
                if isinstance(g.get("winner"), dict)
                else None
            )
        })

    return {
        "id": match.get("id"),
        "team1": team1,
        "team2": team2,
        "time": match.get("scheduled_at", "TBD"),
        "league": match.get("league", {}).get("name", "Unknown"),
        "status": (match.get("status") or "UPCOMING").upper(),

        # overall score
        "score1": score1,
        "score2": score2,

        # NEW: map breakdown
        "maps": maps,

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

.match {
    padding:12px;
    border-bottom:1px solid #222;
}

.match b {
    color:#00ff99;
}

.small {
    margin-top:3px;
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
    try {
        const [cs2, valorant, lol, dota] = await Promise.all([
            fetch("/tier1/cs2").then(r => r.json()),
            fetch("/tier1/valorant").then(r => r.json()),
            fetch("/tier1/lol").then(r => r.json()),
            fetch("/tier1/dota").then(r => r.json())
        ]);

        function isLive(m) {
            return m.status && m.status.toLowerCase() === "running";
        }

        function render(list) {
            const live = list.filter(isLive);

            if (live.length === 0) return "No live matches";

            return live.map(m => {

    let mapsHtml = "";

    if (m.maps && m.maps.length > 0) {

        mapsHtml = m.maps.map(mp => {

            let status = "Pending";

            if (mp.winner) {
                status = mp.winner + " ✅";
            }
            else if (
                mp.status &&
                (
                    mp.status.toLowerCase() === "running" ||
                    mp.status.toLowerCase() === "live"
                )
            ) {
                status = "LIVE 🔥";
            }

            return `
                <div class="small">
                    Map ${mp.map}: ${status}
                </div>
            `;
        }).join("");
    }

    return `
        <div class="match">

            🔴 <b>
                ${m.team1} ${m.score1 || 0}
                -
                ${m.score2 || 0} ${m.team2}
            </b>

            <div class="small">
                ${m.league}
            </div>

            ${mapsHtml}

        </div>
    `;
}).join("");
        }

        document.getElementById("cs2").innerHTML = render(cs2);
        document.getElementById("valorant").innerHTML = render(valorant);
        document.getElementById("lol").innerHTML = render(lol);
        document.getElementById("dota").innerHTML = render(dota);

    } catch (err) {
        console.error(err);
        document.body.innerHTML = "❌ Failed to load live data (check backend)";
    }
}

loadLive();
setInterval(loadLive, 15000);
</script>

</body>
</html>
"""

@app.route("/match/<int:match_id>")
def match_page(match_id):

    game = requests.get(
        f"https://api.pandascore.co/matches/{match_id}",
        headers=headers()
    ).json()

    opp = game.get("opponents")

    # ❌ safety check (prevents crash)
    if not opp or len(opp) < 2:
        return "<h1 style='color:white;background:black'>Match data not available</h1>"

    team1 = opp[0]["opponent"].get("name", "TBD")
    team2 = opp[1]["opponent"].get("name", "TBD")

    logo1 = opp[0]["opponent"].get("image_url")
    logo2 = opp[1]["opponent"].get("image_url")

    results = game.get("results") or []

    score1 = results[0].get("score", 0) if len(results) > 0 else 0
    score2 = results[1].get("score", 0) if len(results) > 1 else 0

    maps_html = ""

    for i, g in enumerate(game.get("games", []), start=1):

        maps_html += f"""
        <div style="padding:10px;border:1px solid #222;margin:10px 0;">
            <b>Map {i}</b><br>
            Status: {g.get("status","unknown")}
        </div>
        """

    return f"""
    <html>
    <body style="background:#0a0a0a;color:white;font-family:Arial;padding:20px">

        <div style="display:flex;align-items:center;gap:15px">

            <img src="{logo1}" width="50">
            <h2>{team1}</h2>

            <h1 style="margin:0 20px">{score1} - {score2}</h1>

            <h2>{team2}</h2>
            <img src="{logo2}" width="50">

        </div>

        <h3>Maps</h3>
        {maps_html}

    </body>
    </html>
    """

def sort_matches(matches):
    return sorted(
        matches,
        key=lambda x: x.get("time", "")
    )

# =========================
# JSON ENDPOINTS
# =========================

@app.route("/tier1/lol")
def tier1_lol():
    matches = [format_match(m) for m in get_lol_matches()]
    matches = [m for m in matches if m is not None]
    matches = sort_matches(matches)
    return jsonify(matches)

@app.route("/tier1/cs2")
def tier1_cs2():
    matches = [format_match(m) for m in get_cs2_matches()]
    matches = [m for m in matches if m is not None]
    matches = sort_matches(matches)
    return jsonify(matches)

@app.route("/tier1/valorant")
def tier1_valorant():
    matches = [format_match(m) for m in get_valorant_matches()]
    matches = [m for m in matches if m is not None]
    matches = sort_matches(matches)
    return jsonify(matches)

@app.route("/tier1/dota")
def tier1_dota():
    matches = [format_match(m) for m in get_dota_matches()]
    matches = [m for m in matches if m is not None]
    matches = sort_matches(matches)
    return jsonify(matches)

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)