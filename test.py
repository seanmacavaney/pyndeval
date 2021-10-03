from timeit import timeit
import pyndeval
from pyndeval import SubtopicQrel, ScoredDoc

i = 0
while True:
    qrels = [
        SubtopicQrel("0", "a", "A", 1),
        SubtopicQrel("0", "b", "B", 1),
        SubtopicQrel("0", "b", "D", 1),
        SubtopicQrel("0", "c", "C", 1),
    ]

    # pyndeval supports various run formats. Here, we'll use {qid: {did: rel}}
    run = [
        ScoredDoc("0", "A", 9.3),
        ScoredDoc("0", "D", 8.4),
        ScoredDoc("0", "E", 8.1), # not in qrels
        ScoredDoc("0", "B", 7.6),
        # C not retrieved
    ]

    ev = pyndeval.RelevanceEvaluator(qrels)

    # print(timeit(lambda: pyndeval.ndeval(qrels, run), number=50000))
    print(timeit(lambda: ev.evaluate(run), number=50000))
    break
    i += 1
    print(i)
