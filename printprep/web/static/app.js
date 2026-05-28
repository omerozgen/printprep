"use strict";

import {
  loadModelFromFile, setOverhang, setHoles, setThin, setBodies, setInverted,
  getBodyCount, setMeasureMode, clearMeasurements, getMeasurements,
  setClipping, getModelBounds,
} from "./viewer.js";

let currentFile = null;
let originalFile = null;     // what the user uploaded (for the before/after toggle)
let fixedBlob = null;        // last successful fix output
let showingFixed = false;

const els = {
  dropZone: document.getElementById("drop-zone"),
  fileInput: document.getElementById("file-input"),
  browseBtn: document.getElementById("browse-btn"),
  fileName: document.getElementById("file-name"),
  status: document.getElementById("status"),
  viewerSection: document.getElementById("viewer-section"),
  overhangToggle: document.getElementById("overhang-toggle"),
  holesToggle: document.getElementById("holes-toggle"),
  thinToggle: document.getElementById("thin-toggle"),
  bodiesToggle: document.getElementById("bodies-toggle"),
  invertedToggle: document.getElementById("inverted-toggle"),
  bodyBadge: document.getElementById("body-badge"),
  measureToggle: document.getElementById("measure-toggle"),
  measureClear: document.getElementById("measure-clear"),
  measureHint: document.getElementById("measure-hint"),
  measureList: document.getElementById("measure-list"),
  clipToggle: document.getElementById("clip-toggle"),
  clipControls: document.getElementById("clip-controls"),
  clipAxis: document.getElementById("clip-axis"),
  clipSlider: document.getElementById("clip-slider"),
  clipValue: document.getElementById("clip-value"),
  clipFlip: document.getElementById("clip-flip"),
  results: document.getElementById("results"),
  props: document.getElementById("props"),
  issues: document.getElementById("issues"),
  fixBtn: document.getElementById("fix-btn"),
  fixReport: document.getElementById("fix-report"),
  orientBtn: document.getElementById("orient-btn"),
  orientReport: document.getElementById("orient-report"),
  baToggle: document.getElementById("ba-toggle"),
  mergeBtn: document.getElementById("merge-btn"),
  mergeReport: document.getElementById("merge-report"),
  suggestSection: document.getElementById("suggest-section"),
  slicerSelect: document.getElementById("slicer-select"),
  materialSelect: document.getElementById("material-select"),
  suggestBtn: document.getElementById("suggest-btn"),
  profileInput: document.getElementById("profile-input"),
  importBtn: document.getElementById("import-btn"),
  profileFile: document.getElementById("profile-file"),
  importClear: document.getElementById("import-clear"),
  profileResult: document.getElementById("profile-result"),
  profileTitle: document.getElementById("profile-title"),
  copyJson: document.getElementById("copy-json"),
  profileGrid: document.getElementById("profile-grid"),
  profileOutput: document.getElementById("profile-output"),
  estimateBlock: document.getElementById("estimate-block"),
  estimateGrid: document.getElementById("estimate-grid"),
  priceInput: document.getElementById("price-input"),
  currencyInput: document.getElementById("currency-input"),
  exportFormat: document.getElementById("export-format"),
  exportPrinter: document.getElementById("export-printer"),
  exportBtn: document.getElementById("export-btn"),
  exportHint: document.getElementById("export-hint"),
  batchInput: document.getElementById("batch-input"),
  batchBtn: document.getElementById("batch-btn"),
  batchCsv: document.getElementById("batch-csv"),
  batchStatus: document.getElementById("batch-status"),
  batchResult: document.getElementById("batch-result"),
};

let importedProfile = null;
let lastProfileJson = "";

// Click an analysis issue -> enable the matching 3D highlight + scroll into view.
function scrollToViewer() {
  els.viewerSection.scrollIntoView({ behavior: "smooth", block: "start" });
}
const ISSUE_ACTIONS = {
  overhang: () => { els.overhangToggle.checked = true; setOverhang(true); scrollToViewer(); },
  holes: () => { els.holesToggle.checked = true; setHoles(true); scrollToViewer(); },
  thin: () => {
    els.thinToggle.checked = true;
    showStatus("İnce duvar hesaplanıyor…", false);
    setTimeout(() => { setThin(true); hideStatus(); scrollToViewer(); }, 30);
  },
  bodies: () => { els.bodiesToggle.checked = true; setBodies(true); scrollToViewer(); },
  inverted: () => { els.invertedToggle.checked = true; setInverted(true); scrollToViewer(); },
};

function showStatus(msg, isError) {
  els.status.textContent = msg;
  els.status.classList.toggle("error", !!isError);
  els.status.hidden = false;
}
function hideStatus() { els.status.hidden = true; }

// ---- file selection ----
els.browseBtn.addEventListener("click", () => els.fileInput.click());
els.dropZone.addEventListener("click", (e) => {
  if (e.target === els.browseBtn) return;
  els.fileInput.click();
});
els.fileInput.addEventListener("change", () => {
  if (els.fileInput.files.length) handleFile(els.fileInput.files[0]);
});

["dragenter", "dragover"].forEach((evt) =>
  els.dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    els.dropZone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((evt) =>
  els.dropZone.addEventListener(evt, (e) => {
    e.preventDefault();
    els.dropZone.classList.remove("dragover");
  })
);
els.dropZone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

function handleFile(file) {
  currentFile = file;
  originalFile = file;
  fixedBlob = null;
  showingFixed = false;
  els.baToggle.hidden = true;
  els.fileName.textContent = file.name;
  els.fixReport.hidden = true;
  els.orientReport.hidden = true;
  els.mergeReport.hidden = true;
  els.profileResult.hidden = true;
  els.viewerSection.hidden = false;
  els.bodyBadge.hidden = true;
  els.bodiesToggle.checked = false;
  els.measureToggle.checked = false;
  els.measureHint.hidden = true;
  els.clipToggle.checked = false;
  els.clipControls.hidden = true;
  delete els.clipSlider.dataset.axis;
  els.measureList.innerHTML = "";
  els.measureClear.hidden = true;
  loadModelFromFile(file)
    .then(() => {
      const n = getBodyCount();
      els.bodyBadge.textContent = `${n} gövde`;
      els.bodyBadge.hidden = false;
      setBodies(false);
    })
    .catch((err) => showStatus("3D önizleme hatası: " + err.message, true));
  analyze();
}

els.overhangToggle.addEventListener("change", () => setOverhang(els.overhangToggle.checked));
els.bodiesToggle.addEventListener("change", () => setBodies(els.bodiesToggle.checked));
els.invertedToggle.addEventListener("change", () => setInverted(els.invertedToggle.checked));

// ---- measurement tool ----
function renderMeasurements() {
  const list = getMeasurements();
  els.measureList.innerHTML = list
    .map((m) => `<li>${m.distance_mm.toFixed(2)} mm</li>`).join("");
  els.measureClear.hidden = list.length === 0;
}
window.__printprepOnMeasure = renderMeasurements;

els.measureToggle.addEventListener("change", () => {
  const on = els.measureToggle.checked;
  setMeasureMode(on);
  els.measureHint.hidden = !on;
});
els.measureClear.addEventListener("click", () => { clearMeasurements(); });

// ---- cross-section ----
function refreshClip() {
  const on = els.clipToggle.checked;
  els.clipControls.hidden = !on;
  if (!on) {
    setClipping(false);
    els.clipValue.textContent = "—";
    return;
  }
  const bounds = getModelBounds();
  if (!bounds) return;
  const axis = els.clipAxis.value;
  const lo = bounds.min[axis], hi = bounds.max[axis];
  // Configure slider range whenever axis changes or first enable.
  if (!els.clipSlider.dataset.axis || els.clipSlider.dataset.axis !== axis) {
    els.clipSlider.min = lo.toFixed(2);
    els.clipSlider.max = hi.toFixed(2);
    els.clipSlider.value = ((lo + hi) / 2).toFixed(2);
    els.clipSlider.dataset.axis = axis;
  }
  const pos = parseFloat(els.clipSlider.value);
  setClipping(true, axis, pos, els.clipFlip.checked);
  els.clipValue.textContent = `${axis.toUpperCase()} = ${pos.toFixed(1)} mm`;
}
els.clipToggle.addEventListener("change", refreshClip);
els.clipAxis.addEventListener("change", () => { delete els.clipSlider.dataset.axis; refreshClip(); });
els.clipSlider.addEventListener("input", refreshClip);
els.clipFlip.addEventListener("change", refreshClip);
els.holesToggle.addEventListener("change", () => setHoles(els.holesToggle.checked));
els.thinToggle.addEventListener("change", () => {
  if (els.thinToggle.checked) showStatus("İnce duvar hesaplanıyor…", false);
  // defer so the status paints before the (blocking) raycast pass
  setTimeout(() => {
    setThin(els.thinToggle.checked);
    if (els.thinToggle.checked) hideStatus();
  }, 30);
});

// ---- analyze ----
async function analyze() {
  showStatus("Analiz ediliyor…", false);
  const form = new FormData();
  form.append("model", currentFile);
  try {
    const res = await fetch("/api/analyze", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Analiz başarısız");
    hideStatus();
    renderResults(data);
  } catch (err) {
    showStatus(err.message, true);
    els.results.hidden = true;
    els.suggestSection.hidden = true;
  }
}

function prop(label, value, cls) {
  const v = cls ? `<span class="value ${cls}">${value}</span>` : `<span class="value">${value}</span>`;
  return `<div class="prop"><span class="label">${label}</span>${v}</div>`;
}

function yn(b) { return b ? ["Evet", "ok"] : ["Hayır", "bad"]; }

function renderResults(d) {
  const dim = d.dimensions_mm.map((x) => x.toFixed(1)).join(" × ");
  const [wt, wtc] = yn(d.is_watertight);
  const [wn, wnc] = yn(d.is_winding_consistent);
  const [pv, pvc] = yn(d.is_volume);

  let overhang = "yok";
  if (d.overhang_face_count > 0) {
    overhang = `${d.overhang_face_count} yüzey, max ${d.steepest_overhang_deg.toFixed(0)}° ` +
      `(%${(d.overhang_area_fraction * 100).toFixed(1)} alan)`;
  }
  const wall = d.wall_thickness
    ? `min ${d.wall_thickness.min_mm.toFixed(2)} / p5 ${d.wall_thickness.p5_mm.toFixed(2)} / med ${d.wall_thickness.p50_mm.toFixed(2)} mm`
    : "n/a";
  const holesSummary = (d.holes && d.holes.length > 0)
    ? `${d.holes.length} (en büyük ${d.holes[0].perimeter_mm.toFixed(1)} mm)`
    : (d.is_watertight ? "yok" : "—");

  const rows = [
    prop("Hacim", `${(d.volume_mm3 / 1000).toFixed(2)} cm³`),
    prop("Yüzey alanı", `${(d.surface_area_mm2 / 100).toFixed(2)} cm²`),
    prop("Boyut", `${dim} mm`),
    prop("Üçgen / vertex", `${d.face_count} / ${d.vertex_count}`),
    prop("Gövde sayısı", d.body_count),
    prop("Su sızdırmaz", wt, wtc),
    prop("Tutarlı normaller", wn, wnc),
    prop("Basılabilir", pv, pvc),
    prop("Bozuk yüzey", d.degenerate_faces),
    prop("Çift yüzey", d.duplicate_faces),
    prop("Overhang", overhang),
    prop("Duvar kalınlığı", wall),
    prop("Delikler", holesSummary),
  ];
  if (d.non_manifold_edges > 0) {
    rows.push(prop("Non-manifold kenar", d.non_manifold_edges, "bad"));
  }
  els.props.innerHTML = rows.join("");

  if (d.issues.length === 0) {
    els.issues.innerHTML = `<li class="none">Sorun bulunamadı — baskıya hazır.</li>`;
  } else {
    els.issues.innerHTML = d.issues.map((i) => {
      const text = typeof i === "string" ? i : i.text;
      const kind = (typeof i === "object" && i.kind) || "";
      const clickable = kind in ISSUE_ACTIONS;
      const cls = clickable ? "issue-row clickable" : "issue-row";
      const hint = clickable ? ' <span class="issue-hint">3D\'de göster →</span>' : "";
      return `<li class="${cls}" data-kind="${kind}">⚠ ${text}${hint}</li>`;
    }).join("");
    els.issues.querySelectorAll("li.clickable").forEach((li) => {
      li.addEventListener("click", () => {
        const fn = ISSUE_ACTIONS[li.dataset.kind];
        if (fn) fn();
      });
    });
  }

  els.results.hidden = false;
  els.suggestSection.hidden = false;
}

// ---- fix ----
els.fixBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  els.fixBtn.disabled = true;
  showStatus("Onarılıyor…", false);
  const form = new FormData();
  form.append("model", currentFile);
  try {
    const res = await fetch("/api/fix", { method: "POST", body: form });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Onarım başarısız");
    }
    const blob = await res.blob();
    const name = (currentFile.name.replace(/\.stl$/i, "") || "model") + "_fixed.stl";

    const before = res.headers.get("X-Watertight-Before");
    const after = res.headers.get("X-Watertight-After");
    const openEdges = parseInt(res.headers.get("X-Open-Edges") || "0", 10);
    const method = res.headers.get("X-Method");
    const residual = after === "True"
      ? ""
      : `<li>Kalan açık kenar: ${openEdges} (manuel onarım gerekebilir)</li>`;
    const methodLine = method === "meshfix"
      ? `<li>Yöntem: agresif onarım (pymeshfix)</li>`
      : "";
    els.fixReport.innerHTML =
      `<strong>Onarım tamamlandı</strong>` +
      `<ul>` +
      `<li>Su sızdırmaz: ${before} → ${after}</li>` +
      methodLine +
      `<li>Birleştirilen vertex: ${res.headers.get("X-Merged-Vertices")}</li>` +
      `<li>Silinen bozuk yüzey: ${res.headers.get("X-Removed-Degenerate")}</li>` +
      `<li>Delikler kapatıldı: ${res.headers.get("X-Holes-Filled")}</li>` +
      `<li>Hacim: ${(parseFloat(res.headers.get("X-Volume-Mm3")) / 1000).toFixed(2)} cm³</li>` +
      residual +
      `</ul>`;
    els.fixReport.hidden = false;

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    // Keep the repaired blob so the user can flip the viewer between before/after.
    fixedBlob = blob;
    showingFixed = false;  // viewer still shows the original; the toggle reveals the repair
    els.baToggle.textContent = "3D'de onarımı göster ↻";
    els.baToggle.hidden = false;
    hideStatus();
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.fixBtn.disabled = false;
  }
});

els.baToggle.addEventListener("click", () => {
  if (!fixedBlob || !originalFile) return;
  showingFixed = !showingFixed;
  const target = showingFixed ? fixedBlob : originalFile;
  currentFile = target;
  els.baToggle.textContent = showingFixed
    ? "3D'de orijinali göster ↻"
    : "3D'de onarımı göster ↻";
  loadModelFromFile(target).catch((err) =>
    showStatus("3D önizleme hatası: " + err.message, true)
  );
});

// ---- orient (suggest best print position) ----
els.orientBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  els.orientBtn.disabled = true;
  showStatus("En iyi pozisyon hesaplanıyor…", false);
  const form = new FormData();
  form.append("model", currentFile);
  try {
    const res = await fetch("/api/orient", { method: "POST", body: form });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Oryantasyon başarısız");
    }
    const blob = await res.blob();
    const improved = res.headers.get("X-Improved") === "True";
    const before = parseFloat(res.headers.get("X-Overhang-Before")) * 100;
    const after = parseFloat(res.headers.get("X-Overhang-After")) * 100;
    const euler = res.headers.get("X-Euler-Deg");

    els.orientReport.innerHTML = improved
      ? `<strong>Önerilen pozisyon uygulandı</strong><ul>` +
        `<li>Döndürme (XYZ°): ${euler}</li>` +
        `<li>Overhang alanı: %${before.toFixed(1)} → %${after.toFixed(1)}</li>` +
        `</ul><span class="muted-note">3D önizleme yeni pozisyonu gösteriyor. Döndürülmüş STL indirildi.</span>`
      : `<strong>Mevcut pozisyon zaten en iyisi</strong><br>` +
        `<span class="muted-note">Overhang alanı %${before.toFixed(1)} — daha iyi bir yatırma bulunamadı.</span>`;
    els.orientReport.hidden = false;

    // show the re-oriented model in the 3D viewer
    loadModelFromFile(blob).catch(() => {});

    if (improved) {
      const name = (currentFile.name.replace(/\.stl$/i, "") || "model") + "_oriented.stl";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }
    hideStatus();
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.orientBtn.disabled = false;
  }
});

// ---- merge separate bodies into one piece ----
els.mergeBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  els.mergeBtn.disabled = true;
  showStatus("Tek parçaya birleştiriliyor…", false);
  const form = new FormData();
  form.append("model", currentFile);
  try {
    const res = await fetch("/api/merge", { method: "POST", body: form });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Birleştirme başarısız");
    }
    const blob = await res.blob();
    const method = res.headers.get("X-Method");
    const before = res.headers.get("X-Bodies-Before");
    const after = res.headers.get("X-Bodies-After");
    const watertight = res.headers.get("X-Watertight-After");
    const methodTr = method === "boolean" ? "boolean union (gerçek kaynaşma)" : "tek dosyada birleştirme";
    els.mergeReport.innerHTML =
      `<strong>Birleştirme tamamlandı</strong><ul>` +
      `<li>Yöntem: ${methodTr}</li>` +
      `<li>Gövde: ${before} → ${after}</li>` +
      `<li>Su sızdırmaz: ${watertight}</li>` +
      `</ul><span class="muted-note">3D önizleme birleşmiş modeli gösteriyor. STL indirildi.</span>`;
    els.mergeReport.hidden = false;

    loadModelFromFile(blob).then(() => {
      els.bodyBadge.textContent = `${getBodyCount()} gövde`;
      els.bodyBadge.hidden = false;
    }).catch(() => {});

    const name = (currentFile.name.replace(/\.stl$/i, "") || "model") + "_merged.stl";
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    hideStatus();
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.mergeBtn.disabled = false;
  }
});

// ---- profile import (option: use your own slicer profile) ----
els.importBtn.addEventListener("click", () => els.profileInput.click());
els.profileInput.addEventListener("change", () => {
  if (els.profileInput.files.length) {
    importedProfile = els.profileInput.files[0];
    els.profileFile.textContent = importedProfile.name;
    els.importClear.hidden = false;
    els.materialSelect.disabled = true;
  }
});
els.importClear.addEventListener("click", () => {
  importedProfile = null;
  els.profileInput.value = "";
  els.profileFile.textContent = "";
  els.importClear.hidden = true;
  els.materialSelect.disabled = false;
});

const PROFILE_LABELS = {
  material: "Malzeme",
  layer_height_mm: ["Katman yüksekliği", "mm"],
  infill_pct: ["Infill", "%"],
  wall_count: "Duvar sayısı",
  supports: "Destek",
  support_style: "Destek tipi",
  brim: "Brim",
  nozzle_temp_c: ["Nozzle sıcaklığı", "°C"],
  bed_temp_c: ["Tabla sıcaklığı", "°C"],
  print_speed_mms: ["Baskı hızı", "mm/s"],
  max_volumetric_speed_mm3s: ["Maks. akış", "mm³/s"],
  retraction_mm: ["Retraction", "mm"],
  retraction_speed_mms: ["Retraction hızı", "mm/s"],
};

function fmtVal(v, unit) {
  if (typeof v === "boolean") return v ? "Evet" : "Hayır";
  return unit ? `${v} ${unit}` : `${v}`;
}

function fmtMinutes(m) {
  if (m == null) return "—";
  if (m < 60) return `${Math.round(m)} dk`;
  const h = Math.floor(m / 60), mm = Math.round(m - h * 60);
  return `${h} sa ${mm} dk`;
}

function renderProfile(payload) {
  // Backwards-compat: api/suggest may return either {profile, estimate} or a flat profile.
  const data = payload && payload.profile ? payload.profile : payload;
  const estimate = payload && payload.estimate ? payload.estimate : null;

  els.profileTitle.textContent = `${data.slicer} · ${data.material}`;
  els.profileGrid.innerHTML = Object.entries(PROFILE_LABELS).map(([key, label]) => {
    if (!(key in data)) return "";
    const [text, unit] = Array.isArray(label) ? label : [label, ""];
    return prop(text, fmtVal(data[key], unit));
  }).join("");
  lastProfileJson = JSON.stringify(data, null, 2);
  els.profileOutput.textContent = lastProfileJson;

  if (estimate) {
    const rows = [
      prop("Filament",
           `${(estimate.filament_length_mm / 1000).toFixed(2)} m  ` +
           `(${estimate.filament_weight_g.toFixed(1)} g)`),
      prop("Tahmini süre", fmtMinutes(estimate.print_time_min)),
    ];
    if (estimate.cost != null) {
      const cur = estimate.currency ? ` ${estimate.currency}` : "";
      rows.push(prop("Maliyet", `${estimate.cost.toFixed(2)}${cur}`));
    }
    els.estimateGrid.innerHTML = rows.join("");
    els.estimateBlock.hidden = false;
  } else {
    els.estimateBlock.hidden = true;
  }
  els.profileResult.hidden = false;
}

// ---- suggest ----
els.suggestBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  els.suggestBtn.disabled = true;
  const form = new FormData();
  form.append("model", currentFile);
  form.append("slicer", els.slicerSelect.value);
  form.append("material", els.materialSelect.value);
  const price = parseFloat(els.priceInput.value);
  if (!isNaN(price) && price > 0) {
    form.append("price_per_kg", String(price));
    form.append("currency", els.currencyInput.value.trim());
  }
  if (importedProfile) form.append("profile", importedProfile);
  try {
    const res = await fetch("/api/suggest", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Öneri başarısız");
    renderProfile(data);
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.suggestBtn.disabled = false;
  }
});

els.copyJson.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(lastProfileJson);
    els.copyJson.textContent = "kopyalandı ✓";
    setTimeout(() => (els.copyJson.textContent = "JSON kopyala"), 1500);
  } catch (_) {
    els.profileOutput.hidden = !els.profileOutput.hidden; // fallback: reveal raw JSON
  }
});

// ---- export importable slicer profile (.zip) ----
els.exportBtn.addEventListener("click", async () => {
  if (!currentFile) return;
  const fmt = els.exportFormat.value;
  els.exportBtn.disabled = true;
  showStatus("Profil dışa aktarılıyor…", false);
  const form = new FormData();
  form.append("model", currentFile);
  form.append("slicer", els.slicerSelect.value);
  form.append("material", els.materialSelect.value);
  form.append("fmt", fmt);
  const printerName = els.exportPrinter.value.trim();
  if (printerName) form.append("printer", printerName);
  if (importedProfile) form.append("profile", importedProfile);
  try {
    const res = await fetch("/api/export", { method: "POST", body: form });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Dışa aktarma başarısız");
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `printprep_${els.slicerSelect.value}_${fmt}.zip`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    els.exportHint.textContent = fmt === "orca"
      ? "OrcaSlicer/Creality Print: .json dosyalarını uygulamaya sürükle veya preset olarak içe aktar."
      : "PrusaSlicer: File > Import > Import Config ile .ini'yi yükle.";
    hideStatus();
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.exportBtn.disabled = false;
  }
});

// ---- init dropdowns ----
(async function loadOptions() {
  try {
    const res = await fetch("/api/options");
    const opts = await res.json();
    els.slicerSelect.innerHTML = opts.slicers
      .map((s) => `<option value="${s}">${s}</option>`).join("");
    els.materialSelect.innerHTML = opts.materials
      .map((m) => `<option value="${m}">${m.toUpperCase()}</option>`).join("");
    // Sensible defaults (match the CLI): Creality + PLA.
    if (opts.slicers.includes("creality")) els.slicerSelect.value = "creality";
    if (opts.materials.includes("pla")) els.materialSelect.value = "pla";
  } catch (_) { /* options endpoint unavailable */ }
})();

// ---- batch analysis ----
let batchRows = [];
let batchSort = { idx: null, dir: 1 };

const BATCH_COLS = [
  { label: "Dosya", text: (r) => r.filename, sort: (r) => r.filename || "" },
  { label: "Boyut (mm)", text: (r) => r.dimensions_mm ? r.dimensions_mm.map((x) => x.toFixed(0)).join("×") : "—",
    sort: (r) => r.dimensions_mm ? r.dimensions_mm[0] * r.dimensions_mm[1] * r.dimensions_mm[2] : -1 },
  { label: "Hacim (cm³)", text: (r) => r.volume_cm3 != null ? r.volume_cm3 : "—", sort: (r) => r.volume_cm3 ?? -1 },
  { label: "Su sızdırmaz", text: (r) => r.error ? "—" : (r.is_watertight ? "Evet" : "Hayır"), sort: (r) => (r.is_watertight ? 1 : 0) },
  { label: "Gövde", text: (r) => r.body_count ?? "—", sort: (r) => r.body_count ?? -1 },
  { label: "Overhang %", text: (r) => r.overhang_pct != null ? r.overhang_pct : "—", sort: (r) => r.overhang_pct ?? -1 },
  { label: "Min duvar", text: (r) => r.min_wall_mm != null ? r.min_wall_mm.toFixed(2) : "—", sort: (r) => r.min_wall_mm ?? -1 },
  { label: "Sorun", text: (r) => r.error ? "hata" : r.issue_count, sort: (r) => r.error ? 999 : (r.issue_count ?? 0) },
];

function renderBatch() {
  if (batchRows.length === 0) { els.batchResult.innerHTML = ""; return; }
  let rows = batchRows.slice();
  if (batchSort.idx != null) {
    const col = BATCH_COLS[batchSort.idx];
    rows.sort((a, b) => {
      const va = col.sort(a), vb = col.sort(b);
      return (va < vb ? -1 : va > vb ? 1 : 0) * batchSort.dir;
    });
  }
  const head = BATCH_COLS.map((c, i) => {
    const arrow = batchSort.idx === i ? (batchSort.dir === 1 ? " ▲" : " ▼") : "";
    return `<th data-idx="${i}">${c.label}${arrow}</th>`;
  }).join("");
  const body = rows.map((r) => {
    if (r.error) {
      return `<tr><td>${r.filename}</td><td colspan="${BATCH_COLS.length - 1}" class="batch-err">${r.error}</td></tr>`;
    }
    return "<tr>" + BATCH_COLS.map((c) => `<td>${c.text(r)}</td>`).join("") + "</tr>";
  }).join("");
  els.batchResult.innerHTML = `<table class="batch-table"><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
  els.batchResult.querySelectorAll("th[data-idx]").forEach((th) => {
    th.addEventListener("click", () => {
      const idx = parseInt(th.dataset.idx, 10);
      if (batchSort.idx === idx) batchSort.dir *= -1;
      else { batchSort.idx = idx; batchSort.dir = 1; }
      renderBatch();
    });
  });
}

els.batchBtn.addEventListener("click", () => els.batchInput.click());
els.batchInput.addEventListener("change", async () => {
  const files = [...els.batchInput.files];
  if (files.length === 0) return;
  els.batchStatus.textContent = `${files.length} dosya analiz ediliyor…`;
  els.batchCsv.hidden = true;
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  try {
    const res = await fetch("/api/batch", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Toplu analiz başarısız");
    batchRows = data.results;
    batchSort = { idx: null, dir: 1 };
    renderBatch();
    const ok = batchRows.filter((r) => !r.error).length;
    els.batchStatus.textContent = `${ok}/${batchRows.length} analiz edildi.`;
    els.batchCsv.hidden = batchRows.length === 0;
  } catch (err) {
    els.batchStatus.textContent = "Hata: " + err.message;
  }
});

els.batchCsv.addEventListener("click", () => {
  const header = BATCH_COLS.map((c) => c.label).join(",");
  const lines = batchRows.map((r) =>
    BATCH_COLS.map((c) => {
      const v = r.error && c.label !== "Dosya" ? "" : String(c.text(r)).replace(/×/g, "x");
      return /[",]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
    }).join(","),
  );
  const csv = [header, ...lines].join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = "printprep_batch.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});
