#!/usr/bin/env node
/**
 * Qimen CLI — stdin JSON → stdout JSON
 * Input:  { birthDate, targetDate, targetHour? }
 *         birthDate, targetDate: ISO 8601 strings
 *         targetHour: number 0-23 (default 12)
 * Output: CompleteQimenResult JSON
 */
const { calculateCompleteQimen } = require('./dist/calculators/qimenCalculator');

(async () => {
  try {
    let raw = '';
    for await (const chunk of process.stdin) raw += chunk;
    const input = JSON.parse(raw);

    if (!input.birthDate || !input.targetDate) {
      throw new Error('birthDate and targetDate are required');
    }

    const birth = new Date(input.birthDate);
    const target = new Date(input.targetDate);
    const hour = input.targetHour ?? 12;

    if (isNaN(birth.getTime())) throw new Error(`invalid birthDate: ${input.birthDate}`);
    if (isNaN(target.getTime())) throw new Error(`invalid targetDate: ${input.targetDate}`);

    const result = calculateCompleteQimen(birth, target, hour);
    process.stdout.write(JSON.stringify(result));
    process.exit(0);
  } catch (e) {
    process.stderr.write(JSON.stringify({ error: e.message, stack: e.stack }));
    process.exit(1);
  }
})();
