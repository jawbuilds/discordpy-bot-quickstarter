# corgs/ 폴더 자동 로드
# 화이트리스트 제한(봇 소유자도 통과하도록 보완)
# 상태 메시지 15초 순환
# Cog 관리 패널(이모지 반응 대신 셀렉트 메뉴와 버튼으로)
# 파일 로그(콘솔에도 같이 출력)

# 고친 것
# Intents 지정, await load_extension, setup_hook 사용
# websockets 의존성과 JSON 반복 읽기 제거. 설정은 전부 config.py에서
# 상태 순환은 tasks.loop로 바꿔서 일시적인 연결 오류 처리를 맡김
# Cog 하나가 로드에 실패해도 봇은 켜지고 로그만 남김
# 권한 없는 유저가 !cog를 쓰면 안내 메시지를 보냄
# 직접 만든 Cog가 생기기 전까지는 기본 !help가 동작함

# 손볼 것
# 1. pyproject.toml : 앞서 예시의 py-modules = ["bot"]을 ["main", "config"로 바꾸기]
# 봇은 python main.py로 실행
# 2. 개발자 포털 : 봇 설정에서 메시지 콘텐츠 intent를 켜야 접두사 명령어가 동작함
# 3. Cog 하나는 있어야 패널을 테스트할 수 있음. corgs/general.py에 핑 명령어를 넣은 예제로 테스트하기

"""
discordpy-bot-quickstarter
discord.py 2.x 기반 디스코드 봇 스타터 템플릿
"""

from __future__ import annotations

import itertools
import logging
from pathlib import Path

import discord
from discord.ext import commands, tasks

from src import config

log = logging.getLogger(__name__)

COGS_DIR = Path(__file__).parent / "cogs"

def available_cogs() -> list[str]:
    """cogs 폴더 안의 Cog 파일 이름(확장자 제외)를 정렬해서 돌려줌."""
    return sorted(p.stem for p in COGS_DIR.glob("*.py") if not p.stem.startswith("_"))

class MyBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        # 접두사 명령어(!ping 등)를 쓰려면 필요함
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or(config.DEFAULT_PREFIX), intents=intents,)
        self._presence = itertools.cycle(config.PRESENCE)

    async def setup_hook(self) -> None:
        """로그인 직후, 연결 전에 한 번만 실행됨. Cog로드와 백그라운드 작업 시작에 알맞음"""
        for name in available_cogs():
            try:
                await self.load_extension(f"cogs.{name}")
            except Exception:
                # Cog 하나가 망가져도 봇 전체는 켜지도록 로그만 남김
                log.exception("Cog 로드 실패 : %s", name)

        if config.PRESENCE:
            self.rotate_presence.start()

    async def close(self) -> None:
        self.rotate_presence.cancel()
        await super().close()

    @tasks.loop(seconds=15)
    async def rotate_presence(self) -> None:
        """상태 메시지를 15초마다 순환함. 일시적인 연결 오류는 task.loop가 알아서 재시도."""
        await self.change_presence(activity=discord.Game(next(self._presence)))

    @rotate_presence.before_loop
    async def before_rotate_presence(self) -> None:
        await self.wait_until_ready()

    async def on_ready(self) -> None:
        # 연결이 끊겼다 다시 붙을 때도 호출되므로 한 번만 해야 하는 작업은 setup_hook에 두기
        log.info("Bot online : %s (debug=%s)", self.user, config.DEBUG)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CheckFailure):
            await ctx.send("이 명령어를 사용할 권한이 없어요.")
            return
        log.error("명령어 오류 (%s)", ctx.command, exc_info=error)

def is_whitelisted():
    """화이트리스트에 있는 유저나 봇 소유자만 통과시키는 체크입니다."""
 
    async def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in config.WHITELIST or await ctx.bot.is_owner(ctx.author)
 
    return commands.check(predicate)

class CogPanel(discord.ui.View):
    """Cog를 로드/언로드/리로드하는 관리 패널입니다. (셀렉트 메뉴 + 버튼)"""
 
    def __init__(self, bot: commands.Bot, author_id: int) -> None:
        super().__init__(timeout=60)
        self.bot = bot
        self.author_id = author_id
        self.selected: str | None = None
        self.message: discord.Message | None = None
        self.names = available_cogs()[:25]  # 셀렉트 옵션과 임베드 필드는 최대 25개
 
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
            description=f"`cogs` 폴더의 Cog 개수: {len(self.names)}개",
            color=discord.Color.from_rgb(225, 225, 225),
        )
        for name in self.names:
            loaded = f"cogs.{name}" in self.bot.extensions
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
            await method(f"cogs.{self.selected}")
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
 
 
bot = MyBot()
 
 
@bot.command(name="cog", aliases=["cogs", "코그"])
@is_whitelisted()
async def cog_panel(ctx: commands.Context) -> None:
    """Cog 관리 패널을 엽니다."""
    if not available_cogs():
        await ctx.send("`cogs` 폴더에 Cog 파일이 없어요.")
        return
    view = CogPanel(ctx.bot, ctx.author.id)
    view.message = await ctx.send(embed=view.build_embed(), view=view)
 
 
def setup_logging() -> None:
    """콘솔과 파일에 동시에 로그를 남깁니다."""
    level = logging.DEBUG if config.DEBUG else logging.INFO
    discord.utils.setup_logging(level=level)  # 콘솔 출력
 
    file_handler = logging.FileHandler(f"{config.BOT_NAME}.log", encoding="utf-8", mode="w")
    file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
    logging.getLogger().addHandler(file_handler)
 
 
if __name__ == "__main__":
    setup_logging()
    bot.run(config.TOKEN, log_handler=None)  # 로깅은 위에서 직접 설정했어요
 