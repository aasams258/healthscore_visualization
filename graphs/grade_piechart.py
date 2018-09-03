import matplotlib.pyplot as plt
import sqlite3

from graphs_common import get_grade_color
from graphs_common import RESTAURANTS_DB

def grade_pie():
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()
    query = '''
        SELECT
            restaurants.health_grade,
            count(1) as ct
        FROM restaurants
        WHERE restaurants.health_grade is not ' '
        GROUP BY health_grade
        ORDER BY ct DESC
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    labels, counts = zip(*results)
    print (labels)
    _, texts, autotexts = plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=[get_grade_color('A'),get_grade_color('B'),get_grade_color('C')])
    plt.axis('equal')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_size('large')
    for text in texts:
        text.set_color(get_grade_color(text.get_text()))
        text.set_size('30')
    db.close()
    plt.title('Health Grade Distribution')
    plt.show()


if __name__ == '__main__':
    grade_pie()