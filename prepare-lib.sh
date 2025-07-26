#!/bin/bash
npm install katex mathlive bootstrap

rm -rf web/lib/*
mkdir web/lib
mkdir web/lib/fonts
mkdir web/lib/sounds


cp node_modules/katex/dist/katex.min.css web/lib
cp node_modules/katex/dist/katex.min.js web/lib
cp node_modules/katex/dist/contrib/auto-render.min.js web/lib
cp node_modules/mathlive/mathlive.min.js web/lib
cp node_modules/@cortex-js/compute-engine/dist/compute-engine.min.js web/lib

cp node_modules/katex/dist/fonts/* web/lib/fonts
cp node_modules/mathlive/sounds/* web/lib/sounds


cp node_modules/bootstrap/dist/css/bootstrap.min.css web/lib
cp node_modules/bootstrap/dist/css/bootstrap.min.css.map web/lib
cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js web/lib
cp node_modules/bootstrap/dist/js/bootstrap.bundle.min.js.map web/lib
