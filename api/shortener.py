import random
import uuid
from api.models import URL

def get_slug():
    slug = generate_slug()
    while slug_exists(slug):
        slug = generate_slug()
    return slug

def slug_exists(slug):
    return URL.objects.filter(slug=slug).exists()

def generate_slug():
    random_number = str(random.randint(0, 100))
    base_slug = str(uuid.uuid4())[-4:]
    slug = base_slug.join(random_number)
    return slug