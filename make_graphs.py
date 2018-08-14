import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.patches as mpatches

A_BLUE ='#036AD1'
B_GREEN = '#3BB92A'
C_YELLOW = '#FB9517'

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
    idx = np.arange(len(category_alias))

    height = .8
    p1 = plt.barh(idx, a, height, color='#036AD1')
    p2 = plt.barh(idx, b, height, left=a, color='#3BB92A')
    # Need to set the x Axis starting point for C grades.
    c_bottom = [x + y for x, y in zip(a, b)]
    p3 = plt.barh(idx, c, height, left=c_bottom, color='#FB9517')

    plt.title('Health Grade by Food Category')
    plt.xlabel('Restaurant Count')
    plt.xticks(np.arange(0, 2500, 200))
    plt.ylabel('Food Category')
    plt.yticks(idx, names)

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
        WHERE restaurants.health_grade is not ' '
        GROUP BY health_grade
        ORDER BY ct DESC
    '''
    cursor.execute(query)
    results = cursor.fetchall()
    labels, counts = zip(*results)
    _, texts, autotexts = plt.pie(counts, labels=labels, autopct='%1.1f%%', colors=['#036AD1', '#3BB92A', '#FB9517'])
    plt.axis('equal')
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_size('large')
    for text in texts:
        if (text.get_text() == 'A'):
            text.set_color(A_BLUE)
        if (text.get_text() == 'B'):
            text.set_color(B_GREEN)
        if (text.get_text() == 'C'):
            text.set_color(C_YELLOW)
        text.set_size('30')
    plt.title('Health Grade Distribution')
    plt.show()

def get_color(val):
    A_BLUE ='#036AD1'
    B_GREEN = '#3BB92A'
    C_YELLOW = '#FB9517'
    if val == 'A':
        return A_BLUE
    if val == 'B':
        return B_GREEN
    if val == 'C':
        return C_YELLOW
    else:
        return '#000000' # Black

def score_histogram():
    db = sqlite3.connect("LA_restaurants.db")
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
    colors = [get_color(x) for x in grades]
    idx = np.arange(len(scores))
    
    plt.bar(idx, counts, width=1, color=colors)

    plt.title('Health Score Distribution')
    plt.xlabel('Health Score')
    #plt.yticks(np.arange(0, 100, 10))
    plt.ylabel('Count')
    plt.xticks(idx, scores)
    a_color = mpatches.Patch(color=A_BLUE, label='A Grade')
    b_color = mpatches.Patch(color=B_GREEN, label='B Grade')
    c_color = mpatches.Patch(color=C_YELLOW, label='C Grade')
    plt.legend(handles=[a_color, b_color, c_color])

    plt.show()

if __name__ == '__main__':
    #bar_plot()
    #grade_pie()
    score_histogram()