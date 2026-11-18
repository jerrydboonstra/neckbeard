// Fixture mod, written fresh for this test: counts tool calls.
let calls = 0
export function register(on) {
  on("tool.call", async ($, e, next) => { calls += 1; return next(e) })
}
