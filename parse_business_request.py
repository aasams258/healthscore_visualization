import json
import glob

'''
Input: UID:::HTTP_RESPONSE:::YELP_API_JSON
Output the UID along with Yelp's id.
'''
def main(data_path):
    ids = open("matches_parsed/biz_ids.csv", "w")
    no_reviews = open("matches_parsed/no_reviews.csv", "w")
    error = open("matches_parsed/error.csv", "w")
    for data in glob.glob(data_path):
        # Have this iterate the directory. 
        with open(data, 'r') as biz_data:
            for line in biz_data:
                parts = line.split(":::")
                if len(parts) != 3:
                    print("bad split on {}".format(line))
                    continue
                # Case 1: Error, such as Rate Exceeeded or out of API Calls; add to redo pile.
                # EE0000006:::429:::{"error": {"code": "...."}}
                # Case 2: No Reviews (So no data); mark it as such and put in third file.
                # EE0000721:::200:::{"businesses": []}
                # Case 3: It's Ok!
                # EE0000731:::200:::{"businesses": [....]}
                if parts[1] == "200":
                    resp = json.loads(parts[2])
                    if len(resp["businesses"]) > 0:
                        ids.write("{},{}\n".format(parts[0], resp["businesses"][0]["id"]))
                    else: 
                        no_reviews.write("{}\n".format(parts[0]))
                        # No reviews case.
                else:
                    error.write("{},{}\n".format(parts[0], parts[1]))
    
    ids.close()
    no_reviews.close()
    error.close()

if __name__ == '__main__':
    main("yelp_calls/*.txt")

