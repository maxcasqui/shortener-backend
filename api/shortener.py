from .validations import validate_url

def shortener(url):
    valid_url = validate_url(url)

    if (valid_url):
        pass
