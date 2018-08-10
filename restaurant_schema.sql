CREATE TABLE la_restaurants (
    id int primary key autoincrement,
    name varchar(255),
    name_alias varchar(255),
    price varchar(255),
    rating float(5,5),
    review_count int,
    img_url varchar(255),
    yelp_url varchar(255),
    address1 varchar(255),
    address2 varchar(255),
    address3 varchar(255),
    city varchar(255),
    zip_code varchar(255),
    longitude float(15,15),
    latitude float(15,15),
    yelp_id varchar(255),

    health_score int,
    health_grade char(1),
    biz_desc varchar(255),
    biz_owner varchar(255),
    inspection_date date,

    is_chain bit
);

CREATE TABLE restaurant_categories (
    id int primary key autoincrement,
    category_name varchar(255),
    category_alias varchar(255),
    restaurant_id int foreign key references la_restaurants.id
);