import test from 'node:test';
import assert from 'node:assert/strict';
import { destination } from '../extensions/ordnung-start/destination.mjs';

test('searches preserve accents and cannot inject query parameters', () => {
  assert.equal(destination(' ordem & café '), 'https://duckduckgo.com/?q=ordem%20%26%20caf%C3%A9');
  assert.equal(destination(''), null);
});
test('valid URLs and bare domains open with HTTPS', () => {
  assert.equal(destination('mozilla.org'), 'https://mozilla.org/');
  assert.equal(destination('https://example.com/a?q=1'), 'https://example.com/a?q=1');
  assert.equal(destination('localhost:8000'), 'https://localhost:8000/');
});
test('executable URLs and embedded credentials are rejected', () => {
  for (const value of ['javascript:alert(1)', 'data:text/html,hi', 'file:///c:/secret', 'https://user:pass@example.com', 'user@example.com', 'https://']) {
    assert.equal(destination(value), null);
  }
});
