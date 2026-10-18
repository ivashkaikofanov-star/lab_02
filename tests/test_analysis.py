from datetime import datetime

from streamstats.analysis import init_stats, update_stat


def test_init_stats():
    """Проверка, что пустая статистика создается правильно."""
    stats = init_stats()
    assert stats["total"] == 0
    assert stats["by_source"] == {}
    assert stats["skipped"] == 0
    assert stats["first_timestamp"] is None
    assert stats["last_timestamp"] is None
    assert (set(stats["by_level"].keys()) ==
            {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
    assert all(count == 0 for count in stats["by_level"].values())


def test_update_stat_total_and_levels():
    """Проверка обновления общего счетчика и уровней."""
    stats = init_stats()
    event_1 = {
        "timestamp": datetime.fromisoformat("2000-01-23T05:04:36+05:00"),
        "level": "INFO", "source": "api", "message": "Go"
    }
    event_2 = {
        "timestamp": datetime.fromisoformat("2000-07-15T20:16:00-05:00"),
        "level": "ERROR", "source": "db", "message": "Failed"
    }
    stats = update_stat(event_1, stats)
    stats = update_stat(event_2, stats)
    assert stats["total"] == 2
    assert stats["by_level"]["INFO"] == 1
    assert stats["by_level"]["ERROR"] == 1
    assert stats["by_level"]["DEBUG"] == 0
    assert stats["by_level"]["WARNING"] == 0
    assert stats["by_level"]["CRITICAL"] == 0


def test_update_stat_sources_and_errors():
    """Проверка двойного счетчика источников (total и error)."""
    stats = init_stats()
    event_1 = {
        "timestamp": datetime.fromisoformat("2008-09-17T00:00:30+00:00"),
        "level": "INFO", "source": "api", "message": "Happy birthday to me"
    }
    event_2 = {
        "timestamp": datetime.fromisoformat("2010-12-29T22:00:36-09:00"),
        "level": "CRITICAL", "source": "api", "message": "New Year is coming soon"
    }
    event_3 = {
        "timestamp": datetime.fromisoformat("1999-01-01T23:59:59+00:00"),
        "level": "WARNING", "source": "db", "message": ""
    }
    stats = update_stat(event_1, stats)
    stats = update_stat(event_2, stats)
    stats = update_stat(event_3, stats)
    assert stats["by_source"]["api"]["total"] == 2
    assert stats["by_source"]["api"]["error"] == 1
    assert stats["by_source"]["db"]["total"] == 1
    assert stats["by_source"]["db"]["error"] == 0


def test_update_stat_timestamps():
    """Проверка, что first_timestamp и last_timestamp обновляются верно."""
    stats = init_stats()
    event_1 = {
        "timestamp": datetime.fromisoformat("2008-10-02T22:10:22+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    event_2 = {
        "timestamp": datetime.fromisoformat("2008-10-29T22:00:00+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    event_3 = {
        "timestamp": datetime.fromisoformat("2008-08-16T22:00:30+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    event_4 = {
        "timestamp": datetime.fromisoformat("2008-01-05T22:22:08+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    event_5 = {
        "timestamp": datetime.fromisoformat("2008-01-05T22:00:00+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    event_6 = {
        "timestamp": datetime.fromisoformat("2008-08-11T22:00:01+00:00"),
        "level": "CRITICAL", "source": "web", "message": ""
    }
    stats = update_stat(event_1, stats)
    stats = update_stat(event_2, stats)
    stats = update_stat(event_3, stats)
    stats = update_stat(event_4, stats)
    stats = update_stat(event_5, stats)
    stats = update_stat(event_6, stats)
    assert stats["first_timestamp"] == event_5["timestamp"]
    assert stats["last_timestamp"] == event_2["timestamp"]