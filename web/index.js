import { MathfieldElement } from "https://unpkg.com/mathlive?module";

const mf = document.querySelector("math-field");
const out = document.getElementById("latex-output");

mf.addEventListener("keydown", async (e) => {
  if (e.key !== "Enter") return;
  
  katex.render(await eel.evaluate(mf.value)(), out);
});
