discordpy-bot-quickstarter

discord.py로 Discord Bot을 빠르게 시작하기 위한 가볍고 확장 가능한 스타터 템플릿입니다.

cogs/에 기능을 추가하는 것부터 시작하세요.






Features

discord.py 2.x 기반

Cog 자동 로딩

cogs/ 중심의 모듈형 구조

.env 기반 환경 설정

Prefix command 지원

Bot owner / whitelist 기반 관리자 명령어 보호

Cog 관리 패널

상태 메시지 자동 순환

콘솔 + 파일 로깅

Cog 로딩 실패 시 전체 Bot이 종료되지 않도록 예외 처리

pyproject.toml 기반 의존성 관리

ruff / pytest 개발 환경 지원

Requirements

Python 3.10+

Discord Application

Discord Bot Token

Python 버전은 pyproject.toml에서 >=3.10으로 지정되어 있습니다.

Quick Start
1. Repository clone
git clone https://github.com/jawbuilds/discordpy-bot-quickstarter.git
cd discordpy-bot-quickstarter

2. 가상환경 생성

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate


Windows:

python -m venv .venv
.venv\Scripts\Activate.ps1

3. 의존성 설치
pip install -e .


개발 도구까지 설치하려면:

pip install -e ".[dev]"


사용하는 패키지 관리자에 따라 uv, pip, poetry 등을 사용할 수 있습니다.

4. 환경변수 설정

.env.example을 복사합니다.

cp .env.example .env


Windows PowerShell:

Copy-Item .env.example .env


.env에 Bot Token 등의 설정을 입력합니다.

DISCORD_TOKEN=your_bot_token


.env는 절대 Git에 commit하지 마세요.

5. Bot 실행
python main.py


Bot이 Discord에 연결되면 로그가 출력됩니다.

Discord Developer Portal 설정

Discord Developer Portal에서 Application을 생성한 뒤 Bot을 추가합니다.

Prefix command를 사용하려면 Message Content Intent가 필요합니다.

이 프로젝트에서는 message_content intent를 코드에서도 활성화하고 있습니다.

따라서 다음 두 곳을 모두 확인하세요.

Discord Developer Portal → Bot → Privileged Gateway Intents

코드의 discord.Intents

실제 사용하지 않는 privileged intent는 활성화하지 않는 것을 권장합니다.

Project Structure
discordpy-bot-quickstarter/
├── cogs/
│   └── *.py              # Discord Bot 기능
│
├── src/
│   ├── config.py         # 환경변수 및 설정
│   └── ui.py             # Cog 관리 UI
│
├── main.py               # Bot entry point
├── .env.example          # 환경변수 예시
├── pyproject.toml        # 프로젝트 및 dependency 설정
├── README.md
└── LICENSE

구조의 핵심
main.py
   │
   ├── Bot 초기화
   │
   ├── cogs/*.py 탐색
   │
   ├── Cog 자동 로드
   │
   └── Discord 연결
          │
          ▼
       cogs/
       ├── general.py
       ├── moderation.py
       └── fun.py


새로운 기능은 가능한 한 cogs/ 안에 독립적인 Cog로 추가하는 것을 권장합니다.

Creating a Cog

예를 들어 cogs/general.py를 생성합니다.

from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))


파일을 추가한 뒤 Bot을 다시 실행하면 자동으로 Cog가 로드됩니다.

cogs/
└── general.py


별도의 main.py 수정은 필요하지 않습니다.

Cog Auto Loading

Bot은 cogs/ 디렉터리의 Python 파일을 검색하여 자동으로 extension을 로드합니다.

await self.load_extension(f"cogs.{name}")


따라서 다음과 같이 기능을 분리할 수 있습니다.

cogs/
├── general.py
├── moderation.py
├── music.py
└── utility.py


각 Cog가 독립적으로 관리되므로 Bot이 커져도 기능별로 코드를 분리하기 쉽습니다.

Cog Management

관리 권한이 있는 사용자는 다음 명령어로 Cog 관리 패널을 열 수 있습니다.

!cog


또는:

!cogs
!코그


Cog 관리 명령은 whitelist에 등록된 사용자 또는 Bot owner만 사용할 수 있습니다.

이를 통해 Bot 기능을 확인하거나 관리할 수 있습니다.

Access Control

관리 명령어에는 whitelist 기반 접근 제한이 적용됩니다.

WHITELIST
   │
   ├── 사용자 ID가 등록되어 있음 → 허용
   │
   └── Bot owner → 허용


일반 사용자가 관리자 명령어를 실행하면 권한 부족 메시지를 반환합니다.

Logging

Bot은 콘솔과 로그 파일에 동시에 로그를 기록합니다.

로그 파일은 Bot 이름을 기준으로 생성됩니다.

예:

mybot.log


로그 레벨은 debug 설정에 따라 DEBUG 또는 INFO로 설정됩니다.

Configuration

Bot 설정은 src/config.py에서 관리합니다.

환경변수와 Bot 동작 설정을 코드에서 분리하여 관리하는 것을 목표로 합니다.

예를 들어 다음과 같은 값을 프로젝트 설정으로 관리할 수 있습니다.

Bot Token

Bot 이름

Prefix

Debug mode

Presence

Whitelist

민감한 값은 소스 코드에 직접 작성하지 말고 .env를 사용하세요.

Development

Ruff:

ruff check .


Pytest:

pytest


새로운 기능을 추가할 때는 가능한 한 독립적인 Cog로 만들고 테스트 가능한 로직은 별도로 분리하는 것을 권장합니다.

Troubleshooting
Bot이 온라인이 되지만 Prefix command가 작동하지 않아요.

Discord Developer Portal에서 Message Content Intent가 활성화되어 있는지 확인하세요.

또한 코드에서도 해당 intent가 활성화되어 있어야 합니다.

Cog가 로드되지 않아요.

다음 사항을 확인하세요.

파일이 cogs/ 안에 있는지

Python 파일 이름이 _로 시작하지 않는지

setup() 함수가 존재하는지

Cog 로딩 오류가 로그에 출력되지 않았는지

.env의 Token이 노출됐어요.

즉시 Discord Developer Portal에서 Bot Token을 재생성하세요.

Token은 GitHub repository, 코드, README, 로그 등에 공개하지 마세요.

References

discord.py Documentation

Discord Developer Documentation

Discord Developer Portal

License

This project is licensed under the MIT License.

See LICENSE for details.