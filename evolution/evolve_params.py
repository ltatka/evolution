import evolUtils as ev


ant = '''    
var S0
var S1
var S2
#S2 -> S1; k0*S2
S2 + S0 -> S0; k1*S2*S0
S0 -> S2; k2*S0
S2 -> S2+S2; k3*S2
#S1 -> S0+S2; k4*S1
k0 = 3.708920735583032
k1 = 4.027285355118902
k2 = 7.450108022248875
k3 = 145.89432306715088
k4 = 16.371587764670334
S0 = 1.0
S1 = 5.0
S2 = 9.0
'''

evolver = ev.Evolver(antimony=ant)

evolver.evolve()