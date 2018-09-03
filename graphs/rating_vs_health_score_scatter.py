import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import matplotlib.patches as mpatches
from numpy import poly1d
from graphs_common import RESTAURANTS_DB
from graphs_common import get_grade_color
from graphs_common import regression

def avg_yelp_score_health_score():
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()
    # Query for the amount of ratings there are.
    query_get_count = '''
        SELECT
            health_score,
            count(rating)
        FROM restaurants
        GROUP BY health_score
        ORDER BY health_score desc
    '''
    score_counts = cursor.execute(query_get_count).fetchall()
    denominators = {}
    for k,v in score_counts:
        denominators[k] = float(v)
    
    query_score_sum = '''
            SELECT
            health_score,
            sum(rating)
        FROM restaurants
        GROUP BY health_score
        HAVING health_score > 69
        ORDER BY health_score desc
        '''
    score_sums = cursor.execute(query_score_sum).fetchall()
    avg_scores = []
    keys = []
    for k,v in score_sums:
        avg_scores.append(v/denominators.get(k, 1.0))
        keys.append(k)
   
    db.close()
    plt.title('Average Yelp Review Score Per Health Score')
    plt.xlabel('Health Score')
    plt.ylabel('Average Review Score')
    plt.scatter(keys, avg_scores)
    # Plot a Regression.
    coefs, r_sq = regression(keys, avg_scores)
    regres_fn = poly1d(coefs)
    y_f = [regres_fn(x_i) for x_i in keys]
    plt.plot(keys, y_f, 'b-')
    plt.yticks(np.arange(3, 5, .5))
    plt.text(97, 3.1, "R^2 = {0:.2f}".format(r_sq), style='italic',
        bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
    plt.show()

if __name__ == "__main__":
    avg_yelp_score_health_score()