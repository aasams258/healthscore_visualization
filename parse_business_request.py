import json

# Case 1: Rate exceeeded; add to redo pile.
# EE0000006:::429:::{"error": {"code": "TOO_MANY_REQUESTS_PER_SECOND", "description": "You have exceeded the queries-per-second limit for this endpoint. Try reducing the rate at which you make queries."}}
# Case 2: Out of tokens; add to redo pile.
# Case 3: No Reviews (So no data); mark it as such and put in third file.
# EE0000721:::200:::{"businesses": []}
# Case 4: It's Ok!
# EE0000731:::200:::{"businesses": [{"id": "rMXaU2reT_fiJ-3Q6udZng", "alias": "taste-of-viet-harbor-city", "name": "Taste of Viet", "coordinates": {"latitude": 33.81653, "longitude": -118.3084}, "location": {"address1": "1650 Sepulveda Blvd", "address2": null, "address3": "", "city": "Harbor City", "zip_code": "90710", "country": "US", "state": "CA", "display_address": ["1650 Sepulveda Blvd", "Harbor City, CA 90710"]}, "phone": "+13103262889", "display_phone": "(310) 326-2889"}]}

'''
Output the UID along with Yelp's id.
This will call 
'''
biz_data = ""
re_parse = []

ids = open("matches_parsed/biz_ids.csv")
no_reviews = open("matches_parsed/no_reviews.csv")
error = open("matches_parsed/error.csv")

with open(biz_data, 'r') as data:
    parts = data.split(":::")
    # Check if not 200
    if parts[1] == "200":
        resp = json.loads(parts[2])
        if len(resp["businesses"]) > 0:
            ids.write({})
        else: 
            # No reviews case.

    else:
        print "error {}".format(parts[1])
        continue
    parts[2] #Parse the json check it for issues
   
ids.close()
no_reviews.close()
error.close()