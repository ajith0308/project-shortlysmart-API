import base64
import datetime
import io
import json
import re
import uuid
from fastapi import FastAPI, Body, HTTPException, Request
import hashlib
from base64 import urlsafe_b64encode
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import *
import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import qrcode
from PIL import Image

app = FastAPI()
url_db = {}
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Client()
(
    client.set_endpoint("https://cloud.appwrite.io/v1")  # Your API Endpoint
    .set_project("666882990016fb1b074a")  # Your project ID
    .set_key(
        "ca05cedd116ccd51e2df5261093e63399f41aa8c6075b885fca8ddfad5e29c827dcc21d05a18370e5b1fc8d1f54292c593c618e3a1f112be294f188183f2e6fdd95dc55db5fe9a40b114f420c2fccb5f5c00f97b8bb96b743cec1bfef7fb324e76e16c7aef749ef3206cb483f612da27db53a197e0e6400aeb6afce0290fd2af"
    )  # Your secret API key
)
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
async def shorten_url(request: dict, urlrequest: Request):
    url = request.get("url")
    baseurl = urlrequest.base_url
    shortened_url = generate_short_url(url)
    databases = Databases(client)
    now = datetime.datetime.now()
    data = {"url": url, "created_by": "12/06/2024", "hash": shortened_url}
    json_string = json.dumps(data)
    my_uuid = uuid.uuid4()
    print("uuid", my_uuid)
    result = databases.create_document(
        "6668855b0003410f5928",
        "api0001",
        str(my_uuid),
        data=json_string,
    )

    """
    Shortens a long URL and returns the shortened version.

    Args:
        url (str): The long URL to be shortened.

    Returns:
        dict: A JSON response containing the shortened URL.
    """

    return {"short_url": f"{baseurl}{shortened_url}", "qrurl": qrurl(shortened_url)}


# (Optional) Implementation for redirecting from shortened URLs to original URLs
# This would require additional logic to store the mapping between shortened and original URLs


# ... (implementation for redirection logic)
@app.get("/{short_hash}")
def redirect_to_long_url(short_hash: str):
    databases = Databases(client)
    data = databases.list_documents(
        "6668855b0003410f5928",
        "api0001",
        [
            Query.equal("hash", short_hash),
        ],
    )
    if data["total"] == 0:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        return RedirectResponse(url=data["documents"][0]["url"])


@app.get("/qr/{short_hash}")
def qr(short_hash: str):
    databases = Databases(client)
    data = databases.list_documents(
        "6668855b0003410f5928",
        "api0001",
        [
            Query.equal("hash", short_hash),
        ],
    )
    if data["total"] == 0:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        url = data["documents"][0]["url"]
        qr = qrcode.make(url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_bytes = buffer.getvalue()
        base64_encoded_string = base64.b64encode(qr_code_bytes).decode("utf-8")
        img = "data:image/png;base64," + base64_encoded_string
        return {"qr": img}


def qrurl(short_hash: str):
    databases = Databases(client)
    data = databases.list_documents(
        "6668855b0003410f5928",
        "api0001",
        [
            Query.equal("hash", short_hash),
        ],
    )
    if data["total"] == 0:
        raise HTTPException(status_code=404, detail="URL not found")
    else:
        url = data["documents"][0]["url"]
        qr = qrcode.make(url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_bytes = buffer.getvalue()
        base64_encoded_string = base64.b64encode(qr_code_bytes).decode("utf-8")
        img = "data:image/png;base64," + base64_encoded_string
        return {"image": img}
