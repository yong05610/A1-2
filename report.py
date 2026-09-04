# report.py
# 프로그램 실행 결과를 results/ 폴더에 파일로 저장하는 모듈입니다.
# ① 원본 데이터 → JSON 파일
# ② 최종 리포트 → Markdown(.md) 파일

import json
import os
from datetime import datetime


# ----------------------------------------
# 헬퍼 함수: get_timestamp()
# ----------------------------------------
def get_timestamp() -> str:
    """
    현재 시각을 'YYYY-MM-DD_HHMMSS' 형식의 문자열로 반환합니다.
    두 함수(save_raw_data, save_report)가 같은 타임스탬프를 쓰려면
    이 함수를 한 번만 호출하고 결과를 두 함수에 넘겨주세요.

    Returns:
        str: 예) "2025-05-15_143022"
    """
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


# ----------------------------------------
# 공통 헬퍼: ensure_results_dir()
# ----------------------------------------
def ensure_results_dir() -> None:
    """
    results/ 폴더가 없으면 자동으로 만듭니다.
    exist_ok=True → 이미 있어도 오류 없이 넘어갑니다.
    """
    os.makedirs("results", exist_ok=True)


# ----------------------------------------
# 함수 1: save_raw_data(data, date_str, timestamp)
# ----------------------------------------
def save_raw_data(data: dict, date_str: str, timestamp: str = None) -> str:
    """
    원본 데이터를 results/ 폴더에 JSON 파일로 저장합니다.

    Args:
        data      (dict): 저장할 데이터
                          {"recommendation": {...}, "restaurants": [...], "errors": [...]}
        date_str  (str) : 사용자가 입력한 날짜 문자열 (예: "2025-05-15")
        timestamp (str) : 파일명에 쓸 타임스탬프 (없으면 자동 생성)
                          save_report와 같은 타임스탬프를 쓰려면 get_timestamp()로
                          미리 만들어서 두 함수에 함께 넘겨주세요.

    Returns:
        str: 저장된 파일의 경로 (예: "results/2025-05-15_143022_data.json")
    """

    # results/ 폴더 없으면 생성
    ensure_results_dir()

    # 타임스탬프가 없으면 지금 시각으로 생성
    if timestamp is None:
        timestamp = get_timestamp()

    # 파일명 조합: YYYY-MM-DD_HHMMSS_data.json
    filename = f"{timestamp}_data.json"
    filepath = os.path.join("results", filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            # ensure_ascii=False : 한글이 \uXXXX 로 깨지지 않게 저장
            # indent=2           : 보기 좋게 들여쓰기
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[저장 완료] 원본 데이터 → {filepath}")
        return filepath

    except Exception as e:
        print(f"[오류] JSON 파일 저장 실패: {e}")
        return ""


# ----------------------------------------
# 함수 2: save_report(markdown_text, date_str, timestamp)
# ----------------------------------------
def save_report(markdown_text: str, date_str: str, timestamp: str = None) -> str:
    """
    Markdown 리포트 텍스트를 results/ 폴더에 .md 파일로 저장합니다.

    Args:
        markdown_text (str): llm.py의 create_report()가 반환한 Markdown 텍스트
        date_str      (str): 사용자가 입력한 날짜 문자열 (예: "2025-05-15")
        timestamp     (str): 파일명에 쓸 타임스탬프 (없으면 자동 생성)
                             save_raw_data와 같은 타임스탬프를 쓰려면
                             get_timestamp()로 미리 만들어서 함께 넘겨주세요.

    Returns:
        str: 저장된 파일의 경로 (예: "results/2025-05-15_143022_report.md")
    """

    # results/ 폴더 없으면 생성
    ensure_results_dir()

    # 타임스탬프가 없으면 지금 시각으로 생성
    if timestamp is None:
        timestamp = get_timestamp()

    # 파일명 조합: YYYY-MM-DD_HHMMSS_report.md
    filename = f"{timestamp}_report.md"
    filepath = os.path.join("results", filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        print(f"[저장 완료] 최종 리포트 → {filepath}")
        return filepath

    except Exception as e:
        print(f"[오류] Markdown 파일 저장 실패: {e}")
        return ""


# ----------------------------------------
# 단독 테스트 코드
# ----------------------------------------
if __name__ == "__main__":

    print("=" * 50)
    print("📁 report.py 테스트 시작")
    print("=" * 50)

    # ── 타임스탬프 1회 생성 (두 파일이 같은 시각을 공유) ──
    ts = get_timestamp()
    print(f"\n🕐 타임스탬프: {ts}")

    # ── 가짜 원본 데이터 ──────────────────────────────────
    fake_data = {
        "recommendation": {
            "date": "2025-05-15",
            "theme": "자연과 힐링",
            "destinations": [
                {
                    "rank": 1,
                    "city": "강릉",
                    "reason": "푸른 바다와 신선한 해산물의 도시"
                },
                {
                    "rank": 2,
                    "city": "제주",
                    "reason": "한라산과 올레길이 있는 힐링 명소"
                },
                {
                    "rank": 3,
                    "city": "경주",
                    "reason": "천년 역사가 살아있는 고도"
                }
            ]
        },
        "restaurants": [
            {"city": "강릉", "name": "초당순두부", "category": "한식", "address": "강릉시 초당동 1"},
            {"city": "강릉", "name": "강릉커피거리", "category": "카페", "address": "강릉시 중앙로 2"},
            {"city": "제주", "name": "흑돼지거리", "category": "한식", "address": "제주시 연동 3"}
        ],
        "errors": []
    }

    # ── 가짜 Markdown 리포트 텍스트 ───────────────────────
    fake_markdown = """# 🗺️ 여행 추천 리포트

## 📅 여행 날짜: 2025-05-15
## 🎨 테마: 자연과 힐링

---

## 🏆 추천 여행지 TOP 3

### 1위. 강릉
> 푸른 바다와 신선한 해산물의 도시

**추천 맛집**
| 맛집명 | 카테고리 | 주소 |
|--------|----------|------|
| 초당순두부 | 한식 | 강릉시 초당동 1 |
| 강릉커피거리 | 카페 | 강릉시 중앙로 2 |

---

### 2위. 제주
> 한라산과 올레길이 있는 힐링 명소

**추천 맛집**
| 맛집명 | 카테고리 | 주소 |
|--------|----------|------|
| 흑돼지거리 | 한식 | 제주시 연동 3 |

---

*이 리포트는 AI가 자동 생성했습니다.*
"""

    # ── 테스트 1: JSON 저장 ───────────────────────────────
    print("\n✅ 테스트 1: save_raw_data() 호출")
    json_path = save_raw_data(fake_data, "2025-05-15", timestamp=ts)

    # ── 테스트 2: Markdown 저장 ───────────────────────────
    print("\n✅ 테스트 2: save_report() 호출")
    md_path = save_report(fake_markdown, "2025-05-15", timestamp=ts)

    # ── 결과 출력 ─────────────────────────────────────────
    print("\n" + "=" * 50)
    print("📂 저장된 파일 경로")
    print("=" * 50)
    print(f"  📄 JSON     : {json_path}")
    print(f"  📝 Markdown : {md_path}")

    # ── 파일 실제 존재 여부 확인 ──────────────────────────
    print("\n" + "=" * 50)
    print("🔍 파일 존재 확인")
    print("=" * 50)

    for path in [json_path, md_path]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ 존재함 | {size:,} bytes | {path}")
        else:
            print(f"  ❌ 없음   | {path}")

    print("\n🎉 테스트 완료! results/ 폴더를 확인해보세요.")
    print("=" * 50)
    