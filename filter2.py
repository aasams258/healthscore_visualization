import csv
def classify_data(data):
    # want to sort into: restaurants, markets.
    res_output = open('restaurants_indeps.csv', 'w')
    res_writer = csv.writer(res_output, delimiter=',')
    mkt_output = open('markets_indeps.csv', 'w')
    mkt_writer = csv.writer(mkt_output, delimiter=',')
    with open(data, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        s = set()
        res = 0
        mkt = 0
        for row in reader:
            if row[11].lower().startswith("restaurant"):
                res += 1
                res_writer.writerow(row)
            elif row[11].lower().startswith("food"):
                mkt += 1
                mkt_writer.writerow(row)
            else:
                print "malformed {}".format(row[11])
    print "Res {}, Mkt {}".format(res,mkt)
    res_output.close()
    mkt_output.close()

def main(path):
    #chains = find_chains(path)
    #print chains
    classify_data(path)
    
if __name__ == '__main__':
    main("/Users/Arthur/Documents/Coding/health_scores/indepedents.csv")