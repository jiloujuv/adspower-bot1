import os
import discord
import pyotp
import asyncio
from discord.ext import commands
from keep_alive import keep_alive


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TOTP_SECRET = os.getenv("TOTP_SECRET")  # مفتاح 2FA من AdsPower


class CodeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.button = discord.ui.Button(label="Click to Get Code | اضغط للحصول على الرمز", style=discord.ButtonStyle.danger)
        self.button.callback = self.send_code
        self.add_item(self.button)
        self.button.disabled = False  
        self.message = None  
        self.code_used = False

    async def disable_button(self):
        await asyncio.sleep(5)
        self.button.disabled = True
        await self.message.edit(view=self)

    async def send_code(self, interaction: discord.Interaction):
        if self.code_used:
            await interaction.response.send_message("🔁 انتظر لإعادة تفعيل الزر...", ephemeral=True)
            return

        self.code_used = True
        totp = pyotp.TOTP(TOTP_SECRET)
        code = totp.now()
        remaining = totp.interval - (int(time.time()) % totp.interval)

        embed = discord.Embed(title="Your 2FA Code", color=discord.Color.red())
        embed.add_field(name="🔐 Code:", value=f"**{code}** (expires in {remaining}s)", inline=False)
        embed.set_footer(text="🔔 سيتم حذف هذه الرسالة بعد 20 ثانية.")
        code_message = await interaction.response.send_message(embed=embed)
        await asyncio.sleep(20)
        await (await interaction.original_response()).delete()

    async def start_timer(self):
        await self.disable_button()

@bot.event
async def on_ready():
    print(f"[✅] Logged in as {bot.user}")

@bot.command(name="getcode")
async def get_code(ctx):
    view = CodeButton()
    view.message = await ctx.send("🔴 اضغط الزر للحصول على رمز AdsPower", view=view)
    await view.start_timer()

keep_alive()
bot.run(TOKEN)
