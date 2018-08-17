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
    p1 = plt.barh(idx, c_norm, height, color=C_YELLOW)
    p2 = plt.barh(idx, b_norm, height, left=c_norm, color=B_GREEN)
    # Need to set the x Axis starting point for C grades.
    a_bottom = [x + y for x, y in zip(b_norm, c_norm)]
    p3 = plt.barh(idx, a_norm, height, left=a_bottom, color=A_BLUE)
    plt.title('Health Grade by Food Category')
    plt.xlabel('Percentage with Grade')
    plt.xticks(np.arange(0, 105, 5))
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
    plt.ylabel('Number of Restaurants with Score')
    plt.xticks(idx, scores)
    a_color = mpatches.Patch(color=A_BLUE, label='A Grade')
    b_color = mpatches.Patch(color=B_GREEN, label='B Grade')
    c_color = mpatches.Patch(color=C_YELLOW, label='C Grade')
    plt.legend(handles=[a_color, b_color, c_color])

    plt.show()

# RGB in 0,1 scale.
# Num should be >2
def gen_rg_color(num):
    # Grab Num points between -1 and 1.
    # Neg values are R and Pos Are G spectrum

    # Start at full red, slowly step up Green.
    # When at max green, step down red.
    # Odd include yellow, even no yellow.
    lst = []
    for r in range(0,num,1):
        print (r)
        step = r/float(num)
        lst.append((1-step, step, 0))
    return lst

def plot_lines():
    colors = {1: '#FF0000', 2: '#FF7700', 3: '#FFFF00', 4: '#7FFF00', 5: '#03a503'}
    db = sqlite3.connect("LA_restaurants.db")
    cursor = db.cursor()
    query_get_count = '''
        SELECT
            health_score,
            count(1)
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
            count(1)
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
        # Normalize ratings to %
        scores, counts = [], []
        for k,v in score_ratings:
            scores.append(k)
            counts.append(v/denominators.get(k, 1.0) * 100.0)
        #scores, counts = zip(*cursor.fetchall())
        plt.scatter(scores, counts, c=colors[score])
    #plt.plot([4,3,2,1], [1,4,9,16], 'bo')
    plt.title('Health Score vs Yelp Review Score')
    plt.xlabel('Health Score')
    #plt.yticks(np.arange(0, 100, 10))
    plt.ylabel('Percentage with Review Score')
    handles = []
    for k, v in colors.items():
        if k < 5:
            handles.append(mpatches.Patch(color=v, label='[{}, {}.5]'.format(k, k)))
        if k == 5:
            handles.append(mpatches.Patch(color=v, label='[{}]'.format(k)))
    plt.legend(handles=handles, title="Review Score", ncol=5, loc='upper center')
    plt.yticks(np.arange(0, 105, 10))
    plt.show()

if __name__ == '__main__':
    #bar_plot()
    #grade_pie()
    #score_histogram()
    plot_lines()
   # print (gen_rg_color(8))