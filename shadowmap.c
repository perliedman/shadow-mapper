#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <numpy/arrayobject.h>

/*  Helper functions adapted from
    http://wiki.scipy.org/Cookbook/C_Extensions/NumPy_arrays */

static int is_floatmatrix(PyArrayObject *mat) {
    if (PyArray_TYPE(mat) != NPY_DOUBLE || PyArray_NDIM(mat) != 2)  {
        printf("%d\n", PyArray_TYPE(mat));
        PyErr_SetString(PyExc_ValueError,
            "Array must be of type Float and 2 dimensional.");
        return 0;
    }

    return 1;
}

static double **ptrvector(long n)  {
    double **v;
    v = (double **)malloc((size_t) (n * sizeof(double)));
    if (!v) {
        printf("Allocation of memory for double array failed.");
        exit(0);
    }
    return v;
}

static void free_Carrayptrs(double **v)  {
    free((char*) v);
}

static double **pymatrix_to_Carrayptrs(PyArrayObject *arrayin)  {
    double **c, *a;
    int i,n,m;
    npy_intp *dims = PyArray_DIMS(arrayin);

    n = dims[0];
    m = dims[1];
    c = ptrvector(n);
    a = (double *) PyArray_DATA(arrayin);  /* pointer to arrayin data as double */
    for (i = 0; i < n; i++)  {
        c[i] = a + i * m;
    }
    return c;
}

static PyObject *shadowmap_calculate(PyObject *self, PyObject *args) {
    PyArrayObject *heightmap_arr, *shadowmap_arr;
    double sun_x, sun_y, sun_z, view_alt, x, y, z;
    double **shadowmap, **heightmap;
    npy_intp *dims;
    int i, j, lit;

    if (!PyArg_ParseTuple(args, "O!dddd", &PyArray_Type, &heightmap_arr,
        &sun_x, &sun_y, &sun_z, &view_alt)) {
        return NULL;
    }

    if (heightmap_arr == NULL || !is_floatmatrix(heightmap_arr)) {
        return NULL;
    }

    dims = PyArray_DIMS(heightmap_arr);
    shadowmap_arr = (PyArrayObject*) PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);

    heightmap = pymatrix_to_Carrayptrs(heightmap_arr);
    shadowmap = pymatrix_to_Carrayptrs(shadowmap_arr);

    for (i = 0; i < dims[0]; i++) {
        for (j = 0; j < dims[1]; j++) {
            x = (double)j;
            y = (double)i;
            z = heightmap[i][j] + view_alt;
            lit = 1;

            // TODO: should also include  z exceeding heightmap's max value
            // as an exit condition as an optimization
            while (x >= 0 && x < dims[0] && y >= 0 && y < dims[1]) {
                if (z < heightmap[(int)y][(int)x]) {
                    lit = 0;
                    break;
                }
                x += sun_x;
                y += sun_y;
                z += sun_z;
            }

            shadowmap[i][j] = lit;
        }
    }

    free_Carrayptrs(heightmap);
    free_Carrayptrs(shadowmap);

    return PyArray_Return(shadowmap_arr);
}

static PyMethodDef ShadowMapMethods[] = {
    {"calculate",  shadowmap_calculate, METH_VARARGS,
     "Calculate a shadowmap."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC initshadowmap(void) {
    (void) Py_InitModule("shadowmap", ShadowMapMethods);
    import_array();  // Must be present for NumPy.  Called first after above line.
}
