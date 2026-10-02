"""
Cog 관리 패널 (셀렉트 메뉴 + 로드/언로드/리로드 버튼).

구조 참고: eunwoo1104/discord-py-bot-template main.py의 Cog 관리 패널 (MIT)
이모지 반응 방식을 discord.py 2.x 컴포넌트(discord.ui.View) 방식으로 재작성했습니다.
"""
from __future__ import annotations

import logging

import discord
from discord.ext import commands

from src import config

log = logging.getLogger(__name__)


class CogPanel(discord.ui.View):
    """Cog를 로드/언로드/리로드하는 관리 패널입니다."""

    def __init__(
        self,
        bot: commands.Bot,
        author_id: int,
        names: list[str],
        package: str = "cogs",
    ) -> None:
        """
        :param bot: 디스코드 봇
        :param author_id: 패널을 조작할 수 있는 유저 ID (명령어를 실행한 사람)
        :param names: 관리할 Cog 이름 목록 (확장자 제외, 예: ["general", "admin"])
        :param package: Cog가 들어 있는 패키지 경로 (기본: "cogs", 예: "src.cogs")
        """
        if not names:
            raise ValueError("names가 비어 있어요.")

        super().__init__(timeout=60)
        self.bot = bot
        self.author_id = author_id
        self.package = package
        self.names = names[:25]  # 셀렉트 옵션과 임베드 필드는 최대 25개
        self.selected: str | None = None
        self.message: discord.Message | None = None

        self.select = discord.ui.Select(
            placeholder="Cog를 선택하세요",
            options=[discord.SelectOption(label=name) for name in self.names],
            row=0,
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title=f"{config.BOT_NAME} Cog 관리 패널",
            description=f"`{self.package}` 폴더의 Cog 개수: {len(self.names)}개",
            color=discord.Color.from_rgb(225, 225, 225),
        )
        for name in self.names:
            loaded = f"{self.package}.{name}" in self.bot.extensions
            marker = "▶ " if name == self.selected else ""
            embed.add_field(
                name=f"{marker}{name}",
                value=f"상태: {'로드됨' if loaded else '언로드됨'}",
                inline=False,
            )
        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("명령어를 실행한 사람만 사용할 수 있어요.", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        if self.message:
            try:
                await self.message.edit(content="Cog 관리 패널이 닫혔습니다.", embed=None, view=None)
            except discord.HTTPException:
                pass  # 메시지가 이미 삭제된 경우 등

    async def on_select(self, interaction: discord.Interaction) -> None:
        self.selected = self.select.values[0]
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def run_action(self, interaction: discord.Interaction, action: str) -> None:
        if self.selected is None:
            await interaction.response.send_message("먼저 Cog를 선택해주세요.", ephemeral=True)
            return

        method = getattr(self.bot, f"{action}_extension")
        error: str | None = None
        try:
            await method(f"{self.package}.{self.selected}")
        except commands.ExtensionAlreadyLoaded:
            error = "이미 Cog가 로드되어 있어요."
        except commands.ExtensionNotLoaded:
            error = "Cog가 로드되어 있지 않아요."
        except commands.ExtensionError as exc:
            log.exception("Cog %s 실패: %s", action, self.selected)
            error = f"실패했어요: {exc}"

        if error:
            await interaction.response.send_message(error, ephemeral=True)
        else:
            await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="로드", style=discord.ButtonStyle.success, row=1)
    async def load_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.run_action(interaction, "load")

    @discord.ui.button(label="언로드", style=discord.ButtonStyle.danger, row=1)
    async def unload_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.run_action(interaction, "unload")

    @discord.ui.button(label="리로드", style=discord.ButtonStyle.primary, row=1)
    async def reload_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.run_action(interaction, "reload")