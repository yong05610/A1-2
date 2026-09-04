# main.py
# 여행 추천 CLI 프로그램 - 메인 실행 파일
# 실행: python main.py --date "2026-08-30"

import argparse
from datetime import datetime

# 우리가 만든 모듈 불러오기
from config import load_dotenv
from llm import recommend_destinations, create_report
from places import search_restaurants
# from cache import save_to_cache, load_cache
from cache import save_to_cache, load_cache, get_from_cache
from report import save_report

# ──────────────────────────────────────────
# 유틸 함수: 구분선 출력
# ──────────────────────────────────────────
def print_divider():
    print("─" * 50)


# ──────────────────────────────────────────
# 유틸 함수: 날짜 정규화 (2026-8-3 → 2026-08-03)
# ──────────────────────────────────────────
def normalize_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str  # 변환 실패 시 원본 반환


# ──────────────────────────────────────────
# 메인 함수
# ──────────────────────────────────────────
def main():
    # ① [인자 파싱] 커맨드라인에서 --date 받기
    print_divider()
    print("① 📅 날짜 인자 파싱 중...")

    parser = argparse.ArgumentParser(description="여행 추천 CLI 프로그램")
    parser.add_argument("--date", required=True, help="여행 날짜 (예: 2026-08-30)")
    args = parser.parse_args()

    date_str = normalize_date(args.date)
    print(f"   ✅ 여행 날짜: {date_str}")

    # 오류 수집 리스트 (나중에 한꺼번에 출력)
    errors = []

    # ② [환경변수] .env 파일 로드
    print_divider()
    print("② 🔑 환경변수 로드 중...")

    try:
        load_dotenv()
        print("   ✅ 환경변수 로드 완료")
    except Exception as e:
        print(f"   ❌ 환경변수 로드 실패: {e}")
        errors.append(f"환경변수 로드 실패: {e}")
        return  # 환경변수 없으면 진행 불가

    # ③ [Gemini] 여행지 추천 요청
    print_divider()
    print("③ 🤖 Gemini에게 여행지 추천 요청 중...")

    destinations = None   # 추천 도시 목록 (list)
    raw_result = None     # Gemini 원본 응답 (dict) ← JSON 구조 확인용

    try:
        # recommend_destinations()가 반환하는 값을 확인하세요!
        # ← JSON 구조 확인: 이 함수가 list[str]을 반환하는지,
        #                   dict(city/weather/events 포함)를 반환하는지 확인 필요
        raw_result = recommend_destinations(date_str)

        # ── 반환값 타입에 따라 분기 ──────────────────
        # [케이스 A] list[str] 반환: ["강릉", "평창", "제주"]
        if isinstance(raw_result, list) and len(raw_result) > 0:
            if isinstance(raw_result[0], str):
                # 단순 문자열 리스트 → 날씨/행사 정보 없음
                destinations = [
                    {"city": c, "weather": "정보 없음", "events": "정보 없음"}
                    for c in raw_result
                ]
            elif isinstance(raw_result[0], dict):
                # dict 리스트 → 날씨/행사 정보 있을 수 있음
                # ← JSON 구조 확인: dict 안의 키 이름을 확인하세요
                #   예) {"city": "강릉", "weather": "맑음 22℃", "events": "강릉단오제"}
                destinations = []
                for item in raw_result:
                    destinations.append({
                        "city":    item.get("city", item.get("name", "알 수 없음")),
                        "weather": item.get("weather", "정보 없음"),
                        "events":  item.get("events", item.get("event", "정보 없음")),
                    })

        # [케이스 B] dict 반환: {"destinations": [...]}
        elif isinstance(raw_result, dict):
            # ← JSON 구조 확인: dict의 최상위 키 이름을 확인하세요
            items = raw_result.get("destinations", raw_result.get("cities", []))
            destinations = []
            for item in items:
                if isinstance(item, str):
                    destinations.append({
                        "city": item, "weather": "정보 없음", "events": "정보 없음"
                    })
                elif isinstance(item, dict):
                    destinations.append({
                        "city":    item.get("city", item.get("name", "알 수 없음")),
                        "weather": item.get("weather", "정보 없음"),
                        "events":  item.get("events", item.get("event", "정보 없음")),
                    })

        if not destinations:
            raise ValueError("추천 결과가 비어 있습니다.")

        print(f"   ✅ Gemini 추천 완료! ({len(destinations)}개 도시)")

    except Exception as e:
        print(f"   ❌ 추천 실패: {e}")
        errors.append(f"Gemini 추천 실패: {e}")
        return  # 추천 실패 시 진행 불가

    # ③-선택 [사용자] 도시 선택 단계
    print_divider()
    print("   📍 추천 도시를 선택하세요:\n")

    # 도시 목록 출력
    for i, dest in enumerate(destinations, start=1):
        city_name = dest["city"]
        weather   = dest["weather"]
        events    = dest["events"]
        print(f"      {i}. {city_name:<6}| 날씨: {weather:<15}| 행사: {events}")

    print()  # 빈 줄

    # 번호 입력 받기 (올바른 번호 입력할 때까지 반복)
    selected_dest = None
    while True:
        try:
            user_input = input(f"   번호 입력 (1-{len(destinations)}): ").strip()

            if not user_input.isdigit():
                print(f"   ❌ 숫자만 입력하세요! (1~{len(destinations)})")
                continue

            idx = int(user_input)
            if 1 <= idx <= len(destinations):
                selected_dest = destinations[idx - 1]
                break  # 올바른 입력 → 반복 종료
            else:
                print(f"   ❌ 1~{len(destinations)} 사이 번호를 입력하세요!")

        except KeyboardInterrupt:
            print("\n   프로그램을 종료합니다.")
            return

    # 선택된 도시 확인
    city = selected_dest["city"]
    print(f"\n   ✨ 선택된 도시: {city}")

    # ④ [Kakao] 맛집 검색
    print_divider()
    print("④ 🍽️  맛집 정보 검색 중...")
    print(f"   🏙️  검색 도시: {city}")

    restaurants = []#

    try:
        # ✅ get_from_cache(city) 사용
        cached = get_from_cache(city)

        if cached:
            restaurants = cached
            print(f"   ✅ 캐시에서 불러옴 ({len(restaurants)}개)")
        else:
            result = search_restaurants(city)

            if isinstance(result, list):
                restaurants = result
            elif isinstance(result, dict):
                restaurants = result.get("restaurants", result.get("places", []))

            # ✅ save_to_cache(city, ...) 사용
            save_to_cache(city, restaurants)
            print(f"   ✅ 맛집 {len(restaurants)}개 검색 완료 + 캐시 저장")

    except Exception as e:
        print(f"   ❌ 맛집 검색 실패: {e}")
        errors.append(f"맛집 검색 실패: {e}")


    # ⑤ [Report] 리포트 생성
    print_divider()
    print("⑤ 📝 리포트 생성 중...")

    report_md = None

    try:
        # save_report(city, restaurants, travel_date) 순서 확인!
        # report_md = save_report(city, restaurants, date_str)
        # print("   ✅ 리포트 생성 완료")

        # 리포트 텍스트 "생성" (저장 X)
        report_md = create_report(city, restaurants, date_str)
        print("   ✅ 리포트 생성 완료")
        
    except Exception as e:
        print(f"   ❌ 리포트 생성 실패: {e}")
        errors.append(f"리포트 생성 실패: {e}")

    # ⑥ [파일 저장] JSON + Markdown 저장
    print_divider()
    print("⑥ 💾 파일 저장 중...")

    try:
        import json
        import os

        # 저장 폴더 생성
        os.makedirs("results", exist_ok=True)

        # JSON 저장 (맛집 데이터)
        json_path = f"results/{city}_{date_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "city": city,
                "date": date_str,
                "restaurants": restaurants
            }, f, ensure_ascii=False, indent=2)
        print(f"   ✅ JSON 저장: {json_path}")

        # Markdown 저장 (리포트)
        if report_md:
            md_path = f"results/{city}_{date_str}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(report_md)
            print(f"   ✅ Markdown 저장: {md_path}")

    except Exception as e:
        print(f"   ❌ 파일 저장 실패: {e}")
        errors.append(f"파일 저장 실패: {e}")

    # ⑥-출력 최종 리포트를 화면에도 출력
    if report_md:
        print()
        print("=" * 50)
        print("           📋 최종 리포트")
        print("=" * 50)
        print(report_md)
        print("=" * 50)

    # ── 최종 요약 ──────────────────────────────
    print_divider()
    print("🏁 프로그램 종료")
    print(f"   📍 선택 도시  : {city}")
    print(f"   📅 여행 날짜  : {date_str}")
    print(f"   🍽️  검색 맛집  : {len(restaurants)}개")

    if errors:
        print(f"\n   ⚠️  발생한 오류 ({len(errors)}건):")
        for err in errors:
            print(f"      - {err}")
    else:
        print("\n   ✅ 모든 단계 정상 완료!")

    print_divider()


# ──────────────────────────────────────────
# 진입점
# ──────────────────────────────────────────
if __name__ == "__main__":
    main()