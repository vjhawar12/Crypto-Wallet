CREATE TABLE data (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for the user
    full_name TEXT,
    pass TEXT,
    phone TEXT,
    email TEXT,
    face_embedding BLOB -- OpenCV creates vectors called "embeddings" with the images
); 



