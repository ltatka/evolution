import countReactions
import json
import os



# Count Controls
query = {"num_nodes": 3, "oscillator": False}
reactionDicts_control = countReactions.countAllReactions_query(query)
save_path = '~/Desktop/3nodeCountsControl.csv'
control_df = countReactions.writeOutCounts(save_path, reactionDicts_control)

# Count oscillators
query = {"num_nodes": 3, "oscillator": True}
reactionDicts_oscillator = countReactions.countAllReactions_query(query)
save_path = '~/Desktop/3nodeCountsOscillator.csv'
osc_df = countReactions.writeOutCounts(save_path, reactionDicts_oscillator)

# store count dicts as json files
os.chdir('/home/hellsbells/Desktop')
with open('controlCountDict.json', 'w') as outfile1:
    json.dump(reactionDicts_control, outfile1)
with open('oscillatorCountDict.json', 'w') as outfile2:
    json.dump(reactionDicts_oscillator, outfile2)


# Compare statistics
# save_path = '~/Desktop/3nodeComparison.csv'
# results = countReactions.getPValues(save_path, control_df, osc_df)
#
# df1 = control_df['Portion Uni-Uni'][:10]
# df2 = osc_df['Portion Uni-Uni'][:10]
# p = countReactions.permutationTest(df1, df2)