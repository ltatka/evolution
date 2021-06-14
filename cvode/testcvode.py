

from uLoadCvode import TCvode
import matplotlib.pyplot as plt

#def fcnModel (t, y, ydot, user_data):
#    cvode.setVectorValue (ydot, 0, -0.1*cvode.getVectorValue (y, 0))
#    return 0

def fcnModel (t, y, ydot, user_data):
    y0 = cvode.getVectorValue (y, 0)
    y1 = cvode.getVectorValue (y, 1)
    print ('yo = ', y0, y1)
    dy0 = -0.1*y0
    dy1 = 0.1*y0 - 0.08*y1

    cvode.setVectorValue (ydot, 0, dy0)
    cvode.setVectorValue (ydot, 1, dy1)
    return 0

cvode = TCvode()
cvode.setModel(fcnModel)
y0 = [10.0, 0]; n = 2
cvode.initialize (n, y0)
cvode.setTolerances ()


hstep = 1
t = 0

#for i in range (10):
t, y = cvode.oneStep (t, hstep)
    
#m = cvode.simulate (0, 20, 10)
#plt.plot (m[:,0], m[:,1])
