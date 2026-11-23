// SPDX-License-Identifier: GPL-2.0-or-later
import stock from "./stock.mjs";

export const validVersion = (version) => /^[0-9]\.[0-9]{2}$/.test(version);

export async function verifyStock(bytes) {
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  const fingerprint = Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, "0")).join("");
  if (fingerprint !== stock.stockHash) {
    throw new Error(`Choose the original ${stock.model} v${stock.stockVersion} ${stock.filename}.`);
  }
}

export function repackStock(bytes, version) {
  if (!validVersion(version)) throw new Error("Enter a version in the form D.DD.");
  // The original update has already been verified. Keep the boot records,
  // compressed MAIN, checksums and all other label bytes intact.
  const output = new Uint8Array(bytes.slice(0));
  output.set(new TextEncoder().encode(version), stock.versionOffset);
  return output;
}
