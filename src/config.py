import os # 환경변수를 읽는데 필요
from dotenv import load_dotenv #파이썬-도트인브가 설치돼있어야함.

load_dotenv() #.env를 읽어 환경변수로 등록함. 다른 os.getenv보다 먼저 호출해야해서 import 바로 아래가 맞는 위치.

BOT_NAME = "MyBot" # 공개해도 되는 설정이라 코드에 둬도 괨. 상수는 대문자로 쓰는게 파이썬 관례
DEFAULT_PREFIX = "!" # 요즘 봇은 슬래시 명령어가 대세라 접두사 명령어를 쓸지는 나중에 정하기
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
#환경변수는 항상 문자열이라 "false"도 참이다. 그래서 .lower() == "true"로 비교해야 함.
#bool(os.get("DEBUG"))로 쓰면 false를 넣어도 켜지는 버그가 생김

STABLE_TOKEN = os.getenv("STABLE_TOKEN")
CANARY_TOKEN = os.getenv("CANARY_TOKEN")
# 토큰 두 개는 비밀값이라 직접 적으면 안 됌.
TOKEN = CANARY_TOKEN if DEBUG else STABLE_TOKEN
#토큰을 DEBUG로 고르는 로직. 테스트용과 운영용 봇을 분리하는 습관은 좋음

WHIELIST = [int(i) for i in os.getenv("WHIELIST", "").split(",") if i.strip()]
#디스코드 계정 ID. ID는 .env에 쉼표로 적고 여기서 정수 리스트로 변환. 개발자모드를 켜고 프로필을 우클릭하면 ID를 복사할 수 있음.
#if i.strip()은 값이 비어있을때 int("") 오류가 나는 걸 막음

PRESENCE = [
    "!help로 도움말 보기",
    "https://github.com/jawbuilds/discordpy-bot-quickstarter",
]
# 상태 메시지.

if not TOKEN:
    raise RuntimeError("토큰이 없어요. .env에 STABLE_TOKEN(또는 DEBUG=true일 때 CANARY_TOKEN))을 설정하세요.")
# 검증 : 토큰이 없을 때 import 시점에 바로 알려주는 구조라 None으로 로그인을 시도하다 생기는 알아보기 힘든 오류를 막아줌.
# 다만 이 줄이 있으면 config.py를 import하는 모든 곳(테스트 포함)에서 토큰이 필수가 된다는 점

# 개선 여지
# 1. import만 해도 부수효과(파일 읽기, 예외 발생)가 생김. 입문용 템플릿에선 괜찮지만 규모가 커지면 dataclass나 pydantic-settings로 바꾸는 선택지가 있음