const express = require('express');
const _ = require('lodash');
const { z } = require('zod');
const jwt = require('jsonwebtoken');

const OrderSchema = z.object({
  orderId: z.string().min(1),
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().positive() })).min(1),
});

function totalQty(order) {
  return _.sumBy(order.items, 'qty');
}

function signToken(payload, secret) {
  return jwt.sign(payload, secret, { algorithm: 'HS256', expiresIn: '1h' });
}

function createApp() {
  const app = express();
  app.use(express.json());
  app.get('/health', (req, res) => res.json({ status: 'ok' }));
  app.post('/orders', (req, res) => {
    const parsed = OrderSchema.safeParse(req.body);
    if (!parsed.success) return res.status(400).json({ error: parsed.error.issues });
    res.json({ orderId: parsed.data.orderId, totalQty: totalQty(parsed.data) });
  });
  return app;
}

module.exports = { createApp, OrderSchema, totalQty, signToken };

if (require.main === module) {
  createApp().listen(process.env.PORT || 3000);
}
