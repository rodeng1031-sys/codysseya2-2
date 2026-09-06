# 📘 함수 명세서 (Function Specification)

## 프로젝트: AI 여행 추천 프로그램

- **작성일**: 2026-09-06
- **버전**: 1.0.0
- **작성자**: [임지수]

---

## 📋 목차

1. [API 연동 함수](#1-api-연동-함수)
2. [Mock 함수](#2-mock-함수)
3. [메인 로직 함수](#3-메인-로직-함수)
4. [유틸리티 함수](#4-유틸리티-함수)

---

## 1. API 연동 함수

### 1.1 `get_gpt_recommendation()`

**설명**: OpenAI GPT API를 호출하여 지역별 여행 추천 텍스트를 생성합니다.

| 항목 | 내용 |
|------|------|
| **입력** | `location: str` - 여행지 이름 (예: "부산") |
| **출력** | `str` - GPT가 생성한 추천 문구 |
| **예외** | `openai.APIError` - API 호출 실패 시 |
| **의존성** | `openai`, `OPENAI_API_KEY` 환경변수 |

**시그니처:**
```python
def get_gpt_recommendation(location: str) -> str:
```

**사용 예시:**
```python
result = get_gpt_recommendation("부산")
# "부산은 해운대, 광안리 등 해변이 유명하고..."
```

---

### 1.2 `search_kakao_places()`

**설명**: Kakao Local API를 호출하여 특정 지역의 장소 목록을 검색합니다.

| 항목 | 내용 |
|------|------|
| **입력** | `location: str` - 검색 지역<br>`keyword: str` - 검색 키워드 (기본값: "관광") |
| **출력** | `list[dict]` - 장소 정보 리스트 |
| **예외** | `requests.RequestException` - HTTP 요청 실패 |
| **의존성** | `requests`, `KAKAO_API_KEY` 환경변수 |

**시그니처:**
```python
def search_kakao_places(location: str, keyword: str = "관광") -> list:
```

**반환 데이터 구조:**
```python
[
    {
        "place_name": "해운대 해수욕장",
        "address_name": "부산 해운대구",
        "category": "관광명소"
    },
    ...
]
```

---

## 2. Mock 함수

### 2.1 `mock_get_gpt_recommendation()`

**설명**: GPT API 호출을 대체하는 Mock 함수. 사전 정의된 응답을 반환합니다.

| 항목 | 내용 |
|------|------|
| **입력** | `location: str` |
| **출력** | `str` - Mock 데이터에서 매칭된 문구 |
| **용도** | 개발/테스트 시 API 비용 절감 |

---

### 2.2 `mock_search_kakao_places()`

**설명**: Kakao API 호출을 대체하는 Mock 함수.

| 항목 | 내용 |
|------|------|
| **입력** | `location: str`, `keyword: str` |
| **출력** | `list[dict]` - Mock 장소 데이터 |
| **용도** | 오프라인 테스트, 단위 테스트 |

---

## 3. 메인 로직 함수

### 3.1 `recommend_travel()`

**설명**: 여행 추천 전체 프로세스를 실행하는 메인 함수입니다.

| 항목 | 내용 |
|------|------|
| **입력** | `location: str` - 여행지 |
| **출력** | `dict` - 추천 결과 (지역, 문구, 장소 목록) |
| **호출 함수** | `get_gpt_recommendation()`, `search_kakao_places()` |

**시그니처:**
```python
def recommend_travel(location: str) -> dict:
```

**반환 데이터 구조:**
```python
{
    "location": "부산",
    "recommendation": "부산은 해운대...",
    "places": [{"place_name": ...}, ...]
}
```

**처리 흐름:**
```
1. 입력 지역 검증
2. GPT 추천 문구 생성
3. Kakao 장소 검색
4. 결과 통합 및 출력
5. 딕셔너리 반환
```

---

## 4. 유틸리티 함수

### 4.1 `load_env()`

**설명**: `.env` 파일에서 환경변수를 로드합니다.

| 항목 | 내용 |
|------|------|
| **입력** | 없음 |
| **출력** | `None` |
| **의존성** | `python-dotenv` |

---

### 4.2 `print_result()`

**설명**: 추천 결과를 사용자 친화적 포맷으로 출력합니다.

| 항목 | 내용 |
|------|------|
| **입력** | `result: dict` |
| **출력** | `None` (콘솔 출력) |

---

## 📊 함수 호출 관계도

```
main()
  └─ recommend_travel(location)
       ├─ get_gpt_recommendation(location)      [API]
       │    └─ (or mock_get_gpt_recommendation)
       ├─ search_kakao_places(location)          [API]
       │    └─ (or mock_search_kakao_places)
       └─ print_result(result)
```