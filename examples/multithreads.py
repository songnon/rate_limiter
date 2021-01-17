#!/usr/bin/env python

import uuid
import time
import logging
import random
from concurrent import futures
from rate_limiter import TokenBucketRateLimiter

logging.basicConfig(level=logging.DEBUG, format="[%(module)s] - %(levelname)s -  %(message)s")

def sleep_and_check(rateLimiter, user_id):
    t = random.random()
    time.sleep(t)
    # print(f'sleep for {t} seconds')
    return rateLimiter.is_allowed(user_id)


def main():
    # 3600 requests per hour, which means
    # one request every 1 seconds (3600 // 3600 )
    rl = TokenBucketRateLimiter(3600)
    user_id = uuid.uuid4()
    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_result = [executor.submit(sleep_and_check, rl, user_id) for _ in range(10)]
        for f in futures.as_completed(future_result):
            print('result is: ', f.result())
    
if __name__ == "__main__":
    main()