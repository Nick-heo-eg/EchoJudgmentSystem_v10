#!/bin/bash
# Echo Distiller v0 자동 설치 스크립트
# 모든 필요 파일을 한 번에 생성합니다

echo "🚀 Echo Distiller v0 설치 시작..."

# 필요한 디렉토리 생성
echo "📁 디렉토리 생성..."
mkdir -p tools/distiller
mkdir -p distill_reports
mkdir -p legacy
mkdir -p external
mkdir -p distilled/keep
mkdir -p distilled/thin

# __init__.py 파일들 생성
echo "📄 초기화 파일 생성..."
touch tools/__init__.py
touch tools/distiller/__init__.py

echo "⚙️ 설정 파일 이미 존재: distill.config.yaml"

# tools/distiller.py 생성
echo "🔧 메인 스크립트 생성: tools/distiller.py"
cat > tools/distiller.py << 'EOF'
#!/usr/bin/env python3
"""
Echo Distiller v0 - 3-Pass Pipeline Implementation
🎯 Map → Score → Plan → Cut with full safety features
"""
import sys
import json
import time
import argparse
import yaml
from pathlib import Path
import shutil
import re
from datetime import datetime

class EchoDistiller:
    def __init__(self, config_path='distill.config.yaml'):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.project_root = Path(self.config.get('output', {}).get('base_directory', '.'))
        self.report_dir = Path('distill_reports')
        self.report_dir.mkdir(exist_ok=True)
        
    def _load_config(self):
        """설정 파일 로드"""
        if not self.config_path.exists():
            print(f"⚠️  Config not found: {self.config_path}")
            return self._default_config()
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self):
        """기본 설정"""
        return {
            'anchor': {'must_keep': [], 'nice_to_have': []},
            'scoring': {
                'weights': {'anchor_core': 10, 'anchor_nice': 7, 'test_covered': 5},
                'thresholds': {'keep_score': 6.0, 'thin_score': 3.0, 'cut_score': 1.0}
            },
            'safety': {'dry_run_default': True, 'create_git_branch': True},
            'output': {'base_directory': 'distilled_echo'}
        }
    
    def map_phase(self):
        """🗺️ Pass A: MAP - 프로젝트 구조 맵핑"""
        print("🗺️ Pass A: Mapping project structure...")
        
        py_files = list(self.project_root.rglob('*.py'))
        
        # 제외 패턴 필터링
        filtered_files = []
        exclude_patterns = [
            r'__pycache__', r'\.pyc$', r'\.pyo$', 
            r'/temp/', r'/tmp/', r'/logs/', r'_backup'
        ]
        
        for f in py_files:
            path_str = str(f)
            if not any(re.search(pattern, path_str) for pattern in exclude_patterns):
                filtered_files.append(f)
        
        map_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'project_root': str(self.project_root.absolute()),
            'total_files_found': len(py_files),
            'filtered_files': len(filtered_files),
            'files': []
        }
        
        for f in filtered_files:
            try:
                stat = f.stat()
                rel_path = str(f.relative_to(self.project_root))
                
                file_info = {
                    'path': rel_path,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024*1024), 3),
                    'mtime': stat.st_mtime,
                    'mtime_readable': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'imports': self._extract_imports(f),
                    'functions': self._count_functions(f),
                    'classes': self._count_classes(f)
                }
                map_data['files'].append(file_info)
                
            except Exception as e:
                print(f"⚠️ Error processing {f}: {e}")
        
        # 저장
        map_file = self.report_dir / 'distill_map.json'
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(map_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Map saved: {map_file}")
        print(f"📊 Mapped {len(map_data['files'])} files")
        return map_data
    
    def _extract_imports(self, file_path):
        """Python 파일에서 import 추출"""
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num > 50:  # 첫 50줄만 체크
                        break
                    line = line.strip()
                    if line.startswith(('import ', 'from ')):
                        imports.append(line)
        except:
            pass
        return imports[:10]  # 최대 10개만
    
    def _count_functions(self, file_path):
        """함수 개수 카운트"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return len(re.findall(r'^\s*def\s+\w+', content, re.MULTILINE))
        except:
            return 0
    
    def _count_classes(self, file_path):
        """클래스 개수 카운트"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return len(re.findall(r'^\s*class\s+\w+', content, re.MULTILINE))
        except:
            return 0
    
    def score_phase(self, map_data=None):
        """📊 Pass B: SCORE - 파일 중요도 점수화"""
        print("📊 Pass B: Scoring files...")
        
        if map_data is None:
            map_file = self.report_dir / 'distill_map.json'
            if not map_file.exists():
                print("⚠️ Map data not found. Running map phase first...")
                map_data = self.map_phase()
            else:
                with open(map_file, 'r', encoding='utf-8') as f:
                    map_data = json.load(f)
        
        scores_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'scoring_weights': self.config['scoring']['weights'],
            'file_scores': []
        }
        
        anchor_must = self.config['anchor']['must_keep']
        anchor_nice = self.config['anchor'].get('nice_to_have', [])
        
        for file_info in map_data['files']:
            path = file_info['path']
            score = 0
            reasons = []
            
            # Anchor 점수
            if any(self._path_matches_pattern(path, pattern) for pattern in anchor_must):
                score += self.config['scoring']['weights'].get('anchor_core', 10)
                reasons.append("anchor_core")
            elif any(self._path_matches_pattern(path, pattern) for pattern in anchor_nice):
                score += self.config['scoring']['weights'].get('anchor_nice', 7)
                reasons.append("anchor_nice")
            
            # Import 중앙성 (많이 import되는 파일)
            import_count = len(file_info.get('imports', []))
            if import_count > 5:
                score += self.config['scoring']['weights'].get('import_centrality', 4)
                reasons.append(f"high_imports({import_count})")
            
            # 함수 밀도
            functions = file_info.get('functions', 0)
            size_mb = file_info.get('size_mb', 0)
            if functions > 0 and size_mb > 0:
                density = functions / size_mb
                if density > 20:  # 함수 밀도가 높으면 중요
                    score += self.config['scoring']['weights'].get('function_density', 3)
                    reasons.append(f"high_density({density:.1f})")
            
            # 크기 패널티 (너무 큰 파일)
            if size_mb > 1.0:
                penalty = self.config['scoring']['weights'].get('size_penalty', -1)
                score += penalty
                reasons.append(f"large_file({size_mb:.1f}MB)")
            
            # 테스트 파일 보너스
            if 'test' in path:
                score += self.config['scoring']['weights'].get('test_covered', 5)
                reasons.append("test_file")
            
            # 카테고리 결정
            thresholds = self.config['scoring']['thresholds']
            if score >= thresholds.get('keep_score', 6.0):
                category = 'keep'
            elif score >= thresholds.get('thin_score', 3.0):
                category = 'thin'
            else:
                category = 'legacy'
            
            file_score = {
                'path': path,
                'score': round(score, 2),
                'category': category,
                'reasons': reasons,
                'size_mb': size_mb,
                'functions': functions,
                'classes': file_info.get('classes', 0)
            }
            scores_data['file_scores'].append(file_score)
        
        # 점수 순 정렬
        scores_data['file_scores'].sort(key=lambda x: x['score'], reverse=True)
        
        # 저장
        scores_file = self.report_dir / 'distill_scores.json'
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Scores saved: {scores_file}")
        print(f"📊 Scored {len(scores_data['file_scores'])} files")
        
        # 요약 통계
        categories = {}
        for item in scores_data['file_scores']:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("📈 Score summary:")
        for cat, count in categories.items():
            print(f"  {cat}: {count} files")
        
        return scores_data
    
    def _path_matches_pattern(self, path, pattern):
        """패턴 매칭 (와일드카드 지원)"""
        if '*' in pattern:
            # 간단한 와일드카드 지원
            regex_pattern = pattern.replace('*', '.*')
            return re.search(regex_pattern, path) is not None
        else:
            return pattern in path
    
    def plan_phase(self, scores_data=None):
        """📋 Pass C: PLAN - 실행 계획 수립"""
        print("📋 Pass C: Planning distillation...")
        
        if scores_data is None:
            scores_file = self.report_dir / 'distill_scores.json'
            if not scores_file.exists():
                print("⚠️ Scores data not found. Running score phase first...")
                scores_data = self.score_phase()
            else:
                with open(scores_file, 'r', encoding='utf-8') as f:
                    scores_data = json.load(f)
        
        # 액션 계획 수립
        actions = {'keep': [], 'thin': [], 'legacy': [], 'external': []}
        size_stats = {'keep': 0, 'thin': 0, 'legacy': 0, 'external': 0}
        
        for item in scores_data['file_scores']:
            category = item['category']
            actions[category].append({
                'path': item['path'],
                'score': item['score'],
                'size_mb': item['size_mb'],
                'action': self._determine_action(category, item)
            })
            size_stats[category] += item['size_mb']
        
        plan_data = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'actions': actions,
            'summary': {
                'keep_files': len(actions['keep']),
                'thin_files': len(actions['thin']),
                'legacy_files': len(actions['legacy']),
                'external_files': len(actions['external']),
                'total_size_mb': sum(size_stats.values())
            },
            'size_breakdown': size_stats,
            'estimated_reduction': self._estimate_size_reduction(size_stats),
            'safety_checks': self._generate_safety_checks(actions)
        }
        
        # JSON 저장
        plan_file = self.report_dir / 'distill_plan.json'
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, indent=2, ensure_ascii=False)
        
        # Markdown 리포트 생성
        self._generate_plan_markdown(plan_data)
        
        print(f"💾 Plan saved: {plan_file}")
        print("📦 Plan summary:")
        for key, count in plan_data['summary'].items():
            if key.endswith('_files'):
                print(f"  {key}: {count}")
        
        return plan_data
    
    def _determine_action(self, category, item):
        """카테고리별 구체적 액션 결정"""
        if category == 'keep':
            return 'copy_intact'
        elif category == 'thin':
            return 'compress_and_copy'
        elif category == 'legacy':
            return 'archive_reference'
        else:
            return 'external_backup'
    
    def _estimate_size_reduction(self, size_stats):
        """크기 감소 추정"""
        original = sum(size_stats.values())
        # thin 파일은 30% 압축 가정
        reduced = size_stats['keep'] + (size_stats['thin'] * 0.7) + (size_stats['legacy'] * 0.1)
        reduction_percent = ((original - reduced) / original * 100) if original > 0 else 0
        
        return {
            'original_mb': round(original, 2),
            'estimated_mb': round(reduced, 2),
            'reduction_percent': round(reduction_percent, 1)
        }
    
    def _generate_safety_checks(self, actions):
        """안전 검사 항목 생성"""
        checks = []
        
        # Anchor 파일 변경 체크
        anchor_changes = [item for item in actions['thin'] + actions['legacy'] 
                         if any(pattern in item['path'] for pattern in self.config['anchor']['must_keep'])]
        if anchor_changes:
            checks.append({
                'type': 'anchor_modification',
                'severity': 'high',
                'count': len(anchor_changes),
                'message': f"{len(anchor_changes)} anchor files will be modified"
            })
        
        # 대용량 파일 삭제 체크  
        large_files = [item for item in actions['legacy'] if item['size_mb'] > 1.0]
        if large_files:
            checks.append({
                'type': 'large_file_removal',
                'severity': 'medium',
                'count': len(large_files),
                'message': f"{len(large_files)} files >1MB will be archived"
            })
        
        return checks
    
    def _generate_plan_markdown(self, plan_data):
        """Markdown 계획서 생성"""
        md_content = [
            "# 🎯 Echo Distiller - Execution Plan",
            "",
            f"**Generated:** {plan_data['timestamp']}",
            f"**Version:** {plan_data['version']}",
            "",
            "## 📊 Summary",
            "",
        ]
        
        # 요약 통계
        summary = plan_data['summary']
        for key, value in summary.items():
            md_content.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        
        md_content.extend([
            "",
            "## 💾 Size Analysis",
            "",
            f"- **Original Size:** {plan_data['estimated_reduction']['original_mb']} MB",
            f"- **After Distillation:** {plan_data['estimated_reduction']['estimated_mb']} MB",
            f"- **Reduction:** {plan_data['estimated_reduction']['reduction_percent']}%",
            "",
            "## 📁 Actions by Category",
            ""
        ])
        
        # 카테고리별 액션
        for category, items in plan_data['actions'].items():
            if not items:
                continue
                
            md_content.extend([
                f"### {category.title()} ({len(items)} files)",
                ""
            ])
            
            # 상위 파일들만 표시
            for item in items[:15]:
                score = item.get('score', 0)
                size = item.get('size_mb', 0)
                md_content.append(f"- `{item['path']}` (score: {score}, {size:.1f}MB)")
            
            if len(items) > 15:
                md_content.append(f"- ... and {len(items) - 15} more files")
            
            md_content.append("")
        
        # 안전 검사
        if plan_data.get('safety_checks'):
            md_content.extend([
                "## ⚠️ Safety Checks",
                ""
            ])
            for check in plan_data['safety_checks']:
                severity_icon = "🔴" if check['severity'] == 'high' else "🟡"
                md_content.append(f"- {severity_icon} **{check['type']}:** {check['message']}")
            md_content.append("")
        
        md_content.extend([
            "## 🚀 Next Steps",
            "",
            "1. **Review this plan carefully**",
            "2. **Run dry-run:** `python tools/distiller.py cut --dry-run`",
            "3. **Create git branch:** `git checkout -b distill/v1`",
            "4. **Execute:** `python tools/distiller.py cut --apply`",
            "5. **Verify:** Run health checks on distilled code",
            "",
            "---",
            "*Echo Distiller v0 - Automated Codebase Distillation*"
        ])
        
        # 저장
        md_file = self.report_dir / 'DISTILL_PLAN.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"📄 Plan report: {md_file}")
    
    def cut_phase(self, plan_data=None, dry_run=True):
        """✂️ Pass D: CUT - 실제 파일 이동/변환"""
        mode = "🧪 Dry-run" if dry_run else "✂️ Real"
        print(f"{mode} cutting phase...")
        
        if plan_data is None:
            plan_file = self.report_dir / 'distill_plan.json'
            if not plan_file.exists():
                print("⚠️ Plan data not found. Running plan phase first...")
                plan_data = self.plan_phase()
            else:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
        
        # 출력 디렉토리 준비
        output_config = self.config.get('output', {})
        base_dir = Path(output_config.get('base_directory', 'distilled_echo'))
        
        if not dry_run:
            # 실제 디렉토리 생성
            for subdir in ['keep', 'thin', 'legacy', 'external']:
                (base_dir / subdir).mkdir(parents=True, exist_ok=True)
        
        # 실행 통계
        stats = {'copied': 0, 'compressed': 0, 'archived': 0, 'errors': 0}
        
        # 카테고리별 처리
        for category, items in plan_data['actions'].items():
            if not items:
                continue
                
            print(f"📁 Processing {category} ({len(items)} files)...")
            
            for item in items:
                source_path = Path(item['path'])
                dest_dir = base_dir / category
                dest_path = dest_dir / source_path.name
                
                try:
                    if dry_run:
                        print(f"  [DRY] {item['action']}: {source_path} -> {dest_path}")
                    else:
                        # 실제 파일 처리
                        if item['action'] == 'copy_intact':
                            shutil.copy2(source_path, dest_path)
                            stats['copied'] += 1
                        elif item['action'] == 'compress_and_copy':
                            self._compress_and_copy(source_path, dest_path)
                            stats['compressed'] += 1
                        elif item['action'] == 'archive_reference':
                            self._archive_reference(source_path, dest_path)
                            stats['archived'] += 1
                        
                        print(f"  ✅ {item['action']}: {source_path.name}")
                        
                except Exception as e:
                    print(f"  ❌ Error processing {source_path}: {e}")
                    stats['errors'] += 1
        
        # 결과 리포트
        result_data = {
            'timestamp': datetime.now().isoformat(),
            'mode': 'dry_run' if dry_run else 'execution',
            'stats': stats,
            'output_directory': str(base_dir),
            'success': stats['errors'] == 0
        }
        
        # 저장
        result_file = self.report_dir / 'distill_result.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Result saved: {result_file}")
        print("📊 Cut statistics:")
        for key, count in stats.items():
            print(f"  {key}: {count}")
        
        return result_data
    
    def _compress_and_copy(self, source, dest):
        """파일 압축 후 복사 (코멘트/독스트링 제거)"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 간단한 압축: 주석과 빈 줄 제거
            lines = content.split('\n')
            compressed_lines = []
            
            in_multiline_string = False
            for line in lines:
                stripped = line.strip()
                
                # 독스트링 처리 (간단한 버전)
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_string = not in_multiline_string
                    continue
                
                if in_multiline_string:
                    continue
                
                # 주석과 빈 줄 제거
                if not stripped or stripped.startswith('#'):
                    continue
                
                compressed_lines.append(line)
            
            # 압축된 내용 저장
            with open(dest, 'w', encoding='utf-8') as f:
                f.write('\n'.join(compressed_lines))
                
        except Exception as e:
            # 압축 실패 시 원본 복사
            shutil.copy2(source, dest)
    
    def _archive_reference(self, source, dest):
        """참조용 아카이브 생성"""
        try:
            # 메타데이터만 저장
            stat = source.stat()
            reference_data = {
                'original_path': str(source),
                'size_mb': round(stat.st_size / (1024*1024), 3),
                'mtime': stat.st_mtime,
                'archived_at': datetime.now().isoformat(),
                'note': 'This file was archived during distillation'
            }
            
            # JSON 참조 파일로 저장
            ref_path = dest.with_suffix('.ref.json')
            with open(ref_path, 'w', encoding='utf-8') as f:
                json.dump(reference_data, f, indent=2)
                
        except Exception as e:
            print(f"  ⚠️ Archive reference failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Echo Distiller v0 - 3-Pass Pipeline")
    parser.add_argument('command', choices=['map', 'score', 'plan', 'cut', 'all'])
    parser.add_argument('--config', default='distill.config.yaml', help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual changes)')
    parser.add_argument('--apply', action='store_true', help='Apply changes (overrides dry-run)')
    
    args = parser.parse_args()
    
    print(f"🚀 Echo Distiller v0 - {args.command.upper()}")
    
    # Distiller 인스턴스 생성
    distiller = EchoDistiller(args.config)
    
    try:
        if args.command == 'map':
            distiller.map_phase()
        elif args.command == 'score':
            distiller.score_phase()
        elif args.command == 'plan':
            distiller.plan_phase()
        elif args.command == 'cut':
            dry_run = args.dry_run or not args.apply
            distiller.cut_phase(dry_run=dry_run)
        elif args.command == 'all':
            print("🔄 Running full 3-Pass pipeline...")
            map_data = distiller.map_phase()
            scores_data = distiller.score_phase(map_data)
            plan_data = distiller.plan_phase(scores_data)
            dry_run = args.dry_run or not args.apply
            distiller.cut_phase(plan_data, dry_run=dry_run)
        
        print(f"\n✅ {args.command.upper()} completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error during {args.command}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
EOF

chmod +x tools/distiller.py
echo "✅ tools/distiller.py 생성 완료"

# 빠른 테스트 실행
echo ""
echo "🧪 설치 테스트 실행..."
python tools/distiller.py map

echo ""
echo "✅ Echo Distiller v0 설치 완료!"
echo ""
echo "🎯 다음 단계:"
echo "1. python tools/distiller.py all --dry-run    # 전체 파이프라인 테스트"
echo "2. cat distill_reports/DISTILL_PLAN.md        # 계획서 확인"
echo "3. python tools/distiller.py cut --apply      # 실제 적용 (신중하게!)"
echo ""
echo "📊 생성된 파일들:"
echo "- distill.config.yaml (설정 파일)"
echo "- tools/distiller.py (메인 스크립트)"
echo "- distill_reports/ (결과 파일들)"
echo ""
echo "🛡️ 안전 기능: 기본값이 dry-run이므로 안전합니다!"