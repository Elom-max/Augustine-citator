#!/usr/bin/env node
// PDF / texte -> reflowable EPUB, command line.
//   node pdf2epub/cli.mjs livre.pdf [sortie.epub] [--title "..."] [--author "..."] [--lang fr]
//   node pdf2epub/cli.mjs notes.txt        (texte brut ou Markdown -> EPUB)
//   node pdf2epub/cli.mjs *.pdf            (conversion en lot, un .epub par fichier)

import { readFile, writeFile } from 'node:fs/promises';
import { basename, extname, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildBook, buildBookFromText, buildEpub, mapTextContent } from './lib/core.mjs';

const PDFJS = 'pdfjs-dist/legacy/build/pdf.mjs';
const TEXT_EXT = new Set(['.txt', '.md', '.markdown', '.text']);

let _pdfjs = null;
const getPdfjs = async () => (_pdfjs ||= await import(PDFJS));

function parseArgs(argv) {
  const opts = { lang: 'fr' };
  const inputs = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--title') opts.title = argv[++i];
    else if (a === '--author') opts.author = argv[++i];
    else if (a === '--lang') opts.lang = argv[++i];
    else if (a === '-o' || a === '--out') opts.out = argv[++i];
    else if (a.startsWith('--')) {} // ignore unknown flags
    else inputs.push(a);
  }
  return { opts, inputs };
}

async function extractPages(pdfjs, data) {
  const doc = await pdfjs.getDocument({
    data,
    useSystemFonts: true,
    isEvalSupported: false,
  }).promise;
  const pages = [];
  let info = {};
  try {
    info = (await doc.getMetadata())?.info || {};
  } catch {}
  for (let n = 1; n <= doc.numPages; n++) {
    const page = await doc.getPage(n);
    const viewport = page.getViewport({ scale: 1 });
    const tc = await page.getTextContent();
    pages.push(mapTextContent(tc, viewport.width, viewport.height));
    page.cleanup();
  }
  await doc.destroy();
  return { pages, info };
}

async function convertOne(inputPath, opts) {
  const ext = extname(inputPath).toLowerCase();
  let book;
  if (TEXT_EXT.has(ext)) {
    const text = await readFile(inputPath, 'utf8');
    book = buildBookFromText(text, {
      title: opts.title || basename(inputPath, ext),
      author: opts.author,
      language: opts.lang,
    });
  } else {
    const pdfjs = await getPdfjs();
    const data = new Uint8Array(await readFile(inputPath));
    const { pages, info } = await extractPages(pdfjs, data);
    book = buildBook(pages, {
      title: opts.title || info.Title || basename(inputPath, ext),
      author: opts.author || info.Author,
      language: opts.lang,
    });
  }

  for (const w of book.warnings) console.warn(`  ⚠️  ${w}`);

  const epub = buildEpub(book);
  const outPath =
    opts.out || join(dirname(inputPath), basename(inputPath, ext) + '.epub');
  await writeFile(outPath, epub);
  const kb = (epub.length / 1024).toFixed(0);
  const size = book.stats.pages ? `${book.stats.pages} pages, ` : '';
  console.log(
    `  ✓ ${outPath}  (${size}${book.stats.chapters} chapitres, ${book.stats.chars} caractères, ${kb} Ko)`
  );
  return book;
}

async function main() {
  const { opts, inputs } = parseArgs(process.argv.slice(2));
  if (!inputs.length) {
    console.error(
      'Usage : node pdf2epub/cli.mjs <fichier.pdf|.txt|.md> [sortie.epub] [--title "..."] [--author "..."] [--lang fr]'
    );
    process.exit(1);
  }

  // A 2nd positional argument is the output path (single-file mode only).
  let outFromPositional = null;
  if (inputs.length === 2 && inputs[1].toLowerCase().endsWith('.epub')) {
    outFromPositional = inputs.pop();
  }

  let failures = 0;
  for (const input of inputs) {
    console.log(`→ ${input}`);
    try {
      await convertOne(input, {
        ...opts,
        out: outFromPositional || opts.out,
      });
    } catch (e) {
      failures++;
      console.error(`  ✗ Échec : ${e.message}`);
    }
  }
  process.exit(failures ? 1 : 0);
}

// Run only when invoked directly.
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  main();
}
