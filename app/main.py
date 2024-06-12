from fastapi import FastAPI, Body
import hashlib
from base64 import urlsafe_b64encode

app = FastAPI()

# Characters to use for encoding the shortened URL
allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_short_url(url: str) -> str:
    """
    Generates a 10-character shortened URL from the provided long URL.

    Args:
        url (str): The long URL to be shortened.

    Returns:
        str: The shortened 10-character URL.
    """

    url_bytes = url.encode("utf-8")
    hashed_url = hashlib.sha256(url_bytes).hexdigest()  # SHA-256 hash

    # Truncate the hash to ensure 10 characters
    short_url_prefix = hashed_url[:10]

    # Base64 encode with URL-safe characters to create the final shortened URL
    encoded_url = urlsafe_b64encode(short_url_prefix.encode("utf-8")).decode("utf-8")

    # Remove trailing padding characters (=) from Base64 encoding
    short_url = encoded_url.rstrip("=")

    # Truncate further if necessary to reach exactly 10 characters
    return short_url[:10]


@app.post("/shorten")
async def shorten_url(url: str = Body(...)):
    """
    Shortens a long URL and returns the shortened version.

    Args:
        url (str): The long URL to be shortened.

    Returns:
        dict: A JSON response containing the shortened URL.
    """

    shortened_url = generate_short_url(url)
    return {"short_url": shortened_url}


# (Optional) Implementation for redirecting from shortened URLs to original URLs
# This would require additional logic to store the mapping between shortened and original URLs

# ... (implementation for redirection logic)
