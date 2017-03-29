"""
    Alexander Clark
    August 9, 2016

    Code for running experiments on CFGs to see if
    they have the 1-FKP. Modified by Yiding Hao.

"""
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cfgfcp
import generatecfg
from copy import deepcopy

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
y_no_lex = []
ctr = 0
for lprod in xrange(25, 301, 25):
    ctr += 1
    print "Experiment " + str(ctr)
    print str(lprod) + " lexical productions"

    # Test a bunch of grammars and see how many have the 1-FKP.
    # Do this with and without lexical rules.
    x.append(lprod)
    factory.number_lexical_productions = lprod
    fkpn = 0.0
    fkpn_no_lex = 0.0
    for i in xrange(number_grammars):
        no_error = False
        while not no_error:
            no_error = True
            grammar = factory.make_grammar(trim=False)

            # Display information about the experiment.
            trial_heading = "Grammar " + str(i + 1) + ": "
            if grammar.language_infinite():
                trial_heading += "Infinite"
            else:
                trial_heading += "Finite"
            trial_heading += " with " + str(len(grammar.nonterminals)) + " nonterminals"
            print trial_heading

            # Test if the grammar has the 1-FKP.
            # Make two copies of the grammar: one with and one without lexical rules.
            grammar_no_lex = deepcopy(grammar)
            try:
                grammar.trim()
                answer = cfgfcp.test_one_fkp_exact(grammar, 10)

                grammar_no_lex.remove_lexical_rules()
                grammar_no_lex.trim()
                answer_no_lex = cfgfcp.test_one_fkp_exact(grammar_no_lex, 10)
            except:
                print "An error occurred. Trying again."
                no_error = False
                continue

            # Report and record the results.
            print "1-kernels: " + str(answer)
            print "1-kernels (no lex): " + str(answer_no_lex)
            if answer:
                fkpn += 1
            if answer_no_lex:
                fkpn_no_lex += 1

    # Report and record the final results.
    ratio = fkpn / number_grammars
    ratio_no_lex = fkpn_no_lex / number_grammars
    y.append(ratio)
    y_no_lex.append(ratio_no_lex)

    print str(round(100 * ratio, 2)) + "% of grammars have the 1-FKP."
    print str(round(100 * ratio_no_lex, 2)) + "% of grammars (no lex) have the 1-FKP.\n"

# Save the results as csv.
rows = [",".join((str(x[i]), str(y[i]))) + ",no" for i in range(len(x))]
rows_no_lex = [",".join((str(x[i]), str(y_no_lex[i]))) + ",yes" for i in range(len(x))]

f = open("../results/results_cnf-1fkp.csv", "w+")
f.write("lprod,ratio,no_lex\n")
f.write("\n".join(rows) + "\n")
f.write("\n".join(rows_no_lex))
f.close()

# Plot the results.
axes = plt.gca()
axes.set_ylim([0, 1])

plt.plot(x, y, 'o-')
plt.plot(x, y_no_lex, 'o-')
plt.xlabel('$|P_L|$')
plt.ylabel('1-FKP')

plt.savefig('../figures/figure_cnf-1fkp.pdf')
