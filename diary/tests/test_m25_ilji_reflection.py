"""M25: 일진통변 + 신살 + 자기성찰 질문."""
from datetime import date, timedelta

from diary.models import SajuInput, DailyContent
from diary.saju import calculate_saju, get_daily_pillar


def test_get_daily_pillar():
    """양력 날짜로 일주 추출."""
    gan, ji = get_daily_pillar(date(2026, 5, 15))
    assert gan in {"갑","을","병","정","무","기","경","신","임","계"}
    assert ji in {"자","축","인","묘","진","사","오","미","신","유","술","해"}


def test_get_daily_pillar_60_cycle():
    """60일 차이 = 같은 일주."""
    g1, j1 = get_daily_pillar(date(2026, 1, 1))
    g2, j2 = get_daily_pillar(date(2026, 1, 1) + timedelta(days=60))
    assert g1 == g2 and j1 == j2


def test_get_daily_pillar_caches():
    """lru_cache 두 번째 호출은 동일 결과 (캐시 동작)."""
    a = get_daily_pillar(date(2026, 5, 15))
    b = get_daily_pillar(date(2026, 5, 15))
    assert a == b


def test_ilji_relation_chong():
    """본인 병오 vs 오늘 병자 → 자오충."""
    from diary.content import _compute_ilji_relation
    r = _compute_ilji_relation("병", "오", "병", "자")
    assert any("충" in s for s in r["relations"])
    assert r["today_pillar"] == "병자"
    assert r["my_pillar"] == "병오"


def test_ilji_relation_yukhap():
    """본인 갑인 vs 오늘 을해 → 인해 육합."""
    from diary.content import _compute_ilji_relation
    r = _compute_ilji_relation("갑", "인", "을", "해")
    assert any("합" in s for s in r["relations"])


def test_ilji_relation_bokeum():
    """같은 일지 → 복음."""
    from diary.content import _compute_ilji_relation
    r = _compute_ilji_relation("병", "오", "정", "오")
    assert any("복음" in s for s in r["relations"])


def test_sinsal_cheoneul_guiin():
    """병일+해/유 → 천을귀인."""
    from diary.content import _extract_sinsal_alerts
    alerts = _extract_sinsal_alerts("병", "오", "해")
    assert any("천을귀인" in a for a in alerts)


def test_sinsal_munchang():
    """갑일+사 → 문창귀인."""
    from diary.content import _extract_sinsal_alerts
    alerts = _extract_sinsal_alerts("갑", "오", "사")
    assert any("문창귀인" in a for a in alerts)


def test_sinsal_dohwa_yeokma():
    """일지 인오술국 → 도화=묘, 역마=신."""
    from diary.content import _extract_sinsal_alerts
    dohwa = _extract_sinsal_alerts("병", "오", "묘")
    yeokma = _extract_sinsal_alerts("병", "오", "신")
    assert any("도화" in a for a in dohwa)
    assert any("역마" in a for a in yeokma)


def test_sinsal_empty_for_neutral_day():
    """기준 외 지지면 alerts 비어 있음."""
    from diary.content import _extract_sinsal_alerts
    # 병일은 천을귀인=유/해, 문창=신, 도화(인오술)=묘, 역마=신.
    # 진(辰)은 어디에도 속하지 않음.
    alerts = _extract_sinsal_alerts("병", "오", "진")
    assert alerts == []


def test_daily_content_m25_fields():
    """DailyContent에 M25 필드 정의."""
    dc = DailyContent(
        date="2026-05-15",
        lucky_color="청록색", lucky_direction="동", lucky_time="오전 3시–5시",
        daily_summary="x"*100, daily_focus="x"*60, daily_caution="x"*60,
        mindfulness="x"*100, right_page_hint="x"*8,
        recommended_actions=["a"*5, "b"*5, "c"*5],
        things_to_avoid=["x"*3, "y"*3],
        ilji_pillar="병자",
        ilji_relation="본인 병오 vs 오늘 병자 자오충 — 변동의 날",
        sinsal_alerts=["천을귀인 발동", "문창귀인 활성"],
        reflection_questions=["질문1?", "질문2?", "질문3?"],
    )
    assert dc.ilji_pillar == "병자"
    assert len(dc.sinsal_alerts) == 2
    assert len(dc.reflection_questions) == 3


def test_park_junsoo_ilji_2026_05_15():
    """박준수(병오일) 5/15의 일진 추출 + 관계 계산."""
    from diary.content import _compute_ilji_relation
    today_gan, today_ji = get_daily_pillar(date(2026, 5, 15))
    r = _compute_ilji_relation("병", "오", today_gan, today_ji)
    assert r["today_pillar"]
    assert r["my_pillar"] == "병오"
