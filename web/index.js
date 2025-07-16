const mf = document.querySelector("math-field");
const steps = document.getElementById("math-steps");
const out = document.getElementById("math-final");
const mode = document.getElementById("mode");

document.getElementById("evaluate").addEventListener("click", evaluate);
mode.addEventListener("change", evaluate);

mf.addEventListener("keyup", (e) => {
  if (e.key == "Enter") evaluate();
});

async function evaluate() {
  let [i, j] = await window.pywebview.api.evaluate(
    mf.value,
    mode.options[mode.selectedIndex].id
  );
  steps.innerHTML = i;
  out.innerHTML = j;
  renderMathInElement(steps);
  renderMathInElement(out);
}
