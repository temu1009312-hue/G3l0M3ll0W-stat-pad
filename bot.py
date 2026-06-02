import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import asyncio
import os

# =========================
# 🔑 TOKENS
# =========================

PANDASCORE_TOKEN = os.environ.get("PANDASCORE_TOKEN")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

LOL_CHANNEL_ID = 1510980848390897734
CS2_CHANNEL_ID = 1510980941634474116
MAIN_CHANNEL_ID = 1510853686203777108

tracked_matches = {}  # match_id -> message_id
sent_matches = set()

# =========================
# 📡 PANDA SCORE - LOL
# =========================
def get_lol_matches():
    url = "https://api.pandascore.co/lol/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print("LoL API status:", res.status_code)

        data = res.json()

        if not isinstance(data, list):
            print("LoL API unexpected response:", data)
            return []

        return data

    except Exception as e:
        print("LoL API Error:", e)
        return []

# =========================
# 📡 PANDA SCORE - CS2
# =========================
def get_cs2_matches():
    url = "https://api.pandascore.co/csgo/matches/upcoming"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        print("CS2 API status:", res.status_code)

        data = res.json()

        if not isinstance(data, list):
            print("CS2 API unexpected response:", data)
            return []

        return data

    except Exception as e:
        print("CS2 API Error:", e)
        return []

# =========================
# 📡 PLAYER MATCHES
# =========================
def get_player_matches(player_id):
    url = f"https://api.pandascore.co/players/{player_id}/matches"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}
    return requests.get(url, headers=headers).json()

# =========================
# 🔄 NORMALIZERS
# =========================
def normalize_lol(match):
    teams = match.get("opponents", [])
    if len(teams) < 2:
        return None

    return {
        "team1": teams[0]["opponent"]["name"],
        "team2": teams[1]["opponent"]["name"],
        "game": "League of Legends",
        "time": match.get("scheduled_at", "TBD"),
        "source": "PandaScore LoL"
    }

def normalize_cs2(match):
    teams = match.get("opponents", [])
    if len(teams) < 2:
        return None

    return {
        "team1": teams[0]["opponent"]["name"],
        "team2": teams[1]["opponent"]["name"],
        "game": "CS2",
        "time": match.get("scheduled_at", "TBD"),
        "source": "PandaScore CS2"
    }

def make_match_id(match):
    return str(match.get("id") or f"{match['team1']}_{match['team2']}_{match['time']}")

# =========================
# 🤖 BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🔁 AUTO POST SYSTEM
# =========================
async def auto_post_matches():
    await bot.wait_until_ready()

    lol_channel = bot.get_channel(1510980848390897734)
    cs2_channel = bot.get_channel(1510980941634474116)

    await asyncio.sleep(10)

    while not bot.is_closed():

        # ================= LOL =================
        for m in get_lol_matches():

            if not is_tier1(m):
                continue

            norm = normalize_lol(m)
            if not norm:
                continue

            match_id = str(m.get("id"))

            status = get_status(m)

            embed = discord.Embed(
                title=f"{status} {norm['team1']} vs {norm['team2']}",
                description="🎮 League of Legends (Tier 1 Tracker)",
                color=0x5865F2
            )

            embed.add_field(name="⏰ Time", value=norm["time"], inline=True)
            embed.add_field(name="📡 Source", value=norm["source"], inline=True)

            # ================= PRO LOGIC =================
            if match_id in tracked_matches:
                try:
                    msg = await lol_channel.fetch_message(tracked_matches[match_id])
                    await msg.edit(embed=embed)
                except:
                    pass
            else:
                msg = await lol_channel.send(embed=embed)
                tracked_matches[match_id] = msg.id

        # ================= CS2 =================
        for m in get_cs2_matches():

            if not is_tier1(m):
                continue

            norm = normalize_cs2(m)
            if not norm:
                continue

            match_id = str(m.get("id"))

            status = get_status(m)

            embed = discord.Embed(
                title=f"{status} {norm['team1']} vs {norm['team2']}",
                description="🔫 Counter-Strike 2 (Tier 1 Tracker)",
                color=0xF1C40F
            )

            embed.add_field(name="⏰ Time", value=norm["time"], inline=True)
            embed.add_field(name="📡 Source", value=norm["source"], inline=True)

            if match_id in tracked_matches:
                try:
                    msg = await cs2_channel.fetch_message(tracked_matches[match_id])
                    await msg.edit(embed=embed)
                except:
                    pass
            else:
                msg = await cs2_channel.send(embed=embed)
                tracked_matches[match_id] = msg.id

        await asyncio.sleep(300)  # 5 min refresh (PRO SPEED)

def is_tier1(match):
    if not isinstance(match, dict):
        return False

    league = match.get("league", {})
    serie = match.get("serie", {})

    league_name = league.get("name", "") if isinstance(league, dict) else ""
    serie_name = serie.get("name", "") if isinstance(serie, dict) else ""

    text = f"{league_name} {serie_name}".lower()

    tier1_keywords = [
        "lck", "lpl", "lec", "lcs",
        "msi", "worlds",
        "iem", "blast", "esl pro league", "major"
    ]

    return any(k in text for k in tier1_keywords)
# =========================
# 📊 COMMANDS
# =========================
@bot.command()
async def matches(ctx):
    all_matches = []

    # ================= LOL =================
    for m in get_lol_matches():
        if is_tier1(m):
            norm = normalize_lol(m)
            if norm:
                all_matches.append(norm)

    # ================= CS2 =================
    for m in get_cs2_matches():
        if is_tier1(m):
            norm = normalize_cs2(m)
            if norm:
                all_matches.append(norm)

    # limit results
    all_matches = all_matches[:10]

    if not all_matches:
        await ctx.send("No Tier 1 matches found.")
        return

    # ================= SEND EMBEDS =================
    for m in all_matches:
        embed = discord.Embed(
            title=f"{m['team1']} vs {m['team2']}",
            description=f"🎮 {m['game']}",
            color=0x00ff99
        )
        embed.add_field(name="⏰ Time", value=m["time"], inline=True)
        embed.add_field(name="📡 Source", value=m["source"], inline=True)

        await ctx.send(embed=embed)

@bot.command()
async def tier1(ctx):
    matches = []

    for m in get_cs2_matches():
        if is_tier1(m):
            norm = normalize_cs2(m)
            if norm:
                matches.append(norm)

    for m in get_lol_matches():
        if is_tier1(m):
            norm = normalize_lol(m)
            if norm:
                matches.append(norm)

    if not matches:
        await ctx.send("No Tier 1 matches found.")
        return

    for m in matches[:10]:
        await ctx.send(
            f"🏆 {m['team1']} vs {m['team2']}\n"
            f"🎮 {m['game']}\n"
            f"⏰ {m['time']}"
        )

# =========================
# 👤 PLAYER STATS
# =========================
@bot.command()
async def player(ctx, name):
    url = f"https://api.pandascore.co/players?search={name}"
    headers = {"Authorization": f"Bearer {PANDASCORE_TOKEN}"}

    res = requests.get(url, headers=headers)
    data = res.json()

    if not data:
        await ctx.send("Player not found ❌")
        return

    p = data[0]
    player_id = p["id"]

    matches = get_player_matches(player_id)

    wins = 0
    losses = 0

    for m in matches[:10]:
        if m.get("winner_id") == player_id:
            wins += 1
        else:
            losses += 1

    embed = discord.Embed(
        title=f"🎮 {p.get('name', 'Unknown')}",
        description="📊 Player Stats",
        color=0x00ff99
    )

    embed.add_field(name="🏆 Team", value=p.get("current_team", {}).get("name", "No team"), inline=True)
    embed.add_field(name="🎯 Role", value=p.get("role", "Unknown"), inline=True)
    embed.add_field(name="🌍 Country", value=p.get("nationality", "Unknown"), inline=True)
    embed.add_field(name="📈 Wins", value=str(wins), inline=True)
    embed.add_field(name="📉 Losses", value=str(losses), inline=True)

    await ctx.send(embed=embed)

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(auto_post_matches())

# =========================
# RUN BOT
# =========================

bot.run(DISCORD_TOKEN)