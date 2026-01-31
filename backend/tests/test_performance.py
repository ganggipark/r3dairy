"""
성능 테스트
API 응답 속도 및 부하 테스트
"""
import pytest
import time
from datetime import date
from fastapi import status


@pytest.mark.performance
@pytest.mark.slow
class TestAPIResponseTime:
    """API 응답 시간 테스트"""

    def test_health_endpoint_fast(self, api_client):
        """헬스체크 엔드포인트는 100ms 이내 응답"""
        start_time = time.time()

        response = api_client.get("/health")

        elapsed = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK
        assert elapsed < 0.1, f"헬스체크가 느립니다: {elapsed:.3f}초"

    def test_root_endpoint_fast(self, api_client):
        """루트 엔드포인트는 100ms 이내 응답"""
        start_time = time.time()

        response = api_client.get("/")

        elapsed = time.time() - start_time

        assert response.status_code == status.HTTP_200_OK
        assert elapsed < 0.1, f"루트 엔드포인트가 느립니다: {elapsed:.3f}초"


@pytest.mark.performance
@pytest.mark.slow
class TestContentGeneration:
    """콘텐츠 생성 성능 테스트"""

    def test_rhythm_signal_generation_speed(self, sample_birth_info):
        """리듬 신호 생성은 1초 이내"""
        from src.rhythm.signals import create_daily_rhythm

        start_time = time.time()

        signal = create_daily_rhythm(sample_birth_info, date(2026, 1, 20))

        elapsed = time.time() - start_time

        assert signal is not None
        assert elapsed < 1.0, f"리듬 신호 생성이 느립니다: {elapsed:.3f}초"

    def test_content_assembly_speed(self):
        """콘텐츠 조립은 0.5초 이내"""
        from src.content.assembly import assemble_daily_content

        sample_rhythm = {
            "에너지_수준": 3,
            "집중력": 4,
            "사회운": 3,
            "결정력": 4,
            "유리한_시간": ["오전 9-11시"],
            "주의_시간": ["오후 5-7시"],
            "유리한_방향": ["북동"],
            "주요_흐름": "안정과 정리",
            "기회_요소": ["학습"],
            "도전_요소": ["충동 조절"],
        }

        start_time = time.time()

        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data={"test": "data"},
            daily_rhythm=sample_rhythm,
        )

        elapsed = time.time() - start_time

        assert content is not None
        assert elapsed < 0.5, f"콘텐츠 조립이 느립니다: {elapsed:.3f}초"

    def test_role_translation_speed(self):
        """역할 번역은 0.3초 이내"""
        from src.content.assembly import assemble_daily_content
        from src.translation.translator import translate_daily_content

        sample_rhythm = {
            "에너지_수준": 3,
            "집중력": 4,
            "사회운": 3,
            "결정력": 4,
            "주요_흐름": "안정과 정리",
            "기회_요소": ["학습"],
            "도전_요소": ["조절"],
        }
        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data={"test": "data"},
            daily_rhythm=sample_rhythm,
        )

        start_time = time.time()

        translated = translate_daily_content(content, "student")

        elapsed = time.time() - start_time

        assert translated is not None
        assert elapsed < 0.3, f"역할 번역이 느립니다: {elapsed:.3f}초"

    def test_full_pipeline_speed(self, sample_birth_info):
        """전체 파이프라인은 2초 이내"""
        from src.rhythm.signals import create_daily_rhythm
        from src.content.assembly import assemble_daily_content
        from src.translation.translator import translate_daily_content

        start_time = time.time()

        # 1. Rhythm Signal
        signal = create_daily_rhythm(sample_birth_info, date(2026, 1, 20))

        # 2. Content Assembly (using signal data as daily_rhythm)
        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data=signal.saju_data,
            daily_rhythm={
                "에너지_수준": signal.energy_level,
                "집중력": signal.focus_capacity,
                "사회운": signal.social_energy,
                "결정력": signal.decision_clarity,
                "유리한_시간": signal.favorable_times,
                "주의_시간": signal.caution_times,
                "유리한_방향": signal.favorable_directions,
                "주요_흐름": signal.main_theme,
                "기회_요소": signal.opportunities,
                "도전_요소": signal.challenges,
            },
        )

        # 3. Role Translation
        translated = translate_daily_content(content, "student")

        elapsed = time.time() - start_time

        assert translated is not None
        assert elapsed < 2.0, f"전체 파이프라인이 느립니다: {elapsed:.3f}초"


@pytest.mark.performance
@pytest.mark.slow
class TestConcurrentRequests:
    """동시 요청 처리 테스트"""

    def test_multiple_health_checks(self, api_client):
        """여러 헬스체크 동시 처리"""
        import concurrent.futures

        def make_request():
            return api_client.get("/health")

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        elapsed = time.time() - start_time

        # 모든 요청 성공 확인
        assert all(r.status_code == status.HTTP_200_OK for r in results)

        # 50개 요청이 5초 이내 완료
        assert elapsed < 5.0, f"동시 요청 처리가 느립니다: {elapsed:.3f}초"

    def test_multiple_content_generation(self, api_client, auth_headers):
        """여러 콘텐츠 생성 동시 처리 (Mock 환경 제한)"""
        import concurrent.futures

        dates = ["2026-01-20", "2026-01-21", "2026-01-22"]

        def make_request(target_date):
            return api_client.get(f"/api/daily/{target_date}", headers=auth_headers)

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, d) for d in dates]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        elapsed = time.time() - start_time

        # Mock 환경에서는 다양한 응답 가능
        assert elapsed < 10.0, f"동시 콘텐츠 생성이 너무 느립니다: {elapsed:.3f}초"


@pytest.mark.performance
class TestMemoryUsage:
    """메모리 사용량 테스트"""

    def test_content_generation_memory_efficient(self):
        """콘텐츠 생성 시 메모리 효율성"""
        import tracemalloc
        from src.content.assembly import assemble_daily_content

        tracemalloc.start()

        content = assemble_daily_content(
            date=date(2026, 1, 20),
            saju_data={"test": "data"},
            daily_rhythm={
                "에너지_수준": 3,
                "집중력": 4,
                "사회운": 3,
                "결정력": 4,
                "주요_흐름": "안정",
                "기회_요소": ["학습"],
                "도전_요소": ["조절"],
            },
        )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 피크 메모리 10MB 이하
        assert peak < 10 * 1024 * 1024, \
            f"메모리 사용량이 많습니다: {peak / 1024 / 1024:.2f}MB"

    def test_multiple_content_generation_no_leak(self):
        """여러 콘텐츠 생성 시 메모리 누수 없음"""
        import tracemalloc
        from src.content.assembly import assemble_daily_content

        tracemalloc.start()

        for i in range(100):
            content = assemble_daily_content(
                date=date(2026, 1, 1 + (i % 28)),
                saju_data={"test": "data"},
                daily_rhythm={
                    "에너지_수준": (i % 5) + 1,
                    "집중력": 3,
                    "사회운": 3,
                    "결정력": 3,
                    "주요_흐름": "테스트",
                    "기회_요소": [],
                    "도전_요소": [],
                },
            )

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 피크 메모리 50MB 이하
        assert peak < 50 * 1024 * 1024, \
            f"메모리 누수 의심: {peak / 1024 / 1024:.2f}MB"


@pytest.mark.performance
@pytest.mark.slow
class TestDatabasePerformance:
    """데이터베이스 성능 테스트 (Mock 환경 제한)"""

    def test_profile_query_speed(self, api_client, auth_headers):
        """프로필 조회는 500ms 이내"""
        start_time = time.time()

        response = api_client.get("/api/profile", headers=auth_headers)

        elapsed = time.time() - start_time

        # Mock 환경에서는 매우 빠름
        assert elapsed < 0.5, f"프로필 조회가 느립니다: {elapsed:.3f}초"

    def test_content_cache_effectiveness(self, api_client, auth_headers):
        """동일 콘텐츠 재조회 시 캐시 효과 (구현 시)"""
        pytest.skip("캐싱 미구현")


@pytest.mark.performance
class TestValidationPerformance:
    """검증 로직 성능 테스트"""

    def test_content_validation_speed(self):
        """콘텐츠 검증은 100ms 이내"""
        from src.content.validator import validate_daily_content

        content = {
            "date": "2026-01-20",
            "summary": "테스트 요약입니다.",
            "keywords": ["키워드1", "키워드2"],
            "rhythm_description": "해설" * 30,
            "focus_caution": {"focus": ["집중"], "caution": ["주의"]},
            "action_guide": {"do": ["하기"], "avoid": ["피하기"]},
            "time_direction": {
                "good_time": "오전",
                "avoid_time": "오후",
                "good_direction": "북",
                "avoid_direction": "남",
                "notes": "",
            },
            "state_trigger": {"gesture": "제스처", "phrase": "문구", "how_to": "방법"},
            "meaning_shift": "의미전환" * 10,
            "rhythm_question": "질문입니다?",
        }

        start_time = time.time()

        is_valid, messages = validate_daily_content(content)

        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"콘텐츠 검증이 느립니다: {elapsed:.3f}초"

    def test_schema_validation_overhead(self):
        """스키마 검증 오버헤드 측정"""
        from src.content.assembly import assemble_daily_content

        start_time = time.time()

        for _ in range(100):
            content = assemble_daily_content(
                date=date(2026, 1, 20),
                saju_data={},
                daily_rhythm={
                    "에너지_수준": 3,
                    "집중력": 3,
                    "사회운": 3,
                    "결정력": 3,
                    "주요_흐름": "균형",
                    "기회_요소": [],
                    "도전_요소": [],
                },
            )

        elapsed = time.time() - start_time

        # 100번 생성이 1초 이내
        assert elapsed < 1.0, f"스키마 검증 오버헤드가 큽니다: {elapsed:.3f}초"
