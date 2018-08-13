-- sqlite3 $database_name.db
-- .read restaurant_schema
-- .schema $TABLE_NAME to check name

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY autoincrement,
    yelp_id TEXT,
    name TEXT,
    name_alias TEXT,
    price TEXT,
    rating REAL,
    review_count INTEGER,
    image_url TEXT,
    yelp_url TEXT,

    address1 TEXT,
    address2 TEXT,
    address3 TEXT,
    city TEXT,
    zip_code TEXT,
    longitude REAL,
    latitude REAL,
    
    health_score INTEGER,
    health_grade TEXT,
    biz_desc TEXT,
    biz_owner TEXT,
    inspection_date TEXT,

    is_chain INTEGER
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY autoincrement,
    category_name TEXT,
    category_alias TEXT,
    restaurant_id INTEGER NOT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);