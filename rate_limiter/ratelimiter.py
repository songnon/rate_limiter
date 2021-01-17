import time
import threading
import abc
import logging

logger = logging.getLogger(__name__)

MICROSECONDS_PER_HOUR = 3600 * 1000000

class RateLimiter(object):
    """
    Rate Limiter abstract class.
    """
    def __init__(self):
        self.user_meta = {}
        self.lock = threading.Lock()

    @abc.abstractmethod
    def is_allowed(self, user_id):
        pass

class TokenBucketRateLimiter(RateLimiter):
    """
    The task is to produce a rate-limiting module that stos a particular requestor
    from making too many http requests within a particular period of time.

    The module should expose a method that keeps track of requests and ​limits it such 
    that a requester can only make 100 requests per hour. After the limit has been reached, 
    return a 429 with the text "Rate limit exceeded. Try again in #{n} seconds".

    Keeps track of requests and ​limits it such that a requester can only make 100 requests per hour.
    After the limit has been reached, return a 429 with the text "Rate limit exceeded. Try again in #{n} seconds".

    This rate limiter is based on token bucket (https://en.wikipedia.org/wiki/Token_bucket).
    it keeps track of the timestamp (in microsecond) of last request. A new request is only allowed if 
    (MICROSECONDS_PER_HOUR // requests_per_hour) microseconds have elapsed since then. 

    Microsecond is chosen in order to support up to 1 million requests per second.
    """
    def __init__(self, requests_per_hour=100):
        self.interval_micros = MICROSECONDS_PER_HOUR // requests_per_hour
        super().__init__()
    
    def is_allowed(self, user_id):
        """
        Check how many microseconds have elapsed since the last request for each user. it returns
        a tuple (status-code, message-body)
        - (200, 'OK')
        - (429, 'Rate limit exceeded. Try again in #{n} seconds)
        """
        with self.lock:
            now_micros = int(round(time.time() * 1000000))
            
            # if user_is is not in self.user_meta, 0 will be return
            last_request_micros = self.user_meta.get(user_id, 0)
            elapsed_micros = now_micros - last_request_micros
            logger.debug(f'lock is acquired by {str(threading.get_ident())}; {elapsed_micros / 1000000} seconds elapsed.')

            if elapsed_micros >= self.interval_micros:
                self.user_meta[user_id] = now_micros
                return (200, 'OK')
            else:
                logger.info(f'Rate limited for user {user_id}')
                wait_seconds = (self.interval_micros - elapsed_micros) / 1000000
                return (429, f'Rate limit exceeded. Try again in {wait_seconds} seconds')
