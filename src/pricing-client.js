const axios = require('axios');

// The pricing service is strict: it validates the exact query encoding it documented
// (filter is a JSON object in a single parameter) and rejects anything else with 400.
async function fetchQuote(baseUrl, { sku, region, tier }) {
  const res = await axios.get(`${baseUrl}/quotes`, {
    params: { sku, filter: { region, tier } },
  });
  return { sku, price: res.data.price, currency: res.data.currency };
}

async function submitOrder(baseUrl, order) {
  const res = await axios.post(`${baseUrl}/orders`, order);
  return res.data;
}

module.exports = { fetchQuote, submitOrder };
