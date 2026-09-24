const AWS = require('aws-sdk');

const BUCKET = process.env.RECEIPTS_BUCKET || 'order-receipts';

function s3Client() {
  return new AWS.S3({
    endpoint: process.env.S3_ENDPOINT || 'https://s3.eu-west-1.amazonaws.com',
    region: process.env.AWS_REGION || 'eu-west-1',
    s3ForcePathStyle: true,
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'test',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'test',
  });
}

function receiptKey(order) {
  return `receipts/${order.orderId}.json`;
}

async function archiveReceipt(order, client = s3Client()) {
  const res = await client
    .putObject({
      Bucket: BUCKET,
      Key: receiptKey(order),
      Body: JSON.stringify(order),
      ContentType: 'application/json',
    })
    .promise();
  return { key: receiptKey(order), etag: res.ETag };
}

async function readReceipt(orderId, client = s3Client()) {
  const res = await client.getObject({ Bucket: BUCKET, Key: `receipts/${orderId}.json` }).promise();
  return JSON.parse(res.Body.toString('utf8'));
}

module.exports = { archiveReceipt, readReceipt, receiptKey, s3Client, BUCKET };
