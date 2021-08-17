import os
import cleanUpMethods as clean




def checkMakeDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)



def process_damped(parent_dir, save_dir):
    checkMakeDir(parent_dir)
    checkMakeDir(save_dir)
    for filename in os.listdir(parent_dir):
        os.chdir(parent_dir)
        if not filename.endswith('.ant'):
            continue
        ant = clean.loadAntimonyText_noLines(filename)
        try:
            isDamped, toInf = clean.isModelDampled(ant)
            if not isDamped and not toInf:
                os.chdir(save_dir)
                with open(f'{filename}', "w") as f:
                    f.write(ant)
                    f.close()
        except Exception as e:
            print(f"Fail: {filename}\n{e}")




#
# ant = clean.loadAntimonyText_noLines("C:\\Users\\tatka\\Desktop\\Models\\TEST\\osc4.ant")

# r = te.loada(ant)
# m = r.simulate(0,100,1000)
# clean.check_infinity(m)
#
#
# damped = clean.isModelDampled(ant)
# print(f'Is damped: {damped}')
# #
# import tellurium as te
# #
# r = te.loada(ant)
# result = r.simulate(0,1000,5000)
# # r.plot()
#
# import pylab
# pylab.plot (result[4900:,2])
# pylab.show()
#
# from scipy.signal import find_peaks
# peaks, _ = find_peaks(result[4900:,2], prominence=1)
# print(f'Peaks found: {len(peaks)}')
#
#
