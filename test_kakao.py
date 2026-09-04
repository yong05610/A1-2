# test_kakao.py
import os
import requests
from dotenv import load_dotenv

# .env 파일 읽기
load_dotenv()

# 카카오 REST API 키 가져오기
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")

if not KAKAO_REST_API_KEY:
    print("❌ KAKAO_REST_API_KEY가 .env에 없습니다.")
    exit()

# 테스트할 검색어
query = "강남역"   # 필요하면 "제주도 카페", "부산 해운대" 등으로 바꿔보세요

# 카카오 Local API 엔드포인트
url = "https://dapi.kakao.com/v2/local/search/keyword.json"

# 헤더: 반드시 KakaoAK + REST API 키 형식
headers = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
}

# 요청 파라미터
params = {
    "query": query,
    "size": 5  # 결과 5개만 가져오기
}

# API 호출
response = requests.get(url, headers=headers, params=params)

# 응답 확인
print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    documents = data.get("documents", [])

    print(f"\n검색어: {query}")
    print(f"검색 결과 수: {len(documents)}개\n")

    for i, place in enumerate(documents, start=1):
        print(f"{i}. {place.get('place_name')}")
        print(f"   주소: {place.get('address_name')}")
        print(f"   카테고리: {place.get('category_name')}")
        print(f"   좌표: ({place.get('x')}, {place.get('y')})")
        print()
else:
    print("❌ 요청 실패")
    print(response.text)