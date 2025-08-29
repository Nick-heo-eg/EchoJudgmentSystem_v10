#!/usr/bin/env python3
"""
🗺️ Maps API Client - Google Maps & Naver Maps 통합
실제 지역 서비스 검색을 위한 API 클라이언트
"""

import os
import requests
import googlemaps
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlaceResult:
    """지역 서비스 검색 결과"""

    name: str
    address: str
    phone: str
    rating: float
    open_now: bool
    opening_hours: str
    distance_km: float
    place_id: str
    place_type: str  # hospital, pharmacy, emergency


class MapsClient:
    """통합 Maps API 클라이언트"""

    def __init__(self):
        # Google Maps API 클라이언트
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.gmaps = None
        if self.google_api_key:
            self.gmaps = googlemaps.Client(key=self.google_api_key)

        # Naver Maps API 키들
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")

        # 기본 설정
        self.default_radius_m = 3000
        self.max_results = 10

        print(f"🗺️ Maps Client 초기화:")
        print(f"  - Google Maps: {'✅' if self.gmaps else '❌ (키 없음)'}")
        print(f"  - Naver Maps: {'✅' if self.naver_client_id else '❌ (키 없음)'}")

    def search_nearby_places(
        self,
        query: str,
        location: str,
        place_type: str = "hospital",
        radius_m: int = None,
        open_now: bool = True,
    ) -> List[PlaceResult]:
        """
        지역 서비스 검색 통합 함수

        Args:
            query: 검색어 (예: "소아과 병원", "응급실", "약국")
            location: 위치 (예: "성남시 분당구 정자동")
            place_type: 장소 유형
            radius_m: 검색 반경 (미터)
            open_now: 현재 영업중인 곳만
        """
        radius_m = radius_m or self.default_radius_m

        # 1) Google Maps 우선 시도
        if self.gmaps:
            try:
                return self._search_google_places(
                    query, location, place_type, radius_m, open_now
                )
            except Exception as e:
                print(f"⚠️ Google Maps 검색 실패: {e}")

        # 2) Naver Maps 시도
        if self.naver_client_id:
            try:
                return self._search_naver_places(query, location, place_type, radius_m)
            except Exception as e:
                print(f"⚠️ Naver Maps 검색 실패: {e}")

        # 3) 둘 다 실패시 목업 반환
        print("⚠️ 실제 API 호출 실패, 목업 데이터 사용")
        return self._get_mock_results(query, location, place_type)

    def _search_google_places(
        self, query: str, location: str, place_type: str, radius_m: int, open_now: bool
    ) -> List[PlaceResult]:
        """Google Places API 검색"""

        # 위치를 좌표로 변환
        geocode_result = self.gmaps.geocode(location)
        if not geocode_result:
            raise Exception(f"위치 '{location}' 좌표 변환 실패")

        lat_lng = geocode_result[0]["geometry"]["location"]

        # 장소 유형 매핑
        google_types = {
            "hospital": ["hospital", "doctor"],
            "pharmacy": ["pharmacy"],
            "emergency": ["hospital"],
        }

        search_types = google_types.get(place_type, ["establishment"])

        # Places API 검색
        places_result = self.gmaps.places_nearby(
            location=lat_lng,
            radius=radius_m,
            keyword=query,
            type=search_types[0] if search_types else None,
            open_now=open_now,
        )

        results = []
        for place in places_result.get("results", [])[: self.max_results]:
            try:
                # 상세 정보 가져오기
                details = self._get_place_details(place["place_id"])

                result = PlaceResult(
                    name=place.get("name", "이름 없음"),
                    address=place.get("vicinity", "주소 정보 없음"),
                    phone=details.get("formatted_phone_number", "전화번호 없음"),
                    rating=place.get("rating", 0.0),
                    open_now=place.get("opening_hours", {}).get("open_now", False),
                    opening_hours=self._format_opening_hours(
                        details.get("opening_hours")
                    ),
                    distance_km=self._calculate_distance(
                        lat_lng, place["geometry"]["location"]
                    ),
                    place_id=place["place_id"],
                    place_type=place_type,
                )
                results.append(result)

            except Exception as e:
                print(f"⚠️ 장소 세부정보 가져오기 실패: {e}")
                continue

        return sorted(results, key=lambda x: x.distance_km)

    def _search_naver_places(
        self, query: str, location: str, place_type: str, radius_m: int
    ) -> List[PlaceResult]:
        """Naver Local Search API 검색"""

        headers = {
            "X-Naver-Client-Id": self.naver_client_id,
            "X-Naver-Client-Secret": self.naver_client_secret,
        }

        params = {
            "query": f"{location} {query}",
            "display": self.max_results,
            "start": 1,
            "sort": "random",
        }

        url = "https://openapi.naver.com/v1/search/local.json"
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        results = []

        for item in data.get("items", []):
            # HTML 태그 제거
            import re

            name = re.sub("<[^<]+?>", "", item.get("title", ""))
            address = re.sub("<[^<]+?>", "", item.get("address", ""))

            result = PlaceResult(
                name=name,
                address=address,
                phone=item.get("telephone", "전화번호 없음"),
                rating=0.0,  # Naver Local Search는 평점 미제공
                open_now=True,  # 현재 영업 여부 확인 불가
                opening_hours="영업시간 정보 없음",
                distance_km=0.0,  # 거리 계산 생략
                place_id=item.get("link", ""),
                place_type=place_type,
            )
            results.append(result)

        return results

    def _get_place_details(self, place_id: str) -> Dict:
        """Google Places 상세 정보 조회"""
        if not self.gmaps:
            return {}

        details = self.gmaps.place(
            place_id=place_id,
            fields=["formatted_phone_number", "opening_hours", "website"],
        )
        return details.get("result", {})

    def _format_opening_hours(self, opening_hours: Optional[Dict]) -> str:
        """영업시간 포맷팅"""
        if not opening_hours:
            return "영업시간 정보 없음"

        weekday_text = opening_hours.get("weekday_text", [])
        if weekday_text:
            # 오늘의 영업시간만 반환
            today_idx = datetime.now().weekday()
            days = ["월", "화", "수", "목", "금", "토", "일"]
            if today_idx < len(weekday_text):
                today_hours = weekday_text[today_idx]
                # "Monday: 9:00 AM – 6:00 PM" -> "09:00-18:00"
                return (
                    today_hours.split(": ", 1)[-1]
                    if ": " in today_hours
                    else today_hours
                )

        return "24시간" if opening_hours.get("open_now") else "영업시간 확인 필요"

    def _calculate_distance(self, origin: Dict, destination: Dict) -> float:
        """두 좌표 간 거리 계산 (km)"""
        from math import radians, sin, cos, sqrt, atan2

        # 하버사인 공식
        R = 6371  # 지구 반지름 (km)

        lat1, lon1 = radians(origin["lat"]), radians(origin["lng"])
        lat2, lon2 = radians(destination["lat"]), radians(destination["lng"])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    def _get_mock_results(
        self, query: str, location: str, place_type: str
    ) -> List[PlaceResult]:
        """API 실패시 목업 데이터"""

        if "소아과" in query:
            return [
                PlaceResult(
                    "정자소아청소년과의원",
                    "분당구 정자일로 123",
                    "031-123-4567",
                    4.5,
                    True,
                    "09:00-18:00",
                    0.5,
                    "mock_1",
                    "hospital",
                ),
                PlaceResult(
                    "분당아이사랑소아과",
                    "분당구 서현로 45",
                    "031-765-4321",
                    4.3,
                    True,
                    "09:00-20:00",
                    0.9,
                    "mock_2",
                    "hospital",
                ),
                PlaceResult(
                    "키즈메디컬소아과",
                    "분당구 불정로 67",
                    "031-555-7890",
                    4.1,
                    True,
                    "10:00-19:00",
                    1.2,
                    "mock_3",
                    "hospital",
                ),
            ]
        elif "응급" in query:
            return [
                PlaceResult(
                    "분당서울대병원 응급센터",
                    "분당구 구미로 173번길",
                    "031-787-0114",
                    4.7,
                    True,
                    "24시간",
                    2.1,
                    "mock_4",
                    "emergency",
                ),
                PlaceResult(
                    "차병원 응급실",
                    "분당구 야탑로 59",
                    "031-780-5114",
                    4.4,
                    True,
                    "24시간",
                    2.8,
                    "mock_5",
                    "emergency",
                ),
            ]
        elif "약국" in query:
            return [
                PlaceResult(
                    "정자온누리약국",
                    "분당구 정자일로 135",
                    "031-123-9876",
                    4.2,
                    True,
                    "09:00-21:00",
                    0.3,
                    "mock_6",
                    "pharmacy",
                ),
                PlaceResult(
                    "24시간약국",
                    "분당구 서현로 123",
                    "031-444-5555",
                    4.0,
                    True,
                    "24시간",
                    0.7,
                    "mock_7",
                    "pharmacy",
                ),
            ]
        else:
            return [
                PlaceResult(
                    "정자가정의학과",
                    "분당구 정자일로 123",
                    "031-123-4567",
                    4.3,
                    True,
                    "09:00-18:00",
                    0.5,
                    "mock_8",
                    "hospital",
                ),
                PlaceResult(
                    "분당서울대병원",
                    "분당구 구미로 173번길",
                    "031-787-7114",
                    4.8,
                    True,
                    "24시간",
                    2.1,
                    "mock_9",
                    "hospital",
                ),
                PlaceResult(
                    "차병원",
                    "분당구 야탑로 59",
                    "031-780-5000",
                    4.6,
                    True,
                    "08:00-18:00",
                    2.8,
                    "mock_10",
                    "hospital",
                ),
            ]


# 편의 함수들
def search_hospitals(
    location: str, query: str = "병원", radius_m: int = 3000
) -> List[PlaceResult]:
    """병원 검색 편의 함수"""
    client = MapsClient()
    return client.search_nearby_places(query, location, "hospital", radius_m)


def search_pharmacies(location: str, radius_m: int = 2000) -> List[PlaceResult]:
    """약국 검색 편의 함수"""
    client = MapsClient()
    return client.search_nearby_places("약국", location, "pharmacy", radius_m)


def search_emergency_rooms(location: str) -> List[PlaceResult]:
    """응급실 검색 편의 함수"""
    client = MapsClient()
    return client.search_nearby_places(
        "응급실", location, "emergency", 5000
    )  # 5km 반경


# 테스트 실행
if __name__ == "__main__":
    print("🗺️ Maps Client 테스트 시작")

    location = "성남시 분당구 정자동"

    print(f"\n1) 소아과 병원 검색 - {location}")
    hospitals = search_hospitals(location, "소아과 병원")
    for i, h in enumerate(hospitals[:3], 1):
        print(f"   {i}. {h.name} ({h.distance_km:.1f}km)")
        print(f"      📍 {h.address}")
        print(f"      📞 {h.phone} | ⭐ {h.rating} | {h.opening_hours}")

    print(f"\n2) 응급실 검색 - {location}")
    emergency = search_emergency_rooms(location)
    for i, e in enumerate(emergency[:2], 1):
        print(f"   {i}. {e.name} ({e.distance_km:.1f}km)")
        print(f"      📍 {e.address}")
        print(f"      📞 {e.phone} | {e.opening_hours}")

    print(f"\n3) 약국 검색 - {location}")
    pharmacies = search_pharmacies(location)
    for i, p in enumerate(pharmacies[:3], 1):
        print(f"   {i}. {p.name} ({p.distance_km:.1f}km)")
        print(f"      📍 {p.address}")
        print(f"      📞 {p.phone} | {p.opening_hours}")

    print("\n🗺️ Maps Client 테스트 완료!")
