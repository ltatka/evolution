from oscillatorDB import mongoMethods as mm
import countReactions as cr

query = {"num_nodes":3, "oscillator":True, "Autocatalysis Present": True}

reactionDicts_oscillator = cr.gatherCounts_query(query)
save_path = '~/Desktop/AC_newP_AConly.csv'
cr.writeOutCounts(save_path, reactionDicts_oscillator)