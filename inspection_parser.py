import csv
import re
import subprocess
from collections import defaultdict

'''
Iterated the sorted [date, UID] rows, and output the most recent date.
'''
def unique_entries(data):
    with open('tmp/uniqued.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',')
        with open(data, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            prev_id = ''
            for row in reader:
                if prev_id != row[4]:
                    prev_id = row[4]
                    writer.writerow(row)

'''
Clean up the name for chain identification
'''
def clean_name(name):
    lower = name.lower()
    # Certain stores are inside another store, signified using @
    # There are also cases where @ is part of the name, 'GRINDZ @ 1601'
    # We will be ok with dropping those entries.
    split_at = lower.split('@')
    # Many chains contain the string #12345 or #12345b.
    removed_num = re.sub("\s#\s?\d{1,10}\w?$", "", split_at[0])
    # Remove any leftover whitespace and return.
    return removed_num.strip()

'''
Determine if the entity is likely a chain.
Done by checking the frequency the name appears.
'''
def aggregate_chains(data):
    chains = defaultdict(int)
    with open(data, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            # 5 is facility name
            chains[clean_name(row[5])] += 1
    # Filter values that are <= 1 and return
    chains = {k: v for k,v in chains.items() if v > 1}
    return chains

''' Pass in a cleaned name '''
def is_chain(cleaned, chain_set):
    # Certain restaurants do not follow the format in aggregate chains. We will manaully filter them out.
    # Smaller nonformat meeting chains we will just ignore. (BJ'S REstaurant, BLACK ANGUS, WINCHELL'S)
    if cleaned in chain_set or re.search("domino's|kfc|panera|panda\sexpress|papa\sjohn's|sizzler|starbucks|subway|taco\sbell|target", cleaned):
        return True
    else:
        return False

''' 
Identify which category data should fall in:
 * chain or independent
'''
def classify_data(data, chain_set):
    # Want to sort into: chains, restaurants, markets.
    chain_output = open('output/chains.csv', 'w')
    chain_writer = csv.writer(chain_output, delimiter=',')
    independent_output = open('output/independents.csv', 'w')
    independent_writer = csv.writer(independent_output, delimiter=',')
    indep = 0
    chain = 0
    with open(data, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            cleaned = clean_name(row[5])
            row.append(cleaned)
            # More clean up, as some restaurants contain different chain phrasing
            if is_chain(cleaned, chain_set): 
                chain_writer.writerow(row)
                chain += 1
            else:
                independent_writer.writerow(row)
                indep += 1
    chain_output.close()
    independent_output.close()
    print "Independents {}, Chains {}".format(indep, chain)

'''
Sort it into further categories, market or restaurant, based on the
health board category

Note may not be fully accurate, as certain convenience stores serve food.
'''
def sort_market_or_restaurant(data):

    res_output = open('output/restaurants_indeps.csv', 'w')
    res_writer = csv.writer(res_output, delimiter=',')
    mkt_output = open('output/markets_indeps.csv', 'w')
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
    res_output.close()
    mkt_output.close()
    print "Restaurants {}, Markets {}".format(res, mkt)

''' 
Take an unaltered inspections.csv file, and progressively filter it down.
1. Sort 
2. Unique-ify
3. Identify Chains [Write to a blacklist]
4a. Write Chains into a new file [Create Dataset chains.csv]
4b. Write Independent Restaurant Dataset. [indepedents.csv]
?. Filter out Markets [Non Chain Markets aren't too intereting]

There is a tmp file to write intermediate values, this can be deleted after the job.
'''
def main(path):
    #chains = find_chains(path)
    #print chains
    subprocess.call(['mkdir', 'tmp'])
    subprocess.call(['mkdir', 'output'])
    with open('tmp/presort.csv', 'w') as presort:
        subprocess.call(['sort', '-r', '-t,', '-k5', '-k1', path], stdout=presort)
    unique_entries('tmp/presort.csv')
    chains = aggregate_chains('tmp/uniqued.csv')
    classify_data('tmp/uniqued.csv', chains)
    sort_market_or_restaurant('output/independents.csv')

if __name__ == '__main__':
    main("/Users/Arthur/Documents/Coding/health_scores/data/inspections.csv")