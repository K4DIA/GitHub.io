// The form. Every control on the page is drawn from catalogue.json, which the
// generator writes out, so adding a radio card or a reference section reaches
// this page without anybody editing JavaScript.

const $ = (id) => document.getElementById(id);
const worker = new Worker("worker.js", { type: "module" });

let cat = null;
let built = null;          // the object URL of the last download, if any
let estimateId = 0;
let busy = false;
let ready = false;   // the generator has finished loading

// --------------------------------------------------------------------------
// drawing the form
// --------------------------------------------------------------------------
function check(name, id, label, extra) {
  const wrap = document.createElement("label");
  wrap.className = "check";
  const box = document.createElement("input");
  box.type = "checkbox";
  box.checked = true;
  box.dataset.group = name;
  box.value = id;
  box.addEventListener("change", changed);
  const text = document.createElement("span");
  text.textContent = label;
  if (extra) {
    const e = document.createElement("span");
    e.className = "pages";
    e.textContent = " " + extra;
    text.appendChild(e);
  }
  wrap.append(box, text);
  return wrap;
}

function drawForm(c) {
  const lic = $("license_class");
  c.license_classes.forEach((k) => lic.add(new Option(k.label, k.key)));
  lic.value = c.defaults.license_class;

  const st = $("state");
  st.add(new Option("Not saying", ""));
  c.states.forEach((s) => st.add(new Option(s.name, s.code)));

  c.parts.forEach((p) => $("parts").appendChild(
    check("parts", p.key, p.label)));
  c.reference.forEach((r) => $("reference").appendChild(
    check("reference", r.tag, r.title)));
  c.records.forEach((r) => $("records").appendChild(
    check("records", r.key, r.title)));

  c.presets.forEach((p) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "preset";
    b.textContent = p.key;
    b.setAttribute("aria-pressed", p.key === "full" ? "true" : "false");
    b.addEventListener("click", () => applyPreset(p));
    $("presets").appendChild(b);
  });
  $("preset-note").textContent = c.presets[0].note;

  c.radios.forEach((r) => $("radios").appendChild(radioRow(r)));

  document.querySelectorAll("[data-all]").forEach((b) =>
    b.addEventListener("click", () => setGroup(b.dataset.all, true)));
  document.querySelectorAll("[data-none]").forEach((b) =>
    b.addEventListener("click", () => setGroup(b.dataset.none, false)));
}

function radioRow(r) {
  const d = document.createElement("details");
  d.className = "radio";
  const s = document.createElement("summary");
  const box = document.createElement("input");
  box.type = "checkbox";
  box.dataset.group = "radios";
  box.value = r.id;
  box.addEventListener("change", changed);
  box.addEventListener("click", (e) => e.stopPropagation());
  const name = document.createElement("span");
  name.textContent = r.name;
  const maker = document.createElement("span");
  maker.className = "maker";
  maker.textContent = r.maker;
  s.append(box, name, maker);

  const prov = document.createElement("p");
  prov.className = "prov";
  prov.textContent = r.verified || "No source line on this card.";
  const blocks = document.createElement("p");
  blocks.className = "blocks";
  blocks.textContent = r.blocks.join(" · ");

  d.append(s, prov, blocks);
  return d;
}

// --------------------------------------------------------------------------
// reading the form
// --------------------------------------------------------------------------
function group(name) {
  return Array.from(
    document.querySelectorAll(`input[data-group="${name}"]`));
}

function picked(name) {
  return group(name).filter((b) => b.checked).map((b) => b.value);
}

function setGroup(name, on) {
  group(name).forEach((b) => { b.checked = on; });
  changed();
}

function applyPreset(p) {
  document.querySelectorAll("#presets .preset").forEach((b) =>
    b.setAttribute("aria-pressed", String(b.textContent === p.key)));
  $("preset-note").textContent = p.note;
  group("parts").forEach((b) => { b.checked = !!p.include.parts[b.value]; });
  group("reference").forEach((b) => {
    b.checked = p.include.reference.indexOf(b.value) >= 0;
  });
  group("records").forEach((b) => {
    b.checked = p.include.records.indexOf(b.value) >= 0;
  });
  changed();
}

function config() {
  const state = $("state").value;
  const include = {};
  cat.parts.forEach((p) => { include[p.key] = false; });
  picked("parts").forEach((k) => { include[k] = true; });
  include.reference = picked("reference");
  include.station_records = picked("records");

  const c = {
    station: {
      name: $("name").value.trim(),
      callsign: $("callsign").value.trim().toUpperCase(),
      license_class: $("license_class").value,
      grid: $("grid").value.trim().toUpperCase(),
      club: $("club").value.trim(),
    },
    book: { deployments: Number($("deployments").value) || 26 },
    radios: picked("radios"),
    include: include,
  };
  if (state) c.station.state = state;
  const sec = $("arrl_section");
  if (!$("section-wrap").hidden && sec.value) c.station.arrl_section = sec.value;
  return c;
}

// --------------------------------------------------------------------------
// reacting
// --------------------------------------------------------------------------
// A part switched off takes its children with it, which the generator does on
// its own. The form shows it happening so nobody is left ticking a box that
// cannot apply.
const CHILDREN = {
  part_one: ["band_plan", "repeaters", "radios"],
  part_two: ["deployment_howto", "deployment_index"],
};

function follow() {
  const on = {};
  group("parts").forEach((b) => { on[b.value] = b.checked; });
  Object.entries(CHILDREN).forEach(([parent, kids]) => {
    kids.forEach((k) => {
      const box = group("parts").find((b) => b.value === k);
      if (box) {
        box.disabled = !on[parent];
        box.closest(".check").style.opacity = on[parent] ? "" : "0.45";
      }
    });
  });
  ["reference", "records", "radios"].forEach((g) => {
    const parent = g === "records" ? "part_three"
      : g === "radios" ? "radios" : "part_one";
    const live = on[parent] !== false && (g !== "radios" || on.part_one !== false);
    group(g).forEach((b) => {
      b.disabled = !live;
      const row = b.closest(".check") || b.closest("details");
      if (row) row.style.opacity = live ? "" : "0.45";
    });
  });
}

function changed() {
  follow();
  const n = Number($("deployments").value);
  const bad = !(n >= 1 && n <= 60);
  $("deployments").setAttribute("aria-invalid", String(bad));
  $("go").disabled = busy || bad || !cat || !ready;
  if (bad) {
    $("pagecount").textContent = "—";
    $("sheetcount").textContent = "—";
    return;
  }
  $("dep-note").textContent = n > 40
    ? "Past about forty the book stops being packable, and building it here "
      + "asks a lot of a phone."
    : "";
  estimateId += 1;
  worker.postMessage({ type: "estimate", config: config(), id: estimateId });
}

function stateChanged() {
  const code = $("state").value;
  const s = cat.states.find((x) => x.code === code);
  const wrap = $("section-wrap");
  const sel = $("arrl_section");
  sel.innerHTML = "";
  if (s && s.sections.length > 1) {
    sel.add(new Option("Leave it blank", ""));
    s.sections.forEach((k) =>
      sel.add(new Option(`${k}, ${cat.section_names[k] || k}`, k)));
    wrap.hidden = false;
  } else {
    wrap.hidden = true;
  }
  $("state-note").textContent = s
    ? `ARRL section, time zone and the repeater heading follow ${s.name}.`
    : "Leave this blank and the section and repeater pages come through unheaded.";
  changed();
}

function readFile(input) {
  const f = input.files && input.files[0];
  if (!f) return Promise.resolve(null);
  return f.text();
}

async function go() {
  if (busy) return;
  busy = true;
  $("go").disabled = true;
  $("result").classList.remove("on");
  $("bar").classList.add("on");
  status("Building. A full book takes about fifteen seconds on a laptop, longer on a phone.");
  try {
    const [repeaters, nets] = await Promise.all(
      [readFile($("repeaters")), readFile($("nets"))]);
    worker.postMessage({
      type: "build", config: config(), repeaters: repeaters, nets: nets,
    });
  } catch (e) {
    finish();
    status("Could not read that CSV: " + e.message, true);
  }
}

function finish() {
  busy = false;
  $("bar").classList.remove("on");
  changed();
}

function status(text, bad) {
  const el = $("status");
  el.textContent = text;
  el.classList.toggle("bad", !!bad);
}

function show(meta, pdf) {
  const blob = new Blob([pdf], { type: "application/pdf" });
  if (built) URL.revokeObjectURL(built);
  built = URL.createObjectURL(blob);
  const a = $("download");
  a.href = built;
  a.download = meta.filename;

  const facts = [
    ["Book", `${meta.pages} pages, ${meta.sheets} sheets printed both sides`],
    ["Operator", `${meta.byline}, ${meta.license_class}`],
  ];
  if (meta.place) {
    facts.push(["Keyed to",
      `${meta.place}. Your UTC day rolls over at ${meta.utc_rollover} local.`]);
  }
  if (meta.deployments) {
    facts.push(["Deployments",
      `${meta.deployments}, four pages each`]);
  }
  if (meta.left_out && meta.left_out.length) {
    const label = {};
    cat.parts.forEach((p) => { label[p.key] = p.label.toLowerCase(); });
    facts.push(["Left out",
      meta.left_out.map((k) => label[k] || k).join(", ")]);
  }
  const dl = $("result-facts");
  dl.innerHTML = "";
  facts.forEach(([k, v]) => {
    const dt = document.createElement("dt");
    dt.textContent = k;
    const dd = document.createElement("dd");
    dd.textContent = v;
    dl.append(dt, dd);
  });
  $("result").classList.add("on");

  let line = "Done. Print it single sided, or both sides on the long edge.";
  if (meta.section_ambiguous) {
    line = `Done. ${meta.place || "Your state"} holds several ARRL sections `
      + `(${meta.section_choices.join(", ")}); the book leaves the line blank `
      + "for you to write in.";
  }
  status(line);
}

// --------------------------------------------------------------------------
worker.onmessage = (e) => {
  const m = e.data;
  if (m.type === "status") status(m.text);
  else if (m.type === "progress") status(capital(m.text) + "…");
  else if (m.type === "ready") {
    ready = true;
    status("Ready. Fill in what applies to you and build.");
    changed();
  } else if (m.type === "estimate") {
    if (m.id !== estimateId || m.pages == null) return;
    $("pagecount").textContent = m.pages;
    $("sheetcount").textContent = Math.ceil(m.pages / 2);
  } else if (m.type === "done") {
    finish();
    show(m.meta, m.pdf);
  } else if (m.type === "error") {
    finish();
    status(capital(m.text), true);
  }
};

function capital(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

async function start() {
  cat = await (await fetch("catalogue.json")).json();
  drawForm(cat);
  $("state").addEventListener("change", stateChanged);
  ["name", "callsign", "grid", "club", "deployments", "license_class"]
    .forEach((id) => $(id).addEventListener("input", changed));
  $("go").addEventListener("click", go);
  stateChanged();
  worker.postMessage({ type: "init" });
}

start();
