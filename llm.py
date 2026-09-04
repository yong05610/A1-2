# llm.py
# 역할: Google Gemini AI와 통신하는 모든 기능을 담당합니다.
# 1) 여행 날짜를 받아 국내 여행지 3곳을 추천받습니다.
# 2) 선택한 도시 + 맛집 정보를 받아 Markdown 여행 리포트를 생성합니다.

import re
import google.generativeai as genai
import json

# config.py에서 Gemini API 키를 가져옵니다.
# config.py가 같은 폴더에 있어야 합니다.
from config import GEMINI_API_KEY

# ─────────────────────────────────────────
# Gemini API 초기화
# genai.configure()를 한 번 호출하면 이후 모든 API 요청에 키가 자동 적용됩니다.
# ─────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)

# 사용할 Gemini 모델을 지정합니다.
# gemini-2.5-flash: 빠르고 안정적인 모델 (무료 티어 사용 가능)
MODEL_NAME = "gemini-3.6-flash"


# ─────────────────────────────────────────
# 함수 1: 여행지 추천
# ─────────────────────────────────────────
def recommend_destinations(travel_date: str) -> list[dict]:
    """
    여행 날짜를 받아 여행지 3곳을 날씨/행사 정보와 함께 추천합니다.

    Returns:
        list[dict]: [{"city": "평창", "weather": "맑음 25도", "events": "..."}, ...]
    """
    prompt = f"""
당신은 대한민국 국내 여행 전문가입니다.

여행 날짜: {travel_date}

이 시기에 가기 좋은 국내 여행지 3곳을 추천해 주세요.
계절, 날씨, 지역 축제, 자연경관 등을 고려하세요.

[출력 규칙 - 반드시 JSON 형식으로만 출력]
아래 형식의 JSON 배열만 출력하세요. 다른 설명이나 마크다운은 절대 넣지 마세요.
weather는 해당 날짜의 예상 날씨, events는 그 시기의 지역 축제/행사를 적으세요.

[
  {{"city": "평창", "weather": "맑음, 25도", "events": "평창더위사냥축제"}},
  {{"city": "삼척", "weather": "흐림, 23도", "events": "특별한 행사 없음"}},
  {{"city": "여수", "weather": "비, 26도", "events": "여수밤바다 축제"}}
]
"""

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        print(f"  🤖 Gemini에게 {travel_date} 여행지 추천 요청 중...")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # ```json ... ``` 감싸는 경우 제거
        raw_text = re.sub(r"```json|```", "", raw_text).strip()

        data = json.loads(raw_text)

        if isinstance(data, list) and len(data) >= 3:
            return data[:3]

        raise ValueError(f"파싱 실패. 원본:\n{raw_text}")

    except Exception as e:
        print(f"  ❌ 여행지 추천 중 오류: {e}")
        print("  ℹ️  기본 여행지 목록 반환")
        return [
            {"city": "강릉", "weather": "정보 없음", "events": "정보 없음"},
            {"city": "경주", "weather": "정보 없음", "events": "정보 없음"},
            {"city": "여수", "weather": "정보 없음", "events": "정보 없음"},
        ]

# ─────────────────────────────────────────
# 함수 2: 여행 리포트 생성
# ─────────────────────────────────────────
def create_report(city: str, restaurants: list[dict], travel_date: str) -> str:
    """
    선택한 도시와 맛집 정보를 바탕으로 Markdown 형식의 여행 리포트를 생성합니다.

    Args:
        city        (str)       : 선택한 여행 도시 (예: "강릉")
        restaurants (list[dict]): 맛집 정보 리스트
                                  각 항목 예시:
                                  {
                                    "name"    : "교동반점",
                                    "category": "중식당",
                                    "address" : "강원 강릉시 교동 123",
                                    "url"     : "http://place.map.kakao.com/..."
                                  }
        travel_date (str)       : 여행 날짜 (예: "2025-06-15")

    Returns:
        str: Markdown 형식의 여행 리포트 문자열
             오류 발생 시 기본 리포트 반환
    """

    # 맛집 정보를 프롬프트에 넣기 좋은 텍스트 형태로 변환합니다.
    restaurant_text = ""
    for i, r in enumerate(restaurants, start=1):
        name     = r.get("name",     "이름 없음")
        category = r.get("category", "카테고리 없음")
        address  = r.get("address",  "주소 없음")
        url      = r.get("url",      "")

        restaurant_text += f"{i}. {name}\n"
        restaurant_text += f"   - 카테고리: {category}\n"
        restaurant_text += f"   - 주소: {address}\n"
        if url:
            restaurant_text += f"   - 카카오맵: {url}\n"
        restaurant_text += "\n"

    # Gemini에게 보낼 프롬프트를 작성합니다.
    prompt = f"""
당신은 감성적인 여행 작가입니다.
아래 정보를 바탕으로 독자가 설레는 여행 리포트를 Markdown 형식으로 작성해 주세요.

[여행 정보]
- 여행지: {city}
- 여행 날짜: {travel_date}

[추천 맛집 목록]
{restaurant_text}

[작성 규칙]
1. 반드시 Markdown 형식으로 작성하세요.
2. 아래 구조를 반드시 따르세요:

# 🗺️ {city} 여행 리포트

## 📅 여행 정보
(날짜, 지역 간단 소개)

## ✨ {city} 이런 곳이에요
(이 도시의 매력, 볼거리, 분위기를 2~3문장으로 소개)

## 🍽️ 추천 맛집 BEST 5
(각 맛집을 ### 소제목으로 나누고, 카테고리/주소/카카오맵 링크 포함)

## 💡 여행 꿀팁
(이 도시 여행 시 알아두면 좋은 팁 3가지를 bullet point로)

## 🎒 마무리
(설레는 마무리 문장 1~2줄)

---
*이 리포트는 AI가 생성했습니다.*
"""

    try:
        # Gemini 모델 인스턴스를 생성합니다.
        model = genai.GenerativeModel(MODEL_NAME)

        print(f"  🤖 Gemini가 {city} 여행 리포트를 작성 중...")

        # Gemini API를 호출합니다.
        response = model.generate_content(prompt)

        # 응답 텍스트를 그대로 반환합니다. (이미 Markdown 형식)
        report = response.text.strip()

        return report

    except Exception as e:
        # API 오류 시 기본 리포트를 반환합니다.
        print(f"  ❌ 리포트 생성 중 오류 발생: {e}")
        print("  ℹ️  기본 리포트를 반환합니다.")

        # 맛집 목록을 간단히 Markdown으로 만들어 반환합니다.
        fallback_lines = [
            f"# 🗺️ {city} 여행 리포트\n",
            f"## 📅 여행 정보\n",
            f"- 여행지: {city}\n",
            f"- 여행 날짜: {travel_date}\n\n",
            f"## 🍽️ 추천 맛집 BEST 5\n",
        ]
        for i, r in enumerate(restaurants, start=1):
            fallback_lines.append(
                f"### {i}. {r.get('name', '이름 없음')}\n"
                f"- 카테고리: {r.get('category', '-')}\n"
                f"- 주소: {r.get('address', '-')}\n\n"
            )
        fallback_lines.append("---\n*이 리포트는 AI가 생성했습니다.*\n")

        return "".join(fallback_lines)


# ─────────────────────────────────────────
# 단독 테스트 블록
# 터미널에서 `python llm.py` 로 실행하면 Gemini 연동을 바로 확인할 수 있습니다.
# main.py에서 import할 때는 이 블록이 실행되지 않습니다.
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("[llm.py] Gemini 연동 단독 테스트")
    print("=" * 60)

    # ── 테스트 1: 여행지 추천 ──
    test_date = "2025-07-20"
    print(f"\n📅 테스트 날짜: {test_date}")
    print("─" * 40)

    result = recommend_destinations(test_date)

    print("\n✅ 추천 여행지 결과:")
    for i, city in enumerate(result, start=1):
        print(f"  {i}. {city}")

    # ── 테스트 2: 리포트 생성 (샘플 데이터 사용) ──
    print("\n" + "─" * 40)
    print("📝 리포트 생성 테스트 (샘플 맛집 데이터 사용)")
    print("─" * 40)

    sample_restaurants = [
        {
            "name"    : "샘플 맛집 A",
            "category": "한식",
            "address" : "강원 강릉시 샘플로 1",
            "url"     : "http://place.map.kakao.com/sample1",
        },
        {
            "name"    : "샘플 맛집 B",
            "category": "해산물",
            "address" : "강원 강릉시 샘플로 2",
            "url"     : "http://place.map.kakao.com/sample2",
        },
    ]

    sample_city = result[0] if result else "강릉"
    report = create_report(sample_city, sample_restaurants, test_date)

    print(f"\n✅ 생성된 리포트 미리보기 (앞 500자):\n")
    print(report[:500])
    print("\n... (이하 생략)")

    print("\n" + "=" * 60)
    print("🎉 llm.py 테스트 완료! STEP 3으로 넘어가세요.")
    print("=" * 60)
    