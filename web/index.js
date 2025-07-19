const mf = document.querySelector("math-field");
const steps = document.getElementById("math-steps");
const out = document.getElementById("math-final");
const ctn = document.getElementById("math-final-container");

const solveTitle = document.getElementById("solve-title");
const evaluateBtn = document.getElementById("evaluate");
const dropdownItems = document.querySelectorAll(".dropdown-item");

let mode = "solve";
const displayMediaOptions = {
  video: true,
  audio: true,
};

evaluateBtn.addEventListener("click", evaluate);

mf.addEventListener("keyup", (e) => {
  if (e.key == "Enter") evaluate();
});

dropdownItems.forEach((item) => {
  item.addEventListener("click", (e) => {
    e.preventDefault();
    // Remove active from all
    dropdownItems.forEach((i) => i.classList.remove("active"));
    // Set active to clicked
    item.classList.add("active");
    // Update current mode
    mode = item.id;
    evaluateBtn.textContent = item.textContent;
    evaluate();
  });
});

async function evaluate() {
  let resp = await window.pywebview.api.evaluate(mf.value, mode);

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
  renderMathInElement(steps);
  renderMathInElement(out);
}
