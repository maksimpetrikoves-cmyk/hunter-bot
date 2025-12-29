import discord
from discord.ext import commands
from datetime import timedelta
import os
import time

TOKEN = os.getenv("TOKEN") or "ВСТАВ_СЮДИ_ТОКЕН"
LOG_CHANNEL_NAME = "hunter-logs"
MODERATOR_ROLE = "Модератор"

SPAM_LIMIT = 5      # повідомлень
SPAM_TIME = 7       # секунд
SPAM_TIMEOUT = 10   # хвилин

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_messages = {}

# ===== СЛОВА =====

FAMILY_INSULTS = [
    "маму", "матір", "мать", "батька", "отца",
    "родних", "семью", "сім'ю"
]

PERSON_INSULTS = [
    "ідіот", "дебіл", "дурак", "лох", "клоун", "даун"
]

HUNTER_INSULTS = [
    "hunter ху", "hunter лох", "hunter гавно",
    "hunter хуй", "hunter чмо", "hunter пид"
]

# ===== ДОПОМІЖНІ =====

def is_moderator(member):
    return any(role.name == MODERATOR_ROLE for role in member.roles)

async def get_log_channel(guild):
    channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
    if not channel:
        channel = await guild.create_text_channel(LOG_CHANNEL_NAME)
    return channel

async def send_dm(member, text):
    try:
        await member.send(text)
    except:
        pass

# ===== ПОДІЇ =====

@bot.event
async def on_ready():
    print(f"✅ Hunter Bot ONLINE: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    member = message.author
    guild = message.guild
    content = message.content.lower()

    # 🛡 Модератор не карається
    if is_moderator(member):
        return

    log = await get_log_channel(guild)

    # ===== АНТИ-СПАМ =====
    now = time.time()
    user_messages.setdefault(member.id, [])
    user_messages[member.id].append(now)

    user_messages[member.id] = [
        t for t in user_messages[member.id]
        if now - t <= SPAM_TIME
    ]

    if len(user_messages[member.id]) >= SPAM_LIMIT:
        await member.timeout(
            timedelta(minutes=SPAM_TIMEOUT),
            reason="Спам"
        )
        await send_dm(
            member,
            "🛑 Ти отримав тайм-аут 10 хвилин за спам."
        )
        embed = discord.Embed(
            title="🛑 Спам",
            description=f"{member.mention}\nТайм-аут 10 хвилин",
            color=discord.Color.blue()
        )
        await log.send(embed=embed)
        user_messages[member.id].clear()
        return

    # 🚫 BAN за Hunter
    if any(w in content for w in HUNTER_INSULTS):
        await member.ban(reason="Оскорбление Hunter Family")
        embed = discord.Embed(
            title="🚫 BAN",
            description=f"{member.mention}\nОскорбление Hunter",
            color=discord.Color.red()
        )
        await log.send(embed=embed)
        return

    # ⛔ 7 днів — родні
    if any(w in content for w in FAMILY_INSULTS):
        await member.timeout(timedelta(days=7), reason="Оскорбление родних")
        await send_dm(
            member,
            "⛔ Ти отримав тайм-аут 7 днів за оскорбление родних."
        )
        embed = discord.Embed(
            title="⛔ Тайм-аут 7 днів",
            description=f"{member.mention}\nОскорбление родних",
            color=discord.Color.orange()
        )
        await log.send(embed=embed)
        return

    # ⚠️ 2 години — людина
    if any(w in content for w in PERSON_INSULTS):
        await member.timeout(timedelta(hours=2), reason="Оскорбление людини")
        await send_dm(
            member,
            "⚠️ Ти отримав тайм-аут 2 години за оскорбление людини."
        )
        embed = discord.Embed(
            title="⚠️ Тайм-аут 2 години",
            description=f"{member.mention}\nОскорбление людини",
            color=discord.Color.yellow()
        )
        await log.send(embed=embed)
        return

    await bot.process_commands(message)

bot.run(TOKEN)
