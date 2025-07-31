import discord
from discord.ext import commands, tasks
import pyotp
import asyncio
import os
from keep_alive import keep_alive

# إعدادات
TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

totp = pyotp.TOTP("2Y6ZQ2MMIBHAQZXB6E5ZWNJUCI3OHS4P")  

cooldown_active = False 

class CodeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GetCodeButton())

class GetCodeButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🔴 Click to Get Code | انتظر للحصول على الرمز", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        global cooldown_active
        if cooldown_active:
            await interaction.response.send_message("⏳ الزر غير متاح الآن، انتظر قليلًا...", ephemeral=True)
            return

        cooldown_active = True
        code = totp.now()
        time_remaining = totp.interval - (discord.utils.utcnow().timestamp() % totp.interval)
        message = await interaction.response.send_message(
            f"📲 Your 2FA code is: **{code}** (expires in {int(time_remaining)}s)\nرمز المصادقة الخاص بك: **{code}**", ephemeral=True
        )

        await asyncio.sleep(20)  # حذف الرسالة بعد 20 ثانية
        await message.delete_original_response()
        await asyncio.sleep(10)  # انتظار حتى يكمل 30 ثانية
        cooldown_active = False

@bot.event
async def on_ready():
    print(f"[✅] Logged in as {bot.user}")
    send_button_message.start()

@tasks.loop(seconds=30)
async def send_button_message():
    global cooldown_active
    cooldown_active = False
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("✅ اضغط الزر للحصول على الكود:", view=CodeButton())

keep_alive()
bot.run(TOKEN)
