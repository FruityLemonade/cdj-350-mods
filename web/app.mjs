import stock from "./stock.mjs";
import { repackStock, validVersion, verifyStock } from "./firmware.mjs";

const get = (id) => document.getElementById(id);
const picker = get("firmware");
const pick = get("pick");
const dropzone = get("dropzone");
const version = get("version");
const modBoxes = [...document.querySelectorAll('#mods-panel input[type="checkbox"]')];
const build = get("build");
const download = get("download");
const patchCount = get("patch-count");

let input = null;
let checking = false;
let fileAttempt = 0;
let downloadUrl = null;
let activeWorker = null;
let displayedPatchCount = -1;

function status(message, tone = "") {
  get("status").textContent = message;
  get("status").dataset.tone = tone;
}

async function updatePatchCount(method) {
  if (!stock.counterUrl) return;
  try {
    const response = await fetch(stock.counterUrl, {
      method,
      credentials: "omit",
      referrerPolicy: "no-referrer",
      keepalive: method === "POST",
    });
    if (!response.ok) return;
    const { count } = await response.json();
    // A delayed read or earlier write can arrive after a newer total.
    if (!Number.isSafeInteger(count) || count <= displayedPatchCount) return;
    displayedPatchCount = count;
    patchCount.textContent = `${count.toLocaleString()} firmware ${count === 1 ? "build" : "builds"} completed`;
    patchCount.hidden = false;
  } catch {
    // The counter is independent of the firmware download.
  }
}

function resetDownload() {
  if (activeWorker) {
    activeWorker.terminate();
    activeWorker = null;
  }
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = null;
  download.removeAttribute("href");
  download.hidden = true;
  build.hidden = false;
}

function selectedMods() {
  return modBoxes.filter((box) => box.checked).map((box) => box.value);
}

function renderControls() {
  const selections = selectedMods();
  const hasMods = selections.length > 0;
  const badFormat = !validVersion(version.value);
  const sameVersion = hasMods && version.value === stock.stockVersion;
  const invalid = badFormat || sameVersion;
  const versionHelp = get("version-help");
  versionHelp.textContent = hasMods
    ? `Choose a version that differs from stock v${stock.stockVersion}.`
    : `Enter ${stock.stockVersion} for an exact copy of the original file.`;
  build.textContent = hasMods ? "Patch firmware" : "Repack firmware";
  get("input-summary").textContent = input ? `Verified v${stock.stockVersion}` : checking ? "Verifying…" : "Awaiting file";
  version.setAttribute("aria-invalid", String(invalid));
  build.disabled = !input || invalid || activeWorker !== null;
  if (!downloadUrl && !activeWorker) {
    if (badFormat) status("Enter a version like 1.15.", "error");
    else if (sameVersion) status("Choose a different output version for the patched update.", "error");
    else if (!input) status("Choose an original firmware file.");
    else status(hasMods ? `Ready to apply ${selections.length} ${selections.length === 1 ? "modification" : "modifications"}.` : "Ready to repack stock firmware.");
  }
}

async function chooseFile(file) {
  if (!file) return;
  const attempt = ++fileAttempt;
  const title = get("file-title");
  const detail = get("file-detail");
  const error = get("file-error");
  error.hidden = true;
  dropzone.dataset.ready = "false";
  input = null;
  checking = true;
  resetDownload();
  title.textContent = file.name;
  detail.textContent = "Checking the firmware fingerprint…";
  renderControls();

  try {
    if (!file.size || file.size > 0x400000) {
      throw new Error(`This file is the wrong size. Choose the original ${stock.model} v${stock.stockVersion} ${stock.filename}.`);
    }
    const bytes = await file.arrayBuffer();
    await verifyStock(bytes);
    if (attempt !== fileAttempt) return;
    input = bytes;
    dropzone.dataset.ready = "true";
    detail.textContent = `Verified v${stock.stockVersion} · ${(file.size / 1048576).toFixed(2)} MiB`;
    pick.textContent = "Change file";
  } catch (failure) {
    if (attempt !== fileAttempt) return;
    title.textContent = "Drop your update file here";
    detail.textContent = `Original v${stock.stockVersion} update · .UPD`;
    pick.textContent = "Choose file";
    error.textContent = failure.message;
    error.hidden = false;
  } finally {
    if (attempt === fileAttempt) {
      checking = false;
      renderControls();
    }
  }
}

pick.addEventListener("click", () => picker.click());
picker.addEventListener("change", () => {
  chooseFile(picker.files[0]);
  picker.value = "";
});
dropzone.addEventListener("dragover", (event) => {
  if (!event.dataTransfer.types.includes("Files")) return;
  event.preventDefault();
  event.dataTransfer.dropEffect = "copy";
  dropzone.classList.add("dragging");
});
dropzone.addEventListener("dragleave", (event) => {
  if (!dropzone.contains(event.relatedTarget)) dropzone.classList.remove("dragging");
});
dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("dragging");
  chooseFile(event.dataTransfer.files[0]);
});
function optionsChanged() {
  resetDownload();
  renderControls();
}

version.addEventListener("input", optionsChanged);
for (const box of modBoxes) box.addEventListener("change", optionsChanged);

function offerDownload(output, label, patched) {
  downloadUrl = URL.createObjectURL(new Blob([output], { type: "application/octet-stream" }));
  download.href = downloadUrl;
  build.hidden = true;
  download.hidden = false;
  status(patched ? `Patched firmware v${label} is ready.` : `Firmware v${label} repacked and verified.`, "success");
  download.focus();
  void updatePatchCount("POST");
}

build.addEventListener("click", () => {
  const label = version.value;
  const selections = selectedMods();
  if (build.disabled || !input) return;
  if (!selections.length) {
    offerDownload(repackStock(input, label), label, false);
    return;
  }

  const worker = new Worker(new URL("./worker.mjs", import.meta.url), { type: "module" });
  activeWorker = worker;
  renderControls();
  status("Loading the patching engine…");

  function finish(error, output) {
    if (activeWorker !== worker) return;
    worker.terminate();
    activeWorker = null;
    renderControls();
    if (error) status(error, "error");
    else offerDownload(output, label, true);
  }

  worker.addEventListener("message", ({ data }) => {
    if (activeWorker !== worker) return;
    if (data.type === "progress") status(data.message);
    if (data.type === "done") finish(null, data.output);
    if (data.type === "error") finish(data.message);
  });
  worker.addEventListener("error", () => finish("The patching engine could not load. Try again."));
  worker.postMessage({ input, selections, version: label });
});

renderControls();
void updatePatchCount("GET");
