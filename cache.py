# cache.py
# 맛집 검색 결과를 cache.json 파일에 저장하고 재사용하는 캐싱 모듈입니다.
# 같은 도시를 다시 검색할 때 API를 호출하지 않고 저장된 결과를 바로 반환합니다.

import json
import os

# ----------------------------------------
# 캐시 파일 경로 설정
# ----------------------------------------
# 이 파일(cache.py)과 같은 폴더에 cache.json을 저장합니다.
CACHE_FILE = "cache.json"


# ----------------------------------------
# 함수 1: load_cache()
# ----------------------------------------
def load_cache() -> dict:
    """
    cache.json 파일을 읽어 딕셔너리로 반환합니다.

    Returns:
        dict: { "도시명": [맛집리스트], ... } 형태
              파일이 없거나 깨진 경우 빈 딕셔너리 {} 반환
    """

    # 파일이 존재하지 않으면 빈 딕셔너리 반환
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        # cache.json 파일 열기 (한글 깨짐 방지: encoding="utf-8")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    except json.JSONDecodeError:
        # 파일이 깨졌거나 JSON 형식이 아닌 경우
        print("[경고] cache.json 파일이 손상되었습니다. 빈 캐시로 시작합니다.")
        return {}

    except Exception as e:
        # 그 외 예상치 못한 오류
        print(f"[오류] 캐시 파일을 읽는 중 오류 발생: {e}")
        return {}


# ----------------------------------------
# 함수 2: get_from_cache(city)
# ----------------------------------------
def get_from_cache(city: str) -> list | None:
    """
    특정 도시의 저장된 맛집 리스트를 반환합니다.

    Args:
        city (str): 도시명 (예: "강릉")

    Returns:
        list : 저장된 맛집 리스트 (캐시가 있을 때)
        None : 해당 도시의 캐시가 없을 때
    """

    # 캐시 파일 전체 불러오기
    cache = load_cache()

    # 해당 도시가 캐시에 있으면 맛집 리스트 반환, 없으면 None 반환
    return cache.get(city, None)


# ----------------------------------------
# 함수 3: save_to_cache(city, restaurants)
# ----------------------------------------
def save_to_cache(city: str, restaurants: list) -> None:
    """
    도시명과 맛집 리스트를 캐시에 저장합니다.
    이미 있는 도시면 덮어씁니다(갱신).

    Args:
        city        (str) : 도시명 (예: "강릉")
        restaurants (list): 맛집 정보 리스트
                            [{"name":..., "category":..., "address":..., "url":...}, ...]
    """

    # 기존 캐시 불러오기 (없으면 빈 딕셔너리)
    cache = load_cache()

    # 해당 도시의 맛집 데이터 추가 또는 갱신
    cache[city] = restaurants

    try:
        # cache.json 파일에 저장
        # ensure_ascii=False : 한글이 깨지지 않게 저장
        # indent=2          : 보기 좋게 들여쓰기
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        print(f"[캐시] '{city}' 맛집 데이터를 cache.json에 저장했습니다.")

    except Exception as e:
        print(f"[오류] 캐시 파일을 저장하는 중 오류 발생: {e}")


# ----------------------------------------
# 단독 테스트 코드
# ----------------------------------------
if __name__ == "__main__":

    print("=" * 45)
    print("📦 cache.py 테스트 시작")
    print("=" * 45)

    # ── 테스트 1: 가짜 맛집 데이터 저장 ──────────
    print("\n✅ 테스트 1: 가짜 데이터 저장")

    fake_restaurants = [
        {"name": "테스트 맛집 A", "category": "한식",  "address": "테스트시 중앙로 1",  "url": "https://place.map.kakao.com/sample1"},
        {"name": "테스트 맛집 B", "category": "해산물", "address": "테스트시 바닷가로 2", "url": "https://place.map.kakao.com/sample2"},
        {"name": "테스트 맛집 C", "category": "카페",   "address": "테스트시 커피길 3",  "url": "https://place.map.kakao.com/sample3"},
    ]

    save_to_cache("테스트시", fake_restaurants)

    # ── 테스트 2: 저장된 데이터 불러오기 ──────────
    print("\n✅ 테스트 2: '테스트시' 캐시 불러오기")

    result = get_from_cache("테스트시")

    if result:
        print(f"   → {len(result)}개의 맛집 데이터를 불러왔습니다!")
        for i, r in enumerate(result, start=1):
            print(f"\n   🍽️  {i}. {r['name']}")
            print(f"      📂 카테고리 : {r['category']}")
            print(f"      📍 주소     : {r['address']}")
            print(f"      🔗 URL      : {r['url']}")
    else:
        print("   → ❌ 데이터를 불러오지 못했습니다.")

    # ── 테스트 3: 없는 도시 조회 ──────────────────
    print("\n✅ 테스트 3: '없는도시' 캐시 조회")

    no_result = get_from_cache("없는도시")

    if no_result is None:
        print("   → ✅ 정상! '없는도시'는 None을 반환했습니다.")
    else:
        print(f"   → ❌ 예상과 다릅니다: {no_result}")

    print("\n" + "=" * 45)
    print("🎉 테스트 완료! cache.json 파일을 확인해보세요.")
    print("=" * 45)