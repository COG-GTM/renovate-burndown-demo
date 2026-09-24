const assert = require('assert');
const http = require('http');
const { fetchQuote, submitOrder } = require('../src/pricing-client');

// Stand-in for the pricing service. It enforces the published contract:
//   GET /quotes?sku=<sku>&filter=<url-encoded JSON object>
//   POST /orders with Content-Type: application/json;charset=utf-8
// Anything else is a 400, exactly as the real service does.
function pricingService() {
  return http.createServer((req, res) => {
    const [path, query = ''] = req.url.split('?');
    const params = new URLSearchParams(query);

    if (path === '/quotes') {
      const filter = params.get('filter');
      let parsed = null;
      try {
        parsed = filter === null ? null : JSON.parse(filter);
      } catch (err) {
        parsed = null;
      }
      if (parsed === null || typeof parsed !== 'object') {
        res.statusCode = 400;
        res.setHeader('content-type', 'application/json');
        return res.end(JSON.stringify({ error: 'filter must be a JSON object', received: query }));
      }
      res.setHeader('content-type', 'application/json');
      return res.end(JSON.stringify({ price: 1200, currency: parsed.region === 'eu' ? 'EUR' : 'USD' }));
    }

    if (path === '/orders') {
      if (req.headers['content-type'] !== 'application/json;charset=utf-8') {
        res.statusCode = 400;
        res.setHeader('content-type', 'application/json');
        return res.end(JSON.stringify({ error: 'unsupported content type', received: req.headers['content-type'] }));
      }
      let body = '';
      req.on('data', (c) => (body += c));
      return req.on('end', () => {
        res.setHeader('content-type', 'application/json');
        res.end(JSON.stringify({ accepted: true, orderId: JSON.parse(body).orderId }));
      });
    }

    res.statusCode = 404;
    res.end('{}');
  });
}

(async () => {
  const server = pricingService().listen(0);
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const quote = await fetchQuote(base, { sku: 'A1', region: 'eu', tier: 'gold' });
    assert.deepStrictEqual(quote, { sku: 'A1', price: 1200, currency: 'EUR' });

    const ack = await submitOrder(base, { orderId: 'o-1', items: [{ sku: 'A1', qty: 1 }] });
    assert.deepStrictEqual(ack, { accepted: true, orderId: 'o-1' });
  } finally {
    server.close();
  }
  console.log('pricing client tests passed');
})().catch((err) => {
  console.error(err.response ? `${err.message} -> ${JSON.stringify(err.response.data)}` : err);
  process.exit(1);
});
