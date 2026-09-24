const assert = require('assert');
const http = require('http');
const { createApp, OrderSchema, totalQty, signToken } = require('../src/server');
const jwt = require('jsonwebtoken');
const _ = require('lodash');
const minimist = require('minimist');

function request(server, method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request(
      { port: server.address().port, method, path, headers: { 'content-type': 'application/json' } },
      (res) => {
        let buf = '';
        res.on('data', (c) => (buf += c));
        res.on('end', () => resolve({ status: res.statusCode, body: JSON.parse(buf) }));
      }
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

(async () => {
  const order = { orderId: 'o-1', items: [{ sku: 'A', qty: 2 }, { sku: 'B', qty: 3 }] };
  assert.strictEqual(OrderSchema.safeParse(order).success, true);
  assert.strictEqual(OrderSchema.safeParse({ orderId: '', items: [] }).success, false);
  assert.strictEqual(totalQty(order), 5);

  const token = signToken({ sub: 'u1' }, 'secret');
  assert.strictEqual(jwt.verify(token, 'secret', { algorithms: ['HS256'] }).sub, 'u1');

  assert.deepStrictEqual(_.pick({ a: 1, b: 2 }, ['a']), { a: 1 });
  assert.strictEqual(minimist(['--port', '8080']).port, 8080);

  const server = createApp().listen(0);
  try {
    const h = await request(server, 'GET', '/health');
    assert.strictEqual(h.status, 200);
    const ok = await request(server, 'POST', '/orders', order);
    assert.strictEqual(ok.status, 200);
    assert.strictEqual(ok.body.totalQty, 5);
    const bad = await request(server, 'POST', '/orders', { orderId: 'x', items: [] });
    assert.strictEqual(bad.status, 400);
  } finally {
    server.close();
  }
  console.log('smoke tests passed');
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
