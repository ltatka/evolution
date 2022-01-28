import tellurium as te
from sympy import *#symbols, diff, subs
import numpy as np


astr = '''
S1 -> S2; k1*S1
S2 -> S1 + S3; k2*S2
S3 + S3 -> S1; k3*S3*S3

S1 = 2
S2 = 4
S3 = 6

k1 = 1
k2 = 3
k3 = 5


'''
r = te.loada(astr)


# st = te.getODEsFromModel(r)
print(te.getODEsFromModel(r))
#
# equations = st.split('\n\n')[1]
# equations = equations.split('\n')[0:3]
#
# v_J0, v_J1, v_J2 = symbols('v_J0 v_J1 v_J2', real=True)
# eq1 = equations[0].split(' = ')[1]
# print(eq1)
# f1 = eval(eq1)
# print(diff(f1, v_J0))

# def get_jacobian(r):
v_J0, v_J1, v_J2 = symbols('v_J0 v_J1 v_J2', real=True)
eqs = te.getODEsFromModel(r)
eqs = eqs.split('\n\n')
rates = eqs[0]
rates = rates.split('\n')[1:]
eqs = eqs[1]
rts = []
for rate in rates:
    rts.append(rate.split(" = ")[1])

eqs = eqs.split('\n')[0:3]
equations = []
for i, eq in enumerate(eqs):
    expr = eq.split(' = ')[1]
    equations.append(eq.split(' = ')[1])
v_J0, v_J1, v_J2 = symbols('v_J0 v_J1 v_J2', real=True)
reactions = [v_J0, v_J1, v_J2]
f1 = eval(equations[0])
for i, r in enumerate(reactions):
    print(r)
    print(rts[i])
    f1.subs(r, rts[i])
print(f1)


# reactions = [v_J0, v_J1, v_J2]
# j = np.zeros([3, 3])
# for i, reaction in enumerate(reactions):
#     for eq in range(3):
#         f = eval(equations[eq])
#         j[eq][i] = diff(f, reaction)
#
# print(j)
#
#
# print(r.getFullJacobian())


