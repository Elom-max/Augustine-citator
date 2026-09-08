// PDF -> reflowable EPUB core engine. Pure JS, no I/O, no pdfjs import: callers
// feed it text already extracted from pdfjs (via `mapTextContent`) so the same
// code runs in Node (cli.mjs) and in the browser (converter.html).

import { zipStore } from './zip.mjs';

// ---------------------------------------------------------------------------
// 1. pdfjs adapter
// ---------------------------------------------------------------------------

/**
 * Convert one pdfjs TextContent into normalised, top-left-origin items.
 * @param {{items:any[]}} textContent  result of page.getTextContent()
 * @param {number} pageWidth
 * @param {number} pageHeight
 */
export function mapTextContent(textContent, pageWidth, pageHeight) {
  const items = [];
  for (const it of textContent.items) {
    if (it.str === undefined) continue; // marked-content markers
    const tr = it.transform; // [a, b, c, d, e, f]
    const size = Math.hypot(tr[1], tr[3]) || it.height || 12;
    items.push({
      str: it.str,
      x: tr[4],
      y: pageHeight - tr[5], // top-based baseline
      w: it.width || 0,
      size,
      bold: /bold|black|semibold/i.test(it.fontName || ''),
      italic: /italic|oblique/i.test(it.fontName || ''),
      eol: !!it.hasEOL,
    });
  }
  return { width: pageWidth, height: pageHeight, items };
}

// ---------------------------------------------------------------------------
// 2. Structure reconstruction
// ---------------------------------------------------------------------------

function median(nums) {
  if (!nums.length) return 0;
  const s = [...nums].sort((a, b) => a - b);
  return s[Math.floor(s.length / 2)];
}

// Cluster a page's items into visual lines (sorted top->bottom, left->right).
function pageToLines(page) {
  const items = page.items.filter((i) => i.str.trim() !== '' || i.str === ' ');
  if (!items.length) return [];
  items.sort((a, b) => a.y - b.y || a.x - b.x);

  const lines = [];
  let cur = null;
  for (const it of items) {
    const tol = Math.max(it.size, 6) * 0.5;
    if (cur && Math.abs(it.y - cur.y) <= tol) {
      cur.items.push(it);
      cur.y = (cur.y * (cur.items.length - 1) + it.y) / cur.items.length;
    } else {
      cur = { y: it.y, items: [it] };
      lines.push(cur);
    }
  }

  for (const ln of lines) {
    ln.items.sort((a, b) => a.x - b.x);
    let text = '';
    let prev = null;
    for (const it of ln.items) {
      if (prev) {
        const gap = it.x - (prev.x + prev.w);
        if (gap > prev.size * 0.25 && !/\s$/.test(text) && !/^\s/.test(it.str)) {
          text += ' ';
        }
      }
      text += it.str;
      prev = it;
    }
    ln.text = text.replace(/\s+/g, ' ').trim();
    ln.x0 = ln.items[0].x;
    ln.x1 = ln.items[ln.items.length - 1].x + ln.items[ln.items.length - 1].w;
    ln.size = median(ln.items.map((i) => i.size));
    ln.bold = ln.items.every((i) => i.bold);
  }
  return lines.filter((l) => l.text !== '');
}

// Drop running headers / footers / page numbers living in the top & bottom margins.
function stripMargins(pageLines, pageHeight) {
  const topLimit = pageHeight * 0.07;
  const botLimit = pageHeight * 0.93;
  const freq = new Map();
  for (const lines of pageLines) {
    for (const ln of lines) {
      if (ln.y <= topLimit || ln.y >= botLimit) {
        const key = ln.text.replace(/\d+/g, '#');
        freq.set(key, (freq.get(key) || 0) + 1);
      }
    }
  }
  const repeatThreshold = Math.max(3, pageLines.length * 0.25);
  return pageLines.map((lines) =>
    lines.filter((ln) => {
      const inMargin = ln.y <= topLimit || ln.y >= botLimit;
      if (!inMargin) return true;
      if (/^[\divxlcdm.\s–—-]+$/i.test(ln.text) && ln.text.length <= 12) return false; // page number / roman
      const key = ln.text.replace(/\d+/g, '#');
      if ((freq.get(key) || 0) >= repeatThreshold) return false; // repeated running head
      return true;
    })
  );
}

const ENDS_SENTENCE = /[.!?»”"')\]]\s*$/;

// Split a flat block list into chapters, starting a new one at each top-level heading.
function blocksToChapters(blocks, meta) {
  const headingLevels = blocks.filter((b) => b.type === 'h').map((b) => b.level);
  const splitLevel = headingLevels.length ? Math.min(...headingLevels) : null;
  const chapters = [];
  let cur = null;
  const newChapter = (title) => {
    cur = { title: title || `Section ${chapters.length + 1}`, blocks: [] };
    chapters.push(cur);
  };
  for (const b of blocks) {
    if (b.type === 'h' && b.level === splitLevel) {
      newChapter(b.text);
      cur.blocks.push(b);
    } else {
      if (!cur) newChapter(meta.title || 'Texte');
      cur.blocks.push(b);
    }
  }
  if (!chapters.length) newChapter(meta.title || 'Texte');
  return chapters;
}

/**
 * Turn raw pages into a structured book.
 * @param {{width:number,height:number,items:any[]}[]} pages
 * @param {{title?:string,author?:string,language?:string}} meta
 */
export function buildBook(pages, meta = {}) {
  const pageHeight = median(pages.map((p) => p.height)) || 800;
  let pageLines = pages.map(pageToLines);
  pageLines = stripMargins(pageLines, pageHeight);

  // Body font size = size carrying the most characters.
  const sizeWeight = new Map();
  for (const lines of pageLines) {
    for (const ln of lines) {
      const k = Math.round(ln.size);
      sizeWeight.set(k, (sizeWeight.get(k) || 0) + ln.text.length);
    }
  }
  let bodySize = 12;
  let best = -1;
  for (const [k, w] of sizeWeight) if (w > best) ((best = w), (bodySize = k));

  const lineHeight = bodySize * 1.3;

  // Flatten lines, remembering page boundaries.
  const flat = [];
  pageLines.forEach((lines, pageIdx) => {
    lines.forEach((ln) => flat.push({ ...ln, page: pageIdx }));
  });

  const blocks = [];
  let para = null;
  const flushPara = () => {
    if (para && para.text.trim()) blocks.push({ type: 'p', text: para.text.trim() });
    para = null;
  };

  const bodyLeft = median(flat.filter((l) => l.size <= bodySize * 1.15).map((l) => l.x0));

  for (let i = 0; i < flat.length; i++) {
    const ln = flat[i];
    const prev = flat[i - 1];

    // Heading: noticeably larger than body text, and reasonably short.
    const ratio = ln.size / bodySize;
    const isHeading = ratio >= 1.2 && ln.text.length <= 120 && /[a-zÀ-ſ]/i.test(ln.text);
    if (isHeading) {
      flushPara();
      const level = ratio >= 1.7 ? 1 : ratio >= 1.35 ? 2 : 3;
      blocks.push({ type: 'h', level, text: ln.text });
      continue;
    }

    // Decide whether this line starts a new paragraph.
    let newPara = false;
    if (!para) {
      newPara = true;
    } else if (prev && ln.page !== prev.page) {
      // page break: continue only if previous line looked unfinished
      newPara = ENDS_SENTENCE.test(prev.text) || ln.x0 > bodyLeft + bodySize * 0.8;
    } else if (prev) {
      const gap = ln.y - prev.y;
      const indented = ln.x0 > bodyLeft + bodySize * 0.8;
      if (gap > lineHeight * 1.6 || indented) newPara = true;
    }

    if (newPara) {
      flushPara();
      para = { text: '' };
    }

    // Join with previous line, honouring hyphenation.
    if (para.text === '') {
      para.text = ln.text;
    } else if (/[‐-]$/.test(para.text) && /^[a-zà-ſ]/.test(ln.text)) {
      para.text = para.text.replace(/[‐-]$/, '') + ln.text;
    } else {
      para.text += ' ' + ln.text;
    }
  }
  flushPara();

  const chapters = blocksToChapters(blocks, meta);

  const charCount = blocks.reduce((n, b) => n + b.text.length, 0);
  const warnings = [];
  const perPage = charCount / Math.max(1, pages.length);
  if (perPage < 40) {
    warnings.push(
      'Très peu de texte sélectionnable détecté : ce PDF est probablement scanné (images). ' +
        "L'EPUB produit sera quasi vide. Un OCR serait nécessaire pour le convertir."
    );
  }

  return {
    meta: {
      title: meta.title || 'Document',
      author: meta.author || 'Inconnu',
      language: meta.language || 'fr',
    },
    chapters,
    warnings,
    stats: { pages: pages.length, chars: charCount, chapters: chapters.length },
  };
}

/**
 * Build a book from plain text (or lightly marked-up text). Paragraphs are
 * separated by blank lines; soft-wrapped lines inside a paragraph are joined
 * (honouring hyphenation). Headings are recognised from Markdown-style
 * `#`/`##`/`###` prefixes or from "Chapitre/Chapter/Partie/Livre…" lines.
 * @param {string} text
 * @param {{title?:string,author?:string,language?:string}} meta
 */
export function buildBookFromText(text, meta = {}) {
  const lines = String(text)
    .replace(/\r\n?/g, '\n')
    .replace(/\u00a0/g, ' ')
    .split('\n');

  const blocks = [];
  let para = '';
  const flushPara = () => {
    const t = para.replace(/\s+/g, ' ').trim();
    if (t) blocks.push({ type: 'p', text: t });
    para = '';
  };
  const appendLine = (s) => {
    if (para === '') para = s;
    else if (/[‐-]$/.test(para) && /^[a-zà-ſ]/.test(s)) para = para.replace(/[‐-]$/, '') + s;
    else para += ' ' + s;
  };

  const headingOf = (line) => {
    const md = /^(#{1,3})\s+(.+?)\s*#*$/.exec(line);
    if (md) return { level: md[1].length, text: md[2].trim() };
    if (line.length <= 80 && /^(chapitre|chapter|chap\.|partie|livre|section)\b/i.test(line))
      return { level: 1, text: line };
    return null;
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (line === '') {
      flushPara();
      continue;
    }
    const h = headingOf(line);
    if (h) {
      flushPara();
      blocks.push({ type: 'h', level: h.level, text: h.text });
    } else {
      appendLine(line);
    }
  }
  flushPara();

  const chapters = blocksToChapters(blocks, meta);
  const charCount = blocks.reduce((n, b) => n + b.text.length, 0);
  const warnings = [];
  if (!charCount) warnings.push('Aucun texte exploitable n’a été trouvé dans la source fournie.');

  return {
    meta: {
      title: meta.title || 'Document',
      author: meta.author || 'Inconnu',
      language: meta.language || 'fr',
    },
    chapters,
    warnings,
    stats: { pages: 0, chars: charCount, chapters: chapters.length },
  };
}

// ---------------------------------------------------------------------------
// 3. EPUB assembly
// ---------------------------------------------------------------------------

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

const CSS = `body{margin:0 5%;line-height:1.5;font-family:Georgia,'Times New Roman',serif;
text-align:justify;hyphens:auto;-webkit-hyphens:auto;}
h1,h2,h3{font-family:Helvetica,Arial,sans-serif;line-height:1.25;text-align:left;
page-break-after:avoid;}
h1{font-size:1.6em;margin:1.2em 0 .6em;}
h2{font-size:1.3em;margin:1em 0 .5em;}
h3{font-size:1.1em;margin:.8em 0 .4em;}
p{margin:0;text-indent:1.4em;}
p.first,h1+p,h2+p,h3+p{text-indent:0;}
p+p{margin-top:0;}`;

function chapterXhtml(chapter, lang) {
  let body = '';
  let prevHeading = false;
  for (const b of chapter.blocks) {
    if (b.type === 'h') {
      body += `<h${b.level}>${esc(b.text)}</h${b.level}>\n`;
      prevHeading = true;
    } else {
      body += `<p${prevHeading ? ' class="first"' : ''}>${esc(b.text)}</p>\n`;
      prevHeading = false;
    }
  }
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="${esc(lang)}" lang="${esc(lang)}">
<head><meta charset="utf-8"/><title>${esc(chapter.title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
${body}</body>
</html>`;
}

function navXhtml(chapters, lang, title) {
  const items = chapters
    .map((c, i) => `<li><a href="chap${i + 1}.xhtml">${esc(c.title)}</a></li>`)
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="${esc(lang)}">
<head><meta charset="utf-8"/><title>${esc(title)}</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>Sommaire</h1><ol>
${items}
</ol></nav>
</body>
</html>`;
}

function ncxXml(chapters, uid, title) {
  const points = chapters
    .map(
      (c, i) => `<navPoint id="n${i + 1}" playOrder="${i + 1}">
<navLabel><text>${esc(c.title)}</text></navLabel>
<content src="chap${i + 1}.xhtml"/></navPoint>`
    )
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="${esc(uid)}"/></head>
<docTitle><text>${esc(title)}</text></docTitle>
<navMap>
${points}
</navMap>
</ncx>`;
}

function contentOpf(book, uid, date) {
  const { chapters, meta } = book;
  const manifestChaps = chapters
    .map((_, i) => `<item id="chap${i + 1}" href="chap${i + 1}.xhtml" media-type="application/xhtml+xml"/>`)
    .join('\n');
  const spine = chapters.map((_, i) => `<itemref idref="chap${i + 1}"/>`).join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">${esc(uid)}</dc:identifier>
<dc:title>${esc(meta.title)}</dc:title>
<dc:creator>${esc(meta.author)}</dc:creator>
<dc:language>${esc(meta.language)}</dc:language>
<meta property="dcterms:modified">${date}</meta>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
<item id="css" href="style.css" media-type="text/css"/>
${manifestChaps}
</manifest>
<spine toc="ncx">
${spine}
</spine>
</package>`;
}

/** @param {ReturnType<typeof buildBook>} book @returns {Uint8Array} */
export function buildEpub(book) {
  const { chapters, meta } = book;
  const uid = 'urn:uuid:' + simpleUuid(meta.title + '|' + meta.author + '|' + chapters.length);
  const date = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

  const entries = [
    { name: 'mimetype', data: 'application/epub+zip' }, // MUST be first
    {
      name: 'META-INF/container.xml',
      data: `<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>`,
    },
    { name: 'OEBPS/style.css', data: CSS },
    { name: 'OEBPS/nav.xhtml', data: navXhtml(chapters, meta.language, meta.title) },
    { name: 'OEBPS/toc.ncx', data: ncxXml(chapters, uid, meta.title) },
    { name: 'OEBPS/content.opf', data: contentOpf(book, uid, date) },
  ];
  chapters.forEach((c, i) => {
    entries.push({ name: `OEBPS/chap${i + 1}.xhtml`, data: chapterXhtml(c, meta.language) });
  });

  return zipStore(entries);
}

function simpleUuid(seed) {
  let h = 0x811c9dc5;
  for (let i = 0; i < seed.length; i++) {
    h ^= seed.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
  }
  const r = h.toString(16).padStart(8, '0');
  return `${r}-0000-4000-8000-${r}0000`;
}
