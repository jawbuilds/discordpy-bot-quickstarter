"""
확인(⭕/❌) 버튼.
이모지 반응 방식을 discord.py 2.x 버튼(discord.ui.View) 방식으로 재작성했습니다.
"""
from __future__ import annotations

import discord
from discord.ext import commands


class ConfirmView(discord.ui.View):
    def __init__(self, author_id: int, timeout: float) -> None:
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value: bool | None = None  # True: 승인, False: 거절, None: 타임아웃

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("명령어를 실행한 사람만 누를 수 있어요.", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="⭕", style=discord.ButtonStyle.success)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = True
        await interaction.response.edit_message(view=None)  # 버튼 제거
        self.stop()

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.danger)
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = False
        await interaction.response.edit_message(view=None)
        self.stop()


async def confirm(ctx: commands.Context, msg: discord.Message, timeout: float = 30) -> bool | None:
    """
    해당 액션을 할지 확인하는 코루틴 함수입니다.

    :param ctx: 명령어 컨텍스트 (이 명령어를 실행한 사람만 누를 수 있어요)
    :param msg: 버튼을 붙일 메시지 (봇이 보낸 메시지여야 해요)
    :param timeout: 타임아웃 시간 (기본: 30초)
    :return: 승인하면 True, 거절하면 False, 타임아웃이면 None
    """
    view = ConfirmView(ctx.author.id, timeout)
    await msg.edit(view=view)
    await view.wait()

    if view.value is None:  # 타임아웃: 버튼 제거
        try:
            await msg.edit(view=None)
        except discord.HTTPException:
            pass  # 메시지가 이미 삭제된 경우 등
    return view.value