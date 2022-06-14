import evolUtils as ev


ant = '''    
var S0
var S1
var S2
S1 -> S1+S0; k0*S1
S2 + S0 -> S0; k1*S2*S0
S2 -> S2+S1; k2*S2
#S0 -> S1; k3*S0
#S1 -> S2; k4*S1
S2 -> S2+S2; k5*S2
k0 = 2.5836905794022447
k1 = 25.106972765617158
k2 = 5.695887678366729
k3 = 12.408803541819541
k4 = 28.62393939037338
k5 = 63.57736252811988
S0 = 1.0
S1 = 5.0
S2 = 9.0
'''

evolver = ev.Evolver(antimony=ant)

evolver.evolve()