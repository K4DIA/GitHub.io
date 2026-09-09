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

// The Python runtime is served from this site, not from a CDN. A logbook is
// a field tool, and the field is where the signal is worst; a generator that
// needs a working connection to a third party is a generator that fails in
// the car park. Everything it needs is in pyodide/ beside this file, so the
// only thing between an operator and a book is this site itself, and after
// one visit the service worker means not even that.
//
// Point this at a directory holding any Pyodide release to move it.
const PYODIDE = "pyodide/";

let pyodide = null;
let webapi = null;
let ready = false;

const say = (text) => self.postMessage({ type: "status", text });

async function boot() {
  say("Starting the Python runtime. This is the slow part, and it is kept "
      + "afterwards.");
  const runtime = new URL(PYODIDE, self.location.href).href;
  let loadPyodide;
  try {
    ({ loadPyodide } = await import(runtime + "pyodide.mjs"));
  } catch (err) {
    // Whatever the browser says here is about module resolution and means
    // nothing to an operator standing at a tailgate.
    throw new Error("The Python runtime would not load. It is served from "
      + "this site, so this usually means the page was opened from a folder "
      + "rather than over the web, or the first visit never finished "
      + "downloading. Open the logbook once with a connection and it will "
      + "work without one afterwards.");
  }
  pyodide = await loadPyodide({ indexURL: runtime });

  const manifest = await grab("manifest.json").then((r) => r.json());

  say("Loading the PDF library.");
  // loadPackage takes wheel URLs directly. Going through micropip would have
  // meant fetching micropip itself, and then letting it resolve reportlab's
  // dependencies over the network, which is the very thing being removed.
  // Resolving them here instead means the list is explicit and auditable:
  // reportlab imports PIL at import time, so Pillow is not optional.
  const wheels = (manifest.wheels || [manifest.wheel])
    .map((w) => new URL(w, self.location.href).href);
  await pyodide.loadPackage(wheels);

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
