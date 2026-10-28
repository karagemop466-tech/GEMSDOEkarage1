// Execute the browser monitor against a fake DOM and network; no internet or
// competition request is made. Run with `node tests/js/test-source-monitor.cjs`.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const script = fs.readFileSync(path.join(__dirname, '../../docs/assets/app.js'), 'utf8');

function chip(site, ref) {
  const target = {textContent: '', dataset: {}};
  return {
    dataset: {sourceRepo: `buffedlizard55-lab/${site}`, sourceRef: ref},
    target,
    querySelector: () => target,
  };
}

async function scenario(disableAbort = false) {
  const a = 'a'.repeat(40);
  const chips = [chip('GEMSDOE24', a), chip('GEMSDOE25', a), chip('GEMSDOE27', a),
                 chip('GEMSDOE28', a), chip('GEMSDOE30', 'not-a-commit')];
  const status = {textContent: ''};
  const events = {};
  const button = {disabled: false, addEventListener: (name, fn) => { events[name] = fn; }};
  const requested = [];
  const document = {
    hidden: false,
    getElementById: id => ({'refresh-sources': button, 'feed-status': status})[id],
    querySelectorAll: () => chips,
    addEventListener: () => {},
  };
  const window = {setTimeout: () => 7, clearTimeout: () => {}, setInterval: () => {}, addEventListener: () => {}};
  const fetch = async (url) => {
    requested.push(url);
    if (url.includes('GEMSDOE24')) return {ok: true, json: async () => ({sha: a})};
    if (url.includes('GEMSDOE25')) return {ok: true, json: async () => ({sha: 'b'.repeat(40)})};
    if (url.includes('GEMSDOE27')) return {ok: false, status: 403};
    throw new Error('offline');
  };
  const context = {document, window, fetch, AbortController: disableAbort ? undefined : AbortController,
                   Date, Promise};
  vm.runInNewContext(script, context, {filename: 'app.js'});
  for (let i = 0; i < 20 && (button.disabled || !status.textContent.startsWith('Checked')); i++) {
    await new Promise(resolve => setImmediate(resolve));
  }
  assert.equal(button.disabled, false);
  assert.equal(typeof events.click, 'function');
  if (disableAbort) {
    assert.equal(requested.length, 0);
    assert.ok(chips.every(c => c.target.dataset.state === 'unknown'));
    assert.match(status.textContent, /5 unavailable/);
  } else {
    assert.equal(requested.length, 4); // an invalid pin must not trigger a request
    assert.ok(requested.every(url => url.startsWith('https://api.github.com/repos/') && url.endsWith('/commits/HEAD')));
    assert.deepEqual(chips.map(c => c.target.dataset.state), ['same', 'changed', 'unknown', 'unknown', 'unknown']);
    assert.match(status.textContent, /1 at audit pin · 1 changed · 3 unavailable/);
    assert.match(status.textContent, /not a pass/);
  }
}

(async () => {
  await scenario();
  await scenario(true);
  console.log('peer revision monitor: unchanged, changed, error and missing browser API cases passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
