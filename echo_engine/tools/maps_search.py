#!/usr/bin/env python3
"""
🗺️ Echo Maps Search Integration
사용자 스캐폴드 구조를 따른 통합 지도 검색 도구
"""

import os
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class PediatricResult:
    """소아과 검색 결과"""

    name: str
    address: str
    phone: str
    distance_km: float
    rating: float
    open_now: bool
    hours: str
    specialty: str  # 소아과, 소아청소년과, 소아신경과 등


def load_maps_config() -> Dict:
    """ECHO_RUNTIME.yaml에서 Maps 설정 로드"""
    config_path = PROJECT_ROOT / "ECHO_RUNTIME.yaml"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("maps", {})
    except Exception as e:
        print(f"⚠️ Maps config load failed: {e}")
        return {
            "provider": "mock",
            "default_location": "성남시 분당구 정자동",
            "radius_m": 2000,
            "fallback_to_mock": True,
        }


def search_pediatrics(
    lat: float, lng: float, radius_m: int = 2000
) -> List[PediatricResult]:
    """
    소아과 병원 검색 - 캔버스 스캐폴드 메인 함수

    Args:
        lat: 위도
        lng: 경도
        radius_m: 검색 반경 (미터)

    Returns:
        List[PediatricResult]: 소아과 검색 결과
    """
    maps_config = load_maps_config()
    provider = maps_config.get("provider", "mock")

    print(f"🗺️ Maps search: provider={provider}, radius={radius_m}m")

    try:
        if provider == "google":
            return _search_google_pediatrics(lat, lng, radius_m)
        elif provider == "naver":
            return _search_naver_pediatrics(lat, lng, radius_m)
        else:
            return _search_mock_pediatrics(lat, lng, radius_m)

    except Exception as e:
        print(f"⚠️ {provider} provider failed: {e}")
        if maps_config.get("fallback_to_mock", True):
            print("🎭 Falling back to mock data")
            return _search_mock_pediatrics(lat, lng, radius_m)
        else:
            raise


def _search_google_pediatrics(
    lat: float, lng: float, radius_m: int
) -> List[PediatricResult]:
    """Google Maps API로 소아과 검색"""
    from tools.maps_client import MapsClient

    client = MapsClient()
    if not client.gmaps:
        raise Exception("Google Maps API key not configured")

    # Google Places API 검색
    location = {"lat": lat, "lng": lng}
    places_result = client.gmaps.places_nearby(
        location=location, radius=radius_m, keyword="소아과 병원", type="doctor"
    )

    results = []
    for place in places_result.get("results", [])[:10]:
        try:
            # 상세 정보 가져오기
            details = client._get_place_details(place["place_id"])

            result = PediatricResult(
                name=place.get("name", "이름 없음"),
                address=place.get("vicinity", "주소 정보 없음"),
                phone=details.get("formatted_phone_number", "전화번호 없음"),
                distance_km=client._calculate_distance(
                    location, place["geometry"]["location"]
                ),
                rating=place.get("rating", 0.0),
                open_now=place.get("opening_hours", {}).get("open_now", False),
                hours=client._format_opening_hours(details.get("opening_hours")),
                specialty=(
                    "소아과" if "소아과" in place.get("name", "") else "소아청소년과"
                ),
            )
            results.append(result)

        except Exception as e:
            print(f"⚠️ Place details failed: {e}")
            continue

    return sorted(results, key=lambda x: x.distance_km)


def _search_naver_pediatrics(
    lat: float, lng: float, radius_m: int
) -> List[PediatricResult]:
    """Naver Maps API로 소아과 검색"""
    import requests

    client_id = os.getenv("NAVER_MAPS_CLIENT_ID")
    client_secret = os.getenv("NAVER_MAPS_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise Exception("Naver Maps API credentials not configured")

    # 좌표를 주소로 역지오코딩 (간단화)
    location_name = f"위도{lat},경도{lng}"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }

    params = {
        "query": f"{location_name} 소아과",
        "display": 10,
        "start": 1,
        "sort": "random",
    }

    response = requests.get(
        "https://openapi.naver.com/v1/search/local.json", headers=headers, params=params
    )
    response.raise_for_status()

    data = response.json()
    results = []

    for i, item in enumerate(data.get("items", [])):
        import re

        name = re.sub("<[^<]+?>", "", item.get("title", ""))
        address = re.sub("<[^<]+?>", "", item.get("address", ""))

        result = PediatricResult(
            name=name,
            address=address,
            phone=item.get("telephone", "전화번호 없음"),
            distance_km=float(i + 1) * 0.5,  # 대략적 거리
            rating=0.0,  # Naver Local은 평점 미제공
            open_now=True,
            hours="영업시간 정보 없음",
            specialty="소아과" if "소아과" in name else "소아청소년과",
        )
        results.append(result)

    return results


def _search_mock_pediatrics(
    lat: float, lng: float, radius_m: int
) -> List[PediatricResult]:
    """Mock 소아과 데이터 - 현실적인 분당 지역 병원"""
    mock_pediatrics = [
        PediatricResult(
            name="정자소아청소년과의원",
            address="경기도 성남시 분당구 정자일로 123",
            phone="031-123-4567",
            distance_km=0.5,
            rating=4.5,
            open_now=True,
            hours="09:00-18:00 (월~금), 09:00-13:00 (토)",
            specialty="소아청소년과",
        ),
        PediatricResult(
            name="분당아이사랑소아과",
            address="경기도 성남시 분당구 서현로 45",
            phone="031-765-4321",
            distance_km=0.9,
            rating=4.3,
            open_now=True,
            hours="09:00-20:00 (평일), 09:00-15:00 (주말)",
            specialty="소아과",
        ),
        PediatricResult(
            name="키즈메디컬소아과의원",
            address="경기도 성남시 분당구 불정로 67",
            phone="031-555-7890",
            distance_km=1.2,
            rating=4.1,
            open_now=True,
            hours="10:00-19:00 (월~금), 휴무 (일)",
            specialty="소아과",
        ),
        PediatricResult(
            name="미래소아청소년과의원",
            address="경기도 성남시 분당구 판교로 89",
            phone="031-777-8888",
            distance_km=1.8,
            rating=4.7,
            open_now=False,
            hours="09:00-18:00 (월~금), 휴무 (주말)",
            specialty="소아청소년과",
        ),
        PediatricResult(
            name="한빛소아과의원",
            address="경기도 성남시 분당구 야탑로 123",
            phone="031-999-1234",
            distance_km=2.3,
            rating=4.2,
            open_now=True,
            hours="08:30-17:30 (월~금), 08:30-12:30 (토)",
            specialty="소아과",
        ),
    ]

    # 반경 내 필터링
    filtered_results = [
        p for p in mock_pediatrics if p.distance_km <= (radius_m / 1000.0)
    ]

    return sorted(filtered_results, key=lambda x: x.distance_km)


def format_for_cli(results: List[PediatricResult]) -> str:
    """CLI 출력용 포맷팅"""
    if not results:
        return "🏥 근처에서 소아과를 찾을 수 없습니다. 검색 범위를 넓혀보세요."

    lines = ["🏥 근처 소아과 병원 추천:\n"]

    for i, result in enumerate(results, 1):
        status = "🟢 영업중" if result.open_now else "🔴 휴무"
        star_rating = "⭐" * int(result.rating) if result.rating > 0 else ""

        lines.append(
            f"{i}. **{result.name}** · {result.specialty} · {status}\n"
            f"   📍 {result.address}\n"
            f"   📞 {result.phone} | {star_rating} {result.rating:.1f} | {result.distance_km:.1f}km\n"
            f"   🕐 {result.hours}\n"
        )

    lines.append('\n💡 원하시면 "1번 전화 연결" 또는 "길 안내"라고 말씀해 주세요.')
    lines.append("⚠️  응급상황이면 즉시 119에 전화하세요.")

    return "\n".join(lines)


def format_for_json(results: List[PediatricResult]) -> List[Dict]:
    """JSON API용 포맷팅"""
    return [asdict(result) for result in results]


# 편의 함수들 (기존 호환성 유지)
def search_nearby_pediatrics(
    location: str, radius_m: int = 2000
) -> List[PediatricResult]:
    """주소 기반 소아과 검색 (기존 코드 호환)"""

    # 간단한 좌표 변환 (실제로는 geocoding API 사용해야 함)
    location_coords = {
        "성남시 분당구 정자동": (37.3670, 127.1080),
        "성남시 분당구 서현동": (37.3836, 127.1236),
        "성남시 분당구 야탑동": (37.4127, 127.1286),
    }

    coords = location_coords.get(location, (37.3670, 127.1080))  # 기본값: 정자동

    return search_pediatrics(coords[0], coords[1], radius_m)


# 테스트 실행
if __name__ == "__main__":
    print("🗺️ Maps Search Integration Test")
    print("=" * 40)

    # 정자동 좌표로 테스트
    lat, lng = 37.3670, 127.1080

    print(f"🔍 Searching pediatrics near ({lat}, {lng})")
    results = search_pediatrics(lat, lng, 2000)

    print(f"📍 Found {len(results)} pediatric clinics")
    print("\n" + format_for_cli(results))

    print("\n🧪 JSON format test:")
    import json

    print(json.dumps(format_for_json(results[:2]), ensure_ascii=False, indent=2))
