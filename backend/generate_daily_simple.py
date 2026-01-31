#!/usr/bin/env python3
"""
일반인용 일간 콘텐츠 생성 (간소화 버전)
"""

import json
import subprocess
import sys
from pathlib import Path

def generate_simple_content():
    """간소화된 일간 콘텐츠 생성"""

    # 파일 경로
    prompt_file = Path('prompts/daily_content_simple.txt')
    energy_file = Path('output/today_energy_simple.json')
    time_file = Path('output/today_time_direction_simple.json')
    output_file = Path('daily/2026-01-31_simple.json')

    # 프롬프트 로드
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # 데이터 로드
    with open(energy_file, 'r', encoding='utf-8') as f:
        energy_data = json.load(f)

    with open(time_file, 'r', encoding='utf-8') as f:
        time_data = json.load(f)

    # 전체 프롬프트 구성
    full_prompt = f"""{prompt}

# INPUT DATA

## today_energy.json
```json
{json.dumps(energy_data, ensure_ascii=False, indent=2)}
```

## today_time_direction.json
```json
{json.dumps(time_data, ensure_ascii=False, indent=2)}
```

NOW GENERATE JSON (JSON만 출력, 설명 제외):
"""

    print("Claude CLI로 콘텐츠 생성 중...")
    print(f"   - 입력: {energy_file}, {time_file}")
    print(f"   - 출력: {output_file}")

    try:
        # Claude CLI 실행
        result = subprocess.run(
            ['claude', '--dangerously-skip-permissions'],
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )

        if result.returncode != 0:
            print(f"❌ Claude CLI 에러:\n{result.stderr}")
            return False

        output = result.stdout.strip()

        # JSON 추출
        if '```json' in output:
            output = output.split('```json')[1].split('```')[0]
        elif '```' in output:
            output = output.split('```')[1].split('```')[0]

        output = output.strip()

        # JSON 파싱
        content = json.loads(output)

        # 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        print(f"[OK] 생성 완료!")
        print(f"   - 총 {len(content)}개 키 생성됨")

        # 주요 섹션 확인
        if 'summary' in content:
            print(f"   - 요약: {content['summary'][:50]}...")
        if 'keywords' in content:
            print(f"   - 키워드: {', '.join(content['keywords'][:5])}...")

        return True

    except subprocess.TimeoutExpired:
        print("[ERROR] 타임아웃 (120초 초과)")
        return False
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 에러: {e}")
        print(f"   출력:\n{output[:500]}")
        return False
    except Exception as e:
        print(f"[ERROR] 에러: {e}")
        return False

if __name__ == '__main__':
    success = generate_simple_content()
    sys.exit(0 if success else 1)
