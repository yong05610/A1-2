# places.py
# Kakao Local API를 사용해 도시별 맛집을 검색하는 모듈입니다.

import requests
from config import KAKAO_REST_API_KEY

# ----------------------------------------
# Kakao Local API 설정
# ----------------------------------------
KAKAO_API_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


def search_restaurants(city: str, count: int = 5) -> list[dict]:
    """
    Kakao Local API로 특정 도시의 맛집을 검색합니다.

    Args:
        city  (str): 도시명 (예: "강릉")
        count (int): 가져올 맛집 개수 (기본값 5)

    Returns:
        list[dict]: 맛집 정보 리스트
                    각 항목은 {"name", "category", "address", "url"} 4개 키를 가집니다.
                    API 실패 또는 결과 없으면 빈 리스트 [] 반환
    """

    # 검색 키워드: "강릉 맛집" 형태로 구성
    keyword = f"{city} 맛집"

    # Kakao API 인증 헤더
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }

    # 요청 파라미터
    params = {
        "query": keyword,   # 검색 키워드
        "size": count       # 가져올 결과 개수 (최대 15)
    }

    try:
        # ----------------------------------------
        # Kakao API 호출
        # ----------------------------------------
        response = requests.get(KAKAO_API_URL, headers=headers, params=params)

        # HTTP 오류 발생 시 예외 처리 (예: 401 인증 실패, 500 서버 오류 등)
        response.raise_for_status()

        # JSON 응답 파싱
        data = response.json()

        # 검색 결과 목록 추출 (없으면 빈 리스트)
        documents = data.get("documents", [])

        # 결과가 없을 경우 빈 리스트 반환
        if not documents:
            print(f"[안내] '{keyword}' 검색 결과가 없습니다.")
            return []

        # ----------------------------------------
        # 맛집 정보 추출 및 변환
        # ----------------------------------------
        restaurants = []

        for place in documents[:count]:  # count 개수만큼만 처리

            # address: road_address_name 우선, 없으면 address_name 사용
            address = place.get("road_address_name") or place.get("address_name", "주소 없음")

            restaurant = {
                "name"    : place.get("place_name", "이름 없음"),
                "category": place.get("category_name", "카테고리 없음"),
                "address" : address,
                "url"     : place.get("place_url", "")
            }

            restaurants.append(restaurant)

        return restaurants

    except requests.exceptions.HTTPError as e:
        # HTTP 오류 (인증 실패, 요청 오류 등)
        print(f"[오류] Kakao API HTTP 오류: {e}")
        return []

    except requests.exceptions.ConnectionError:
        # 인터넷 연결 오류
        print("[오류] 인터넷 연결을 확인해주세요.")
        return []

    except requests.exceptions.Timeout:
        # 요청 시간 초과
        print("[오류] Kakao API 요청 시간이 초과되었습니다.")
        return []

    except Exception as e:
        # 그 외 예상치 못한 오류
        print(f"[오류] 예상치 못한 오류 발생: {e}")
        return []


# ----------------------------------------
# 단독 테스트 코드
# ----------------------------------------
if __name__ == "__main__":

    test_city = "강릉"
    print(f"🔍 '{test_city}' 맛집 검색 중...\n")

    results = search_restaurants(test_city, count=5)

    if results:
        print(f"✅ 총 {len(results)}곳의 맛집을 찾았습니다!\n")
        for i, r in enumerate(results, start=1):
            print(f"{'='*40}")
            print(f"🍽️  {i}. {r['name']}")
            print(f"   📂 카테고리 : {r['category']}")
            print(f"   📍 주소     : {r['address']}")
            print(f"   🔗 카카오맵 : {r['url']}")
        print(f"{'='*40}")
    else:
        print("❌ 맛집 검색 결과가 없습니다.")

        