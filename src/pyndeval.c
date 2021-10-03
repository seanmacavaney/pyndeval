#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "structmember.h"

#include "ndeval.c"


/*
 * class Qrels(qrels, cutoff)
*/


// Adapted from the version in ndeval.c that reads from a file
struct rList *pyProcessQrels(PyObject *data, int cutoff, long *has_multiple_subtopics)
{
  Py_ssize_t len = PyList_Size(data);
  int n = (int)len;
  struct qrel *q = localMalloc(n*sizeof(struct qrel));
  int i = 0;
  has_multiple_subtopics[0] = 0;

  for (Py_ssize_t i=0; i<len; i++) {
    PyObject *item = PyList_GetItem(data, i);
    q[i].topic = 0; // only 1 query at a time
    q[i].subtopic = (int)PyLong_AsLong(PyTuple_GetItem(item, 0));
    q[i].docno = PyUnicode_AsUTF8(PyTuple_GetItem(item, 1));
    q[i].judgment = (int)PyLong_AsLong(PyTuple_GetItem(item, 2));
    if (i > 0 && has_multiple_subtopics[0] == 0 && q[i].subtopic != q[0].subtopic) {
      has_multiple_subtopics[0] = 1;
    }
  }

  int count[1];
  count[0] = 1;

  qrelSort(q, n);

  struct rList* result = qrelToRList(q, n, &count);
  free(q);
  return result;
}

typedef struct {
    PyObject_HEAD
    struct rList* qrels;
    int n;
    int cutoff;
    long has_multiple_subtopics;
} QrelsObject;

static void
Qrels_dealloc(QrelsObject *self)
{
  free(self->qrels);
  Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
Qrels_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    QrelsObject *self;
    self = (QrelsObject *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}

static int
Qrels_init(QrelsObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"qrels", "cutoff", NULL};
    PyObject *qrels = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Oi", kwlist,
                                     &qrels,
                                     &self->cutoff))
        return -1;

    if (!PyList_Check(qrels)) {
        return NULL;
    }

    self->qrels = pyProcessQrels(qrels, self->cutoff, &self->has_multiple_subtopics);
    self->n = (int)PyList_Size(qrels);
    return 0;
}

static PyObject*
Qrels_has_multiple_subtopics(QrelsObject *self)
{
    return PyBool_FromLong(self->has_multiple_subtopics);
}


static PyMemberDef Qrels_members[] = {
    {NULL}  /* Sentinel */
};


static PyMethodDef Qrels_methods[] = {
    {"has_multiple_subtopics", Qrels_has_multiple_subtopics, METH_NOARGS, "does this query have multiple graded subtopics?"},
    {NULL}  /* Sentinel */
};


static PyTypeObject QrelsType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "_pyndeval.Qrels",
    .tp_doc = "ndeval qrels",
    .tp_basicsize = sizeof(QrelsObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Qrels_new,
    .tp_init = (initproc) Qrels_init,
    .tp_dealloc = (destructor) Qrels_dealloc,
    .tp_members = Qrels_members,
    .tp_methods = Qrels_methods,
};


/*
 * funcion eval(qrels, run)
*/

// Adapted from the version in ndeval.c that reads from a file
struct rList *pyProcessRun (PyObject *data, int *topics, char **runid, struct result **rref)
{
  Py_ssize_t len = PyList_Size(data);
  int n = (int)len;
  struct result *r = localMalloc (n*sizeof (struct result));
  int i = 0;

  for (Py_ssize_t i=0; i<len; i++) {
    PyObject *item = PyList_GetItem(data, i);
    r[i].docno = PyUnicode_AsUTF8(PyTuple_GetItem(item, 0));
    r[i].topic = 0; // only 1 query at a time
    r[i].rank = (int)PyLong_AsLong(PyTuple_GetItem(item, 1));;
    r[i].rel = (int *) 0;
  }

  *topics = resultCountTopics (r, n);
  struct rList *rl = (struct rList *) localMalloc ((*topics)*sizeof (struct rList));
  resultSortByDocno (r, n);
  populateResultList (r, n, rl, *topics);
  
  rref = &r; // allows this memory to be freed later

  return rl;
}


static PyObject *eval(PyObject *self, PyObject *args) {
  QrelsObject *qrels;
  PyObject *run;
  PyObject *measures;

  /* Parse arguments */
  if(!PyArg_ParseTuple(args, "OOO", &qrels, &run, &measures)) {
      return NULL;
  }

  if (!PyList_Check(run)) {
      return NULL;
  }

  if (!PyList_Check(measures)) {
      return NULL;
  }

  PyObject *key, *value;
  Py_ssize_t pos = 0;

  int rTopics = 1;
  char* runid = "";
  struct result *rref = NULL;

  struct rList* rrl = pyProcessRun(run, &rTopics, &runid, &rref);
  applyQrels(qrels->qrels, rTopics, rrl, rTopics);

  Py_ssize_t len = PyList_Size(measures);
  PyObject* result = PyList_New(len);

  for (Py_ssize_t i=0; i<len; i++) {
    double value;
    PyObject *measure = PyList_GetItem(measures, i);
    int m = (int)PyLong_AsLong(PyTuple_GetItem(measure, 0));
    if (m < 6) {
      int cutoffIdx = (int)PyLong_AsLong(PyTuple_GetItem(measure, 1)) - 1;
      if (m == 0)
        value = rrl[0].err[cutoffIdx];
      else if (m == 1)
        value = rrl[0].nerr[cutoffIdx];
      else if (m == 2)
        value = rrl[0].dcg[cutoffIdx];
      else if (m == 3)
        value = rrl[0].ndcg[cutoffIdx];
      else if (m == 4)
        value = rrl[0].precision[cutoffIdx];
      else if (m == 5)
        value = rrl[0].strec[cutoffIdx];
    }
    else if (m == 6)
      value = rrl[0].nrbp;
    else if (m == 7)
      value = rrl[0].nnrbp;
    else if (m == 8)
      value = rrl[0].mapIA;
    PyList_SET_ITEM(result, i, PyFloat_FromDouble(value));
  }

  free(rrl);
  free(rref);

  return result;
}


static PyObject *set_global_alpha_beta(PyObject *self, PyObject *args) {
  double a, b;

  /* Parse arguments */
  if(!PyArg_ParseTuple(args, "dd", &a, &b)) {
      return NULL;
  }

  // set global params
  alpha = a;
  beta = b;

  Py_RETURN_NONE;
}


static PyMethodDef PyNdevalMethods[] = {
    {"eval", eval, METH_VARARGS, "eval ndeval"},
    {"set_global_alpha_beta", set_global_alpha_beta, METH_VARARGS, "set global params"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef pyndevalmodule = {
    PyModuleDef_HEAD_INIT,
    "_pyndeval",
    "Python interface for ndeval",
    -1,
    PyNdevalMethods
};


PyMODINIT_FUNC PyInit__pyndeval(void) {
  PyObject *m;
  if (PyType_Ready(&QrelsType) < 0)
    return NULL;
  m = PyModule_Create(&pyndevalmodule);
  Py_INCREF(&QrelsType);
  if (PyModule_AddObject(m, "Qrels", (PyObject *) &QrelsType) < 0) {
    Py_DECREF(&QrelsType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
