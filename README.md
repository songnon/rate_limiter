# Rate Limiter

## Overview

There are several techniques for limiting rates, e.g.:
1. fixed window
2. sliding window
3. token bucket

Each one has its disadvantage, e.g. **fixed window** will subject to spikes at the edges of windows, and **sliding window** has larger memory footprint.

The module implements `TokenBucketRateLimiter` based on token bucket. There is only one token available for each client/user. If that token has been consumed, client/user should wait for a specific time interval so that another token will become available. The time interval is calculated based on the rate (how many requests are allowed in every hour). For example, for a rate of 100 requests per hour (3600/100 = 36 seconds), client/user needs to wait for every 36 seonds so that a request is allowed. By doing this, we'll have a very smooth/steady rate control.

`TokenBucketRateLimiter` provides a method `is_allowed` which takes a user ID as input to check if a new request of current user can be granted or not.

## Installation

```bash
pip install -e .
```

## Usage/Example

Following is a simple example. Please refer to `examples/` directory for more examples.

```python
import uuid
from rate_limiter import TokenBucketRateLimiter

rl = TokenBucketRateLimiter()
status_code, _ = rl.is_allowed(uuid.uuid4())
```

## Limition
The first request of each client/user is always allowed.

Theoretically, the `TokenBucketRateLimiter` can support up to 1 million concurrent requests per second within one process.

## Testcases

`unittest` testing framework is used for all testcases.