import evolUtils as ev


ant = '''
var S0
var S1
var S2
S2 -> S1; k0*S2
S2 + S0 -> S0; k1*S2*S0
S2 -> S2+S2; k2*S2
S1 -> S0+S2; k3*S1
k0 = 9.934763571703128
k1 = 11.052219344700799
k2 = 95.19348327982753
k3 = 81.87268654914789
S0 = 1.0
S1 = 5.0
S2 = 9.0
'''

evolver = ev.Evolver(antimony=ant)

evolver.evolve()