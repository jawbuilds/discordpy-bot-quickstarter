from __future__ import annotations

import discord
from discord.ext import commands


class Basic(commands.Cog):
    """기본적인 봇 명령어를 제공하는 Cog입니다."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="ping",
        aliases=["핑"],
    )
    async def ping(self, ctx: commands.Context) -> None:
        """봇의 현재 WebSocket latency를 확인합니다."""

        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="Pong!",
            description=f"현재 지연 시간은 **{latency}ms**입니다.",
            color=discord.Color.blurple(),
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Basic(bot))