# Experiments on Distributional Learnability Properties of CFGs

This is a copy of the repository [testcfg](https://github.com/alexc17/testcfg), which contains code for running experiments described in Alexander Clark's paper [Testing Distributional Properties of Context-Free Grammars](http://www.jmlr.org/proceedings/papers/v57/clark16.pdf). This fork contains code I have written to run additional experiments based on those described in the paper.

## Additional Experiments
The following sections describe additional experiments I have created.

### CNF Grammars without Lexical Rules
It was noted in the Clark paper that lexical rules are responsible for causing a large number of CNF grammars to have the 1-FKP. I have added code to remove lexical rules from a CNF grammar and repeat the experiment for the 1-FKP.