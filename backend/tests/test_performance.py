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

    def test_content_assembly_speed(self, sample_rhythm_signal):
        """콘텐츠 조립은 0.5초 이내"""
        from src.content.assembly import create_daily_content

        start_time = time.time()

        content = create_daily_content(sample_rhythm_signal)

        elapsed = time.time() - start_time

        assert content is not None
        assert elapsed < 0.5, f"콘텐츠 조립이 느립니다: {elapsed:.3f}초"

    def test_role_translation_speed(self, sample_daily_content):
        """역할 번역은 0.3초 이내"""
        from src.translation.translator import RoleTranslator, Role

        translator = RoleTranslator()

        start_time = time.time()

        translated = translator.translate(sample_daily_content, Role.STUDENT)

        elapsed = time.time() - start_time

        assert translated is not None
        assert elapsed < 0.3, f"역할 번역이 느립니다: {elapsed:.3f}초"

    def test_full_pipeline_speed(self, sample_birth_info):
        """전체 파이프라인은 2초 이내"""
        from src.rhythm.signals import create_daily_rhythm
        from src.content.assembly import create_daily_content
        from src.translation.translator import RoleTranslator, Role

        start_time = time.time()

        # 1. Rhythm Signal
        signal = create_daily_rhythm(sample_birth_info, date(2026, 1, 20))

        # 2. Content Assembly
        content = create_daily_content(signal)

        # 3. Role Translation
        translator = RoleTranslator()
        translated = translator.translate(content, Role.STUDENT)

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
        # 실제 환경에서는 성능 측정 중요
        assert elapsed < 10.0, f"동시 콘텐츠 생성이 너무 느립니다: {elapsed:.3f}초"


@pytest.mark.performance
class TestMemoryUsage:
    """메모리 사용량 테스트"""

    def test_content_generation_memory_efficient(self, sample_birth_info):
        """콘텐츠 생성 시 메모리 효율성"""
        import tracemalloc
        from src.rhythm.signals import create_daily_rhythm
        from src.content.assembly import create_daily_content

        tracemalloc.start()

        # 콘텐츠 생성
        signal = create_daily_rhythm(sample_birth_info, date(2026, 1, 20))
        content = create_daily_content(signal)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 피크 메모리 10MB 이하
        assert peak < 10 * 1024 * 1024, \
            f"메모리 사용량이 많습니다: {peak / 1024 / 1024:.2f}MB"

    def test_multiple_content_generation_no_leak(self, sample_birth_info):
        """여러 콘텐츠 생성 시 메모리 누수 없음"""
        import tracemalloc
        from src.rhythm.signals import create_daily_rhythm
        from src.content.assembly import create_daily_content

        tracemalloc.start()

        # 100번 생성
        for i in range(100):
            target_date = date(2026, 1, 1 + (i % 28))
            signal = create_daily_rhythm(sample_birth_info, target_date)
            content = create_daily_content(signal)

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
        # 첫 요청
        start_time1 = time.time()
        response1 = api_client.get("/api/daily/2026-01-20", headers=auth_headers)
        elapsed1 = time.time() - start_time1

        # 두 번째 요청 (캐시 활용)
        start_time2 = time.time()
        response2 = api_client.get("/api/daily/2026-01-20", headers=auth_headers)
        elapsed2 = time.time() - start_time2

        # 캐시가 구현되면 두 번째 요청이 더 빨라야 함
        # Mock 환경에서는 스킵
        pytest.skip("캐싱 미구현")


@pytest.mark.performance
class TestValidationPerformance:
    """검증 로직 성능 테스트"""

    def test_content_validation_speed(self, sample_daily_content):
        """콘텐츠 검증은 100ms 이내"""
        from src.content.validator import ContentValidator

        try:
            validator = ContentValidator()
        except FileNotFoundError:
            pytest.skip("DAILY_CONTENT_SCHEMA.json 파일 없음")

        start_time = time.time()

        is_valid, messages = validator.validate_daily_content(sample_daily_content)

        elapsed = time.time() - start_time

        assert elapsed < 0.1, f"콘텐츠 검증이 느립니다: {elapsed:.3f}초"

    def test_schema_validation_overhead(self):
        """스키마 검증 오버헤드 측정"""
        from src.content.models import DailyContent
        from datetime import date

        # Pydantic 검증 속도 테스트
        start_time = time.time()

        for _ in range(100):
            content = DailyContent(
                date=date(2026, 1, 20),
                summary="테스트 요약입니다.",
                keywords=["키워드1", "키워드2"],
                rhythm_description="테스트 해설입니다." * 10,
                focus_caution={"focus": ["집중"], "caution": ["주의"]},
                action_guide={"do": ["하기"], "avoid": ["피하기"]},
                time_direction={
                    "good_time": "오전",
                    "avoid_time": "오후",
                    "good_direction": "북",
                    "avoid_direction": "남"
                },
                state_trigger={
                    "gesture": "제스처",
                    "phrase": "문구",
                    "how_to": "방법"
                },
                meaning_shift="의미 전환입니다." * 5,
                rhythm_question="질문입니다?"
            )

        elapsed = time.time() - start_time

        # 100번 생성이 1초 이내
        assert elapsed < 1.0, f"스키마 검증 오버헤드가 큽니다: {elapsed:.3f}초"


# ============================================================================
# 성능 벤치마크 기준
# ============================================================================
"""
성능 목표:

1. API 응답 시간:
   - 헬스체크: < 100ms
   - 프로필 조회: < 500ms
   - 일간 콘텐츠 생성: < 2000ms (전체 파이프라인)
   - PDF 생성: < 5000ms

2. 처리량:
   - 동시 요청 50개: < 5초
   - 콘텐츠 생성 100회: < 200초

3. 메모리:
   - 단일 콘텐츠 생성: < 10MB
   - 100회 생성: < 50MB (메모리 누수 없음)

실행 방법:
   pytest tests/test_performance.py -v -m performance -s
   pytest tests/test_performance.py -v -m "performance and slow"

프로파일링:
   python -m cProfile -o profile.stats -m pytest tests/test_performance.py
   python -m pstats profile.stats
"""
