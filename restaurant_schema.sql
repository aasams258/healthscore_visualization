-- sqlite3
-- .read restaurant_schema, then check with .schema $TABLE_NAME
CREATE TABLE la_restaurants (
    id INTEGER PRIMARY KEY autoincrement,
    name TEXT,
    name_alias TEXT,
    price TEXT,
    rating REAL,
    review_count int,
    img_url TEXT,
    yelp_url TEXT,
    address1 TEXT,
    address2 TEXT,
    address3 TEXT,
    city TEXT,
    zip_code TEXT,
    longitude REAL,
    latitude REAL,
    yelp_id TEXT,

    health_score int,
    health_grade TEXT,
    biz_desc TEXT,
    biz_owner TEXT,
    inspection_date NUMERIC,

    is_chain INTEGER
);

CREATE TABLE restaurant_categories (
    id INTEGER PRIMARY KEY autoincrement,
    category_name TEXT,
    category_alias TEXT,
    restaurant_id INTEGER NOT NULL,
    FOREIGN KEY (restaurant_id) REFERENCES la_restaurants(id)
);

