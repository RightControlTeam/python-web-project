from urllib.parse import urlparse
from shared.config import settings
from app import app

if __name__ == '__main__':
    parsed_url = urlparse(settings.REVIEW_SERVICE_URL)
    app.run(
        debug=True,
        host=parsed_url.hostname,
        port=parsed_url.port
    )