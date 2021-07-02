from pymongo import MongoClient
import os
import pymongo
import cleanUpMethods as clean


class Connect(object):

    @staticmethod
    def get_connection():
        return MongoClient("mongodb+srv://data:VuRWQ@networks.wqx1t.mongodb.net")

    connection = Connect.get_connection()

    # Path to models to add
    dir = 'C:\\Users\\tatka\\Desktop\\Models\\3node_oscillator\\trimmed_antimony'
    nNodes = 3
    oscillator = True

    # user: data
    # pwd:  VuRWQ
    astr = "mongodb+srv://data:VuRWQ@networks.wqx1t.mongodb.net"
    client = MongoClient(astr)
    database_names = client.list_database_names()
    db = client['networks']
    col = db['networks']
    #
    # modelList = []
    # os.chdir(dir)
    # for filename in os.listdir(dir):
    #     os.chdir(dir)
    #     os.chdir(filename)
    #
    #     ant_lines = clean.loadAntimonyText(f'{filename}.ant')
    #     nReactions = clean.getNumReactions(ant_lines)
    #     ant = clean.loadAntimonyText_noLines(f'{filename}.ant')
    #
    #     modelDict = {}
    #     modelDict['ID'] = filename
    #     modelDict['num_nodes'] = nNodes
    #     modelDict['num_reactions'] = nReactions
    #     modelDict['model'] = ant
    #     modelList.append(modelDict)
    #
    # col.insert_many(modelList)

    query = {'ID': '4590'}
    doc = col.find(query)
    for x in doc:
        print(x['model'])

    query = {'num_reactions': '4590'}
    doc = col.find(query)
    for x in doc:
        print(x['model'])
