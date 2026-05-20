#!/usr/bin/env node
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const ROOT = __dirname;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm':  'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.xml':  'application/xml; charset=utf-8',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg':  'image/svg+xml',
  '.ico':  'image/x-icon',
  '.woff':  'font/woff',
  '.woff2': 'font/woff2',
  '.txt':  'text/plain; charset=utf-8',
  '.map':  'application/json; charset=utf-8',
};

function safeJoin(root, urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0]);
  const normalized = path.posix.normalize(decoded).replace(/^\/+/, '');
  const full = path.join(root, normalized);
  if (!full.startsWith(root)) return null;
  return full;
}

function send(res, status, body, headers = {}) {
  res.writeHead(status, {
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    ...headers,
  });
  res.end(body);
}

function handler(req, res) {
  let urlPath = req.url === '/' ? '/taskpane.html' : req.url;
  const filePath = safeJoin(ROOT, urlPath);
  if (!filePath) return send(res, 400, 'Bad Request');

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      console.log(`[404] ${req.method} ${req.url}`);
      return send(res, 404, 'Not Found', { 'Content-Type': 'text/plain' });
    }
    const ext = path.extname(filePath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    console.log(`[200] ${req.method} ${req.url}`);
    res.writeHead(200, {
      'Content-Type': type,
      'Content-Length': stats.size,
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
    });
    const stream = fs.createReadStream(filePath);
    stream.on('error', () => res.destroy());
    stream.pipe(res);
  });
}

const KEY = path.join(ROOT, 'key.pem');
const CERT = path.join(ROOT, 'cert.pem');

if (!fs.existsSync(KEY) || !fs.existsSync(CERT)) {
  console.error('\nMissing SSL files: key.pem and/or cert.pem');
  console.error('Generate them with:');
  console.error('  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"\n');
  process.exit(1);
}

const options = {
  key:  fs.readFileSync(KEY),
  cert: fs.readFileSync(CERT),
};

https.createServer(options, handler).listen(PORT, () => {
  console.log(`Augustinus Citator dev server running:`);
  console.log(`  https://localhost:${PORT}/taskpane.html`);
  console.log(`  Accept the self-signed certificate in your browser first.`);
});
