#!/usr/bin/env node
/**
 * Qimen CLI — stdin JSON → stdout JSON
 * Input:  { birthDate, targetDate, targetHour?, yongSinScore? }
 *         yongSinScore: 사주 용신 분석 (M21) - 오행별 0-100 점수
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
    const result = calculateCompleteQimen(birth, target, hour, input.yongSinScore);
    process.stdout.write(JSON.stringify(result));
    process.exit(0);
  } catch (e) {
    process.stderr.write(JSON.stringify({ error: e.message, stack: e.stack }));
    process.exit(1);
  }
})();
