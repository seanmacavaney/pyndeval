# py_ndeval

A python interface to TREC's `ndeval.c`, used for computing diversity retrieval metrics.

## Getting Started

```bash
python setup.py install
```

## Usage

```python
import py_ndeval

# py_ndeval supports various qrel formats. Here, we'll use {qid: {sid: {did: rel}}}
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

py_ndeval.ndeval(qrels, run)
{'0': {
	'ERR-IA@5': 0.3933,
	'ERR-IA@10': 0.3907,
	'ERR-IA@20': 0.3907,
	'nERR-IA@5': 0.8297,
	'nERR-IA@10': 0.8297,
	'nERR-IA@20': 0.8297,
	'alpha-DCG@5': 0.4052,
	'alpha-DCG@10': 0.3998,
	'alpha-DCG@20': 0.3997,
	'alpha-nDCG@5': 0.7868,
	'alpha-nDCG@10': 0.7868,
	'alpha-nDCG@20': 0.7868,
	'NRBP': 0.3906,
	'nNRBP': 0.8620,
	'MAP-IA': 0.5000,
	'P-IA@5': 0.2000,
	'P-IA@10': 0.1000,
	'P-IA@20': 0.0500,
	'strec@5': 0.6666,
	'strec@10': 0.6666,
	'strec@20': 0.6666
}}
```

## Supported measures

`py_ndeval` supports the following measures:

 - `ERR-IA@k`
 - `nERR-IA@k`
 - `alpha-DCG@k`
 - `alpha-nDCG@k`
 - `P-IA@k`
 - `strec@k`
 - `NRBP`
 - `nNRBP`
 - `MAP-IA`

Measures with `@k` support values from 1-20 (upper limit from `ndeval.c`).

Measures are provided as a list of strings with the `measures=` parameter.

```python
py_ndeval.ndeval(qrels, run, measures=["ERR-IA@7", "MAP-IA"])
```

## Reusing qrels

If you're running multiple times for the same set of qrels and measures, you can speed it up by
building a `RelevanceEvaluator` object, which caches the internal qrel representations.

```python
ev = py_ndeval.RelevanceEvaluator(qrels)
ev.evaluate(run1)
ev.evaluate(run2)
ev.evaluate(run3)
ev.evaluate(run4)
```

## Iterable results

```python
for result in py_ndeval.ndeval_iter(qrels, run):
	{"query_id": "0", ...}
for result in py_ndeval.evaluate_iter(run):
	{"query_id": "0", ...}
```
