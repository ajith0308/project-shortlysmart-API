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
    .set_project("66681a22000266663d8b")  # Your project ID
    .set_key(
        "ef0cce0a8a08f0b5fdbfc5ccfdddbadf993f7834bace49bf9009bac80f0008e8329099711e8edf8d7de43e20ee33ca370b9d876f28640df835a67d8127db57d707abcbf81c5d692dcf5e62ce932337bf57725ec4939d9fa0098b55c7e84d27030d880af1dc60499fbebaa8c45f1c73d2819ea5aa3c0852af1ce6e0181f54afb1"
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

    return {
        "short_url": f"{baseurl}{shortened_url}",
        "qrurl": qrurl(baseurl, shortened_url),
    }


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


def qrurl(baseurl, short_hash: str):
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
        url = f"{baseurl}{short_hash}"
        qr = qrcode.make(url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_code_bytes = buffer.getvalue()
        base64_encoded_string = base64.b64encode(qr_code_bytes).decode("utf-8")
        img = "data:image/png;base64," + base64_encoded_string
        return {"image": img}


@app.post("/add-task")
def create_task(request: dict):
    data = {
        "name": request["name"],
        "created_at": request["created_at"],
        "lable": request["lable"],
        "updated_at": request["updated_at"],
        "user_id": request["user_id"],
        "categories_id": request["categories_id"],
        "deadlines": request["deadlines"],
        "status": request["status"],
    }
    json_string = json.dumps(data)
    my_uuid = uuid.uuid4()
    databases = Databases(client)
    databases.create_document(
        "66b2fbdd0020749b80ae",
        "66b2fbfb002d9632ebd4",
        str(my_uuid),
        data=json_string,
    )
    return {"data": "Created Successfully"}


@app.post("/updated")
def create_task(request: dict):
    coloction_id = request["document_id"]
    data = {
        "name": request["name"],
        "created_at": request["created_at"],
        "lable": request["lable"],
        "updated_at": request["updated_at"],
        "user_id": request["user_id"],
        "categories_id": request["categories_id"],
        "deadlines": request["deadlines"],
        "status": request["status"],
    }
    json_string = json.dumps(data)
    my_uuid = uuid.uuid4()
    databases = Databases(client)
    databases.update_document(
        "66b2fbdd0020749b80ae",
        "66b2fbfb002d9632ebd4",
        coloction_id,
        data=json_string,
    )
    return {"data": "Updated Successfully"}


@app.post("/list")
def create_task(request: dict):
    user_id = request["id"]
    my_uuid = uuid.uuid4()
    databases = Databases(client)
    data = databases.list_documents("66b2fbdd0020749b80ae", "66b2fbfb002d9632ebd4")
    return {"data": data}
