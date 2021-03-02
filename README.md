# pysrim-docker
[![pypi-badge][]][pypi] 

[pypi-badge]: https://img.shields.io/pypi/v/pysrim-docker
[pypi]: https://pypi.org/project/pysrim-docker

Docker executor for PySRIM

## Getting Started
To use this package, simply remove calls to `run()` method of `SR` and `TRIM`, and replace them with a call to the executor `run` dispatch method, e.g.:

```python
from srim.executor import DockerExecutor
from srim import TRIM

executor = DockerExecutor()

trim = TRIM(...)
result = executor.run(trim)
```

Out of the box, the `DockerExecutor` uses the `costrouc/srim` Docker image, and writes the input and output files to a temporary directory. 

### Example
```python3
from srim.executor import DockerExecutor
from srim import Ion, Layer, Target, TRIM

from matplotlib import pyplot as plt

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

# Create executor and run TRIM
executor = DockerExecutor()
result = executor.run(trim)

# Pull out ionization
ioniz = result.ioniz

# Plot results
_, ax = plt.subplots()
ax.plot(ioniz.depth, ioniz.ions, label='Ionization from Ions')
ax.plot(ioniz.depth, ioniz.recoils, label='Ionization from Recoils')
plt.show()
```

## Why?
There are a number of different ways that SRIM can be invoked to run simulations. Unix-like OS users have the option of using `wine` with or without `xvfb`.
Windows users can directly call the binaries. Docker users can choose to defer to a pre-built SRIM container.

By abstracting the executor from the SRIM input file generation, executors can easily be swapped in and out, or extended as necessary.