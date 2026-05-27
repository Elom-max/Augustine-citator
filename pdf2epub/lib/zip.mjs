// Minimal ZIP writer (STORED / no compression). Pure JS, runs in Node and the
// browser. Sufficient for EPUB: the spec only requires that the first entry be
// the uncompressed `mimetype` file; other entries may also be stored.

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(bytes) {
  let c = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

const enc = new TextEncoder();
function toBytes(data) {
  return typeof data === 'string' ? enc.encode(data) : data;
}

/**
 * @param {{name:string,data:string|Uint8Array}[]} entries  ordered; first = mimetype
 * @returns {Uint8Array} the .epub/.zip bytes
 */
export function zipStore(entries) {
  const files = entries.map((e) => {
    const nameBytes = enc.encode(e.name);
    const data = toBytes(e.data);
    return { nameBytes, data, crc: crc32(data), offset: 0 };
  });

  const chunks = [];
  let offset = 0;
  const push = (buf) => {
    chunks.push(buf);
    offset += buf.length;
  };

  // Local file headers + data
  for (const f of files) {
    f.offset = offset;
    const h = new DataView(new ArrayBuffer(30));
    h.setUint32(0, 0x04034b50, true);
    h.setUint16(4, 20, true); // version needed
    h.setUint16(6, 0, true); // flags
    h.setUint16(8, 0, true); // method: stored
    h.setUint16(10, 0, true); // mod time
    h.setUint16(12, 0, true); // mod date
    h.setUint32(14, f.crc, true);
    h.setUint32(18, f.data.length, true); // compressed size
    h.setUint32(22, f.data.length, true); // uncompressed size
    h.setUint16(26, f.nameBytes.length, true);
    h.setUint16(28, 0, true); // extra len
    push(new Uint8Array(h.buffer));
    push(f.nameBytes);
    push(f.data);
  }

  // Central directory
  const cdStart = offset;
  for (const f of files) {
    const h = new DataView(new ArrayBuffer(46));
    h.setUint32(0, 0x02014b50, true);
    h.setUint16(4, 20, true); // version made by
    h.setUint16(6, 20, true); // version needed
    h.setUint16(8, 0, true); // flags
    h.setUint16(10, 0, true); // method
    h.setUint16(12, 0, true); // mod time
    h.setUint16(14, 0, true); // mod date
    h.setUint32(16, f.crc, true);
    h.setUint32(20, f.data.length, true);
    h.setUint32(24, f.data.length, true);
    h.setUint16(28, f.nameBytes.length, true);
    h.setUint16(30, 0, true); // extra
    h.setUint16(32, 0, true); // comment
    h.setUint16(34, 0, true); // disk
    h.setUint16(36, 0, true); // internal attrs
    h.setUint32(38, 0, true); // external attrs
    h.setUint32(42, f.offset, true);
    push(new Uint8Array(h.buffer));
    push(f.nameBytes);
  }
  const cdSize = offset - cdStart;

  // End of central directory
  const eocd = new DataView(new ArrayBuffer(22));
  eocd.setUint32(0, 0x06054b50, true);
  eocd.setUint16(4, 0, true);
  eocd.setUint16(6, 0, true);
  eocd.setUint16(8, files.length, true);
  eocd.setUint16(10, files.length, true);
  eocd.setUint32(12, cdSize, true);
  eocd.setUint32(16, cdStart, true);
  eocd.setUint16(20, 0, true);
  push(new Uint8Array(eocd.buffer));

  // Concatenate
  const total = chunks.reduce((n, c) => n + c.length, 0);
  const out = new Uint8Array(total);
  let p = 0;
  for (const c of chunks) {
    out.set(c, p);
    p += c.length;
  }
  return out;
}
