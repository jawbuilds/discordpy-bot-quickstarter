from __future__ import annotations

import discord
from discord.ext import commands


class Help(commands.Cog):
    """봇의 명령어 도움말을 제공하는 Cog입니다."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="help",
        aliases=["도움", "도움말"],
    )
    async def help(self, ctx: commands.Context) -> None:
        """현재 사용 가능한 명령어를 표시합니다."""

        embed = discord.Embed(
            title="명령어 도움말",
            description=(
                f"기본 접두사: `{ctx.prefix}`\n"
                "사용 가능한 명령어 목록입니다."
            ),
            color=discord.Color.blurple(),
        )

        for cog_name, cog in self.bot.cogs.items():
            commands_list = [
                command
                for command in cog.get_commands()
                if not command.hidden
            ]

            if not commands_list:
                continue

            command_names = [
                f"`{ctx.prefix}{command.name}`"
                for command in commands_list
            ]

            embed.add_field(
                name=f"{cog_name}",
                value=" ".join(command_names),
                inline=False,
            )

        embed.set_footer(
            text=f"요청자: {ctx.author.display_name}"
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot))
