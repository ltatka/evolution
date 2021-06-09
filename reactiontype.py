import numpy as np
import os
import zipfile
import cleanUpMethods as clean


directory = "C:\\Users\\tatka\\Desktop\\Models\\TEST"
isZipFile = False

os.chdir(directory)

all_nReactions = []
all_uniuni = []
all_unibi = []
all_biuni = []
all_bibi = []
all_uniuni_portion = []
all_unibi_portion = []
all_biuni_portion = []
all_bibi_portion= []
all_synthesis = []
all_degradation = []
all_autocatalysis = []
all_catalysis = []
all_synthesis_portion = []
all_degradation_portion = []
all_autocatalysis_portion = []
all_catalysis_portion = []
noSynthesis = 0
noAutocatalysis = 0
noDegradation = 0
noCatalysis = 0

def avg(items):
    return sum(items)/len(items)

count = 0
for filename in os.listdir(directory):
    os.chdir(directory)
    if count%10 == 0:
        print(f"working on model {count}...")
    count +=1
    if isZipFile:
        if filename.endswith('zip'):
            zf = clean.readSavedRun(os.path.join(directory, filename))
            numGenerations = clean.getNumGenerations(zf)
            # Pull out the antimony model
            lines = clean.readModel(zf, numGenerations - 1, 0)
    elif filename.startswith('individual') or filename.startswith('Model'):
        lines = clean.loadAntimonyText(os.path.join(directory, filename))
    else:
        continue

    start = clean.findStart(lines)
    end = clean.findEnd(lines)

    nReactions = 0
    uniuni = 0
    unibi = 0
    biuni = 0
    bibi = 0
    synthesis = 0
    degradation = 0
    autocatalysis = 0
    catalysis = 0

    for i in range(start, end+1):
        if not lines[i].startswith('#') and '->' in lines[i]:  # skip it if it's commented out
            nReactions += 1
            # split each reaction by spaces
            rxnType = ''
            line = lines[i].replace(' ', '')  # strip spaces
            # separate products and reactants by splitting at ->
            reaction = line.split('->')
            # If theres a '+' in the substrates, the reaction is bi-________
            # Else it's uni-________
            if '+' in reaction[0]:
                rxnType += 'bi-'
            else:
                rxnType += 'uni-'
            # Now we do the same thing for the product half
            if len(reaction) > 1:
                if '+' in reaction[1]:
                    rxnType += 'bi'
                else:
                    rxnType += 'uni'
            # Add to the tally
            if rxnType == 'uni-uni':
                uniuni += 1
            elif rxnType == 'uni-bi':
                unibi += 1
            elif rxnType == 'bi-uni':
                biuni += 1
            else:
                print(rxnType)
                bibi += 1

            # Look for "special" reactions
            if rxnType == 'bi-uni' or rxnType == 'uni-bi':
                # separate rate law
                s = reaction[1].split(';')
                reaction2 = s[0]
                ratelaw = s[1]
                # separate individual products and subtrates
                if rxnType.startswith('bi'):
                    substrates = reaction[0].split('+')
                    s1 = substrates[0]
                    s2 = substrates[1]
                else:
                    s1 = reaction[0]
                if rxnType.endswith('bi'):
                    products = reaction2.split('+')
                    p1 = products[0]
                    p2 = products[1]
                else:
                    p1 = reaction2

                # If the reaction is uni-bi and the substrate is also in the product = synthesis (X -> X + Y)
                if rxnType == 'uni-bi' and s1 in products:
                    synthesis += 1
                    # If all three are the same = autocatalysis (X -> X + X)
                    if s1 == p1 and s1 == p2:
                        autocatalysis += 1
                # If the reactions is bi-uni and the product is also in the substrate = degradation (X + Y -> X)
                elif rxnType == 'bi-uni' and p1 in substrates:
                    degradation += 1
                # If the reaction is bi-bi and one of the substrates is also in the product AND the other product is
                # NOT in the substrate at all = catalysis (X + Y -> X + Z) or (X + X -> X + Y)
            elif rxnType == 'bi-bi':
                print(f'{s1} + {s2} -> {p1} + {p2}')
                if s1 == p1 and p2 not in substrates:
                    catalysis += 1
                elif s1 == p2 and p1 not in substrates:
                    catalysis += 1
                elif s2 == p1 and p1 not in substrates:
                    catalysis += 1
                elif s2 == p2 and p2 not in substrates:
                    catalysis += 1

    # Check if this model lacks any "special" reactions
    if synthesis == 0:
        noSynthesis += 1
    if degradation == 0:
        noDegradation += 1
    if autocatalysis == 0:
        noAutocatalysis += 1
    if catalysis == 0:
        noCatalysis += 1

    # Add to total tallies:
    all_nReactions.append(nReactions)
    all_uniuni.append(uniuni)
    all_unibi.append(unibi)
    all_biuni.append(biuni)
    all_bibi.append(bibi)

    all_uniuni_portion.append(uniuni / nReactions)
    all_unibi_portion.append(unibi / nReactions)
    all_biuni_portion.append(biuni / nReactions)
    all_bibi_portion.append(bibi / nReactions)

    all_synthesis.append(synthesis)
    all_degradation.append(degradation)
    all_autocatalysis.append(autocatalysis)
    all_catalysis.append(catalysis)

    all_synthesis_portion.append(synthesis / nReactions)
    all_degradation_portion.append(degradation / nReactions)
    all_autocatalysis_portion.append(autocatalysis / nReactions)
    all_catalysis_portion.append(catalysis / nReactions)

    # Save model summary
    savePath = os.path.join(directory, 'summaries')
    if not os.path.isdir(savePath):
        os.mkdir(savePath)
    os.chdir(savePath)

    with open(os.path.join(savePath, filename[:-4]+'_reaction_summary.txt'), "w") as f:
        f.write(f'total reactions = {nReactions}\n')
        f.write(f'uni-uni = {uniuni} = {uniuni/nReactions}\n')
        f.write(f'bi-uni = {biuni} = {biuni/nReactions}\n')
        f.write(f'uni-bi = {unibi} = {unibi/nReactions}\n')
        f.write(f'bi-bi = {bibi} = {bibi/nReactions}\n')
        f.write(f'synthesis = {synthesis}\n')
        f.write(f'autocatalysis = {autocatalysis}\n')
        f.write(f'degradation = {degradation}\n')
        f.write(f'catalysis = {catalysis}')
        f.close()
    # Summary Summary:

for filename in os.listdir(os.path.join(directory,'summaries')):
    os.chdir((os.path.join(directory,'summaries')))
    if filename.endswith('reaction_summary.txt'):
        try:
            with open('overall_summary.txt', "w") as f:

                f.write(f'total reactions = {avg(all_nReactions)}\n'
                        f'total models = {len(all_uniuni)}\n'
                        f'Number of reactions (avg):\n'
                        f'uni-uni = {avg(all_uniuni)}   +/- {np.std(all_uniuni)}\n'
                        f'uni-bi = {avg(all_unibi)}   +/- {np.std(all_unibi)}\n'
                        f'bi-uni = {avg(all_biuni)}   +/- {np.std(all_biuni)}\n'
                        f'bi-bi = {avg(all_bibi)}  +/- {np.std(all_bibi)}\n'
                        f'synthesis = {avg(all_synthesis)}  +/- {np.std(all_synthesis)}\n'
                        f'autocatalysis = {avg(all_autocatalysis)}  +/- {np.std(all_autocatalysis)}\n'
                        f'degradation = {avg(all_degradation)}  +/- {np.std(all_degradation)}\n'
                        f' catalysis = {avg(all_catalysis)} +/- {np.std(all_catalysis)}\n\n'
                        
                        f'Portion of reactions (avg):\n'
                        f'uni-uni = {avg(all_uniuni_portion)} +/- {np.std(all_uniuni_portion)}\n'
                        f'uni-bi = {avg(all_unibi_portion)} +/- {np.std(all_unibi_portion)}\n'
                        f'bi-uni = {avg(all_biuni_portion)} +/- {np.std(all_biuni_portion)}\n'
                        f'bi-bi = {avg(all_bibi_portion)} +/- {np.std(all_bibi_portion)}\n'
                        f'synthesis = {avg(all_synthesis_portion)} +/- {np.std(all_synthesis_portion)}\n'
                        f'autocatalysis = {avg(all_autocatalysis_portion)} +/- {np.std(all_autocatalysis_portion)}\n'
                        f'degradation = {avg(all_degradation_portion)} +/- {np.std(all_degradation_portion)}\n'
                        f'catalysis = {avg(all_catalysis_portion)} +/- {np.std(all_catalysis_portion)}\n\n'

                        f'models with 0 synthesis reactions: = {noSynthesis}\n'
                        f'models with 0 autocatalysis reactions: = {noAutocatalysis}\n'
                        f'models with 0 degradation reactions: = {noDegradation}\n'
                        f'models with 0 catalysis reactions: = {noCatalysis}\n'
                        )
                f.close()
        except FileNotFoundError:
            continue

