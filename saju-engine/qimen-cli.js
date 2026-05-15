#!/usr/bin/env node
/**
 * Qimen CLI — stdin JSON → stdout JSON
 * Input modes:
 *   { dailyBest: true, yongSinScore? }              — 12시진 중 best
 *   { workdayRange: [start, end], yongSinScore? }   — 일과시간 내 best (M24)
 *   { targetHour: number, yongSinScore? }           — 단일 시점 (기본)
 */
const {
  calculateCompleteQimen,
  getDailyBestQimen,
  getDailyBestQimenInRange,
} = require('./dist/calculators/qimenCalculator');

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
    if (isNaN(birth.getTime())) throw new Error(`invalid birthDate: ${input.birthDate}`);
    if (isNaN(target.getTime())) throw new Error(`invalid targetDate: ${input.targetDate}`);

    let result;
    if (input.workdayRange && Array.isArray(input.workdayRange)) {
      const [ws, we] = input.workdayRange;
      result = getDailyBestQimenInRange(birth, target, ws, we, input.yongSinScore);
    } else if (input.dailyBest) {
      result = getDailyBestQimen(birth, target, input.yongSinScore);
    } else {
      const hour = input.targetHour ?? 12;
      result = calculateCompleteQimen(birth, target, hour, input.yongSinScore);
    }
    process.stdout.write(JSON.stringify(result));
    process.exit(0);
  } catch (e) {
    process.stderr.write(JSON.stringify({ error: e.message, stack: e.stack }));
    process.exit(1);
  }
})();
