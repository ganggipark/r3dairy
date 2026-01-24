#!/usr/bin/env node

/**
 * 사주 계산기 CLI
 * Python subprocess에서 호출하여 JSON 입력을 받고 사주 계산 결과를 JSON으로 출력
 */

import { fileURLToPath, pathToFileURL } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let inputData = '';

process.stdin.setEncoding('utf8');

process.stdin.on('data', (chunk) => {
  inputData += chunk;
});

process.stdin.on('end', async () => {
  try {
    const input = JSON.parse(inputData);

    // 필수 필드 검증
    if (!input.year || !input.month || !input.day || !input.hour || !input.gender) {
      throw new Error('필수 필드 누락: year, month, day, hour, gender');
    }

    // ES 모듈 동적 import (Windows 경로를 file:// URL로 변환)
    const modulePath = join(__dirname, 'dist', 'completeSajuCalculator.js');
    const moduleURL = pathToFileURL(modulePath).href;
    const { calculateCompleteSajuData } = await import(moduleURL);

    // 사주 계산 실행
    const result = calculateCompleteSajuData({
      year: input.year,
      month: input.month,
      day: input.day,
      hour: input.hour,
      minute: input.minute || 0,
      gender: input.gender,
      isLunar: input.isLunar || false,
      isLeapMonth: input.isLeapMonth || false,
      useTrueSolarTime: input.useTrueSolarTime !== undefined ? input.useTrueSolarTime : true,
      birthPlace: input.birthPlace || '서울',
    });

    // JSON 출력
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  } catch (error) {
    console.error(JSON.stringify({
      error: error.message,
      stack: error.stack,
    }));
    process.exit(1);
  }
});
