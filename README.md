# Symbolic Math Engine 🧮

A fast symbolic algebra engine built in Python for solving and simplifying algebraic expressions.  
Supports rational simplification, polynomial manipulation, factoring, root finding, equation solving, and many more!  

✅ Offline  
✅ Tree-based expression evaluation  
✅ Designed to match Algebra II and Pre-Calc workflows  
🚫 (Trigonometric and exponential solving planned)

## ✨ Features

- [x] Expression parser
- [x] GCD/LCM computation (numeric and symbolic)
- [x] Exact numeric radical representation
- [x] Expansion and Factoring (numeric and symbolic, univariates & multivariates alike)
- [x] Solving linear and polynomial systems
- [x] Solving equations and inequalities with domain analysis
- [x] Verbose equation transformation steps with Custom pretty-printer (`LaTeX` + `HTML` or python rich library in terminal)
- [ ] Exponential equations and trig

## 🚀 Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/frusaka/algebra-engine.git
   cd algebra-engine
2. Install requirements:
   ```bash
   pip install -r requirements.txt
3. Try it:
    - REPL (Does not support function calls, e.g simplify(expr))
       ```bash
       python terminal.py
    - Or start the GUI (Recommended ✅) 
      ```bash
      python main.py
      
NOTE: If solving from a multivariate equation, type `target`=>`equation`  
Example: P => C = Prt + P, gets interpreted as find `P` given that `C = Prt + P`
