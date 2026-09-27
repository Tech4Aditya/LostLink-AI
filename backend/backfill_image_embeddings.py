from app.db import SessionLocal
from app.models import Image
from app.ai.encoder import get_encoder

db = SessionLocal()
encoder = get_encoder()

try:
    images = db.query(Image).all()
    print("IMAGES:", len(images))

    count = 0

    for image in images:
        print("Processing:", image.storage_path)

        embedding = encoder.image(image.storage_path)

        if embedding is not None:
            image.embedding = embedding
            count += 1

    db.commit()
    print("BACKFILLED:", count)

finally:
    db.close()
