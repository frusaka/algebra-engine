const resources = [
  {
    tag: "link",
    rel: "stylesheet",
    href: "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css",
    integrity:
      "sha384-LN+7fdVzj6u52u30Kp6M/trliBMCMKTyK833zpbD+pXdCLuTusPj697FH4R/5mcr",
    crossOrigin: "anonymous",
  },
  {
    tag: "link",
    rel: "stylesheet",
    href: "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.css",
    integrity:
      "sha384-5TcZemv2l/9On385z///+d7MSYlvIEw9FuZTIdZ14vJLqWphw7e7ZPuOiCHJcFCP",
    crossOrigin: "anonymous",
  },
  {
    tag: "script",
    src: "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js",
    integrity:
      "sha384-ndDqU0Gzau9qJ1lfW4pNLlhNTkCfHzAVBReH9diLvGRem5+R9g2FzA8ZGN954O5Q",
    crossOrigin: "anonymous",
  },
  {
    tag: "script",
    defer: true,
    type: "module",
    src: "https://esm.run/@cortex-js/compute-engine",
  },
  {
    tag: "script",
    defer: true,
    type: "module",
    src: "https://cdn.jsdelivr.net/npm/mathlive",
  },
  {
    tag: "script",
    defer: true,
    src: "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/katex.min.js",
    integrity:
      "sha384-cMkvdD8LoxVzGF/RPUKAcvmm49FQ0oxwDF3BGKtDXcEc+T1b2N+teh/OJfpU0jr6",
    crossOrigin: "anonymous",
  },
  // {
  //   tag: "script",
  //   defer: true,
  //   src: "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js",
  //   integrity:
  //     "sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh",
  //   crossOrigin: "anonymous",
  // },
];

if (
  await import("./lib/bootstrap.bundle.min.js").then(
    () => true,
    () => false
  )
) {
  ["lib/katex.min.css", "lib/bootstrap.min.css"].forEach((p) => {
    const el = document.createElement("link");
    el.rel = "stylesheet";
    el.href = p;
    document.head.appendChild(el);
  });

  import("./lib/mathlive.min.js");
  import("./lib/compute-engine.min.js").then(() => {
    document.dispatchEvent(new Event("ceready"));
  });
  import("./lib/katex.min.js").then(() => import("./lib/auto-render.min.js"));
} else {
  for (const res of resources) {
    if (res.tag == "script") {
      import(res.src).then(() => {
        if (res.src.endsWith("katex.min.js"))
          import(
            "https://cdn.jsdelivr.net/npm/katex@0.16.22/dist/contrib/auto-render.min.js"
          );
        else if (res.src.endsWith("compute-engine.min.js"))
          document.dispatchEvent(new Event("ceready"));
      });
    } else {
      const el = document.createElement(res.tag);
      Object.entries(res).forEach(([key, value]) => {
        if (key !== "tag") {
          el[key] = value;
        }
      });
      document.head.appendChild(el);
    }
  }
}
