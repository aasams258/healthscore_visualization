# Helper class for all graphs
from numpy import polyfit, poly1d # For lin regressions.

A_BLUE ='#036AD1'
B_GREEN = '#3BB92A'
C_YELLOW = '#FB9517'

RESTAURANTS_DB = "../LA_restaurants.db"

'''
Get the colors that match most closely to the grade placards.
'''
def get_grade_color(val):
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
        return '#000000' # Unknown will be Black


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
    return (coefs, 1.0-(SS_res/SS_tot))