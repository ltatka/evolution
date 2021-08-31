import os
import antUtils


def isMassConserved_single(ant):
    ant = ant.splitlines()
    for line in ant:
        if '->' in line and not line.startswith('#'):
            line = line.replace(' ', '')  # strip spaces
            # separate products and reactants by splitting at ->
            reaction = line.split('->')
            reactants = reaction[0]
            # Remove the rate constant part
            products = reaction[1].split(';')[0]
            rxnType = ''
            # Get reaction type by number of reactants and products
            if '+' in reactants:
                rxnType += 'bi-'
            else:
                rxnType += 'uni-'
            # Now we do the same thing for the product half
            if '+' in products:
                rxnType += 'bi'
            else:
                rxnType += 'uni'

            if rxnType == 'uni-bi':
                # Separate products (reactants is already just one item
                products = products.split('+')
                if reactants in products:
                    # mass is not conserved, write to dir
                    return False
            elif rxnType == 'bi-uni':
                # products is already one item, need to split reactants
                reactants = reactants.split('+')
                if products in reactants:
                    # mass is not conserved, write to dir
                    return False
            else:  # If the reaction type is uni-uni or bi-bi, we ignore and move to next reaction
                continue
        else:  # if the line is not a reaction, move to the next line
            continue
    return True

def isMassConserved(source_dir, true_dir, false_dir):
    if not os.path.isdir(source_dir):
        raise ValueError('The given source directory does not exist')
    antUtils.checkMakeDir(true_dir)
    antUtils.checkMakeDir(false_dir)
    for file in os.listdir(source_dir):
        os.chdir(source_dir)
        full_ant = antUtils.loadAntimonyText_noLines(file)
        massConserved = isMassConserved_single(full_ant)
        if massConserved:
            os.chdir(true_dir)
        else:
            os.chdir(false_dir)
        with open(file, "w") as f:
            f.write(full_ant)
            f.close()
