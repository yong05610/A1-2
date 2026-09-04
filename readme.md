# AI 협업 여행 추천 프로그램 개발 리포트

## 1. 프로젝트 개요
- **목표**: 사용자가 여행 날짜를 입력하면, AI가 여행지를 추천하고 해당 지역의 맛집까지 검색하여 Markdown 리포트로 정리해주는 CLI 프로그램 개발
- **기술스택**: Gemini(여행지 추천 LLM) / Kakao Local API(맛집 검색) / Python
- **개발환경**: VS Code + Claude Sonnet

## 2. AI 협업 전략
- **역할 분담**: 기획 AI(PRD·시나리오 설계) → 코딩 AI(Sonnet, 실제 코드 작성) → 프로그램 내 LLM(Gemini, 여행지 추천 담당)
- **이유**:
  - 기획과 코딩을 분리해 **설계 단계에서 방향을 확정**한 뒤 개발에 착수 → 재작업 최소화
  - 코딩 AI(Sonnet)는 **모듈 단위 구현·디버깅**에 활용, 실행 중 추천 로직은 **Gemini**가 담당하여 역할을 명확히 구분

## 3. 주요 의사결정 기록 (STEP별)
| 단계 | 결정 내용 | 이유 |
|------|----------|------|
| 설계 | 맛집 = 도시 선택 후 1곳만 검색 | API 호출 절약 + 흐름 자연스러움 |
| 설계 | 여행지 복수 추천 후 사용자가 번호 선택 | 사용자 선택권 보장, 재입력 지원 |
| llm.py | 추천 결과를 **dict로 반환** | 날씨·행사 등 부가정보를 함께 전달하기 위함 |
| cache | API 응답 캐싱 도입(보너스) | 동일 요청 시 API 재호출 방지·속도 개선 |
| main.py | 리포트 생성/저장/출력 단계 분리 | 생성(`create_report`)과 저장(`save_report`) 책임 분리 |

## 4. 단계별 개발 과정

### STEP 1. 시나리오 및 PRD 

#### 1.1 사용자 시나리오

1. 사용자가 프로그램 실행 → 날짜 입력 요청
2. 날짜 입력(YYYY-MM-DD) → 형식 검증 (틀리면 재입력)
3. Gemini API 가 여행지 3곳 추천 (날씨·행사 포함)
4. 화면에 번호와 함께 표시 → 사용자가 번호 선택
5. 선택 도시로 Kakao Local API 맛집 검색 (1곳)
6. 리포트 생성 → JSON + Markdown 저장 → 화면 출력

#### 1.2 제품요구사항 (PRD}

| 항목 | 내용 |
|------|------|
| 핵심 기능 | ①날짜 입력 ②여행지 복수 추천 ③사용자 선택 ④맛집 검색 ⑤리포트 생성/저장 |
| 입력 | 여행 날짜(`YYYY-MM-DD`) |
| 출력 | JSON 원본 + Markdown 리포트 |
| 성공 기준 | 오류 없이 전체 흐름 완주 + 리포트 파일 생성 |
| 제약 | Kakao API는 선택 도시 1곳만 검색(호출 절약) |

### STEP 2. 데이터 스키마 

#### 2-1. LLM 반환 JSON 필수 키
```json
{
  "recommended_city": "강릉",
  "weather": "맑음, 22℃",
  "events": "강릉 커피축제 (6/14~6/16)",
  "reason": "초여름 해변과 커피거리를 함께 즐기기 좋음"
}
```
| 키 | 타입 | 필수 | 설명 |
|----|------|------|------|
| `recommended_city` | string | ✅ | 추천 도시명 |
| `weather` | string | ✅ | 날씨 정보 |
| `events` | string | ✅ | 행사 정보 |
| `reason` | string | ✅ | 추천 이유 |

#### 2-2. 필수키 검증 & 파싱 실패 재시도 정책 
- 파싱 후 **필수 키 4개 존재 여부 + 타입 검사**
- **파싱 실패 시**: 재요청 **1회** (프롬프트에 "JSON 형식으로만 출력" 문구 강화)
- 재시도 후에도 실패 → **기본 여행지(fallback)** 반환하여 중단 방지

#### 2.3  파일 저장 구조 

```
results/
 ├── report_2025-06-15.json   # LLM 원본 JSON
 └── report_2025-06-15.md     # 최종 Markdown 리포트
```
| 파일 | 내용 |
|------|------|
| `report_{date}.json` | LLM 원본 응답(JSON) |
| `report_{date}.md` | 사용자용 최종 리포트 |

```
📌[results/ 폴더 내 실제 생성된 파일 목록 덤프]
📌[report_xxxx.md 파일 내용 덤프]
```
  <img width="324" height="330" alt="image" src="https://github.com/user-attachments/assets/3ef9673a-1dc9-4076-83ac-57062275d515" />

  <img width="900" height="747" alt="image" src="https://github.com/user-attachments/assets/efe11261-56fa-4715-9176-f2fcf01d7e88" />

 <img width="987" height="779" alt="image" src="https://github.com/user-attachments/assets/32119df4-a281-4e9d-b6d7-f6da76b06f5e" />


### STEP 3. 프로젝트 뼈대 (config)

- **프롬프트 요약**: 환경변수 로드 및 API 키 관리 구조 요청
- **결과**: `load_dotenv()`로 `.env`의 키를 안전하게 불러오는 구조 완성
- **트러블슈팅**: 없음

#### 1.1 API 설계 (지적 #3, #10, #12 반영)

##### 3.1-1. GET/POST 사용 구분 (지적 #10)
| API | 메서드 | 이유 | 엔드포인트 |
|-----|--------|------|-----------|
| Kakao Local | **GET** | 검색 조회(멱등·부작용 없음) | `https://dapi.kakao.com/v2/local/search/keyword.json` |
| Gemini | **POST** | 프롬프트 본문 전송 필요 | Gemini SDK 내부 호출 |

##### 3.1-2. 도시 변수 전달 흐름 (지적 #3)
- `recommended_city` → 사용자 선택 → `places.search_restaurants(city)`로 전달
- **API 실패 시**: 맛집 데이터 없이 **리포트 계속 생성**("맛집 정보 없음" 표기)

##### 3.1-3. 인증 오류(401/403) 디버깅 절차 (지적 #12)
| 코드 | 원인 | 확인 항목 |
|------|------|-----------|
| 401 | 키 오류 | `.env` API 키 값 확인 |
| 403 | 권한/도메인 | Kakao 앱 도메인·권한 설정, 헤더 `Authorization: KakaoAK {key}` 확인 |

---


### STEP 4. llm.py (여행지 추천)
- **프롬프트 요약**: Gemini로 날짜 기반 여행지 복수 추천 + 날씨/행사 정보 포함
- **결과**: `recommend_destinations()`, `create_report()` 구현
- **트러블슈팅**: 초기엔 문자열 반환 → 부가정보 전달 위해 **dict 반환으로 수정**

### STEP 5. places.py (맛집 검색)
- **프롬프트 요약**: Kakao Local API로 선택 도시의 맛집 검색
- **결과**: `search_restaurants()` 구현
- **트러블슈팅**: (해당 시 기입)

### STEP 6. cache.py (캐싱 · 보너스)
- **프롬프트 요약**: API 응답을 저장·재사용하는 캐시 로직 요청
- **결과**: `save_to_cache()`, `get_from_cache()` 구현
- **트러블슈팅**: import 중복(`load_cache`/`get_from_cache`) 정리

### STEP 7. report.py (리포트 저장)
- **프롬프트 요약**: Markdown 리포트를 파일로 저장
- **결과**: `save_report()` 구현
- **트러블슈팅**: 없음

### STEP 8. main.py (전체 흐름 통합)
- **프롬프트 요약**: 날짜 입력 → 추천 → 선택 → 맛집 검색 → 리포트 생성/저장/출력 통합
- **결과**: 도시 선택 UI(번호 입력·재입력), JSON+Markdown 저장, 화면 출력 완성
- **트러블슈팅**: `create_report` import 누락 / `save_report`와 `create_report` 혼동 해결

## 5. 트러블슈팅 모음

| 문제 | 원인 | 해결 |
|------|------|------|
| 날씨·행사 정보 미표시 | llm이 문자열만 반환 | **dict 반환**으로 구조 변경 |
| 리포트가 화면에 안 나옴 | 리포트 생성 함수 미호출 | `save_report`→`create_report`로 수정 |
| `NameError: create_report` | import 누락 | `from llm import ..., create_report` 추가 |
| cache 중복 import | 같은 모듈 2줄로 import | 한 줄로 통합 정리 |

## 6. 회고

- **잘된 점**: 설계를 먼저 확정하고 개발해 흐름이 명확했다. 보너스(캐싱·복수 추천)까지 구현 완료.
- **어려웠던 점**: 함수 역할 구분(생성 vs 저장), import 누락 디버깅
- **AI 협업에서 배운 점**: 역할을 나눠 협업하니 각 단계 책임이 명확해졌다.
- **다음에 개선하고 싶은 점**:  설계, 코딩, 리포트 작성, 기타 질의 등 역할을 더 세세히 분할 하여 협업 할수 있도록 하여야겠음  
