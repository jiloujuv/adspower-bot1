import discord

def create_embed(remaining_seconds: int, ready: bool) -> discord.Embed:
    embed = discord.Embed(
        title="AutoLogin Guide\nدليل تسجيل الدخول التلقائي",
        description=(
            "**Step 1:**\nDownload AdsPower Browser from here\n"
            "**Step 2:**\nLogin to AdsPower using the provided credentials\n"
            "**Step 3:**\nClick the button below to get your Authenticator Verification Code and enter it.\n"
            f"**Time remaining for current code:** {remaining_seconds}s {'✅ Ready' if ready else '❌ Not Ready'}\n"
            f"الوقت المتبقي للرمز الحالي: {remaining_seconds}s {'✅ جاهز' if ready else '❌ غير جاهز'}\n"
            "**Step 4:**\nClick OPEN on the profile you want to access\n\n"
            "⏳ انتظر للحصول على الرمز ⏳"
        ),
        color=discord.Color.red()
    )
    return embed

from discord.ext import commands
import pyotp
import os
import asyncio
from flask import Flask
from threading import Thread
import datetime


BOT_TOKEN = os.getenv("BOT_TOKEN")


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


app = Flask('keep_alive')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


TOTP_SECRET = os.getenv("TOTP_SECRET") 


weekly_limit = 10
used_codes = 0


button_enabled = False

async def toggle_button_state():
    global button_enabled
    while True:
        button_enabled = True
        await asyncio.sleep(5)
        button_enabled = False
        await asyncio.sleep(25) 


@bot.event
async def on_ready():
    print(f"[✅] Logged in as {bot.user}")
    
    channel = bot.get_channel(1394380083623366676)  
    if channel:
        view = CodeButton() 
        await channel.send(embed=create_embed(remaining_seconds=0, ready=True), view=view)



class CodeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click to Get Code | اضغط للحصول على الرمز", style=discord.ButtonStyle.danger)
    async def get_code(self, interaction: discord.Interaction, button: discord.ui.Button):
        global used_codes

       
        if not button_enabled:
            await interaction.response.send_message("⏳ الزر غير متاح الآن، انتظر قليلًا...", ephemeral=True)
            return

        if used_codes >= weekly_limit:
            await interaction.response.send_message("❌ لقد استخدمت جميع الرموز لهذا الأسبوع.", ephemeral=True)
            return

     
        totp = pyotp.TOTP(TOTP_SECRET)
        code = totp.now()
        time_left = totp.interval - datetime.datetime.now().second % totp.interval
        used_codes += 1

        msg = (
            f"📲 Your 2FA code is: **{code}** (expires in {time_left}s)\n"
            f"🔢 You have {weekly_limit - used_codes} codes left this week.\n"
            f"رمز المصادقة الخاص بك هو: **{code}** (ينتهي خلال {time_left}s)\n"
            f"تبقّى {weekly_limit - used_codes} رمزًا لهذا الأسبوع."
        )

       
        code_msg = await interaction.response.send_message(msg)
        await asyncio.sleep(20)
        await interaction.delete_original_response()


@bot.command()
async def login(ctx):
    view = CodeButton()
    totp = pyotp.TOTP(TOTP_SECRET)
    time_left = totp.interval - datetime.datetime.now().second % totp.interval

    msg = (
        "**AutoLogin Guide**\n"
        "دليل تسجيل الدخول التلقائي\n"
        "**Step 1:** Download AdsPower Browser from here\n"
        "**Step 2:** Login to AdsPower using the provided credentials\n"
        "**Step 3:** Click the button below to get your Authenticator Verification Code and enter it.\n"
        f"**Time remaining for current code: {time_left}s ✅ Ready**\n"
        f"الوقت المتبقي للرمز الحالي: {time_left}s ✅ جاهز\n"
        "**Step 4:** Click OPEN on the profile you want to access\n"
        "⏳ انتظر للحصول على الرمز ⏳"
    )

    await ctx.send(msg, view=view)


keep_alive()
bot.run(BOT_TOKEN)
