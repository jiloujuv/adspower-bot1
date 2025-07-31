import discord
from discord.ext import commands, tasks
import pyotp
import asyncio
from keep_alive import keep_alive

BOT_TOKEN = "MTQwMDE0OTEyODk4MTM4NTM5MA.GzO_6s.wvdeb6E-6xbZjcL4wJE6pIPF1hqYuNqO1fTk74"
TOTP_SECRET = "2Y6ZQ2MMIBHAQZXB6E5ZWNJUCI3OHS4P"
CHANNEL_ID = 1394380083623366676

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

cooldown = False  # To control button reactivation


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


class CodeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click to Get Code | انتظر للحصول على الرمز", style=discord.ButtonStyle.danger, disabled=False)
    async def get_code(self, interaction: discord.Interaction, button: discord.ui.Button):
        totp = pyotp.TOTP(TOTP_SECRET)
        code = totp.now()
        message = await interaction.response.send_message(
            f"🔐 **Your 2FA code is:** `{code}` (expires in 30s)\n"
            f"رمز المصادقة الخاص بك هو: `{code}` (ينتهي في 30 ثانية)",
            ephemeral=False
        )
        await asyncio.sleep(20)
        await interaction.followup.delete_message(message.id)


@bot.command()
async def login(ctx):
    global cooldown
    if cooldown:
        await ctx.send("⏳ Please wait 30 seconds before requesting again.")
        return

    cooldown = True
    totp = pyotp.TOTP(TOTP_SECRET)
    time_left = totp.interval - (int(asyncio.get_event_loop().time()) % totp.interval)

    view = CodeButton()
    msg = await ctx.send(
        f"""**AutoLogin Guide**
📥 Download AdsPower Browser
🔑 Login using your credentials

**Step 3:** Click the button below to get your code.
Time remaining for current code: {time_left}s ✅ Ready
الوقت المتبقي للرمز الحالي: {time_left}s ✅ Ready

⏳ انتظر للحصول على الرمز ⏳""",
        view=view
    )

    await asyncio.sleep(5)
    for child in view.children:
        child.disabled = True
    await msg.edit(view=view)

    await asyncio.sleep(25)
    cooldown = False


keep_alive()
bot.run(BOT_TOKEN)
