'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');

const {
  buildStockRequestConfig,
  normaliseQuote,
  formatQuoteSummary,
} = require('../index.js');

describe('buildStockRequestConfig', () => {
  it('sets method to GET and url to the quote endpoint', () => {
    const config = buildStockRequestConfig({ symbol: 'AAPL' });
    assert.equal(config.method, 'GET');
    assert.match(config.url, /\/quote$/);
  });

  it('includes only allowed params', () => {
    const config = buildStockRequestConfig({
      symbol: 'TSLA',
      exchange: 'NASDAQ',
      unknown: 'drop-me',
    });
    assert.equal(config.params.symbol, 'TSLA');
    assert.equal(config.params.exchange, 'NASDAQ');
    assert.equal(config.params.unknown, undefined);
  });

  it('deep-merges overrides without mutating defaults', () => {
    const override = { timeout: 9000, headers: { 'X-Custom': 'yes' } };
    const config = buildStockRequestConfig({ symbol: 'GOOG' }, override);
    assert.equal(config.timeout, 9000);
    assert.equal(config.headers['X-Custom'], 'yes');
    // Accept header from defaults must still be present
    assert.equal(config.headers['Accept'], 'application/json');
  });

  it('returns independent configs on successive calls', () => {
    const a = buildStockRequestConfig({ symbol: 'X' });
    const b = buildStockRequestConfig({ symbol: 'Y' });
    a.headers['Mutate'] = 'yes';
    assert.equal(b.headers['Mutate'], undefined);
  });
});

describe('normaliseQuote', () => {
  it('maps upstream fields to canonical keys', () => {
    const raw = { ticker: 'AAPL', last_price: 172.5, currency: 'USD', timestamp: 1700000000 };
    const q = normaliseQuote(raw);
    assert.equal(q.symbol, 'AAPL');
    assert.equal(q.price, 172.5);
    assert.equal(q.currency, 'USD');
    assert.equal(q.ts, 1700000000);
  });

  it('defaults currency to USD when absent', () => {
    const q = normaliseQuote({ ticker: 'BTC', last_price: 60000 });
    assert.equal(q.currency, 'USD');
  });

  it('returns undefined for missing fields without throwing', () => {
    const q = normaliseQuote({});
    assert.equal(q.symbol, undefined);
    assert.equal(q.price, undefined);
  });
});

describe('formatQuoteSummary', () => {
  it('produces the expected summary string', () => {
    const summary = formatQuoteSummary({ symbol: 'AAPL', price: 172.5, currency: 'USD' });
    assert.equal(summary, 'AAPL: USD 172.5');
  });

  it('handles integer prices', () => {
    const summary = formatQuoteSummary({ symbol: 'BTC', price: 60000, currency: 'EUR' });
    assert.equal(summary, 'BTC: EUR 60000');
  });
});
