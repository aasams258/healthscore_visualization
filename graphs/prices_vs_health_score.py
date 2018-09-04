import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import matplotlib.patches as mpatches
from graphs_common import RESTAURANTS_DB

'''
'''
def prices():
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()

    price_counts = '''
        SELECT
            price,
            count(1) as ct
        FROM
            restaurants
        WHERE price IS NOT NULL AND health_grade IS ?
        GROUP BY price
        ORDER BY price asc;
        '''

    grade_distros = [('A', []), ('B', []), ('C', [])]
    for val in grade_distros:
        prices = cursor.execute(price_counts, (val[0],)).fetchall()
        assert len(prices) == 4
        data_pts = float(sum([p[1] for p in prices]))
        for p in prices:
            val[1].append(p[1]/data_pts * 100)

    idx = np.arange(3)
    height = .8

    price_abc = list(zip(grade_distros[0][1], grade_distros[1][1], grade_distros[2][1]))
    bottom = (0,0,0)
    colors = {1: '#FF0000', 2: '#FF7700', 3: '#FFFF00', 4: '#7FFF00', 5: '#03a503'}
    handles = []
    for s in range(0, len(list(price_abc))):
        plt.barh(idx, price_abc[s], height, left=bottom, color=colors[s+1])
        bottom = [sum(x) for x in zip(bottom, price_abc[s])]
        handles.append(mpatches.Patch(color=colors[s+1], label='{}'.format('\\$'*(s+1))))
    db.close()

    
    plt.legend(handles=handles, title="Price")
    plt.title('Yelp Price vs Health Grade')
    plt.xlabel('Percent with Price')
    plt.ylabel('Grade')
    plt.yticks(idx, ["A", "B", "C"])
    plt.xticks(np.arange(0, 110, 10))
    plt.show()

if __name__ == '__main__':
    prices()