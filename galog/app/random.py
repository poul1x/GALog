import random
from datetime import datetime

# Initialize pseudorandom sequences
random.seed(datetime.now().timestamp())


def randomDigit():
    return str(random.randint(0, 9))


def randomChar():
    return random.choice("abcdefghijklmnopqrstuvwxyz")


def randomSessionId():
    return "{}-{}".format(
        datetime.now().replace(microsecond=0).isoformat().replace(":", "-"),
        randomChar() + randomChar() + randomDigit() + randomDigit(),
    )
