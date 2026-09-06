"""
결과를 파일로 저장하는 모듈
"""
import json
import os


def save_results(date: str, recommendation: dict, restaurants: list, errors: list, report_md: str):
    """
    results/ 폴더에 원본 JSON과 최종 Markdown을 저장한다.
    """
    os.makedirs("results", exist_ok=True)

    # 1. 원본 데이터 JSON
    json_path = f"results/{date}_raw.json"
    raw_data = {
        "date": date,
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    # 2. 최종 리포트 Markdown
    md_path = f"results/{date}_travel_plan.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    return json_path, md_path