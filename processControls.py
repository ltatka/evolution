import postprocessReactions as pp
from oscillatorDB import mongoMethods as mm
from damped_analysis import isModelDampled
import countReactions as cr

# Delete the current 3-node non-oscillators in database

query = {"num_nodes": 3, "isControl": True}

r = mm.query_database(query)

for item in r[0]:
    print(item)
# proceed = mm.yes_or_no("Do you want to proceed?")
# if proceed:
#     mm.delete_by_query(query, yesno=False)

control = cr.makeList({"isControl": True}, "Degradation Present")
print(control)
osc = cr.makeList({"num_nodes":3, "oscillator":True}, "Degradation Present")

cr.permutationTest(control, osc)