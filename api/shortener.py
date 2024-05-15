from api.models import URL
from random import choice
from string import ascii_letters, digits

AVAILABLE_CHARS = ascii_letters + digits

def create_random_slug(chars=AVAILABLE_CHARS):
    return "".join([choice(chars) for _ in range(6)])

def generate_slug():
    random_slug = create_random_slug()
    if URL.objects.filter(slug=random_slug).exists():
        return generate_slug()
    return random_slug