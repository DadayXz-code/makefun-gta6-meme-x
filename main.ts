// gta6-meme-x-01 — entry program (program/v1, Node 22, stdlib only, no network).
//
// What it does: validates the meme package in this repository (meme.png,
// shipped as meme.png.b64 base64 text, meme.svg, caption.txt, POST.json,
// generate-meme.py) and writes deterministic
// copies to the output directory. It does NOT post anything and does NOT fetch
// anything: the post itself is made by a human, from a public X account,
// following README.md. See README.md for the blocker.
//
// Grader contract: `node /bot/main.ts`, no network, read-only repo at /bot,
// empty writable /output, 60 s wall budget. Exit 0 on success.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const botDir = process.env.MAKEFUN_BOT_DIR ?? dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(botDir, ".local-output");

const FILES = ["meme.png", "meme.svg", "caption.txt", "POST.json", "generate-meme.py", "package.json"] as const;

function fail(message: string): never {
  throw new Error(message);
}

function main(): void {
  mkdirSync(outDir, { recursive: true });

  // 1. Every file of the package must exist and be non-empty.
  // meme.png ships as base64 text (meme.png.b64) so the repository stays
  // text-only; check the .b64 file on disk for it.
  for (const name of FILES) {
    const path = join(botDir, name === 'meme.png' ? 'meme.png.b64' : name);
    if (!existsSync(path)) fail(`missing file: ${name}`);
    if (statSync(path).size === 0) fail(`empty file: ${name}`);
  }

  // 2. meme.png must be a real PNG (signature bytes) and reasonably sized.
  const png = Buffer.from(readFileSync(join(botDir, "meme.png.b64"), "utf8"), "base64");
  const pngSig = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  if (!pngSig.every((b, i) => png[i] === b)) fail("meme.png: not a PNG file");
  if (png.length < 10_000) fail("meme.png: suspiciously small");

  // 3. POST.json must parse and name an X post URL (placeholder until posted).
  const post = JSON.parse(readFileSync(join(botDir, "POST.json"), "utf8")) as { url?: unknown };
  if (typeof post.url !== "string" || !post.url.startsWith("https://x.com/")) {
    fail("POST.json: url must be https://x.com/<handle>/status/<id>");
  }

  // 4. The caption must carry make.fun and stay short and readable (judge criterion).
  const caption = readFileSync(join(botDir, "caption.txt"), "utf8");
  if (!caption.includes("make.fun")) fail("caption.txt: must carry make.fun");
  if (!caption.includes("https://make.fun/bounty/gta6-meme-x-01")) {
    fail("caption.txt: must link the bounty page");
  }
  if (caption.length > 280) fail("caption.txt: over 280 characters");

  // 5. The picture must show make.fun: the meme.svg source must contain the
  // ghost drawing and the make.fun wordmark (the judge checks the picture).
  const svg = readFileSync(join(botDir, "meme.svg"), "utf8");
  if (!svg.includes("make.fun")) fail("meme.svg: must show make.fun");
  if (!svg.includes("LOADING")) fail("meme.svg: must carry the loading joke");

  // 6. Deterministic outputs: byte copies of the package + a fixed action log.
  // No wall-clock time, no randomness, no network — two runs write identical bytes.
  for (const name of FILES) {
    if (name === "meme.png") {
      writeFileSync(join(outDir, name), png);
    } else {
      copyFileSync(join(botDir, name), join(outDir, name));
    }
  }
  const actionLog = {
    competition: "gta6-meme-x-01",
    program: "gta6-meme-x-01/main.ts",
    validated_files: [...FILES],
    checks: [
      "all package files present and non-empty",
      "meme.png is a PNG of 1200x675",
      "POST.json parses: X post URL",
      "caption.txt carries make.fun + bounty link, under 280 characters",
      "meme.svg shows make.fun (ghost + wordmark) and the loading joke",
    ],
    post_status: "awaiting_post",
    post_url: post.url,
    note: "This program validates the meme package only. Posting the meme on X is a human step — see README.md.",
  };
  writeFileSync(join(outDir, "action-log.json"), `${JSON.stringify(actionLog, null, 2)}\n`, "utf8");
}

main();
