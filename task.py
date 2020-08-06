import os
import random
from huey import RedisHuey

huey = RedisHuey(url=os.getenv('REDIS_URL'))


@huey.task(retries=5, retry_delay=5)
def get_random_num():
    print("This is a task to get a random number")
    num = random.randint(1, 3)
    print("Random number is {}".format(num))

    if num == 1:
        return True
    else:
        raise Exception("Error in the worker... :(")

