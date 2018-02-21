from sympy import *
from sympy import symbols
from sympy import expand, factor
import math
import numpy 

x = symbols('x')
a = Integral(cos(x)*exp(x), x)
print Eq(a, a.doit())

print math.sqrt(9)
print sqrt(9)
print sqrt(8)

x, y = symbols('x y')
expr = x + 2*y
r = [expr, (expr+1),  (expr-x)] #note: reduced '- X'
r = [ str(i) for i in r]
print ' | '.join(r)

expanded_expr = expand(x*expr)
print expanded_expr
print factor(expanded_expr)

x, t, z, nu = symbols('x t z nu')
init_printing(use_unicode=True)

print diff(sin(x)*exp(x), x) #dirivative of sin(x)*(E^x)
print integrate(exp(x)*sin(x) + exp(x)*cos(x), x)
print integrate(sin(x**2), (x, -oo, oo))
print limit(sin(x)/x, x, 0) #x --> 0
print solve(x**2 - 2, x) # x^2 -2 = 0

y = Function('y')
# solve differential equation y'' - y = e^t
print dsolve(Eq(y(t).diff(t, t) - y(t), exp(t)), y(t))
print Matrix([[1, 2], [2, 2]]).eigenvals()
print besselj(nu, z).rewrite(jn)
print latex(Integral(cos(x)**2, (x, 0, pi)))

#substitution
x, y = symbols('x y')
expr = cos(x) + 1
print expr.subs(x, y)

expr = x**y + 1
print expr.subs(y, x**y)
print expr.subs(y, x**x)

expr = sin(2*x) + cos(2*x)
print expand_trig(expr)
print expr.subs(sin(2*x), 2*sin(x)*cos(x))

expr = x**3 + 4*x*y - z
print expr.subs([(x, 2), (y, 4), (z, 0)])

str_expr = "x**2 + 3*x - 1/2"
expr = sympify(str_expr)
print expr

expr = sqrt(8)
print expr.evalf()

expr = cos(2*x)
print expr.evalf(subs={x: 2.4})

#lambda
#lambdify uses eval. Don't use it on unsanitized input.
a = numpy.arange(10) 
expr = sin(x)
f = lambdify(x, expr, "numpy")
print f(a)

f = lambdify(x, expr, "math")
print f(0.1)

def mysin(x):
    """
    My sine. Note that this is only accurate for small x.
    """
    return x
f = lambdify(x, expr, {"sin":mysin})
print f(0.1)

#simplify
print simplify(sin(x)**2 + cos(x)**2)
print simplify((x**3 + x**2 - x - 1)/(x**2 + 2*x + 1))
print simplify(gamma(x)/gamma(x - 2))

#expand
print expand((x + 1)**2)



