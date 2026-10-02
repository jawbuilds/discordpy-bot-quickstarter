from __future__ import annotations

import logging

import discord
from discord.ext import commands

from src import config

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    """명령어 실행 중 발생하는 오류를 처리하는 Cog입니다."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        # 다른 Cog나 명령어에서 직접 처리한 오류는 무시합니다.
        if getattr(ctx.command, "on_error", None):
            return

        # 이미 command에 local error handler가 있는 경우
        if ctx.command and hasattr(ctx.command, "on_error"):
            return

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            message = (
                "봇에게 필요한 권한이 없습니다.\n"
                f"필요한 권한: `{', '.join(error.missing_perms)}`"
            )

        elif isinstance(error, commands.MissingPermissions):
            message = (
                "이 명령어를 사용할 권한이 없습니다.\n"
                f"필요한 권한: `{', '.join(error.missing_perms)}`"
            )

        elif isinstance(error, commands.CheckFailure):
            message = "이 명령어를 사용할 권한이 없습니다."

        elif isinstance(error, commands.CommandOnCooldown):
            message = (
                f"아직 **{error.retry_after:.1f}초** 동안 "
                "이 명령어를 사용할 수 없습니다."
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            message = (
                f"필수 인자가 누락되었습니다: "
                f"`{error.param.name}`"
            )

        elif isinstance(error, commands.BadArgument):
            message = "명령어 인자를 올바르게 입력해주세요."

        else:
            log.exception(
                "처리되지 않은 명령어 오류: command=%s",
                ctx.command,
                exc_info=error,
            )

            if config.DEBUG:
                message = (
                    "디버그 모드에서 처리되지 않은 오류가 발생했습니다.\n"
                    f"```py\n{error}\n```"
                )
            else:
                message = "명령어를 실행하는 중 오류가 발생했습니다."

        embed = discord.Embed(
            title="명령어 오류",
            description=message,
            color=discord.Color.red(),
        )

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            log.exception("오류 메시지를 Discord에 전송하지 못했습니다.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
