const mf = document.querySelector("math-field");
const steps = document.getElementById("math-steps");
const out = document.getElementById("math-final");
const ctn = document.getElementById("math-final-container");

const solveTitle = document.getElementById("solve-title");

let ce;
let customMacros = {
  approx: "\\operatorname{approx}",
  factor: "\\operatorname{factor}",
  solve: "\\operatorname{solve}",
  expand: "\\operatorname{expand}",
  lcm: "\\operatorname{lcm}",
  gcd: "\\operatorname{gcd}",
};

mf.addEventListener("mount", () => {
  mf.macros = { ...customMacros, ...mf.macros, i: "\\operatorname{i}" };

  mf.inlineShortcuts = {
    ...mf.inlineShortcuts,
    ...Object.fromEntries(
      Object.keys(customMacros).map((k) => [
        k,
        "\\" + k + "{\\left(#1\\right)}",
      ])
    ),
    root: "\\sqrt[#?]{#1}",
    i: "\\i",
  };
  loadParse();
});

document.addEventListener("ceready", loadParse);
mf.addEventListener("change", evaluate);

async function evaluate() {
  let resp = await window.pywebview.api.evaluate(
    ce.parse(mf.value, { parseNumbers: "rational" }).json
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

function loadParse() {
  if (
    typeof MathfieldElement == "undefined" ||
    !MathfieldElement.computeEngine ||
    ce
  )
    return;
  ce = MathfieldElement.computeEngine;
  ce.latexDictionary = [
    ...ce.latexDictionary,
    ...Object.keys(customMacros).map((k) => ({
      latexTrigger: "\\" + k,
      kind: "function",
      parse: (parser) => {
        let g = parser.parseGroup() ?? ["Error", "'missing'"];
        if (typeof g == "object" && g[0] == "Delimiter") {
          if (!g[2]) return [k, g[1]];
          if (g[2].str == "(,)") return [k, ...g[1].slice(1)];
        }
        return [k, g];
      },
    })),
    { latexTrigger: "\\i", parse: "Imag" },
  ];
}
