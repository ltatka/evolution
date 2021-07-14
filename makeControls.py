import os
import cleanUpMethods as clean


parent_dir = "/home/hellsbells/Desktop/3nodeControls"
save_dir = "/home/hellsbells/Desktop/3nodeControls-success"



os.chdir(parent_dir)
for filename in os.listdir(parent_dir):
    os.chdir(parent_dir)
    with open(filename, "r") as f:
        ant = f.read()
    try:
        isDamped, toInf = clean.isModelDampled(ant)
        print(isDamped, toInf)
        if isDamped==True and toInf==False:

            # savepath = os.path.join(save_dir, f'{filename[:-4]}.ant')

            os.chdir(save_dir)
            with open(f'{filename}', "w") as f:
                f.write(ant)
                f.close()
    except Exception as e:
        print(e)
        continue