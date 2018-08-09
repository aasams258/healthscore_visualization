'''

1. Strip down both the data to essentials.
2. Put in dict with street address as key, value is [restaurant name, other_data]
3. Join dicts on key, and output concatted value to a csv file.

'''
import csv
import json

error_dict = {"malformed_row": 0, "non_200": 0, "empty_yelp_json": 0, "key_not_in_health": 0, "yelp_key_not_in_yelp": 0}
count_dict = {"200_status": 0, "yelp_key_in_health": 0, "health_rows": 0}
def load_healthscores(path):
    health = {}
    o = 0
    with open(path) as data:
        health_reader = csv.reader(data, delimiter=',')
        for row in health_reader:
            if len(row) == 21:
                data = {"score": row[16], "grade": row[8], "owner": row[10], "biz_desc": row[11], "inspection_date": row[0]}
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
    # Yelp will be the smaller dataset, as more likely for http errors
    for key, val in yelp.items():
        if key in health:
            count_dict["yelp_key_in_health"] += 1
            pass
        else:
            error_dict["yelp_key_not_in_yelp"] += 1

def writeToSQL():
    pass
    
def main():
    healthscores = load_healthscores("output/restaurants_indeps.csv")
   # print(healthscores.items()[0:10])
    yelp = load_yelp("yelp_calls/details_all.txt")
    merge(yelp, healthscores)

if __name__ == '__main__':
    main()
    print(count_dict)
    print(error_dict)
   #main("output/restaurants_indeps.csv")
   #check_unique("output/restaurants_indeps.csv")
