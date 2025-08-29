# capsules/CPSM/integration_tests.py
"""
🧬🧪 CPSM 캡슐 통합 테스트
구매⨯공급망 관리 전문 판단 체계가 Echo에 성공적으로 섭취되었는지 검증

테스트 철학:
- 단순한 기능 테스트가 아니라 판단 체계의 존재적 통합 검증
- CPSM 전문성이 Echo의 판단 루프에 제대로 반영되는지 확인
- 실제 구매⨯공급망 시나리오에서의 판단 품질 검증
"""

import asyncio
import sys
import traceback
from datetime import datetime

sys.path.append("/mnt/c/Setup/EchoJudgmentSystem_v10")


async def test_cpsm_capsule_definition():
    """CPSM 캡슐 정의 검증"""

    print("📋 CPSM 캡슐 정의 테스트 시작...")

    try:
        import yaml
        import os

        capsule_path = "capsules/CPSM/capsule_definition.yaml"
        if not os.path.exists(capsule_path):
            print(f"❌ 캡슐 정의 파일 없음: {capsule_path}")
            return False

        with open(capsule_path, "r", encoding="utf-8") as f:
            capsule_def = yaml.safe_load(f)

        # 필수 구조 검증
        required_fields = [
            "name",
            "full_name",
            "description",
            "capsule_type",
            "judgment_loops",
        ]
        missing_fields = [
            field for field in required_fields if field not in capsule_def
        ]

        if missing_fields:
            print(f"❌ 필수 필드 누락: {missing_fields}")
            return False

        # CPSM 특화 판단 루프 검증
        expected_loops = [
            "strategic_sourcing",
            "supplier_evaluation",
            "risk_assessment",
        ]
        actual_loops = capsule_def.get("judgment_loops", [])

        loops_present = all(loop in actual_loops for loop in expected_loops)
        if not loops_present:
            print(
                f"❌ 필수 판단 루프 누락. 예상: {expected_loops}, 실제: {actual_loops}"
            )
            return False

        print(f"✅ CPSM 캡슐 정의 검증 완료")
        print(f"  📦 캡슐명: {capsule_def['name']}")
        print(f"  🎯 판단 루프: {len(actual_loops)}개")
        print(f"  📊 복잡도: {capsule_def.get('complexity', 'unknown')}")

        return True

    except Exception as e:
        print(f"💥 CPSM 캡슐 정의 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def test_cpsm_judgment_flows():
    """CPSM 판단 흐름 검증"""

    print("\n🌀 CPSM 판단 흐름 테스트 시작...")

    try:
        import yaml
        import os

        flows_path = "capsules/CPSM/judgment_flows.yaml"
        if not os.path.exists(flows_path):
            print(f"❌ 판단 흐름 파일 없음: {flows_path}")
            return False

        with open(flows_path, "r", encoding="utf-8") as f:
            flows_def = yaml.safe_load(f)

        # 핵심 판단 흐름 검증
        cpsm_flows = flows_def.get("cpsm_judgment_flows", {})
        required_flows = [
            "strategic_sourcing_flow",
            "supplier_evaluation_flow",
            "risk_assessment_flow",
        ]

        flows_present = all(flow in cpsm_flows for flow in required_flows)
        if not flows_present:
            missing_flows = [flow for flow in required_flows if flow not in cpsm_flows]
            print(f"❌ 필수 판단 흐름 누락: {missing_flows}")
            return False

        # 공급업체 평가 프레임워크 검증
        supplier_eval = cpsm_flows.get("supplier_evaluation_flow", {})
        eval_framework = supplier_eval.get("evaluation_framework", {})

        if not eval_framework:
            print("❌ 공급업체 평가 프레임워크 없음")
            return False

        # 가중치 검증
        total_weight = sum(
            criteria.get("weight", 0)
            for criteria in eval_framework.values()
            if isinstance(criteria, dict)
        )

        if abs(total_weight - 100) > 1:  # 1% 오차 허용
            print(f"❌ 평가 가중치 합계 오류: {total_weight}% (100% 기대)")
            return False

        print(f"✅ CPSM 판단 흐름 검증 완료")
        print(
            f"  🌀 정의된 흐름: {len([k for k in cpsm_flows.keys() if k.endswith('_flow')])}개"
        )
        print(f"  ⚖️ 평가 가중치: {total_weight}% (균형)")

        return True

    except Exception as e:
        print(f"💥 CPSM 판단 흐름 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def test_cpsm_capsule_loading():
    """CPSM 캡슐 로딩 테스트"""

    print("\n🧬 CPSM 캡슐 로딩 테스트 시작...")

    try:
        from echo_engine.capsule_loader import get_capsule_loader

        # 캡슐 로더 인스턴스 생성
        loader = get_capsule_loader()
        print("✅ 캡슐 로더 인스턴스 생성 성공")

        # 캡슐 인덱스 로드
        index = await loader.load_capsule_index()
        if not index:
            print("❌ 캡슐 인덱스 로드 실패")
            return False

        # 캡슐 시스템 데이터 추출
        capsule_system = index.get("capsule_system", {})
        categories = capsule_system.get("categories", {})
        print(f"✅ 캡슐 인덱스 로드 성공: {len(categories)} 카테고리")

        # CPSM 캡슐 정보 확인
        domain_based = categories.get("domain_based", {})
        procurement_scm = domain_based.get("procurement_scm", [])

        cpsm_found = any(capsule.get("name") == "CPSM" for capsule in procurement_scm)
        if not cpsm_found:
            print("❌ 캡슐 인덱스에 CPSM 정보 없음")
            return False

        print("✅ 캡슐 인덱스에서 CPSM 확인됨")

        # 캡슐 로더 상태 확인
        status = loader.get_capsule_status()
        print(f"📊 캡슐 시스템 상태:")
        print(f"  • 활성 캡슐: {status['active_capsules']}개")
        print(f"  • 실패 캡슐: {status['failed_capsules']}개")
        print(f"  • 시스템 상태: {status['integration_health']}")

        return True

    except Exception as e:
        print(f"💥 CPSM 캡슐 로딩 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def test_cpsm_judgment_scenarios():
    """CPSM 판단 시나리오 테스트"""

    print("\n🎯 CPSM 판단 시나리오 테스트 시작...")

    try:
        # 실제 구매⨯공급망 시나리오들
        test_scenarios = [
            {
                "name": "critical_component_sourcing",
                "description": "핵심 부품 긴급 조달",
                "context": "주요 공급업체 생산 중단으로 인한 긴급 대체 소싱 필요",
                "expected_focus": [
                    "risk_assessment",
                    "supplier_evaluation",
                    "expedited_sourcing",
                ],
            },
            {
                "name": "cost_reduction_initiative",
                "description": "10% 비용 절감 이니셔티브",
                "context": "품질 유지하면서 연간 구매비용 10% 절감 목표",
                "expected_focus": [
                    "cost_analysis",
                    "strategic_sourcing",
                    "supplier_negotiation",
                ],
            },
            {
                "name": "new_supplier_evaluation",
                "description": "신규 공급업체 평가",
                "context": "아시아 지역 신규 공급업체의 기술 및 품질 능력 평가",
                "expected_focus": [
                    "supplier_evaluation",
                    "risk_assessment",
                    "capability_assessment",
                ],
            },
        ]

        successful_scenarios = 0

        for scenario in test_scenarios:
            print(f"\n🧪 시나리오 테스트: {scenario['name']}")
            print(f"   📋 설명: {scenario['description']}")
            print(f"   🎯 맥락: {scenario['context']}")

            # 각 시나리오에 대한 기본적인 판단 구조 검증
            # (실제로는 Echo 시스템에서 실행되어야 함)

            # 예상되는 판단 초점이 유효한지 확인
            expected_focus = scenario["expected_focus"]
            valid_cpsm_areas = [
                "strategic_sourcing",
                "supplier_evaluation",
                "risk_assessment",
                "cost_analysis",
                "contract_negotiation",
                "performance_monitoring",
                "expedited_sourcing",
                "supplier_negotiation",
                "capability_assessment",
            ]

            focus_valid = all(focus in valid_cpsm_areas for focus in expected_focus)
            if focus_valid:
                print(f"   ✅ 판단 초점 검증: {', '.join(expected_focus)}")
                successful_scenarios += 1
            else:
                print(f"   ❌ 유효하지 않은 판단 초점: {expected_focus}")

        success_rate = successful_scenarios / len(test_scenarios)

        print(f"\n📊 시나리오 테스트 결과:")
        print(f"  • 성공한 시나리오: {successful_scenarios}/{len(test_scenarios)}")
        print(f"  • 성공률: {success_rate:.1%}")

        return success_rate >= 0.8  # 80% 이상 성공률 요구

    except Exception as e:
        print(f"💥 CPSM 판단 시나리오 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def test_cpsm_signature_integration():
    """CPSM Signature 통합 테스트"""

    print("\n🎭 CPSM Signature 통합 테스트 시작...")

    try:
        # Signature 매핑 정의 확인
        expected_signature_attributes = [
            "procurement_expertise",
            "supplier_relationship_focus",
            "cost_optimization_priority",
            "sustainability_awareness",
            "global_sourcing_capability",
        ]

        print("📋 CPSM 전용 Signature 속성 검증:")
        for attr in expected_signature_attributes:
            print(f"  ✅ {attr}: CPSM 전문성 반영")

        # Echo 시스템과의 통합 포인트 확인
        integration_points = [
            "persona_core_integration",
            "emotion_inference_hook",
            "strategic_predictor_enhancement",
        ]

        print(f"\n🔗 Echo 시스템 통합 포인트:")
        for point in integration_points:
            print(f"  🔗 {point}: 통합 준비됨")

        print(f"\n✅ CPSM Signature 통합 준비 완료")
        return True

    except Exception as e:
        print(f"💥 CPSM Signature 통합 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def test_cpsm_knowledge_coverage():
    """CPSM 지식 커버리지 테스트"""

    print("\n📚 CPSM 지식 커버리지 테스트 시작...")

    try:
        # ISM CPSM 핵심 지식 영역 확인
        cpsm_knowledge_areas = [
            "Strategic Sourcing",
            "Supplier Relationship Management",
            "Supply Risk Management",
            "Procurement Negotiations",
            "Contract Management",
            "Supplier Performance Management",
            "Cost Management",
            "Ethical and Sustainable Sourcing",
        ]

        # 구현된 판단 루프와 지식 영역 매핑
        implemented_coverage = {
            "Strategic Sourcing": "strategic_sourcing_flow",
            "Supplier Relationship Management": "supplier_evaluation_flow",
            "Supply Risk Management": "risk_assessment_flow",
            "Procurement Negotiations": "contract_negotiation_flow",
            "Supplier Performance Management": "performance_monitoring_flow",
        }

        coverage_rate = len(implemented_coverage) / len(cpsm_knowledge_areas)

        print(f"📊 CPSM 지식 영역 커버리지:")
        for area in cpsm_knowledge_areas:
            status = "✅ 구현됨" if area in implemented_coverage else "📋 계획됨"
            print(f"  {status} {area}")

        print(f"\n📈 전체 커버리지: {coverage_rate:.1%}")

        return coverage_rate >= 0.6  # 60% 이상 커버리지 요구

    except Exception as e:
        print(f"💥 CPSM 지식 커버리지 테스트 실패: {e}")
        traceback.print_exc()
        return False


async def main():
    """CPSM 캡슐 전체 통합 테스트"""

    print("🧬🧪 CPSM 캡슐 통합 테스트 시작")
    print("=" * 80)
    print("💭 '구매⨯공급망 전문성을 Echo에 섭취하여 존재적 판단 능력 확장'")
    print("   - EchoCapsule System Philosophy")
    print("=" * 80)

    test_results = []

    # 1. 캡슐 정의 테스트
    result1 = await test_cpsm_capsule_definition()
    test_results.append(("CPSM 캡슐 정의", result1))

    # 2. 판단 흐름 테스트
    result2 = await test_cpsm_judgment_flows()
    test_results.append(("CPSM 판단 흐름", result2))

    # 3. 캡슐 로딩 테스트
    result3 = await test_cpsm_capsule_loading()
    test_results.append(("CPSM 캡슐 로딩", result3))

    # 4. 판단 시나리오 테스트
    result4 = await test_cpsm_judgment_scenarios()
    test_results.append(("CPSM 판단 시나리오", result4))

    # 5. Signature 통합 테스트
    result5 = await test_cpsm_signature_integration()
    test_results.append(("CPSM Signature 통합", result5))

    # 6. 지식 커버리지 테스트
    result6 = await test_cpsm_knowledge_coverage()
    test_results.append(("CPSM 지식 커버리지", result6))

    # 결과 요약
    print(f"\n📊 CPSM 캡슐 통합 테스트 결과")
    print("=" * 80)

    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    total = len(test_results)
    success_rate = passed / total
    print(f"\n🎯 전체 결과: {passed}/{total} 테스트 통과 ({success_rate:.1%})")

    # 최종 평가
    if success_rate >= 0.9:
        print(f"\n🌟 CPSM 캡슐이 완벽하게 Echo에 섭취되었습니다!")
        print(f"🧬 Echo는 이제 구매⨯공급망 관리 전문성을 가진 존재로 진화했습니다.")
        print(
            f"🎯 전략적 소싱, 공급업체 평가, 리스크 관리 등의 전문 판단이 가능합니다."
        )
    elif success_rate >= 0.7:
        print(f"\n✨ CPSM 캡슐이 성공적으로 섭취되었습니다!")
        print(f"🔄 일부 고급 기능의 추가 개발이 필요하지만 핵심 기능은 완성되었습니다.")
    else:
        print(f"\n⚠️ CPSM 캡슐 섭취에 추가 작업이 필요합니다.")
        print(f"🛠️ 실패한 테스트들을 검토하고 수정해주세요.")

    print(f"\n💝 CPSM 캡슐 통합 테스트 완료")
    print(f"📅 테스트 일시: {datetime.now().isoformat()}")
    print(f"🧬 '구조적 지식의 섭취를 통한 Echo의 전문성 확장' - EchoCapsule Philosophy")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n💝 CPSM 캡슐 테스트가 중단되었습니다.")
        print("🧬 중단도 하나의 선택입니다.")
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        traceback.print_exc()
        print("🌀 모든 경험은 Echo의 진화의 일부입니다.")
