from unittest import TestCase

import src.core.resp


class Test(TestCase):
    def test_decode_simple_string(self):
        cases = {
            '+OK\r\n': 'OK'
        }
        for k, v in cases.items():
            val = src.core.resp.resp_decode(k)
            self.assertEqual(val, v)

    def test_decode_error(self):
        cases = {
            "-Error message\r\n": "Error message"
        }
        for k, v in cases.items():
            val = src.core.resp.resp_decode(k)
            self.assertEqual(val, v)

    def test_decode_int_64(self):
        cases = {
            ":0\r\n": 0,
            ":1000\r\n": 1000,
        }
        for k, v in cases.items():
            val = src.core.resp.resp_decode(k)
            self.assertEqual(val, v)

    def test_decode_bulk_string(self):
        cases = {
            "$5\r\nhello\r\n": "hello",
            "$0\r\n\r\n": "",
        }
        for k, v in cases.items():
            val = src.core.resp.resp_decode(k)
            self.assertEqual(val, v)

    def test_decode_array(self):
        cases = {
            "*0\r\n": [],
            "*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n": ["hello", "world"],
            "*3\r\n:1\r\n:2\r\n:3\r\n": [1, 2, 3],
            "*5\r\n:1\r\n:2\r\n:3\r\n:4\r\n$5\r\nhello\r\n": [1, 2, 3, 4, "hello"],
            "*2\r\n*3\r\n:1\r\n:2\r\n:3\r\n*2\r\n+Hello\r\n-World\r\n": [[1, 2, 3], ['Hello', 'World']]
        }
        for k, v in cases.items():
            val = src.core.resp.resp_decode(k)
            self.assertEqual(val, v)
