"""Smoke tests for arbitrage_api scrapers.

Run: PYTHONPATH=. python -m pytest tests/test_scrapers.py -v
"""

import pytest


def test_import_all_scrapers():
    """Verify all scraper modules import without errors."""
    modules = [
        "scrapers.base_scraper",
        "scrapers.china_trends_aggregator",
        "scrapers.zhihu",
        "scrapers.douyin",
        "scrapers.bilibili",
        "scrapers.toutiao",
        "scrapers.baidu_api",
        "scrapers.weibo_api",
    ]
    for mod_name in modules:
        __import__(mod_name)


def test_import_core():
    """Verify core modules import."""
    import core.database
    from core.database import RawTrend, CleanTrend, heat_to_level
    assert heat_to_level(0) == "normal"
    assert heat_to_level(50000) == "trending"   # 10000-99999
    assert heat_to_level(200000) == "hot"        # 100000-499999
    assert heat_to_level(600000) == "top"        # 500000-999999
    assert heat_to_level(2000000) == "viral"      # >= 1000000


def test_database_schema():
    """Verify database tables exist."""
    from core.database import RawTrend, CleanTrend, raw_engine, clean_engine
    from sqlmodel import Session, select

    with Session(raw_engine) as s:
        count = s.exec(select(RawTrend)).all()
        assert len(count) >= 0  # table exists

    with Session(clean_engine) as s:
        count = s.exec(select(CleanTrend)).all()
        assert len(count) >= 0  # table exists


def test_data_integrity():
    """Verify raw and clean data are consistent."""
    from core.database import RawTrend, CleanTrend, raw_engine, clean_engine
    from sqlmodel import Session, select

    with Session(raw_engine) as rs, Session(clean_engine) as cs:
        raw_count = rs.exec(select(RawTrend)).all()
        clean_count = cs.exec(select(CleanTrend)).all()
        # Clean <= Raw is expected (some items may fail enrichment)
        assert len(clean_count) <= len(raw_count) + 5  # small buffer
        # Should have data
        assert len(raw_count) > 0, "Database has no raw data!"


def test_heat_to_level_boundaries():
    """Verify heat_to_level classification boundaries."""
    from core.database import heat_to_level

    assert heat_to_level(0) == "normal"
    assert heat_to_level(9999) == "normal"
    assert heat_to_level(10000) == "trending"
    assert heat_to_level(99999) == "trending"
    assert heat_to_level(100000) == "hot"
    assert heat_to_level(499999) == "hot"
    assert heat_to_level(500000) == "top"
    assert heat_to_level(999999) == "top"
    assert heat_to_level(1000000) == "viral"
    assert heat_to_level(999999999) == "viral"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
