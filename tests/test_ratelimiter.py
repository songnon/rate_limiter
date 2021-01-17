import time
from concurrent import futures
from unittest import TestCase
from unittest.mock import patch
from rate_limiter import TokenBucketRateLimiter

class TestTokenBucketRateLimiter(TestCase):
    def setUp(self):
        self.now_seconds = time.time()

    @patch('rate_limiter.ratelimiter.time')
    def test_rate_limiting_single_thread_allowed(self, time_mock):
        user_id = 'user_a'
        time_mock.time.side_effect = [self.now_seconds, self.now_seconds + 3600//100]
        rl = TokenBucketRateLimiter()
        status_code, _ = rl.is_allowed(user_id)
        self.assertEqual(status_code, 200)
        status_code_2, _ = rl.is_allowed(user_id)
        self.assertEqual(status_code_2, 200)
    
    @patch('rate_limiter.ratelimiter.time')
    def test_rate_limiting_single_thread_rejected(self, time_mock):
        user_id = 'user_a'
        requests_per_hour = 100
        # one 1 second smaller
        time_mock.time.side_effect = [self.now_seconds, self.now_seconds  - 1 + 3600//requests_per_hour]
        rl = TokenBucketRateLimiter(requests_per_hour)
        status_code, _ = rl.is_allowed(user_id)
        self.assertEqual(status_code, 200)
        status_code_2, error_body = rl.is_allowed(user_id)
        self.assertEqual(status_code_2, 429)
        # ensure ' 1.0 seconds' is inside the error_body
        self.assertRegex(error_body, r'\s1.0\sseconds')
    
    @patch('rate_limiter.ratelimiter.time')
    def test_rate_limiting_single_thread_same_ts_rejected(self, time_mock):
        user_id = 'user_a'
        requests_per_hour = 36000
        rl = TokenBucketRateLimiter(requests_per_hour)
        time_mock.time.return_value = self.now_seconds
        status_code, _ = rl.is_allowed(user_id)
        self.assertEqual(status_code, 200)
        status_code_2, error_body = rl.is_allowed(user_id)
        self.assertEqual(status_code_2, 429)
        # ensure ' 0.1 seconds' is inside the error_body
        self.assertRegex(error_body, r'\s0.1\sseconds')
    
    @patch('rate_limiter.ratelimiter.time')
    def test_rate_limiting_single_thread_multi_user_same_ts_allowed(self, time_mock):
        user_id_a = 'user_a'
        user_id_b = 'user_b'
        requests_per_hour = 36000
        rl = TokenBucketRateLimiter(requests_per_hour)
        time_mock.time.return_value = self.now_seconds
        status_code, _ = rl.is_allowed(user_id_a)
        self.assertEqual(status_code, 200)
        status_code_2, _ = rl.is_allowed(user_id_b)
        self.assertEqual(status_code_2, 200)
    
    @patch('rate_limiter.ratelimiter.time')
    def test_rate_limiting_multi_threads_same_ts_rejected(self, time_mock):
        user_id = 'user_a'
        requests_per_hour = 36000
        rl = TokenBucketRateLimiter(requests_per_hour)

        number_of_threads = 5
        # all threads are triggered at the same time
        time_mock.time.return_value = self.now_seconds
        with futures.ThreadPoolExecutor() as executor:
            results = executor.map(rl.is_allowed, [user_id] * number_of_threads)

        expected_results = [200] + [429] * (number_of_threads - 1)
        # assert only one is granted and the others are rejected.
        self.assertCountEqual([status_code for status_code, _ in results], expected_results)
