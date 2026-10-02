"""
페이지 넘기기 버튼 (⬅ ⏹ ➡).
이모지 반응 방식을 discord.py 2.x 버튼(discord.ui.View) 방식으로 재작성했습니다.
"""
from __future__ import annotations

import discord
from discord.ext import commands

Page = str | discord.Embed


class PageView(discord.ui.View):
    def __init__(self, author_id: int, pages: list[Page], timeout: float) -> None:
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.pages = pages
        self.index = 0
        self.message: discord.Message | None = None
        self._update_buttons()

    def render(self) -> dict:
        """현재 페이지를 send/edit에 넘길 인자로 바꿉니다. (문자열이면 content, Embed면 embed)"""
        page = self.pages[self.index]
        if isinstance(page, discord.Embed):
            return {"content": None, "embed": page}
        return {"content": page, "embed": None}

    def _update_buttons(self) -> None:
        # 첫/마지막 페이지에서는 해당 방향 버튼을 비활성화합니다.
        self.prev_button.disabled = self.index == 0
        self.next_button.disabled = self.index == len(self.pages) - 1

    async def _show(self, interaction: discord.Interaction) -> None:
        self._update_buttons()
        await interaction.response.edit_message(**self.render(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("명령어를 실행한 사람만 누를 수 있어요.", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        if self.message:
            try:
                await self.message.edit(view=None)  # 버튼 제거
            except discord.HTTPException:
                pass  # 메시지가 이미 삭제된 경우 등

    @discord.ui.button(emoji="⬅", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.index -= 1
        await self._show(interaction)

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(view=None)
        self.stop()

    @discord.ui.button(emoji="➡", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.index += 1
        await self._show(interaction)


async def start_page(ctx: commands.Context, pages: list[Page], timeout: float = 30) -> discord.Message:
    """
    페이지 기능 코루틴 함수입니다.

    :param ctx: 명령어 컨텍스트 (이 명령어를 실행한 사람만 누를 수 있어요)
    :param pages: 보낼 페이지 리스트 (문자열이나 discord.Embed, 섞어서 써도 돼요)
    :param timeout: 마지막 조작 후 버튼이 유지되는 시간 (기본: 30초)
    :return: 보낸 메시지. 버튼 처리는 백그라운드에서 진행되니 이 함수는 바로 끝나요.
    """
    if not pages:
        raise ValueError("pages가 비어 있어요.")

    if len(pages) == 1:  # 넘길 페이지가 없으면 버튼 없이 보냅니다.
        view = PageView(ctx.author.id, pages, timeout)
        return await ctx.send(**view.render())

    view = PageView(ctx.author.id, pages, timeout)
    view.message = await ctx.send(**view.render(), view=view)
    return view.message