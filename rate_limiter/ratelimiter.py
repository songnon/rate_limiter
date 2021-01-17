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
    This rate limiter is based on token bucket (https://en.wikipedia.org/wiki/Token_bucket).
    It keeps track of the timestamp (in microsecond) of last request. A new request is only allowed if 
    (MICROSECONDS_PER_HOUR // requests_per_hour) microseconds have elapsed since then. 

    Microsecond is chosen in order to support up to 1 million requests per second.
    """
    def __init__(self, requests_per_hour=100):
        self.interval_micros = MICROSECONDS_PER_HOUR // requests_per_hour
        super().__init__()
    
    def is_allowed(self, user_id):
        """
        Check how many microseconds have elapsed since the last request for each user.
        A tuple (status-code, message-body) is returned:
        - (200, 'OK')
        - (429, 'Rate limit exceeded. Try again in #{n} seconds)
        """
        with self.lock:
            now_micros = int(round(time.time() * 1000000))
            
            # if user_id is not in self.user_meta, 0 will be return to 
            # ensure elapsed_micros is greater than self.interval_micros.
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
