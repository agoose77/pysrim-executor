# pysrim-executor
[![pypi-badge][]][pypi] 

[pypi-badge]: https://img.shields.io/pypi/v/pysrim-executor
[pypi]: https://pypi.org/project/pysrim-executor

Extensible executor backends for pysrim.

## Getting Started
Let's define a simple model using the pysrim example:
```python3
from srim import Ion, Layer, Target, TRIM

# Construct a 3MeV Nickel ion
ion = Ion('Ni', energy=3.0e6)

# Construct a layer of nick 20um thick with a displacement energy of 30 eV
layer = Layer({
        'Ni': {
            'stoich': 1.0,
            'E_d': 30.0,
            'lattice': 0.0,
            'surface': 3.0
        }}, density=8.9, width=20000.0)

# Construct a target of a single layer of Nickel
target = Target([layer])

# Initialize a TRIM calculation with given target and ion for 25 ions, quick calculation
trim = TRIM(target, ion, number_ions=25, calculation=1)

```
Normally, we would execute this with the `.run` method.
```python3
result = trim.run(srim_executable_directory)
```
pysrim-executor allows you to invert the relationship, and use multiple kinds of executors e.g. the `DockerExecutor`:
```python
from srim.executor import DockerExecutor

executor = DockerExecutor()
result = executor.run(trim)
```

Out of the box, the `DockerExecutor` uses the `costrouc/srim` Docker image, and writes the input and output files to a temporary directory. 

## Why?
There are a number of different ways that SRIM can be invoked to run simulations. Unix-like OS users have the option of using `wine` with or without `xvfb`.
Windows users can directly call the binaries. Docker users can choose to defer to a pre-built SRIM container.

By abstracting the executor from the SRIM input file generation, executors can easily be swapped in and out, or extended as necessary.
