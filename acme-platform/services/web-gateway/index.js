'use strict';

const _ = require('lodash');
const axios = require('axios');

const UPSTREAM_BASE_URL = 'https://api.stocks.example.com';

const DEFAULT_HEADERS = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
};

/**
 * Build an axios request config for fetching a stock quote.
 * No network call is made here; the caller decides whether to execute it.
 *
 * @param {object} params - Query parameters (e.g. { symbol: 'AAPL' })
 * @param {object} [overrides={}] - Config overrides merged with _.merge
 * @returns {object} Axios request config
 */
function buildStockRequestConfig(params, overrides = {}) {
  const base = {
    method: 'GET',
    url: `${UPSTREAM_BASE_URL}/quote`,
    headers: _.cloneDeep(DEFAULT_HEADERS),
    params: _.pick(params, ['symbol', 'exchange', 'interval']),
    timeout: 5000,
  };
  return _.merge({}, base, overrides);
}

/**
 * Extract the quote fields we care about from an upstream API response body.
 * Uses _.get so missing fields return undefined cleanly.
 *
 * @param {object} responseData - Raw response body from the upstream API
 * @returns {object} Normalised quote object
 */
function normaliseQuote(responseData) {
  return {
    symbol:   _.get(responseData, 'ticker'),
    price:    _.get(responseData, 'last_price'),
    currency: _.get(responseData, 'currency', 'USD'),
    ts:       _.get(responseData, 'timestamp'),
  };
}

/**
 * Apply a simple template to produce a human-readable summary string.
 *
 * @param {object} quote - Normalised quote (symbol, price, currency)
 * @returns {string}
 */
function formatQuoteSummary(quote) {
  const tpl = _.template('<%= symbol %>: <%= currency %> <%= price %>');
  return tpl(quote);
}

module.exports = { buildStockRequestConfig, normaliseQuote, formatQuoteSummary };
