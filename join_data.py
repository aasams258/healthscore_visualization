'''
Note the UUID is not actually unique, Kaggle messed up.

We need to instead join on street address, and use the name as a tie breaker. 
[Multiple restaurants might have same address?]

1. Strip down both the data to essentials.
2. Put in dict with street address as key, value is [restaurant name, other_data]
3. Join dicts on key, and output concatted value to a csv file.

'''
import csv
import json

def create_key(name, street):
    dirty_key = street
    lower_key = dirty_key.lower()
    # Characters to remove to keep a simple code.
    for c in [" ", "-", ".", ",", "_", "'", '"', '&', "$", "(", ")", "#", "@"]:
        lower_key = lower_key.replace(c, "")
    return lower_key.strip()

def load_health(path):
    health = {}
    o = 0
    with open(path) as data:
        health_reader = csv.reader(data, delimiter=',')
        for row in health_reader:
            if len(row) == 21:
                key = create_key(row[20], row[2])
                addy = row[2]
                if key in health:
                    o += 1
                    health[key].append(row[20])
                else:
                    health[key] = [row[20]]
            else:
                print("Malformed row")
                continue
    # for k,v in health.items():
    #     if len(v) > 1:
    #         print("{} :: {}".format(k,v))
    # print(o)
    return health

def load_reviews(path):
    reviews = {}
    o = 0
    with open(path, 'r') as data:
        for line in data:
            parts = line.split(":::")
            if len(parts) != 3:
                print("bad split on {}".format(line))
            if parts[1] == "200":
                resp = json.loads(parts[2])
                name = resp["name"]
                addy = resp["location"]["address1"]
                key = create_key(name, addy)
                if key in reviews:
                    reviews[key].append(name)
                    o += 1
                else:
                    reviews[key] = [name]
    # for k,v in reviews.items():
    #     if len(v) > 1:
    #         print("{} :: {}".format(k,v))
    # print(o)
    return reviews
def merge():
    merged = {}
    # Have this iterate the directory. 
    with open(data, 'r') as biz_data:
        for line in biz_data:
            parts = line.split(":::")
            if len(parts) != 3:
                print("bad split on {}".format(line))
                continue
            if parts[1] == "200":
                resp = json.loads(parts[2])
                if len(resp["businesses"]) > 0:
                    ids.write("{},{}\n".format(parts[0], resp["businesses"][0]["id"]))

def main(data_path):
    health = load_health(data_path)
    reviews = load_reviews("yelp/details.txt")
    print(len(health))
    print(len(reviews))
    i = 0
    n = 0
    for k,v in reviews.items():
        if k in health:
            i += 1
        else:
            n += 1
            print(k)
    print("in: {} out: {}".format(i,n))

# check 4 and 6th from end
def check_unique(data):
    uniques = {}
    # Have this iterate the directory. 
    with open(data, 'r') as biz_data:
        health_reader = csv.reader(biz_data, delimiter=',')
        for row in health_reader:
            idx = row[4] # Row 15 is record id; row 4 is facultyID
            if idx in uniques:
                print ("error")
            else:
                uniques[row[4]] = ""
    print("DONE")

if __name__ == '__main__':
   #main("output/restaurants_indeps.csv")
   check_unique("output/restaurants_indeps.csv")
