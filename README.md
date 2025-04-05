# PyLexFLP

**PyLexFLP** is a Python package for solving **Fuzzy Linear Programming** problems using the [**Lexicographic Method**](https://doi.org/10.1016/j.eswa.2019.01.041). This tool is designed to help researchers and practitioners in **Operations Research** and **Fuzzy Optimization** to model and solve fuzzy optimization problems effectively.

## Features

- Solves fuzzy linear programming models in which the coefficients are arbitrary triangular fuzzy numbers and the decision variables are non-negative triangular fuzzy numbers.
- Utilizes **Lexicographic Ranking** criteria for ordering triangular fuzzy numbers.
- Built on top of the [**PuLP**](https://github.com/coin-or/pulp) optimization framework.

## Installation

You can install PyLexFLP from GitHub:

```bash
pip install git+https://github.com/bpcanedo/pylexflp.git
```

Or, from PyPI:

```bash
pip install pylexflp
```

## Requirements

- **Python** \>= 3.7
- **PuLP** \>= 2.6
- **SciPy** \>= 1.21

## Usage

Here's a simple example of how to use PyLexFLP:

```python
from pylexflp import FLP, TFN_Var, TFN, flpMaximize, getSolver

# Lexicographic ranking method
def f1(x): return (x.al+2*x.am+x.au)/4
def f2(x): return x.am
def f3(x): return x.au-x.al
criteria = [f1, f2, f3]

# The problem
p = FLP(criteria=criteria, sense=flpMaximize)

# Variable definition
x1, x2, I1, I2, I3 = TFN_Var("x1"), TFN_Var("x2"), TFN_Var("I1"), TFN_Var("I2"), TFN_Var("I3")

# Let PyLexFLP know the variables
p += x1
p += x2
p += I1
p += I2
p += I3

# Insert the constraints
p += I1 + TFN(0.15,0.20,0.25)*I1 == x1+I2
p += I2 + TFN(0.10,0.15,0.20)*I2 == x2+I3
p += I1 == TFN(950, 1000, 1050)
p += I3 >= TFN(622, 624, 627)

# The last expression or variable entered becomes the objective function
p += x1 + x2

# Select the linear programming solver
# msg = True if you want verbosity
solver = getSolver("COIN_CMD", msg=False)

# Solve the problem
# status = [1, 1, 1] means the three criteria were successfully optimized
status = p.solve(solver=solver)

# Fuzzy proposition example
## Membership function
def High(x): return max(0, min(1, (x-500)/500))

# Print the solution
solution = f"""
Status: {status}
Solution:
    x1 = {x1}
    x2 = {x2}
    obj = {x1+x2}
    I1 = {I1}
    I2 = {I2}
    I3 = {I3}
    # Fuzzy proposition
    x2 is High = {x2.IS(High)}
"""
print(solution)
```

## Documentation

Detailed documentation and examples can be found on the [GitHub
repository](<https://github.com/bpcanedo/pylexflp>).

## Contributing

Contributions are welcome! Please feel free to submit issues or pull
requests to the [GitHub repository](<https://github.com/bpcanedo/pylexflp>).

## License

This project is licensed under the MIT License. See the LICENSE file for
details.

## Authors

**Boris Pérez-Cañedo**

Email: <bpcanedo@gmail.com>

GitHub: [bpcanedo](<https://github.com/bpcanedo>)

**Eduardo René Concepción-Morales**

Email: <econcep@ucf.edu.cu>

**José Luis Verdegay**

Email: <verdegay@decsai.ugr.es>
