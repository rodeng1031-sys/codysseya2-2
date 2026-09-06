"""
메인 실행 파일
사용법: python travel_planner.py --date "2025-03-15"
"""
import argparse
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from llm_client import LLMClient
from map_client import MapClient
from report_generator import save_results


def validate_date(date_str: str) -> str:
    """YYYY-MM-DD 형식 검증"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"날짜 형식이 올바르지 않습니다: '{date_str}'. YYYY-MM-DD 형식으로 입력하세요."
        )


def main():
    # ─────────────────────────────────────
    # 1) CLI 인자 파싱
    # ─────────────────────────────────────
    parser = argparse.ArgumentParser(description="국내 여행 추천 프로그램")
    parser.add_argument(
        "--date",
        type=validate_date,
        required=True,
        help='여행 날짜 (YYYY-MM-DD 형식, 예: "2025-03-15")',
    )
    args = parser.parse_args()
    date = args.date

    # ─────────────────────────────────────
    # 2) 환경변수 로드 & 키 검증
    # ─────────────────────────────────────
    load_dotenv()
    openai_key = os.getenv("OPENAI_API_KEY")
    kakao_key = os.getenv("KAKAO_API_KEY")

    if not openai_key:
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY=sk-... 형식으로 추가하세요.")
        sys.exit(1)

    if not kakao_key:
        print("❌ KAKAO_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 KAKAO_API_KEY=... 형식으로 추가하세요.")
        sys.exit(1)

    # 오류 누적용 리스트
    errors = []

    # 클라이언트 초기화
    llm = LLMClient(openai_key)
    mapc = MapClient(kakao_key)

    print(f"\n🗺️  {date} 국내 여행 추천을 시작합니다.\n")

    # ─────────────────────────────────────
    # 3) [1/3] LLM 1차 호출 - 여행지 추천
    # ─────────────────────────────────────
    print("[1/3] 여행지 추천 중...")
    try:
        recommendation = llm.recommend_city(date)
        city = recommendation.get("recommended_city", "")
        print(f"    ✅ 추천 도시: {city}")
    except Exception as e:
        print(f"    ❌ LLM 추천 실패: {e}")
        errors.append({
            "step": "llm_recommend",
            "type": "LLM_ERROR",
            "message": str(e),
        })
        # 여행지 추천 자체가 실패하면 종료
        print("\n여행지 추천에 실패하여 프로그램을 종료합니다.")
        sys.exit(1)

    # ─────────────────────────────────────
    # 4) [2/3] Kakao Local 호출 - 맛집 검색
    # ─────────────────────────────────────
    print("\n[2/3] 맛집 검색 중...")
    restaurants, err = mapc.search_restaurants(city)

    if err:
        errors.append(err)
        if err["type"] == "AUTH_ERROR":
            print(f"    - 오류: 인증 실패({err['message']}). 키 설정을 확인하세요.")
        elif err["type"] == "EMPTY_RESULT":
            print(f"    - 오류: 검색 결과 0건.")
        else:
            print(f"    - 오류: {err['type']} - {err['message']}")
        print("    - 맛집 섹션은 '데이터 없음'으로 처리하고 계속 진행합니다.")
    else:
        print(f"    ✅ 맛집 {len(restaurants)}곳 검색 완료")

    # ─────────────────────────────────────
    # 5) [3/3] LLM 2차 호출 - 최종 리포트 생성
    # ─────────────────────────────────────
    print("\n[3/3] 최종 리포트 생성 중...")
    try:
        report_md = llm.generate_report(date, recommendation, restaurants, errors)
        print("    ✅ 리포트 생성 완료")
    except Exception as e:
        print(f"    ❌ 리포트 생성 실패: {e}")
        errors.append({
            "step": "llm_report",
            "type": "LLM_ERROR",
            "message": str(e),
        })
        # 실패해도 최소한의 fallback 리포트 저장
        report_md = f"# {date} 국내 여행 추천 리포트\n\n리포트 생성 실패: {e}\n"

    # ─────────────────────────────────────
    # 6) 결과 저장
    # ─────────────────────────────────────
    json_path, md_path = save_results(date, recommendation, restaurants, errors, report_md)

    print(f"\n✨ 완료!")
    print(f"   📄 원본 JSON: {json_path}")
    print(f"   📝 최종 리포트: {md_path}")

    if errors:
        print(f"\n⚠️  총 {len(errors)}건의 오류가 기록되었습니다. (리포트의 '오류 요약' 섹션 확인)")


if __name__ == "__main__":
    main()