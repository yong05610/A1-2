# config.py
# 역할: .env 파일에서 API 키를 불러오고, 키가 있는지 확인합니다.
# 다른 파일에서 "from config import GEMINI_API_KEY" 형태로 사용합니다.

import os
import sys
from dotenv import load_dotenv

# ─────────────────────────────────────────
# .env 파일 로드
# load_dotenv()는 프로젝트 폴더의 .env 파일을 읽어서
# 환경변수로 등록해 줍니다.
# ─────────────────────────────────────────
load_dotenv()


def _get_key(key_name: str, guide: str) -> str:
    """
    환경변수에서 키를 가져옵니다.
    키가 없으면 어떤 키가 없는지 알려주고 프로그램을 종료합니다.

    Args:
        key_name : 환경변수 이름 (예: "GEMINI_API_KEY")
        guide    : 키를 어디서 발급받는지 안내 문구
    Returns:
        str : 키 값
    """
    value = os.getenv(key_name)

    if not value:
        # 빨간색 느낌의 구분선으로 눈에 잘 띄게 출력합니다.
        print("=" * 60)
        print(f"[오류] '{key_name}' 키를 찾을 수 없습니다.")
        print()
        print("▶ 해결 방법:")
        print("  1) 프로젝트 폴더에 '.env' 파일이 있는지 확인하세요.")
        print("  2) '.env' 파일 안에 아래 줄이 있는지 확인하세요:")
        print(f"       {key_name}=발급받은_키_붙여넣기")
        print(f"  3) 키 발급 위치: {guide}")
        print("=" * 60)
        sys.exit(1)   # 키가 없으면 프로그램을 즉시 종료합니다.

    return value


# ─────────────────────────────────────────
# API 키 변수 (다른 파일에서 import해서 사용)
# ─────────────────────────────────────────

# Google Gemini API 키
# 발급: https://aistudio.google.com/app/apikey
GEMINI_API_KEY: str = _get_key(
    key_name="GEMINI_API_KEY",
    guide="https://aistudio.google.com/app/apikey",
)

# Kakao REST API 키
# 발급: https://developers.kakao.com → 내 애플리케이션 → 앱 키
KAKAO_REST_API_KEY: str = _get_key(
    key_name="KAKAO_REST_API_KEY",
    guide="https://developers.kakao.com",
)


# ─────────────────────────────────────────
# 이 파일을 직접 실행하면 키 로드 성공 여부를 확인할 수 있습니다.
# 터미널에서: python config.py
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("[config.py] API 키 로드 확인")
    print(f"  GEMINI_API_KEY     : {GEMINI_API_KEY[:6]}{'*' * 10}  ✅")
    print(f"  KAKAO_REST_API_KEY : {KAKAO_REST_API_KEY[:6]}{'*' * 10}  ✅")
    print("모든 키가 정상적으로 로드되었습니다! 🎉")
    print("=" * 60)