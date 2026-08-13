import { createHash } from "node:crypto";
import { readdir, readFile, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const downloads = path.join(root, "public", "downloads");
const output = path.join(root, "content", "download-manifest.json");

const names = (await readdir(downloads)).sort();
const files = [];

for (const name of names) {
  const file = path.join(downloads, name);
  const details = await stat(file);
  if (!details.isFile()) continue;
  const bytes = await readFile(file);
  files.push({
    name,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    size: details.size,
  });
}

await writeFile(output, `${JSON.stringify({ schema: "kairali.portal-downloads/v1", files }, null, 2)}\n`, "utf8");
console.log(`PORTAL DOWNLOAD MANIFEST: ${files.length} files`);
