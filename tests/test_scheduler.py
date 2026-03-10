from smallder import Request, Spider
from smallder.core.dupfilter import MemoryFilter
from smallder.core.scheduler import MemoryScheduler


def make_scheduler():
    spider = Spider()
    spider.thread_count = 1
    return MemoryScheduler(spider, MemoryFilter())


def test_memory_scheduler_filters_duplicate_requests_before_enqueue():
    scheduler = make_scheduler()
    first_request = Request(url="http://example.com")
    duplicate_request = Request(url="http://example.com")

    scheduler.add_job(first_request)
    scheduler.add_job(duplicate_request)

    assert scheduler.size() == 1
    assert scheduler.next_job() is first_request
    assert scheduler.empty()


def test_memory_scheduler_keeps_dont_filter_requests():
    scheduler = make_scheduler()

    scheduler.add_job(Request(url="http://example.com", dont_filter=True))
    scheduler.add_job(Request(url="http://example.com", dont_filter=True))

    assert scheduler.size() == 2
