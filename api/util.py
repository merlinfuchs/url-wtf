import random
import string


__all__ = (
    "URL_TYPES",
)


BASE_36 = string.ascii_lowercase + string.digits
INVISIBLE = ["\u2060", "\u2061", "\u2062", "\u2063"]

URL_TYPES = {
    "default": lambda: "".join([random.choice(BASE_36) for _ in range(6)]),
    "invisible": lambda: "".join([random.choice(INVISIBLE) for _ in range(16)]),
}
