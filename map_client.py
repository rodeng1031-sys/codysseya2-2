"""
Kakao Local API 호출을 담당하는 모듈
- 키워드 기반 맛집 검색
"""
import requests


class MapClient:
    BASE_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

    def __init__(self, api_key: str):
        self.api_key = api_key
        # Kakao는 "KakaoAK {키}" 형식으로 인증
        self.headers = {"Authorization": f"KakaoAK {api_key}"}

    def search_restaurants(self, city: str, size: int = 5) -> tuple[list, dict | None]:
        """
        도시명 + '맛집'으로 검색.
        반환값: (맛집 리스트, 오류 dict 또는 None)
        """
        params = {
            "query": f"{city} 맛집",
            "size": size,
            "category_group_code": "FD6",  # FD6 = 음식점
        }

        try:
            response = requests.get(self.BASE_URL, headers=self.headers, params=params, timeout=10)
        except requests.exceptions.RequestException as e:
            return [], {"step": "place_search", "type": "NETWORK_ERROR", "message": str(e)}

        # 인증 실패
        if response.status_code in (401, 403):
            return [], {
                "step": "place_search",
                "type": "AUTH_ERROR",
                "message": f"HTTP {response.status_code}",
            }

        # 기타 HTTP 오류
        if response.status_code != 200:
            return [], {
                "step": "place_search",
                "type": "HTTP_ERROR",
                "message": f"HTTP {response.status_code}",
            }

        # 정상 응답 파싱
        try:
            data = response.json()
        except ValueError as e:
            return [], {"step": "place_search", "type": "PARSE_ERROR", "message": str(e)}

        documents = data.get("documents", [])

        # 결과 0건
        if not documents:
            return [], {
                "step": "place_search",
                "type": "EMPTY_RESULT",
                "message": f"0 results for query={params['query']}",
            }

        # 필요한 필드만 정리
        restaurants = [
            {
                "name": doc.get("place_name", ""),
                "address": doc.get("road_address_name") or doc.get("address_name", ""),
                "category": doc.get("category_name", ""),
                "url": doc.get("place_url", ""),
                "x": doc.get("x"),  # 경도(lng)
                "y": doc.get("y"),  # 위도(lat)
            }
            for doc in documents
        ]
        return restaurants, None