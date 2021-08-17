import os
import cleanUpMethods as clean


def isMassConserved(source_dir, true_dir, false_dir):
    for file in os.listdir(source_dir):
        if file == 'Model_3246966383208899508.ant':
            print('here')
        os.chdir(source_dir)
        ant = clean.loadAntimonyText(file)
        full_ant = clean.loadAntimonyText_noLines(file)
        global massConserved
        massConserved = True
        for line in ant:
            if '->' in line and not line.startswith('#'):
                line = line.replace(' ', '')  # strip spaces
                if line == 'S1->S1+S2;k1*S1' or line == 'S1->S2+S1;k1*S1':
                    print('hi')
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
                        os.chdir(false_dir)
                        with open(file, "w") as f:
                            f.write(full_ant)
                            f.close()
                        # If we find a reaction that violates mass conservation, we can move to the next model
                        massConserved = False
                        break
                elif rxnType == 'bi-uni':
                    # products is already one item, need to split reactants
                    reactants = reactants.split('+')
                    if products in reactants:
                        # mass is not conserved, write to dir
                        os.chdir(false_dir)
                        with open(file, "w") as f:
                            f.write(full_ant)
                            f.close()
                        # If we find a reaction that violates mass conservation, we can move to the next model
                        massConserved = False
                        break
                else: # If the reaction type is uni-uni or bi-bi, we ignore and move to next reaction
                    continue
            else: # if the line is not a reaction, move to the next line
                continue
            # If we've gone through every reaction without breaking out of the loop and changing the status of
            # massConserved, then we can write the model out to the true_dir
            if massConserved:
                os.chdir(true_dir)
                with open(file, "w") as f:
                    f.write(full_ant)
                    f.close()



