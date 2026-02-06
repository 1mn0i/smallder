import inspect
import unittest

from smallder import Spider


class SpiderTest(unittest.TestCase):
    spider_class = Spider

    def test_start_requests(self):
        spider = self.spider_class()
        # Set start_urls BEFORE calling start_requests
        spider.start_urls = ["https://www.example.com"]
        start_requests = spider.start_requests()
        self.assertTrue(inspect.isgenerator(start_requests))
        self.assertEqual(len(list(start_requests)), 1)

    def test_start_requests_empty_urls(self):
        spider = self.spider_class()
        spider.start_urls = []
        with self.assertRaises(AttributeError):
            list(spider.start_requests())
