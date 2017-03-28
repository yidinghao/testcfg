"""
    Alexander Clark
    August 9, 2016

    Code for running experiments on CFGs to see if
    they have the 1-FKP.

"""
import random

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cfgfcp
import generatecfg

# logging.basicConfig(level=logging.DEBUG)

print "Running experiment on CFGs with the 1 FKP"

# Initialize the CFG generator.
# random.seed(8)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals = 100
factory.number_binary_productions = 30
factory.number_lexical_productions = 50
# factory.no_lexical_ambiguity = True

# Set the parameters of the experiment.
number_grammars = 100
max_length = 20
nyields = 10

# Run the experiment.
x = []
y = []
ctr = 0
for lprod in xrange(25, 301, 25):
    ctr += 1
    print "Experiment " + str(ctr)
    print str(lprod) + " lexical productions"

    # Test a bunch of grammars and see how many have the 1-FKP.
    x.append(lprod)
    factory.number_lexical_productions = lprod
    fkpn = 0.0
    for i in xrange(number_grammars):
        grammar = factory.make_grammar()
        trial_heading = "Grammar " + str(i) + ": "
        if grammar.language_infinite():
            trial_heading += "infinite"
        else:
            trial_heading += "finite"
        trial_heading += " with " + str(len(grammar.nonterminals)) + " nonterminals"
        print trial_heading
        # print grammar
        # grammar.dump()
        # us = uniformsampler.UniformSampler(grammar,max_length)

        # Test if the grammar has the 1-FKP.
        answer = cfgfcp.test_one_fkp_exact(grammar, 10)
        print "1-kernels: " + str(answer)
        if answer:
            fkpn += 1

    # Print the results.
    ratio = fkpn / number_grammars
    y.append(ratio)
    print str(round(100 * ratio, 2)) + "% of grammars have the 1-FKP.\n"

print x
print y

# Save the results as csv.
f = open("../results/results_cnf-1fkp.csv", "w+")
f.write("lprod,ratio\n")
f.write("\n".join([",".join((str(x[i]), str(y[i]))) for i in range(len(x))]))
f.close()

# Plot the results.
axes = plt.gca()
axes.set_ylim([0, 1])

plt.plot(x, y, 'o-')
plt.xlabel('$|P_L|$')
plt.ylabel('1-FKP')
# plt.legend(legend, loc='lower right')

plt.savefig('../figures/figure_cnf-1fkp.pdf')
