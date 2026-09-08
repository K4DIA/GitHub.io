// The generator, running off the main thread.
//
// Pyodide is CPython compiled to WebAssembly. The book is laid out by the same
// Python that builds it on a desktop, so a book built here and a book built
// from a command line come out the same. Nothing is uploaded: the runtime, the
// code and the fonts come down once, and what the operator types stays here.
//
// This has to be a module worker. Pyodide's runtime is an ES module and will
// not load through importScripts. The file is named .js rather than .mjs
// because some static hosts serve an unknown extension as plain text, and a
// worker refused for its content type is a hard thing to diagnose.

// One line to change if you would rather serve Pyodide yourself than lean on
// a CDN. Point it at a directory holding a Pyodide release.
const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.6/full/";

let pyodide = null;
let webapi = null;
let ready = false;

const say = (text) => self.postMessage({ type: "status", text });

async function boot() {
  say("Fetching the Python runtime. This is the slow part, and it is cached "
      + "afterwards.");
  const { loadPyodide } = await import(PYODIDE + "pyodide.mjs");
  pyodide = await loadPyodide({ indexURL: PYODIDE });

  const manifest = await grab("manifest.json").then((r) => r.json());

  say("Installing the PDF library.");
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(new URL(manifest.wheel, self.location.href).href);
  micropip.destroy();

  say("Unpacking the book.");
  const zip = await grab(manifest.payload).then((r) => r.arrayBuffer());
  // unpackArchive writes into the working directory, which is already on
  // sys.path, so the modules and the fonts land where Python will find them.
  pyodide.unpackArchive(zip, "zip");
  pyodide.runPython(
    "import os, sys\n" +
    "if os.getcwd() not in sys.path:\n" +
    "    sys.path.insert(0, os.getcwd())\n");

  webapi = pyodide.pyimport("webapi");
  ready = true;
  self.postMessage({ type: "ready" });
}

async function grab(path) {
  const r = await fetch(new URL(path, self.location.href).href,
                        { cache: "force-cache" });
  if (!r.ok) throw new Error(`could not load ${path} (${r.status})`);
  return r;
}

// Called from Python once per layout pass, so the page can show something
// moving during the wait.
const progress = (text) =>
  self.postMessage({ type: "progress", text: String(text) });

function build(msg) {
  const cfg = pyodide.toPy(msg.config);
  let out = null;
  try {
    out = webapi.build(cfg, ".", progress,
                       msg.repeaters || null, msg.nets || null);
    const meta = out.toJs({ dict_converter: Object.fromEntries });
    const pdf = new Uint8Array(meta.pdf);   // off the wasm heap, into our own
    delete meta.pdf;
    self.postMessage({ type: "done", pdf, meta }, [pdf.buffer]);
  } finally {
    cfg.destroy();
    if (out) out.destroy();
  }
}

function estimate(msg) {
  const cfg = pyodide.toPy(msg.config);
  try {
    self.postMessage({ type: "estimate", id: msg.id,
                       pages: webapi.estimate(cfg, ".") });
  } finally {
    cfg.destroy();
  }
}

self.onmessage = async (e) => {
  const msg = e.data;
  try {
    if (msg.type === "init") {
      await boot();
      return;
    }
    if (!ready) return;
    if (msg.type === "build") build(msg);
    else if (msg.type === "estimate") estimate(msg);
  } catch (err) {
    self.postMessage({ type: "error", what: msg && msg.type,
                       text: readable(err) });
  }
};

// A Python exception arrives with its whole traceback attached. The last line
// is the part somebody can act on; the rest belongs in the console.
function readable(err) {
  const text = err && err.message ? err.message : String(err);
  console.error(text);
  const lines = text.trim().split("\n").filter((l) => l.trim());
  const last = lines[lines.length - 1] || "something went wrong";
  return last.replace(/^[\w.]*(Error|Exception):\s*/, "");
}
