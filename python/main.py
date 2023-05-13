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
def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name}, category: {category}, image: {image.filename}")
    
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    
    image_file = image.file.read()
    image_hash = hashlib.sha256(image_file).hexdigest()
    image_filename = f"{image_hash}.jpg"
    image_path = images / image_filename
    
    with open(image_path, 'wb') as f:
        f.write(image_file)
    
    cursor.execute("SELECT id FROM category WHERE name = ?", (category,))
    category_id = cursor.fetchone()

    if category_id is None:
        cursor.execute("INSERT INTO category (name) VALUES (?)", (category,))
        category_id = cursor.lastrowid
    else:
        category_id = category_id[0]
    
    cursor.execute("SELECT id FROM items WHERE name = ?", (name,))
    item_id = cursor.fetchone()


    if item_id is not None:
        return {"error": f"Item with the same name already exists: {name}"}
    
    cursor.execute("INSERT INTO items (name, category_id, image_filename) VALUES (?, ?, ?)",
                   (name, category_id, image_filename,))
    conn.commit()

    return {"message": f"Item received: {name}, category: {category}, image: {image_filename}"}


@app.get("/items")
def list_item():
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute((
        SELECT items.id, items.name, category.name, items.image_filename
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
