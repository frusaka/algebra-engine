# Algebra Engine 🧮

An educational math software built in Python for manipulating algebraic expressions.
Supports rational simplification, polynomial manipulation, factoring, root finding, equation solving, and many more!

It was initially built as a side project to test my understanding of Algebra II and Pre-Calculus concepts in High School and improve my development skills, but I hope it can be useful to others as well. It is built with a focus on educational value, and it even surpasses its original scope by being able to handle advanced topics like multivariate factoring, high-degree systems of equations, and Groebner bases.

## ✨ Features

- [x] Expression parser (including commands like approx() and solve())
- [x] GCD/LCM computation (numeric and symbolic)
- [x] Exact numeric radical representation
- [x] Expansion and Factoring (numeric and symbolic, univariates & multivariates alike)
- [x] Solving linear and polynomial systems
- [x] Solving equations and inequalities with domain analysis
- [x] Verbose equation transformation steps with Custom pretty-printer (`LaTeX` + `HTML` or python rich library in terminal)

## Examples

<img style="display: block; margin : 5px;" src="examples/ae-poly-solve.png" alt="Equation example" width="400"/> 
<img style="display: block; margin : 5px;" src="examples/ae-sys-solve.png" alt="Systems of equations example" width="400"/>

<img style="display: block; margin : 5px;" src="examples/ae-expr.png" alt="Expressions example" width="400"/>

### Terminal REPL

<img style="display: block; margin : 5px;" src="examples/ae-default-terminal.png" alt="Terminal REPL example" width="350"/>  
<img style="display: block; margin : 5px;" src="examples/ae-ineq-terminal.png" alt="Terminal REPL example" width="280"/>

## 🚀 Getting Started

Download the latest release executable for your operating system from the [Releases](https://github.com/frusaka/algebra-engine/releases) page.

If you want to run it from source, follow these steps:

1. 📥 Clone the repo:

   ```bash
   git clone https://github.com/frusaka/algebra-engine.git
   cd algebra-engine
   ```

2. 📦 Install dependencies:  
   Ensure that you have [Python 3.10](https://www.python.org/downloads/) or higher installed. Then, create a virtual environment and install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. 🎨 Build the frontend assets:  
   Ensure that you have [Node.js](https://nodejs.org) and npm installed to build the frontend assets. Then, run the following commands:
   ```bash
   cd web
   npm install
   npm run build
   cd ..
   ```
   If you change the React frontend code, rebuild the frontend assets by running `npm run build` in the `web` directory before starting the GUI.
4. ▶️ Try it:
   - 💻 REPL
     ```bash
     python terminal.py
     ```
   - 🖥️ Or start the GUI

     ```bash
     python main.py

     ```

## 🐍 Running Python Code

You can also import the classes and functions and use them in your own code.  
Here are some quick, simple examples to get you started:

```python
from datatypes import Var
x, y = Var("x"), Var("y")
print(x + y - 2)  # prints "x + y - 2"
```

You can also parse expressions from strings:

```python
from parsing import parser
expr = parser.parse("2x + 3 - y")
print(expr)  # prints "2x - y + 3"
```

For more examples or inspirations, check out the tests in the `tests` directory.  
If this project gains traction, I might add more detailed documentation and invite collaborators 😊
