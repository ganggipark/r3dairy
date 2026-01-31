/**
 * 화기격(化氣格) 판단 테스트
 */

import { describe, it, expect } from 'vitest';
import { checkHwaGiGyeok, determineGeukGuk } from './index';
import type { GeukGukInput } from './index';
import type { CheonGan, JiJi } from '@/types/saju';

describe('화기격(化氣格) 판단', () => {
  describe('checkHwaGiGyeok', () => {
    it('갑기합토 - 진월 완전 성립', () => {
      // 갑일간 + 기월간 + 진월 (토왕절) → 화토격 완전 성립
      // 병(화), 신(금)은 토를 극하지 않음
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '진' as JiJi,
        fourPillarGan: ['병' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '신' as CheonGan],
        fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화토격');
      expect(result.combinationPair).toEqual(['갑', '기']);
      expect(result.transformedElement).toBe('토');
      expect(result.isComplete).toBe(true);
      expect(result.interpretation).toContain('완전 성립');
    });

    it('을경합금 - 유월 완전 성립', () => {
      // 을일간 + 경월간 + 유월 (금왕절) → 화금격 완전 성립
      // 정(화), 무(토)는 금을 극하지 않음 (화극금이지만 정은 음화라 약함)
      const input: GeukGukInput = {
        dayGan: '을' as CheonGan,
        monthJi: '유' as JiJi,
        fourPillarGan: ['무' as CheonGan, '경' as CheonGan, '을' as CheonGan, '임' as CheonGan],
        fourPillarJi: ['묘' as JiJi, '유' as JiJi, '해' as JiJi, '축' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화금격');
      expect(result.combinationPair).toEqual(['을', '경']);
      expect(result.transformedElement).toBe('금');
      expect(result.isComplete).toBe(true);
    });

    it('병신합수 - 자월 완전 성립', () => {
      // 병일간 + 신월간 + 자월 (수왕절) → 화수격 완전 성립
      // 금(신,경)과 수(임,계)는 수를 극하지 않음 (토극수인데 토가 없음)
      const input: GeukGukInput = {
        dayGan: '병' as CheonGan,
        monthJi: '자' as JiJi,
        fourPillarGan: ['경' as CheonGan, '신' as CheonGan, '병' as CheonGan, '임' as CheonGan],
        fourPillarJi: ['진' as JiJi, '자' as JiJi, '인' as JiJi, '해' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화수격');
      expect(result.transformedElement).toBe('수');
      expect(result.isComplete).toBe(true);
    });

    it('정임합목 - 인월 완전 성립', () => {
      // 정일간 + 임월간 + 인월 (목왕절) → 화목격 완전 성립
      const input: GeukGukInput = {
        dayGan: '정' as CheonGan,
        monthJi: '인' as JiJi,
        fourPillarGan: ['갑' as CheonGan, '임' as CheonGan, '정' as CheonGan, '을' as CheonGan],
        fourPillarJi: ['자' as JiJi, '인' as JiJi, '사' as JiJi, '미' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화목격');
      expect(result.transformedElement).toBe('목');
      expect(result.isComplete).toBe(true);
    });

    it('무계합화 - 오월 완전 성립', () => {
      // 무일간 + 계월간 + 오월 (화왕절) → 화화격 완전 성립
      // 목(갑,을)과 수(임,계)는 화를 극하지 않음 (수극화인데 이미 계는 합의 일부)
      const input: GeukGukInput = {
        dayGan: '무' as CheonGan,
        monthJi: '오' as JiJi,
        fourPillarGan: ['갑' as CheonGan, '계' as CheonGan, '무' as CheonGan, '병' as CheonGan],
        fourPillarJi: ['인' as JiJi, '오' as JiJi, '술' as JiJi, '사' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화화격');
      expect(result.transformedElement).toBe('화');
      expect(result.isComplete).toBe(true);
    });

    it('갑기합토 - 자월 불완전 (계절 불일치)', () => {
      // 갑일간 + 기월간 + 자월 (수왕절) → 화토격이지만 불완전
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '자' as JiJi,
        fourPillarGan: ['병' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '을' as CheonGan],
        fourPillarJi: ['인' as JiJi, '자' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화토격');
      expect(result.isComplete).toBe(false);
      expect(result.interpretation).toContain('불완전');
      expect(result.interpretation).toContain('수왕절');
    });

    it('시간 합 - 월간 합보다 우선순위 낮음', () => {
      // 갑일간 + 기시간 + 진월 → 화토격
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '진' as JiJi,
        fourPillarGan: ['병' as CheonGan, '을' as CheonGan, '갑' as CheonGan, '기' as CheonGan],
        fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '술' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.hwaGiGyeokType).toBe('화토격');
      expect(result.interpretation).toContain('시간');
    });

    it('천간합 없음 - 화기격 아님', () => {
      // 갑일간이지만 월간/시간에 기가 없음
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '진' as JiJi,
        fourPillarGan: ['병' as CheonGan, '을' as CheonGan, '갑' as CheonGan, '정' as CheonGan],
        fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(false);
      expect(result.hwaGiGyeokType).toBe(null);
      expect(result.interpretation).toContain('천간합이 없어');
    });

    it('파격 요소 있음 - 불완전 화기격', () => {
      // 갑기합토 + 진월이지만 목(갑)이 토를 극함
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '진' as JiJi,
        fourPillarGan: ['갑' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '갑' as CheonGan],
        fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = checkHwaGiGyeok(input);

      expect(result.isHwaGiGyeok).toBe(true);
      expect(result.isComplete).toBe(false);
      expect(result.interpretation).toContain('극하는 오행');
    });
  });

  describe('determineGeukGuk 통합', () => {
    it('화토격이 정격보다 우선', () => {
      // 갑일간 + 기월간 + 진월 → 화토격 (정격 판단 전에 결정)
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '진' as JiJi,
        fourPillarGan: ['병' as CheonGan, '기' as CheonGan, '갑' as CheonGan, '을' as CheonGan],
        fourPillarJi: ['인' as JiJi, '진' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = determineGeukGuk(input);

      expect(result.geukguk).toBe('화토격');
      expect(result.isJeongGyeok).toBe(false);  // 특수 격국
      expect(result.description).toContain('합토');
    });

    it('화기격 아니면 정격 판단', () => {
      // 갑일간 + 술월 (편재격) - 화기격 조건 없음
      const input: GeukGukInput = {
        dayGan: '갑' as CheonGan,
        monthJi: '술' as JiJi,
        fourPillarGan: ['병' as CheonGan, '을' as CheonGan, '갑' as CheonGan, '정' as CheonGan],
        fourPillarJi: ['인' as JiJi, '술' as JiJi, '오' as JiJi, '신' as JiJi],
      };

      const result = determineGeukGuk(input);

      expect(result.geukguk).not.toContain('화');  // 화기격이 아님
      expect(result.isJeongGyeok).toBe(true);  // 정격
    });
  });
});
