"""
OpenAI API 호출을 담당하는 모듈
- 1차 호출: 여행지 추천 (JSON 반환)
- 2차 호출: 최종 리포트 생성 (Markdown 반환)
"""
import json
from openai import OpenAI


class LLMClient:
    def __init__(self, api_key: str):
        # OpenAI 클라이언트 생성 (키를 전달)
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # 저렴하고 빠른 모델

    def recommend_city(self, date: str) -> dict:
        """
        1차 호출: 날짜를 기반으로 여행지 추천 JSON을 받는다.
        실패 시 1회 재시도한다.
        """
        prompt = f"""
당신은 국내 여행 전문가입니다. 사용자가 {date}에 국내 여행을 계획 중입니다.
아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요.

{{
  "recommended_city": "도시명 (예: 제주, 강릉)",
  "weather": "해당 시기 일반적인 날씨 요약 (1~2문장)",
  "events": ["행사1", "행사2"],
  "reason": "추천 근거 2~4문장"
}}
"""
        # 1차 시도
        try:
            return self._call_and_parse(prompt)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"    ⚠️  JSON 파싱 실패, 1회 재시도합니다... ({e})")

        # 재시도: 프롬프트를 더 엄격하게
        retry_prompt = prompt + "\n\n반드시 유효한 JSON만 출력하세요. 코드블록(```)도 쓰지 마세요."
        return self._call_and_parse(retry_prompt)

    def _call_and_parse(self, prompt: str) -> dict:
        """OpenAI 호출 후 JSON 파싱"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},  # JSON 강제 모드
        )
        content = response.choices[0].message.content
        return json.loads(content)

    def generate_report(self, date: str, recommendation: dict, restaurants: list, errors: list) -> str:
        """
        2차 호출: 1차 추천 + 맛집 목록으로 최종 Markdown 리포트를 생성한다.
        """
        # 맛집 리스트를 텍스트로 변환
        if restaurants:
            restaurants_text = "\n".join(
                f"- {r['name']} ({r.get('category', '카테고리 미상')}) / 주소: {r['address']} / {r.get('url', '')}"
                for r in restaurants
            )
        else:
            restaurants_text = "데이터 없음"

        # 오류 요약을 텍스트로
        errors_text = json.dumps(errors, ensure_ascii=False, indent=2) if errors else "없음"

        prompt = f"""
아래 정보를 바탕으로 {date} 국내 여행 리포트를 Markdown 형식으로 작성하세요.

[추천 데이터]
- 추천 도시: {recommendation.get('recommended_city')}
- 날씨: {recommendation.get('weather')}
- 행사: {recommendation.get('events')}
- 추천 이유: {recommendation.get('reason')}

[맛집 목록]
{restaurants_text}

[오류 요약]
{errors_text}

반드시 아래 구조를 정확히 따르세요:

# {date} 국내 여행 추천 리포트

## 추천 지역

## 추천 이유

## 날씨 요약

## 행사/축제

## 맛집 추천
(맛집이 없으면 "데이터 없음 (장소 검색 결과 0건)" 로 표기)

## 1일 일정 제안
(오전/오후/저녁으로 구분)

## 오류 요약(errors)
(오류가 없으면 "없음" 로 표기)
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content