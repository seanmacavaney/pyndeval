from timeit import timeit
import py_ndeval

i = 0
while True:
	qrels = {
		"0": { # query ID 0
			"a": { # subtopic a
				"A": 1, # document A
				# "D": 1
			},
			"b": {
				"B": 1,
				"D": 1,
			},
			"c": {
				"C": 1
			}
		}
	}

	# py_ndeval supports various run formats. Here, we'll use {qid: {did: rel}}
	run = {
		"0": {
			"A": 9.3,
			"D": 8.4,
			"E": 8.1, # no in qrels
			"B": 7.6,
			# no C
		}
	}

	ev = py_ndeval.RelevanceEvaluator(qrels)

	# print(timeit(lambda: py_ndeval.ndeval(qrels, run), number=50000))
	print(timeit(lambda: ev.evaluate(run), number=50000))
	break
	i += 1
	print(i)

