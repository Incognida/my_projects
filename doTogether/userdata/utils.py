from random import choice
from string import digits, ascii_letters


def id_generator(size=25, chars=digits + ascii_letters):
    return ''.join(choice(chars) for _ in range(size))
