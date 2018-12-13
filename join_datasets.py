'''

Strip down the data to essentials.
Insert them into an existing DB, in this case one created from restaurant_schema.sql.

If I ever run this for chains/markets, change the value IS_PARSING_CHAINS

'''
import csv
import json
import sqlite3

error_dict = {"malformed_row": 0, "non_200": 0, "empty_yelp_json": 0,
    "key_not_in_health": 0, "yelp_key_not_in_yelp": 0}

count_dict = {"200_status": 0, "yelp_key_in_health": 0, "health_rows": 0}
IS_PARSING_CHAINS = False

def load_healthscores(path):
    health = {}
    o = 0
    with open(path) as data:
        health_reader = csv.reader(data, delimiter=',')
        for row in health_reader:
            if len(row) == 21:
                data = {"health_score": row[16], "health_grade": row[8], "biz_owner": row[10],
                    "biz_desc": row[11], "inspection_date": row[0]}
                health[row[15]] = data
                count_dict["health_rows"] += 1
            else:
                error_dict["malformed_row"] += 1
                continue
    return health

def load_yelp(path):
    reviews = {}
    with open(path, 'r') as data:
        for line in data:
            parts = line.split(":::")
            if parts[1] == "200":
                count_dict["200_status"] += 1
                data = json.loads(parts[2])
                if data:
                    reviews[parts[0]] = data
                else:
                    error_dict["empty_yelp_json"] += 1
            else: 
                error_dict["non_200"] += 1
    return reviews

def merge(yelp, health):
    # Prepare for DB insertion.
    db = sqlite3.connect("LA_restaurants.db")
    cursor = db.cursor()
    for key, yelp_val in yelp.items():
        if key in health:
            count_dict["yelp_key_in_health"] += 1
            health_val = health[key]
            insert_data(yelp_val, health_val, cursor)
        else:
            error_dict["yelp_key_not_in_yelp"] += 1
    db.commit()
    db.close()

'''
Given a corresponding row from both yelp and health data,
extract the pertinent data and insert into the DB using the supplied cursor.
'''
def insert_data(yelp, health, cursor):
    address = yelp.get("location")
    coordinates = yelp.get("coordinates")
    restaurants = { "name": yelp.get("name"),
                    "name_alias": yelp.get("alias"),
                    "price": yelp.get("price"),
                    "rating": yelp.get("rating"),
                    "review_count": yelp.get("review_count"),
                    "image_url": yelp.get("image_url"),
                    "yelp_url": yelp.get("url"),
                    "yelp_id": yelp.get("id"),
                    "address1": address.get("address1") if address else None,
                    "address2": address.get("address2") if address else None,
                    "address3": address.get("address3") if address else None,
                    "city": address.get("city") if address else None,
                    "zip_code": address.get("zip_code") if address else None,
                    "longitude": coordinates.get("latitude") if coordinates else None,
                    "latitude": coordinates.get("latitude") if coordinates else None,
                    "health_score": health.get("health_score"),
                    "health_grade": health.get("health_grade"),
                    "biz_desc": health.get("biz_desc"),
                    "biz_owner": health.get("biz_owner"),
                    "inspection_date": health.get("inspection_date"),
                    "is_chain": IS_PARSING_CHAINS
                }
    cursor.execute(
    ''' INSERT INTO restaurants(name, name_alias, price, rating, review_count,
        image_url, yelp_url, address1, address2, address3, city, zip_code, longitude,
        latitude, yelp_id, health_score, health_grade, biz_desc, biz_owner, inspection_date, is_chain)
        VALUES(:name, :name_alias, :price, :rating, :review_count,
        :image_url, :yelp_url, :address1, :address2, :address3, :city, :zip_code, :longitude,
        :latitude, :yelp_id, :health_score, :health_grade, :biz_desc, :biz_owner, :inspection_date, :is_chain)
    ''' , restaurants)
    restaurant_key = cursor.lastrowid
    for category in yelp.get("categories"):
        categories = {}
        categories["category_alias"] = category.get("alias")
        categories["category_name"] = category.get("title")
        categories["restaurant_id"] = restaurant_key
        cursor.execute(
        '''INSERT INTO categories(category_alias, category_name, restaurant_id)
           VALUES(:category_alias, :category_name, :restaurant_id)
        ''' , categories)

def main():
    healthscores = load_healthscores("output/restaurants_indeps.csv")
    yelp = load_yelp("yelp_calls/details_all.txt")
    merge(yelp, healthscores)

if __name__ == '__main__':
    # Change this based on the dataset being parsed.
    IS_PARSING_CHAINS = False
    main()
    print(count_dict)
    print(error_dict)
