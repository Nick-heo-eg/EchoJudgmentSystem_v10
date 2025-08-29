#!/usr/bin/env python3
"""
🗺️ Maps API Smoke Test
사용자가 올려준 지도 스캐폴드 구조에 맞춘 테스트
"""

import os
import sys
from pathlib import Path
import yaml

# Project root setup
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_maps_config():
    """ECHO_RUNTIME.yaml에서 maps 설정 로드"""
    config_path = PROJECT_ROOT / "ECHO_RUNTIME.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("maps", {})
    except Exception as e:
        print(f"❌ Config load failed: {e}")
        return {}


def test_google_maps_integration():
    """Google Maps API 테스트"""
    print("\n🔍 Google Maps API Test")
    print("-" * 30)

    try:
        # 기존 maps_client 활용
        from tools.maps_client import MapsClient

        client = MapsClient()
        if client.gmaps:
            print("✅ Google Maps client initialized")

            # 실제 검색 테스트
            results = client.search_nearby_places(
                query="소아과 병원",
                location="성남시 분당구 정자동",
                place_type="hospital",
            )

            print(f"📍 Found {len(results)} pediatric hospitals")
            for i, place in enumerate(results[:3], 1):
                print(f"   {i}. {place.name} ({place.distance_km:.1f}km)")

        else:
            print("⚠️ Google Maps API key not configured, using mock data")
            print("   To test with real data, set: export GOOGLE_MAPS_API_KEY=your_key")

    except Exception as e:
        print(f"❌ Google Maps test failed: {e}")


def test_naver_maps_integration():
    """Naver Maps API 테스트"""
    print("\n🔍 Naver Maps API Test")
    print("-" * 30)

    naver_client_id = os.getenv("NAVER_MAPS_CLIENT_ID")
    naver_client_secret = os.getenv("NAVER_MAPS_CLIENT_SECRET")

    if naver_client_id and naver_client_secret:
        try:
            from tools.maps_client import MapsClient

            client = MapsClient()
            if client.naver_client_id:
                print("✅ Naver Maps client initialized")

                results = client._search_naver_places(
                    query="소아과 병원",
                    location="성남시 분당구 정자동",
                    place_type="hospital",
                    radius_m=2000,
                )

                print(f"📍 Found {len(results)} places via Naver API")
                for i, place in enumerate(results[:3], 1):
                    print(f"   {i}. {place.name}")

        except Exception as e:
            print(f"❌ Naver Maps test failed: {e}")
    else:
        print("⚠️ Naver Maps API credentials not configured")
        print("   To test with real data, set:")
        print("   export NAVER_MAPS_CLIENT_ID=your_id")
        print("   export NAVER_MAPS_CLIENT_SECRET=your_secret")


def test_mock_fallback():
    """Mock fallback 테스트"""
    print("\n🎭 Mock Fallback Test")
    print("-" * 30)

    try:
        from tools.maps_client import search_hospitals

        # Mock 모드로 강제 실행 (API 키 없이)
        results = search_hospitals(location="성남시 분당구 정자동", query="소아과 병원")

        print(f"✅ Mock fallback working: {len(results)} results")
        for i, place in enumerate(results[:3], 1):
            print(f"   {i}. {place.name} - {place.phone}")

    except Exception as e:
        print(f"❌ Mock fallback failed: {e}")


def test_echo_integration():
    """Echo 시스템 통합 테스트"""
    print("\n🌌 Echo Integration Test")
    print("-" * 30)

    try:
        from echo_engine.response_runner import answer

        test_query = "남율이가 열이 나는데 근처 소아과 병원 찾아줘"
        print(f"Test query: {test_query}")

        result = answer(test_query)

        if "소아과" in result and "병원" in result:
            print("✅ Echo medical search routing works")
            print(f"First line of result: {result.split(chr(10))[0][:60]}...")
        else:
            print("❌ Echo medical search routing failed")
            print(f"Result: {result[:100]}...")

    except Exception as e:
        print(f"❌ Echo integration test failed: {e}")


def main():
    """메인 스모크 테스트 실행"""
    print("🗺️ Maps API Smoke Test Suite")
    print("=" * 50)

    # 설정 확인
    maps_config = load_maps_config()
    print(f"Maps provider: {maps_config.get('provider', 'not configured')}")
    print(f"Default location: {maps_config.get('default_location', 'not configured')}")
    print(f"Radius: {maps_config.get('radius_m', 'not configured')}m")
    print(f"Fallback to mock: {maps_config.get('fallback_to_mock', True)}")

    # 테스트 실행
    test_google_maps_integration()
    test_naver_maps_integration()
    test_mock_fallback()
    test_echo_integration()

    print("\n🎉 Maps API Smoke Test Complete!")
    print("\n💡 Next steps:")
    print("   1. Add API keys to .env file for real data")
    print("   2. Test with 'python echo.py' and ask: '근처 소아과 찾아줘'")
    print("   3. Verify GPS coordinates integration")


if __name__ == "__main__":
    main()
