#!/usr/bin/env python

import uuid
import time
import logging
from rate_limiter import TokenBucketRateLimiter

logging.basicConfig(level=logging.DEBUG, format="[%(module)s] - %(levelname)s -  %(message)s")

def main():
    # By default, it allows 100 requests per hour, which means
    # one request every 36 seconds (3600 // 100 )
    rl = TokenBucketRateLimiter()
    user_id = uuid.uuid4()
    status_code, _ = rl.is_allowed(user_id)
    print(status_code)
    # this one should be rejected
    status_code, _ = rl.is_allowed(user_id)
    print(status_code)
    # take a break for 36 seconds, and new request should be
    # accepted again
    time.sleep(36)
    status_code, _ = rl.is_allowed(user_id)
    print(status_code)


if __name__ == "__main__":
    main()