"use strict";

import { loadModelFromFile, setOverhang, setHoles, setThin, setBodies, setInverted, getBodyCount } from "./viewer.js";

let currentFile = null;

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
  results: document.getElementById("results"),
  props: document.getElementById("props"),
  issues: document.getElementById("issues"),
  fixBtn: document.getElementById("fix-btn"),
  fixReport: document.getElementById("fix-report"),
  orientBtn: document.getElementById("orient-btn"),
  orientReport: document.getElementById("orient-report"),
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
  exportFormat: document.getElementById("export-format"),
  exportBtn: document.getElementById("export-btn"),
  exportHint: document.getElementById("export-hint"),
};

let importedProfile = null;
let lastProfileJson = "";

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
  els.fileName.textContent = file.name;
  els.fixReport.hidden = true;
  els.orientReport.hidden = true;
  els.mergeReport.hidden = true;
  els.profileResult.hidden = true;
  els.viewerSection.hidden = false;
  els.bodyBadge.hidden = true;
  els.bodiesToggle.checked = false;
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
  const minWall = d.min_wall_mm != null ? `${d.min_wall_mm.toFixed(2)} mm` : "n/a";

  els.props.innerHTML = [
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
    prop("Min duvar (tahmini)", minWall),
  ].join("");

  if (d.issues.length === 0) {
    els.issues.innerHTML = `<li class="none">Sorun bulunamadı — baskıya hazır.</li>`;
  } else {
    els.issues.innerHTML = d.issues.map((i) => `<li>⚠ ${i}</li>`).join("");
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
    const residual = after === "True"
      ? ""
      : `<li>Kalan açık kenar: ${openEdges} (manuel onarım gerekebilir)</li>`;
    els.fixReport.innerHTML =
      `<strong>Onarım tamamlandı</strong>` +
      `<ul>` +
      `<li>Su sızdırmaz: ${before} → ${after}</li>` +
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
    hideStatus();
  } catch (err) {
    showStatus(err.message, true);
  } finally {
    els.fixBtn.disabled = false;
  }
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

function renderProfile(data) {
  els.profileTitle.textContent = `${data.slicer} · ${data.material}`;
  els.profileGrid.innerHTML = Object.entries(PROFILE_LABELS).map(([key, label]) => {
    if (!(key in data)) return "";
    const [text, unit] = Array.isArray(label) ? label : [label, ""];
    return prop(text, fmtVal(data[key], unit));
  }).join("");
  lastProfileJson = JSON.stringify(data, null, 2);
  els.profileOutput.textContent = lastProfileJson;
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
