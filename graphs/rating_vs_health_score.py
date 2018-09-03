import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import matplotlib.patches as mpatches

from graphs_common import RESTAURANTS_DB

def yelp_score_v_health_score():
    colors = {1: '#FF0000', 2: '#FF7700', 3: '#FFFF00', 4: '#7FFF00', 5: '#03a503'}
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()
    # Query for the count of ratings per health score.
    # Used for normalization.
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
    
    query_get_scores = '''
        SELECT
            health_score,
            count(rating)
        FROM restaurants
        WHERE rating = ? or rating = ?
        GROUP BY health_score
        HAVING health_score > 69
        ORDER BY health_score desc
        ;
    '''
    for score in range(1, 6, 1):
        half_score = score + .5
        cursor.execute(query_get_scores, (score, half_score, ))
        score_ratings = cursor.fetchall()
        # Normalize ratings to %'s.
        scores, counts = [], []
        for k,v in score_ratings:
            scores.append(k)
            counts.append(v/denominators.get(k, 1.0) * 100.0)
        plt.scatter(scores, counts, c=colors[score])
    db.close()
    plt.title('Health Score vs Yelp Review Score')
    plt.xlabel('Health Score')
    plt.ylabel('Percentage with Review Score')
    handles = []
    for k, v in colors.items():
        handles.append(mpatches.Patch(color=v, label='{}'.format(k)))
    plt.legend(handles=handles, title="Yelp Review Score", ncol=5, loc='upper center')
    plt.yticks(np.arange(0, 105, 10))
    plt.show()

if __name__ == "__main__":
    yelp_score_v_health_score()