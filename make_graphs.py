import numpy as np
import matplotlib.pyplot as plt
import sqlite3

# Supply a list of category aliases to fetch.
# Returns a tuple of (A, B, C, Category_Names) lists.
def _load_breakdown_data(categories):
    db = sqlite3.connect("LA_restaurants.db")
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

    #
    # special categories combine them: "tradamerican", "newamerican",
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
                if len(result) < 3:
                    print (result)
                grades_list.append(result[2])
                # Get the proper name.
                formal_name = result[1]
            else:
                grades_list.append(0)
        category_names.append(formal_name)
    db.close()
    return(a_grades, b_grades, c_grades, category_names)

def bar_plot():
    category_alias = ["mexican", "chinese", "japanese", "pizza", "burgers", 
    "italian", "korean", "thai", "mediterranean", "indpak", "mideastern", "french", "tradamerican", "newamerican"]
    a, b, c, names = _load_breakdown_data(category_alias)
    N = len(category_alias)
    ind = np.arange(N)

    height = .8
    p1 = plt.barh(ind, a, height, color='#036AD1')
    p2 = plt.barh(ind, b, height, left=a, color='#3BB92A')
    # Need to set the x Axis starting point for C grades.
    c_bottom = [x + y for x, y in zip(a, b)]
    p3 = plt.barh(ind, c, height, left=c_bottom, color='#FB9517')

    plt.title('Health Grade by Food Category')
    plt.xlabel('Restaurant Count')
    plt.xticks(np.arange(0, 2500, 200))
    plt.ylabel('Food Category')
    plt.yticks(ind, names)

    plt.legend((p1[0], p2[0], p3[0]), ('A', 'B', 'C'))

    plt.show()

def grade_pie():
    db = sqlite3.connect("LA_restaurants.db")
    cursor = db.cursor()
    query = '''
        SELECT
            restaurants.health_grade,
            count(1) as ct
        FROM restaurants
        GROUP BY health_grade
        ORDER BY ct DESC
    '''
    cursor.execute(query)
    results = cursor.fetchall()[0:3]
    labels, counts = zip(*results)
    _, _, autotexts = plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=['#036AD1', '#3BB92A', '#FB9517'])
    plt.axis('equal')
    for autotext in autotexts:
        autotext.set_color('white')
    plt.show()

if __name__ == '__main__':
    #bar_plot()
    grade_pie()