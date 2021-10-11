import countReactions



query = {"num_nodes": 3, "oscillator": False}
reactionDicts = countReactions.countAllReactions_query(query)

path = '~/Desktop/3nodeCountsControl.csv'

countReactions.writeOutCounts(path, reactionDicts)
