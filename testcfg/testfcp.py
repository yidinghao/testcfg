# testfcp
# CODE FOR TESTING whether a given pcfg has the k-FCP
# for some given value of k

import collections
import random
import sys
import argparse
import logging

import cfg
#import pcfg

sys.setrecursionlimit(10000)
max_length = 20
max_context_length = 10
max_attempts = 10

def test_fcp(grammar, k, ncontexts, nsamples):
	""" 
	test whether the grammar has the k-fcp.
	(NOT, whether the language defined by the grammar has the FCP)

	Method: sample a bunch of contexts for each nonterminal.
	Take random sets of size k. 
	Take the intersection of things that occur in those contexts.
	Then check whether all of these can be generated by the nonterminal.

	If we can find such a set for each nonterminal, then the grammar has the FCP.
	"""
	context_map = dict()
	context_map[grammar.start] = [ ((),()) ]
	for nonterminal in grammar.nonterminals:
		if nonterminal != grammar.start:
			print "Testing ", nonterminal 
			contexts = test_fcp_nt(grammar,k, nonterminal, ncontexts, nsamples)
			if contexts:
				print "PASS"
				context_map[nonterminal] = contexts
			else:
				print "FAIL", nonterminal
				return False
	return context_map


def test_fcp_nt(grammar, k,nonterminal, ncontexts, nsamples):
	"""
	Test FCP of a given nonterminal.

	Returns a suitable k-tuple of contexts.

	"""
	
	possible_contexts = set()
	for i in range(ncontexts):
		try:
			tree = grammar.sample_tree(5 * max_length)
			#print "Tree width %d depth %d " % (tree.width(), tree.depth())
			contexts = tree.collect_contexts_of_nt(nonterminal)
			#print len(contexts)
			for c in contexts:
				if len(c[0]) + len(c[1]) < max_context_length:
					possible_contexts.add(c)
		except ValueError:
			logging.warning("Sampled too deep. Discarding")
	#print "Total contexts", len(possible_contexts)
	# now we should have some good contexts.
	if len(possible_contexts) == 0:
		# so this nonterminal is rare.
		return False

	if len(possible_contexts) < k:
		# then this one is rare.
		#print "Rare NT"
		return False
	for i in xrange(max_attempts):
		contexts = random.sample(possible_contexts,k)
		#print contexts
		if test_cp_nt(grammar, nonterminal,contexts, nsamples):
			return contexts
	return False


def test_cp_nt(grammar, nonterminal, contexts, nsamples):
	"""
	Test whether these contexts characterise this nonterminal.

	Pick nsamples that occur in all the contexts, and check that they are generated
	by the nonterminal.
	"""
	intersected = intersect_contexts(grammar, contexts, nsamples)
	for x in intersected:
		if not grammar.parse_start(x,nonterminal):
			return False
	return True


def intersect_contexts(grammar, contexts, n):
	"""
	Return a set of strings that can occur in all of these contexts.
	
	Sample from the first context; then check for all of the remaining ones. 
	"""
	context = contexts[0]
	l = len(context[0])
	r = len(context[1])
	#print "Intersecting: root  context is ", context
	cg = grammar.construct_context_grammar(context)
	#print "grammar constructed"
	expected_length = cg.isConsistent()
	#print "grammar constructed ok: prods=", len(cg.productions), " length ", expected_length
	samples = collections.Counter()
	
	done = 0
	total_sampled = 0
	iterations = 0
	maxdepth = 2 * (max_length + l + r)
	while done < n and iterations < n * n:
		iterations += 1
		try:
			ctree = cg.sample_tree(maxdepth)
			#print "Context tree width %d, depth %d" % (ctree.width(), ctree.depth())
			lwr = ctree.collectYield()
			total_sampled += 1
			if r > 0:
				w = lwr[l:-r]
			else:
				w = lwr[l:]
			if len(w) < max_length:
				w = tuple(w)
				if w in samples:
					samples[w] += 1
				else:
					## now check to see whether these 
					## are in all the other contexts.
					for j in range(1, len(contexts)):
						# check if it is generated by the other contexts.
						ocontext = contexts[j]
						lwr2 = tuple(ocontext[0]) + w + tuple(ocontext[1])
						if not grammar.parse(lwr2):
							break
					else:
						# it is accepted by all contexts
						samples[w] += 1
						done += 1
		except ValueError:
			logging.warning("Too deep:" + grammar.description + "depth " + str(maxdepth))
	#logging.warning("Finished done %d iterations %d" % (done, iterations))
	return samples

# Now the primal stuff.

def test_fkp(grammar, k, nstrings, nsamples):
	"""
	Test whether the grammar has the strong k-FKP.
	If it does, return a dict mapping nonterminals to lists of strings.
	"""
	string_map = dict()
	for nt in grammar.nonterminals:
		strings = test_fkp_nt(grammar, nt, k, nstrings, nsamples)
		if strings:
			string_map[nt] = strings
		else:
			return False
	return string_map

def test_fkp_nt(grammar, nonterminal, k, nstrings, nsamples):
	"""
	Test whether this nonterminal has the (strong) k-finite kernel property.

	Method: sample from nonterminal to get a small set  of strings.
	Intersect them to get a lot of  contexts.
	Check that each of these contexts is a context of the nonterminal.

	"""
	possible_strings = set()
	for j in xrange(nstrings):
		y = grammar.sample_tree_from(nonterminal).collectYield()
		if len(y) <= max_length:
			possible_strings.add(tuple(y))
	# now we have a collection of trees.

	possible_strings = list(possible_strings)
	if len(possible_strings) < k:
		logging.warning("possible strings too small.")
		return test_kp_nt(grammar, nonterminal, list(possible_strings), nsamples)

	for i in xrange(max_attempts):
		# sample k distinct strings from the nonterminal.
		strings = random.sample(possible_strings, k)
		if test_kp_nt(grammar, nonterminal, strings, nsamples):
			return strings
	return False


def test_kp_nt(grammar, nonterminal, substrings, nsamples):
	"""
	Test whether this nonterminal is characterised by these substrings.
	
	Method: get the shared contexts of the substrings; check that they are contexts of the nonterminal.
	This is a stronger test.
	(These will be a superset of the contexts of the nonterminal)
	
	"""
	#print "Intersecting"
	intersected = intersect_strings(grammar, substrings, nsamples)
	#print "Checking", len(intersected)
	for context in intersected:
		if not grammar.parse_nonterminal_context(context[0], nonterminal, context[1]):
			return False
	return True


def intersect_strings(grammar, substrings, n):
	"""
	Return some contexts that are shared by all these strings.
	Ideally returns n contexts, but may be less if for example the distribution has very low entropy.

	In a counter object.
	"""
	w = substrings[0]
	lw = len(w)
	# sample from contexts of this string.
	cg = grammar.construct_infix_grammar(w)
	samples = collections.Counter()
	iteration = 0
	while len(samples) < n and iteration < n * n:
		iteration += 1
		# add another condition in case there aren't enough.
		# for example there might be only 1 string that occurs in this context.
		sentence = tuple(cg.sample_tree(max_context_length + max_length).collectYield())
		#print "Sampled" , sentence
		# now loop through all occurrences of w in this string
		# there might be more than one of course
		l = len(sentence)
		if l < max_context_length + max_length:
			for i in xrange(l):
				# naive string matching probably enough.

				if sentence[i:i+lw] == w:
					#print "match"
					# match
					context = (sentence[0:i],sentence[i+lw:l])
					if context in samples:
						samples[context] += 1
					else:
						# check to see if is accepted by all 
						if test_context(grammar, context, substrings[1:]):
							samples[context] += 1
	return samples

def test_context(grammar, context, substrings):
	"""
	Return true if all of these substrings can occur in this single context.
	"""
	for substring in substrings:
		lwr = context[0] + substring + context[1]
		if not grammar.parse(lwr):
			return False
	return True




if __name__ == '__main__':
	# command line thing here.
	parser = argparse.ArgumentParser("Test whether a given grammar has the FCP and FKP or not.")
	parser.add_argument("grammar",help="filename of pcfg.")
	parser.add_argument("--ncontexts", help="number of trees to sample to get contexts for FCP",type=int,default=100)
	parser.add_argument("--nstrings", help="number of trees to sample to get strings for FKP",type=int,default=100)
	parser.add_argument("--fcp", help="Number of contexts to try. Set to 0 to skip.", type =int,default=2)
	parser.add_argument("--fkp", help="Number of strings to try. Set to 0 to skip", type =int,default=2)
	parser.add_argument("--maxattempts", help="Maximum number of attempts to find suitable contexts.", type=int,default=10)
	parser.add_argument("--maxlength", help="Maximum length of samples.", type=int,default=20)
	parser.add_argument("--maxcontextlength", help="Maximum length of contexts to try.", type=int,default=10)
	parser.add_argument("--nsamples", help="number of samples to draw from contexts for test", type=int,default=100)
	args = parser.parse_args()
	max_context_length = args.maxcontextlength
	max_attempts = args.maxattempts
	max_length = args.maxlength
	grammar = pcfg.load_from_file(args.grammar)
	if args.fcp > 0:
		if test_fcp(grammar, args.fcp, args.ncontexts,args.nsamples):
			print "Grammar has the %d-fcp" % args.fcp
		else:
			print "Fail. (FCP)"
	if args.fkp > 0:
		if test_fkp(grammar, args.fkp, args.nstrings,args.nsamples):
			print "Grammar has the %d-fkp" % args.fkp
		else:
			print "Fail. (%d-FKP)" % args.fkp


