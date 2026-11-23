import stock from "./stock.mjs";
import { repackStock, validVersion, verifyStock } from "./firmware.mjs";

const get = (id) => document.getElementById(id);
const picker = get("firmware");
const pick = get("pick");
const dropzone = get("dropzone");
const version = get("version");
const build = get("build");
const download = get("download");
const patchCount = get("patch-count");

let input = null;
let checking = false;
let fileAttempt = 0;
let downloadUrl = null;
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
    patchCount.textContent = `${count.toLocaleString()} firmware ${count === 1 ? "repack" : "repacks"} completed`;
    patchCount.hidden = false;
  } catch {
    // The counter is independent of the firmware download.
  }
}

function resetDownload() {
  if (downloadUrl) URL.revokeObjectURL(downloadUrl);
  downloadUrl = null;
  download.removeAttribute("href");
  download.hidden = true;
  build.hidden = false;
}

function renderControls() {
  const invalid = !validVersion(version.value);
  get("input-summary").textContent = input ? `Verified v${stock.stockVersion}` : checking ? "Verifying…" : "Awaiting file";
  version.setAttribute("aria-invalid", String(invalid));
  build.disabled = !input || invalid;
  if (!downloadUrl) {
    if (invalid) status("Enter a version like 1.15.", "error");
    else if (!input) status("Choose an original firmware file.");
    else status("Ready to repack stock firmware.");
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
version.addEventListener("input", () => {
  resetDownload();
  renderControls();
});

build.addEventListener("click", () => {
  const label = version.value;
  if (!input || !validVersion(label)) return;

  const output = repackStock(input, label);
  downloadUrl = URL.createObjectURL(new Blob([output], { type: "application/octet-stream" }));
  download.href = downloadUrl;
  build.hidden = true;
  download.hidden = false;
  status(`Firmware v${label} repacked and verified.`, "success");
  download.focus();
  void updatePatchCount("POST");
});

renderControls();
void updatePatchCount("GET");
