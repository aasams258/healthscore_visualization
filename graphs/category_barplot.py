import matplotlib.pyplot as plt
import sqlite3
import numpy as np
import matplotlib.patches as mpatches

from graphs_common import RESTAURANTS_DB
from graphs_common import get_grade_color

'''
Supply a list of category aliases to fetch.
Returns a tuple of (A, B, C, Category_Names) lists.
'''
def _load_breakdown_data(categories):
    db = sqlite3.connect(RESTAURANTS_DB)
    cursor = db.cursor()
    grade_fetch_query = ''' 
        SELECT 
            restaurants.health_grade,
            categories.category_name,
            COUNT(1)
        FROM restaurants
        JOIN categories ON restaurants.id=categories.restaurant_id
        WHERE categories.category_alias=? and restaurants.health_grade=?
        GROUP BY restaurants.health_grade 
    '''
    a_grades = []
    b_grades = []
    c_grades = []
    category_names = []
    for category in categories:
        formal_name = ""
        for grade_tuple in [('A', a_grades), ('B', b_grades), ('C', c_grades)]:
            grades_list = grade_tuple[1]
            cursor.execute(grade_fetch_query, (category, grade_tuple[0],))
            result = cursor.fetchone()
            if result:
                assert len(result) == 3
                grades_list.append(result[2])
                # Get the proper name.
                formal_name = result[1]
            else:
                grades_list.append(0)
        category_names.append(formal_name)
    db.close()
    return(a_grades, b_grades, c_grades, category_names)

def category_bar_plot():
    # Include "tradamerican", "newamerican"?
    category_alias = ["mexican", "chinese", "japanese", "korean", "thai", 
    "pizza", "burgers", "italian", "french", "mediterranean", "indpak", "mideastern"]
    a, b, c, names = _load_breakdown_data(category_alias)
    idx = np.arange(len(category_alias))
    denominator = [sum(x) for x in zip(a,b,c)]
    divide = lambda x: float(x[0])/x[1] if x[1] != 0 else 0 
    a_norm = [divide(x) * 100 for x in zip(a, denominator)]
    b_norm = [divide(x) * 100 for x in zip(b, denominator)]
    c_norm = [divide(x) * 100 for x in zip(c, denominator)]
    height = .8
    p1 = plt.barh(idx, c_norm, height, color=get_grade_color('C'))
    p2 = plt.barh(idx, b_norm, height, left=c_norm, color=get_grade_color('B'))
    # Need to set the x Axis starting point for C grades.
    a_bottom = [x + y for x, y in zip(b_norm, c_norm)]
    p3 = plt.barh(idx, a_norm, height, left=a_bottom, color=get_grade_color('A'))
    plt.title('Health Grade by Food Category')
    plt.xlabel('Percentage with Grade')
    plt.xticks(np.arange(0, 105, 5))
    plt.ylabel('Food Category')
    plt.yticks(idx, names)

    plt.legend((p1[0], p2[0], p3[0]), ('A', 'B', 'C'))

    plt.show()

if __name__ == "__main__":
    category_bar_plot()