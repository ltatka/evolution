import countReactions


query = {'num_nodes': 3, 'oscillator': True}

reactionDicts = countReactions.countAllReactions(query)

path = '~/Desktop/3nodeCounts.csv'

countReactions.writeOutCounts(path, reactionDicts)
