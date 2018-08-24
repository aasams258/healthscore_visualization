'''
This class generates the various graphs in the analysis.

No real order here.
'''
import numpy as np
from numpy import polyfit, poly1d # For lin regressions.
import matplotlib.pyplot as plt
import sqlite3
import matplotlib.patches as mpatches

A_BLUE ='#036AD1'
B_GREEN = '#3BB92A'
C_YELLOW = '#FB9517'

def _get_color(val):
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

'''
Supply a list of category aliases to fetch.
Returns a tuple of (A, B, C, Category_Names) lists.
'''
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
    colors = [_get_color(x) for x in grades]
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

'''
Do a linear regression on X,Y and return the R^2 value, as well as the Coefficents.

Returns ([coefficients], R2 error).
Where coefficients are (a,b) for ax + b
'''
def regression(x,y):
    coefs = polyfit(x,y,1)
    regres_fn = poly1d(coefs)
    y_f = [regres_fn(x_i) for x_i in x]
    # Variables for R-Square computation.
    y_hat = sum(y)/float(len(y))
    SS_tot = sum(map(lambda y_i: (y_i - y_hat)**2, y))
    SS_res = sum(map(lambda y_i, f_i: (y_i - f_i)**2, y, y_f))
    print(x)
    print()
    print(list(map(lambda y_i, f_i: (y_i - f_i), y, y_f)))
    return (coefs, 1.0-(SS_res/SS_tot))

def yelp_score_distro():
    colors = {1: '#FF0000', 2: '#FF7700', 3: '#FFFF00', 4: '#7FFF00', 5: '#03a503'}
    db = sqlite3.connect("LA_restaurants.db")
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
    
    plt.title('Health Score vs Yelp Review Score')
    plt.xlabel('Health Score')
    plt.ylabel('Percentage with Review Score')
    handles = []
    for k, v in colors.items():
        handles.append(mpatches.Patch(color=v, label='{}'.format(k)))
    plt.legend(handles=handles, title="Yelp Review Score", ncol=5, loc='upper center')
    plt.yticks(np.arange(0, 105, 10))
    plt.show()

def avg_yelp_score_health_score():
    db = sqlite3.connect("LA_restaurants.db")
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
   

    plt.title('Average Yelp Review Score Per Health Score')
    plt.xlabel('Health Score')
    plt.ylabel('Average Review Score')
    plt.scatter(keys, avg_scores)
    # Plot a Regression.
    coefs, r_sq = regression(keys, avg_scores)
    regres_fn = poly1d(coefs)
    y_f = [regres_fn(x_i) for x_i in keys]
    print (r_sq)
    plt.plot(keys, y_f, 'b-')
    plt.yticks(np.arange(3, 5, .5))
    plt.text(97, 3.1, "R^2 = {0:.2f}".format(r_sq), style='italic',
        bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
    plt.show()

def review_vs_score_scatter():
    db = sqlite3.connect("LA_restaurants.db")
    cursor = db.cursor()
    # Query for the amount of ratings there are.
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

    query_counts = '''
        SELECT
         health_score,
         SUM(review_count)
        FROM restaurants
        GROUP BY health_score
        ORDER BY health_score desc;
        '''
    review_sums = cursor.execute(query_counts).fetchall()
    avg_counts = []
    keys = []
    for k,v in review_sums:
        avg_counts.append(v/denominators.get(k, 1.0))
        keys.append(k)

    plt.title('Yelp Reviews vs Health Score')
    plt.xlabel('Health Score')
    plt.ylabel('Average Number of Reviews')
    plt.scatter(keys, avg_counts)
    # Plot a Regression.
    # coefs, r_sq = regression(keys, avg_scores)
    # regres_fn = poly1d(coefs)
    # y_f = [regres_fn(x_i) for x_i in keys]
    # print (r_sq)
    # plt.plot(keys, y_f, 'b-')
    # plt.yticks(np.arange(3, 5, .5))
    # plt.text(97, 3.1, "R^2 = {0:.2f}".format(r_sq), style='italic',
    #     bbox={'facecolor':'red', 'alpha':0.5, 'pad':5})
    plt.show()

def prices():
    pass
    # Graph, Grade VS Price, where its normalized by total amount in that price range.
    # EG: $$$$ are 70% A, 30% B .
# Comment which graphs you would like generated.
if __name__ == '__main__':
    #category_bar_plot()
    #grade_pie()
    #score_histogram()
    #yelp_score_distro()
    #avg_yelp_score_health_score()
    review_vs_score_scatter()