import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import matplotlib.patches as mpatches

from graphs_common import RESTAURANTS_DB
from graphs_common import get_grade_color

"""
Health Score Histogram
"""
def score_histogram():
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()
    query = '''
        SELECT
            health_score,
            health_grade,
            count(1) as ct
        FROM
            restaurants
        GROUP BY health_score
        ORDER BY health_score desc;
    '''
    cursor.execute(query)
    scores, grades, counts = zip(*cursor.fetchall())
    colors = [get_grade_color(x) for x in grades]
    idx = np.arange(len(scores))
    
    plt.bar(idx, counts, width=1, color=colors)

    plt.title('Health Score Distribution')
    plt.xlabel('Health Score')
    #plt.yticks(np.arange(0, 100, 10))
    plt.ylabel('Number of Restaurants with Score')
    plt.xticks(idx, scores)
    a_color = mpatches.Patch(color=get_grade_color('A'), label='A Grade')
    b_color = mpatches.Patch(color=get_grade_color('B'), label='B Grade')
    c_color = mpatches.Patch(color=get_grade_color('C'), label='C Grade')
    plt.legend(handles=[a_color, b_color, c_color])

    plt.show()

if __name__ == '__main__':
    score_histogram()