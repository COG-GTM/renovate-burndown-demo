const assert = require('assert');
const http = require('http');
const { archiveReceipt, readReceipt, receiptKey, s3Client } = require('../src/receipts');

// Minimal S3 stand-in: stores PUT bodies in memory and serves them back on GET.
function fakeS3() {
  const objects = new Map();
  const server = http.createServer((req, res) => {
    const key = decodeURIComponent(req.url.split('?')[0]).replace(/^\//, '');
    if (req.method === 'PUT') {
      let body = '';
      req.on('data', (c) => (body += c));
      return req.on('end', () => {
        objects.set(key, body);
        res.setHeader('ETag', '"deadbeef"');
        res.end();
      });
    }
    if (req.method === 'GET') {
      const body = objects.get(key);
      if (body === undefined) {
        res.statusCode = 404;
        return res.end('<Error><Code>NoSuchKey</Code></Error>');
      }
      return res.end(body);
    }
    res.statusCode = 405;
    res.end();
  });
  return { server, objects };
}

(async () => {
  const { server, objects } = fakeS3();
  server.listen(0);
  const port = server.address().port;
  process.env.S3_ENDPOINT = `http://127.0.0.1:${port}`;

  const order = { orderId: 'o-1', items: [{ sku: 'A1', qty: 2 }], total: 2400 };
  try {
    const client = s3Client();
    const put = await archiveReceipt(order, client);
    assert.strictEqual(put.key, 'receipts/o-1.json');
    assert.strictEqual(put.etag, '"deadbeef"');
    assert.strictEqual(objects.get(`${require('../src/receipts').BUCKET}/receipts/o-1.json`), JSON.stringify(order));

    const roundTripped = await readReceipt('o-1', client);
    assert.deepStrictEqual(roundTripped, order);

    assert.strictEqual(receiptKey({ orderId: 'x' }), 'receipts/x.json');
  } finally {
    server.close();
  }
  console.log('receipt archive tests passed');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
