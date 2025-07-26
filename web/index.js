const mf = document.querySelector("math-field");
const steps = document.getElementById("math-steps");
const out = document.getElementById("math-final");
const ctn = document.getElementById("math-final-container");

const solveTitle = document.getElementById("solve-title");

let customMacros = {
  approx: "\\operatorname{approx}(#?)",
  factor: "\\operatorname{factor}(#?)",
  solve: "\\operatorname{solve}(#?)",
  expand: "\\operatorname{expand}(#?)",
  lcm: "\\operatorname{lcm}(#?)",
  gcd: "\\operatorname{gcd}(#?)",
  root: "\\sqrt[#?]{#?}",
  i: "\\imaginaryI",
};

mf.addEventListener("mount", () => {
  mf.macros = { ...mf.macros, ...customMacros };

  mf.inlineShortcuts = {
    ...mf.inlineShortcuts,
    ...customMacros,
  };
});

mf.addEventListener("change", evaluate);

async function evaluate() {
  let resp = await window.pywebview.api.evaluate(
    MathfieldElement.computeEngine.parse(mf.value).json
  );

  if (resp.error) {
    document.getElementById("math-success").innerText = "🚫";
    ctn.classList.remove("bg-success");
    ctn.classList.add("bg-danger");
    out.innerHTML = resp.error;
  } else {
    document.getElementById("math-success").innerText = "✅";
    ctn.classList.remove("bg-danger");
    ctn.classList.add("bg-success");
    out.innerHTML = resp.final;
  }

  solveTitle.innerHTML = "";
  steps.innerHTML = resp.steps;

  if (resp.steps) {
    solveTitle.innerText = ": " + steps.firstElementChild.dataset.aeTitle;
    steps.innerHTML =
      steps.firstElementChild.firstElementChild.lastElementChild.lastElementChild.innerHTML;
  }
  renderMathInElement(document.body);
}
