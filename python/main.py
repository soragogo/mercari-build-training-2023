import os
import logging
import pathlib
import json
import hashlib
import sqlite3
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
dbpath = pathlib.Path(__file__).parent.resolve() / "db" / "mercari.sqlite3"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item():
    logger.info(f"Receive item: {name}, {category}, {image.filename}")

    # get hash and save image
    file = image.file.read()
    image_hash = hashlib.sha256(file).hexdigest()
    image_filename = image_hash + ".jpg"
    path = "images/" + image_filename
    with open(path, "wb") as f:
        f.write(file)

    # update json
    with open("items.json", "r") as f:
        di = json.load(f)
    if not "items" in di:
        di["items"] = []
    di["items"].append(
        {"name": name, "category": category, "image_filename": image_filename}
    )

    with open("items.json", "w") as f:
        json.dump(di, f)
    return {"message": f"item received: {name}"}

@app.get("/items")
def list_item():
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute((
        SELECT items.'id', items.name, category.name, items.image_filename
        FROM items
        INNER JOIN category ON items.category_id = category.id
    ))
    items = cursor.fetchall()
    list_items = []
    for item in items:
        dict_item = {
            "id": item[0],
            "name": item[1],
            "category": item[2],
            "image_filename": item[3]
        }
        list_items.append(dict_item)
    conn.close()
    return{"items": list}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    with open("items.json", "r") as f:
        di = json.load(f)
    try:
        return di["items"][item_id]
    except KeyError:
        raise HTTPException(
            status_code=404, detail="'items' key not found in items.json"
        )
    except IndexError:
        raise HTTPException(
            status_code=404, detail=f"item_id {item_id} not found in items.json"
        )


@app.get("/image/{image_filename}")
def get_image(image_filename):
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
