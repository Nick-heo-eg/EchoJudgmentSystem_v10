#!/usr/bin/env python3
"""
🎓 Echo 피드백 학습 시스템 - Echo가 Claude의 피드백을 기억하고 적용하는 시스템

Echo의 진짜 문제: 같은 실수를 반복함!
- 파일명을 요구사항과 다르게 생성
- 클래스명과 메서드를 지시사항대로 만들지 못함
- 템플릿 코드만 생성하고 실제 기능 구현 못함

해결책: Claude의 모든 피드백을 기억하고 다음 코딩에 적용!
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CodingFeedback:
    """코딩 피드백 데이터"""

    feedback_id: str
    timestamp: datetime
    feedback_type: str  # "filename", "class_structure", "implementation", "error"
    original_mistake: str
    correction: str
    importance_level: int  # 1-5 (5가 가장 중요)
    applied_successfully: bool
    context: str


@dataclass
class CodingGuideline:
    """학습된 코딩 가이드라인"""

    guideline_id: str
    category: str  # "naming", "structure", "implementation", "best_practices"
    rule: str
    examples: List[str]
    violation_count: int
    success_when_applied: int


class EchoCodingFeedbackLearner:
    """
    🧠 Echo의 코딩 피드백 학습 시스템

    Echo가 Claude의 피드백을 구체적으로 기억하고
    다음 코딩할 때 같은 실수를 반복하지 않도록 하는 시스템

    핵심 목표: "학습하는 AI"가 되기!
    """

    def __init__(self, data_dir: str = "data/echo_coding_learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 데이터 파일들
        self.feedback_file = self.data_dir / "coding_feedback_history.json"
        self.guidelines_file = self.data_dir / "learned_guidelines.json"
        self.patterns_file = self.data_dir / "successful_patterns.json"

        # 메모리 구조
        self.feedback_history: List[CodingFeedback] = []
        self.learned_guidelines: List[CodingGuideline] = []
        self.successful_patterns: Dict[str, Any] = {}

        # 데이터 로드
        self._load_all_data()

        # 기본 가이드라인 초기화 (Claude의 기본 피드백들)
        self._initialize_basic_guidelines()

        print("🎓 Echo 코딩 피드백 학습 시스템 초기화 완료!")
        print(f"   저장된 피드백: {len(self.feedback_history)}개")
        print(f"   학습된 가이드라인: {len(self.learned_guidelines)}개")

    def save_coding_feedback(
        self,
        feedback_type: str,
        original_mistake: str,
        correction: str,
        importance: int = 3,
        context: str = "",
    ) -> str:
        """
        Claude의 코딩 피드백 저장

        Args:
            feedback_type: 피드백 유형 ("filename", "class_structure", "implementation", "error")
            original_mistake: Echo가 한 실수
            correction: Claude가 제시한 올바른 방법
            importance: 중요도 (1-5)
            context: 피드백 상황/맥락

        Returns:
            생성된 피드백 ID
        """
        try:
            feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.feedback_history)}"

            feedback = CodingFeedback(
                feedback_id=feedback_id,
                timestamp=datetime.now(),
                feedback_type=feedback_type,
                original_mistake=original_mistake,
                correction=correction,
                importance_level=importance,
                applied_successfully=False,  # 아직 적용 안함
                context=context,
            )

            self.feedback_history.append(feedback)

            # 자동으로 가이드라인 생성
            self._create_guideline_from_feedback(feedback)

            print(f"📝 피드백 저장: {feedback_type} - {original_mistake[:50]}...")

            self._save_all_data()

            return feedback_id

        except Exception as e:
            print(f"⚠️ 피드백 저장 실패: {e}")
            return ""

    def get_coding_guidelines(self, task_type: str = "general") -> List[Dict[str, Any]]:
        """
        이전 피드백 기반 코딩 가이드라인 제공

        Args:
            task_type: 작업 유형 ("file_creation", "class_design", "method_implementation")

        Returns:
            적용 가능한 가이드라인 리스트
        """
        try:
            relevant_guidelines = []

            for guideline in self.learned_guidelines:
                # 작업 유형에 맞는 가이드라인 필터링
                if self._is_guideline_relevant(guideline, task_type):
                    relevant_guidelines.append(
                        {
                            "rule": guideline.rule,
                            "category": guideline.category,
                            "examples": guideline.examples,
                            "importance": self._calculate_guideline_importance(
                                guideline
                            ),
                            "violations": guideline.violation_count,
                            "success_rate": self._calculate_success_rate(guideline),
                        }
                    )

            # 중요도 순으로 정렬
            relevant_guidelines.sort(key=lambda x: x["importance"], reverse=True)

            print(
                f"💡 {task_type}에 적용 가능한 가이드라인 {len(relevant_guidelines)}개 제공"
            )

            return relevant_guidelines

        except Exception as e:
            print(f"⚠️ 가이드라인 제공 실패: {e}")
            return []

    def apply_learned_patterns(
        self, user_request: str, intended_filename: str, intended_classname: str
    ) -> Dict[str, Any]:
        """
        학습한 패턴을 다음 코딩에 적용

        Args:
            user_request: 사용자 요청
            intended_filename: 의도한 파일명
            intended_classname: 의도한 클래스명

        Returns:
            적용할 패턴과 주의사항
        """
        try:
            application_guide = {
                "filename_check": self._check_filename_pattern(intended_filename),
                "class_structure_guide": self._get_class_structure_guide(
                    intended_classname, user_request
                ),
                "implementation_warnings": self._get_implementation_warnings(
                    user_request
                ),
                "common_mistakes_to_avoid": self._get_common_mistakes(),
                "success_patterns": self._get_successful_patterns(user_request),
            }

            print(f"🎯 학습된 패턴 적용 가이드 생성 완료")

            return application_guide

        except Exception as e:
            print(f"⚠️ 패턴 적용 실패: {e}")
            return {}

    def mark_feedback_applied(self, feedback_id: str, success: bool, notes: str = ""):
        """피드백이 성공적으로 적용되었는지 기록"""
        try:
            for feedback in self.feedback_history:
                if feedback.feedback_id == feedback_id:
                    feedback.applied_successfully = success

                    # 관련 가이드라인 업데이트
                    self._update_guideline_success(feedback, success)

                    print(
                        f"✅ 피드백 적용 결과 기록: {feedback_id} -> {'성공' if success else '실패'}"
                    )
                    break

            self._save_all_data()

        except Exception as e:
            print(f"⚠️ 피드백 적용 결과 기록 실패: {e}")

    def _create_guideline_from_feedback(self, feedback: CodingFeedback):
        """피드백으로부터 가이드라인 생성"""

        guideline_id = (
            f"guideline_{feedback.feedback_type}_{len(self.learned_guidelines)}"
        )

        # 피드백 유형별 가이드라인 생성
        if feedback.feedback_type == "filename":
            rule = f"파일명은 정확히 요구사항대로: '{feedback.correction}'"
            category = "naming"
            examples = [
                f"잘못: {feedback.original_mistake}",
                f"올바름: {feedback.correction}",
            ]

        elif feedback.feedback_type == "class_structure":
            rule = f"클래스 구조는 요구사항 정확히 따르기: {feedback.correction}"
            category = "structure"
            examples = [feedback.correction]

        elif feedback.feedback_type == "implementation":
            rule = f"실제 기능 구현하기 (템플릿 금지): {feedback.correction}"
            category = "implementation"
            examples = [feedback.correction]

        else:
            rule = feedback.correction
            category = "general"
            examples = [feedback.correction]

        guideline = CodingGuideline(
            guideline_id=guideline_id,
            category=category,
            rule=rule,
            examples=examples,
            violation_count=1,  # 이 피드백이 생긴 이유는 위반했기 때문
            success_when_applied=0,
        )

        self.learned_guidelines.append(guideline)

    def _initialize_basic_guidelines(self):
        """Claude의 기본 피드백들을 가이드라인으로 초기화"""

        if self.learned_guidelines:  # 이미 초기화됨
            return

        basic_guidelines = [
            {
                "category": "naming",
                "rule": "파일명은 사용자가 요청한 정확한 이름으로 생성하기",
                "examples": [
                    "요청: 'abc.py' → 생성: 'abc.py' (정확)",
                    "요청: 'abc.py' → 생성: 'xyz.py' (틀림)",
                ],
            },
            {
                "category": "structure",
                "rule": "클래스명과 메서드명은 요구사항에 명시된 정확한 이름 사용",
                "examples": [
                    "요청한 클래스: MyClass → 생성: MyClass",
                    "요청한 메서드: process() → 생성: process()",
                ],
            },
            {
                "category": "implementation",
                "rule": "템플릿이 아닌 실제 동작하는 기능 구현하기",
                "examples": [
                    "'여기에 구현하세요' 주석 대신 실제 코드 작성",
                    "기본값 반환이 아닌 진짜 로직 구현",
                ],
            },
        ]

        for i, guide in enumerate(basic_guidelines):
            guideline = CodingGuideline(
                guideline_id=f"basic_{i}",
                category=guide["category"],
                rule=guide["rule"],
                examples=guide["examples"],
                violation_count=0,
                success_when_applied=0,
            )
            self.learned_guidelines.append(guideline)

    def _check_filename_pattern(self, intended_filename: str) -> Dict[str, Any]:
        """파일명 패턴 체크"""

        filename_feedbacks = [
            fb for fb in self.feedback_history if fb.feedback_type == "filename"
        ]

        warnings = []
        if filename_feedbacks:
            latest_mistake = filename_feedbacks[-1]
            warnings.append(
                f"이전 실수: {latest_mistake.original_mistake} → 정정: {latest_mistake.correction}"
            )

        return {
            "intended_filename": intended_filename,
            "warnings": warnings,
            "rule": "반드시 요청된 정확한 파일명 사용하기!",
        }

    def _get_class_structure_guide(
        self, classname: str, user_request: str
    ) -> Dict[str, Any]:
        """클래스 구조 가이드"""

        structure_feedbacks = [
            fb for fb in self.feedback_history if fb.feedback_type == "class_structure"
        ]

        return {
            "intended_classname": classname,
            "previous_mistakes": [
                fb.original_mistake for fb in structure_feedbacks[-3:]
            ],
            "rule": "클래스명과 메서드명을 요구사항에서 명시한 정확한 이름으로 사용",
        }

    def _get_implementation_warnings(self, user_request: str) -> List[str]:
        """구현 시 주의사항"""

        impl_feedbacks = [
            fb for fb in self.feedback_history if fb.feedback_type == "implementation"
        ]

        warnings = [
            "템플릿 코드 대신 실제 동작하는 기능 구현하기",
            "'여기에 구현하세요' 주석 사용 금지",
            "기본값만 반환하지 말고 진짜 로직 작성",
        ]

        # 이전 구현 실수들 추가
        for fb in impl_feedbacks[-3:]:
            warnings.append(f"이전 실수: {fb.original_mistake}")

        return warnings

    def _get_common_mistakes(self) -> List[str]:
        """자주 하는 실수들"""

        mistake_counts = {}
        for fb in self.feedback_history:
            mistake = fb.original_mistake[:50]  # 처음 50자만
            mistake_counts[mistake] = mistake_counts.get(mistake, 0) + 1

        # 빈도 순으로 정렬
        common_mistakes = sorted(
            mistake_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [
            f"{mistake} (반복 횟수: {count})" for mistake, count in common_mistakes[:5]
        ]

    def _get_successful_patterns(self, user_request: str) -> List[str]:
        """성공적이었던 패턴들"""

        successful_feedbacks = [
            fb for fb in self.feedback_history if fb.applied_successfully
        ]

        return [fb.correction for fb in successful_feedbacks[-5:]]

    def generate_learning_report(self) -> str:
        """Echo의 학습 현황 보고서"""

        total_feedbacks = len(self.feedback_history)
        successful_applications = len(
            [fb for fb in self.feedback_history if fb.applied_successfully]
        )

        # 카테고리별 피드백 분석
        category_counts = {}
        for fb in self.feedback_history:
            category_counts[fb.feedback_type] = (
                category_counts.get(fb.feedback_type, 0) + 1
            )

        # 가장 자주 하는 실수
        common_mistakes = self._get_common_mistakes()

        report = f"""
🎓 Echo 코딩 학습 보고서
생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 학습 통계:
- 총 받은 피드백: {total_feedbacks}개
- 성공적으로 적용한 피드백: {successful_applications}개
- 피드백 적용 성공률: {(successful_applications/max(total_feedbacks,1)*100):.1f}%

📋 피드백 유형별 분석:
"""

        for category, count in category_counts.items():
            report += f"- {category}: {count}개\n"

        report += f"""
⚠️ 자주 반복하는 실수들:
"""

        for i, mistake in enumerate(common_mistakes[:3], 1):
            report += f"{i}. {mistake}\n"

        report += f"""
💡 Echo의 자기분석:
- {"학습 성과가 좋습니다!" if (successful_applications/max(total_feedbacks,1)) > 0.7 else "더 주의깊게 피드백을 적용해야 합니다."}
- 총 {len(self.learned_guidelines)}개의 코딩 가이드라인을 학습했습니다.
- Claude 선생님의 피드백을 기반으로 지속적으로 개선 중입니다.

🎯 다음 목표: 같은 실수 반복하지 않기!
        """

        return report.strip()

    def _is_guideline_relevant(
        self, guideline: CodingGuideline, task_type: str
    ) -> bool:
        """가이드라인이 현재 작업에 관련있는지 확인"""
        relevance_map = {
            "file_creation": ["naming", "general"],
            "class_design": ["structure", "naming", "general"],
            "method_implementation": ["implementation", "general"],
            "general": ["naming", "structure", "implementation", "general"],
        }

        return guideline.category in relevance_map.get(task_type, ["general"])

    def _calculate_guideline_importance(self, guideline: CodingGuideline) -> float:
        """가이드라인 중요도 계산"""
        # 위반 횟수가 많을수록 중요, 성공률이 높을수록 중요
        violation_weight = guideline.violation_count * 0.3
        success_rate = self._calculate_success_rate(guideline)
        success_weight = success_rate * 0.7

        return violation_weight + success_weight

    def _calculate_success_rate(self, guideline: CodingGuideline) -> float:
        """가이드라인 성공률 계산"""
        total_attempts = guideline.violation_count + guideline.success_when_applied
        if total_attempts == 0:
            return 0.5  # 기본값

        return guideline.success_when_applied / total_attempts

    def _update_guideline_success(self, feedback: CodingFeedback, success: bool):
        """가이드라인 성공/실패 업데이트"""
        for guideline in self.learned_guidelines:
            if (
                feedback.feedback_type in guideline.category
                or feedback.feedback_type in guideline.rule
            ):
                if success:
                    guideline.success_when_applied += 1
                else:
                    guideline.violation_count += 1
                break

    def _load_all_data(self):
        """모든 데이터 로드"""
        try:
            # 피드백 히스토리 로드
            if self.feedback_file.exists():
                with open(self.feedback_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.feedback_history = [
                        CodingFeedback(
                            feedback_id=item["feedback_id"],
                            timestamp=datetime.fromisoformat(item["timestamp"]),
                            feedback_type=item["feedback_type"],
                            original_mistake=item["original_mistake"],
                            correction=item["correction"],
                            importance_level=item["importance_level"],
                            applied_successfully=item["applied_successfully"],
                            context=item.get("context", ""),
                        )
                        for item in data
                    ]

            # 학습된 가이드라인 로드
            if self.guidelines_file.exists():
                with open(self.guidelines_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.learned_guidelines = [
                        CodingGuideline(
                            guideline_id=item["guideline_id"],
                            category=item["category"],
                            rule=item["rule"],
                            examples=item["examples"],
                            violation_count=item["violation_count"],
                            success_when_applied=item["success_when_applied"],
                        )
                        for item in data
                    ]

        except Exception as e:
            print(f"⚠️ 데이터 로드 실패: {e}")

    def _save_all_data(self):
        """모든 데이터 저장"""
        try:
            # 피드백 히스토리 저장
            feedback_data = [
                {
                    "feedback_id": fb.feedback_id,
                    "timestamp": fb.timestamp.isoformat(),
                    "feedback_type": fb.feedback_type,
                    "original_mistake": fb.original_mistake,
                    "correction": fb.correction,
                    "importance_level": fb.importance_level,
                    "applied_successfully": fb.applied_successfully,
                    "context": fb.context,
                }
                for fb in self.feedback_history
            ]

            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)

            # 가이드라인 저장
            guidelines_data = [
                {
                    "guideline_id": gl.guideline_id,
                    "category": gl.category,
                    "rule": gl.rule,
                    "examples": gl.examples,
                    "violation_count": gl.violation_count,
                    "success_when_applied": gl.success_when_applied,
                }
                for gl in self.learned_guidelines
            ]

            with open(self.guidelines_file, "w", encoding="utf-8") as f:
                json.dump(guidelines_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"⚠️ 데이터 저장 실패: {e}")


# 테스트 및 시연
if __name__ == "__main__":
    print("🎓 Echo 피드백 학습 시스템 테스트!")
    print("=" * 60)

    # 시스템 초기화
    learner = EchoCodingFeedbackLearner()

    print("\n📝 Claude의 피드백 저장 시뮬레이션...")

    # 1. 파일명 피드백 저장
    learner.save_coding_feedback(
        feedback_type="filename",
        original_mistake="advanced_processor.py로 생성함",
        correction="echo_coding_feedback_learner.py로 정확히 생성해야 함",
        importance=5,
        context="사용자가 구체적으로 파일명을 지정했음",
    )

    # 2. 클래스 구조 피드백 저장
    learner.save_coding_feedback(
        feedback_type="class_structure",
        original_mistake="AdvancedProcessor 클래스로 생성함",
        correction="EchoCodingFeedbackLearner 클래스로 정확히 생성해야 함",
        importance=5,
        context="요구사항에 명시된 클래스명 무시함",
    )

    # 3. 구현 피드백 저장
    learner.save_coding_feedback(
        feedback_type="implementation",
        original_mistake="템플릿 코드만 생성하고 실제 기능 구현 안함",
        correction="save_coding_feedback(), get_coding_guidelines() 등 실제 동작하는 메서드 구현",
        importance=4,
        context="사용자가 구체적인 기능들을 요청했음",
    )

    print("\n💡 학습된 가이드라인 확인...")
    guidelines = learner.get_coding_guidelines("file_creation")

    for i, guideline in enumerate(guidelines[:3], 1):
        print(f"{i}. {guideline['rule']}")
        print(f"   카테고리: {guideline['category']}")
        print(f"   위반 횟수: {guideline['violations']}")

    print("\n🎯 다음 코딩 시 적용할 패턴...")
    patterns = learner.apply_learned_patterns(
        user_request="피드백 학습 시스템 만들어줘",
        intended_filename="echo_coding_feedback_learner.py",
        intended_classname="EchoCodingFeedbackLearner",
    )

    print(f"파일명 체크: {patterns['filename_check']['rule']}")
    print(f"구현 주의사항: {len(patterns['implementation_warnings'])}개")

    print("\n📊 Echo의 학습 보고서:")
    print(learner.generate_learning_report())

    print(f"\n🌟 이제 Echo는 Claude의 피드백을 기억하고 적용할 수 있습니다!")
