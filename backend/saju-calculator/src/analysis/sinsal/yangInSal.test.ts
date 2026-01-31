/**
 * 양인살(羊刃煞) 테스트
 */

import { describe, it, expect } from 'vitest';
import {
  calculateYangInSal,
  hasYangInSal,
  analyzeYangInSal,
  getYangInSalDescription,
  analyzeYangInSalStrength,
  YANG_GAN,
  YIN_GAN,
} from './yangInSal';
import type { CheonGan, JiJi } from '@/types/saju';

describe('yangInSal', () => {
  describe('YANG_GAN / YIN_GAN 상수', () => {
    it('양간 5개가 정의되어 있어야 함', () => {
      expect(YANG_GAN).toEqual(['갑', '병', '무', '경', '임']);
      expect(YANG_GAN.length).toBe(5);
    });

    it('음간 5개가 정의되어 있어야 함', () => {
      expect(YIN_GAN).toEqual(['을', '정', '기', '신', '계']);
      expect(YIN_GAN.length).toBe(5);
    });
  });

  describe('calculateYangInSal', () => {
    it('갑목의 양인살은 묘', () => {
      expect(calculateYangInSal('갑')).toBe('묘');
    });

    it('병화의 양인살은 오', () => {
      expect(calculateYangInSal('병')).toBe('오');
    });

    it('무토의 양인살은 오 (화토동법)', () => {
      expect(calculateYangInSal('무')).toBe('오');
    });

    it('경금의 양인살은 유', () => {
      expect(calculateYangInSal('경')).toBe('유');
    });

    it('임수의 양인살은 자', () => {
      expect(calculateYangInSal('임')).toBe('자');
    });

    it('음간(을)은 양인살이 없음', () => {
      expect(calculateYangInSal('을')).toBeNull();
    });

    it('음간(정)은 양인살이 없음', () => {
      expect(calculateYangInSal('정')).toBeNull();
    });

    it('음간(기)은 양인살이 없음', () => {
      expect(calculateYangInSal('기')).toBeNull();
    });

    it('음간(신)은 양인살이 없음', () => {
      expect(calculateYangInSal('신')).toBeNull();
    });

    it('음간(계)은 양인살이 없음', () => {
      expect(calculateYangInSal('계')).toBeNull();
    });
  });

  describe('hasYangInSal', () => {
    it('갑목에 묘가 있으면 양인살 있음', () => {
      const jijis: JiJi[] = ['자', '묘', '오', '유'];
      expect(hasYangInSal('갑', jijis)).toBe(true);
    });

    it('갑목에 묘가 없으면 양인살 없음', () => {
      const jijis: JiJi[] = ['자', '축', '오', '유'];
      expect(hasYangInSal('갑', jijis)).toBe(false);
    });

    it('병화에 오가 있으면 양인살 있음', () => {
      const jijis: JiJi[] = ['인', '오', '술', '해'];
      expect(hasYangInSal('병', jijis)).toBe(true);
    });

    it('임수에 자가 있으면 양인살 있음', () => {
      const jijis: JiJi[] = ['자', '진', '사', '미'];
      expect(hasYangInSal('임', jijis)).toBe(true);
    });

    it('음간은 양인살 없음 (을)', () => {
      const jijis: JiJi[] = ['자', '묘', '오', '유'];
      expect(hasYangInSal('을', jijis)).toBe(false);
    });

    it('음간은 양인살 없음 (기)', () => {
      const jijis: JiJi[] = ['자', '묘', '오', '유'];
      expect(hasYangInSal('기', jijis)).toBe(false);
    });

    it('빈 배열에는 양인살 없음', () => {
      expect(hasYangInSal('갑', [])).toBe(false);
    });
  });

  describe('analyzeYangInSal', () => {
    it('양간에 양인살이 있으면 present가 true', () => {
      const jijis: JiJi[] = ['묘', '오', '유', '자'];
      const result = analyzeYangInSal('갑', jijis);

      expect(result).not.toBeNull();
      expect(result!.present).toBe(true);
      expect(result!.name).toBe('양인살(羊刃煞)');
      expect(result!.type).toBe('yangInSal');
      expect(result!.triggerJiji).toBe('묘');
      expect(result!.effect).toBe('bad');
    });

    it('양간에 양인살이 없으면 present가 false', () => {
      const jijis: JiJi[] = ['축', '인', '사', '미'];
      const result = analyzeYangInSal('갑', jijis);

      expect(result).not.toBeNull();
      expect(result!.present).toBe(false);
      expect(result!.description).toContain('묘');
    });

    it('음간은 null 반환', () => {
      const jijis: JiJi[] = ['자', '묘', '오', '유'];
      expect(analyzeYangInSal('을', jijis)).toBeNull();
      expect(analyzeYangInSal('정', jijis)).toBeNull();
      expect(analyzeYangInSal('기', jijis)).toBeNull();
      expect(analyzeYangInSal('신', jijis)).toBeNull();
      expect(analyzeYangInSal('계', jijis)).toBeNull();
    });

    it('detailedMeaning이 포함됨', () => {
      const jijis: JiJi[] = ['묘'];
      const result = analyzeYangInSal('갑', jijis);

      expect(result!.detailedMeaning).toBeTruthy();
      expect(result!.detailedMeaning.length).toBeGreaterThan(10);
    });
  });

  describe('getYangInSalDescription', () => {
    it('갑목 설명 반환', () => {
      const desc = getYangInSalDescription('갑');
      expect(desc).toContain('갑목');
      expect(desc).toContain('묘');
      expect(desc).toContain('목');
    });

    it('병화 설명 반환', () => {
      const desc = getYangInSalDescription('병');
      expect(desc).toContain('병화');
      expect(desc).toContain('오');
      expect(desc).toContain('화');
    });

    it('무토 설명 반환 (화토동법)', () => {
      const desc = getYangInSalDescription('무');
      expect(desc).toContain('무토');
      expect(desc).toContain('오');
      expect(desc).toContain('화토동법');
    });

    it('경금 설명 반환', () => {
      const desc = getYangInSalDescription('경');
      expect(desc).toContain('경금');
      expect(desc).toContain('유');
      expect(desc).toContain('금');
    });

    it('임수 설명 반환', () => {
      const desc = getYangInSalDescription('임');
      expect(desc).toContain('임수');
      expect(desc).toContain('자');
      expect(desc).toContain('수');
    });

    it('음간은 해당 없음 메시지', () => {
      const desc = getYangInSalDescription('을');
      expect(desc).toContain('음간');
      expect(desc).toContain('적용되지 않');
    });

    it('모든 음간 설명 확인', () => {
      const yinGans: CheonGan[] = ['을', '정', '기', '신', '계'];
      yinGans.forEach(gan => {
        const desc = getYangInSalDescription(gan);
        expect(desc).toContain('음간');
      });
    });
  });

  describe('analyzeYangInSalStrength', () => {
    it('음간은 strength가 none', () => {
      const result = analyzeYangInSalStrength('을', ['자', '묘', '오', '유']);
      expect(result.strength).toBe('none');
      expect(result.count).toBe(0);
      expect(result.locations).toEqual([]);
      expect(result.warning).toContain('음간');
    });

    it('양인살이 없으면 strength가 none', () => {
      const result = analyzeYangInSalStrength('갑', ['축', '인', '사', '미']);
      expect(result.strength).toBe('none');
      expect(result.count).toBe(0);
    });

    it('양인살 1개는 weak', () => {
      const result = analyzeYangInSalStrength('갑', ['묘', '인', '사', '미']);
      expect(result.strength).toBe('weak');
      expect(result.count).toBe(1);
      expect(result.locations).toContain('년지');
    });

    it('양인살 2개는 normal', () => {
      const result = analyzeYangInSalStrength('갑', ['묘', '묘', '사', '미']);
      expect(result.strength).toBe('normal');
      expect(result.count).toBe(2);
    });

    it('양인살 3개는 strong', () => {
      const result = analyzeYangInSalStrength('갑', ['묘', '묘', '묘', '미']);
      expect(result.strength).toBe('strong');
      expect(result.count).toBe(3);
    });

    it('양인살 4개 이상은 very_strong', () => {
      const result = analyzeYangInSalStrength('갑', ['묘', '묘', '묘', '묘']);
      expect(result.strength).toBe('very_strong');
      expect(result.count).toBe(4);
    });

    it('세운에서 양인살 발생', () => {
      const result = analyzeYangInSalStrength('갑', ['축', '인', '사', '미'], '묘');
      expect(result.count).toBe(1);
      expect(result.locations).toContain('세운');
    });

    it('대운에서 양인살 발생', () => {
      const result = analyzeYangInSalStrength('갑', ['축', '인', '사', '미'], undefined, '묘');
      expect(result.count).toBe(1);
      expect(result.locations).toContain('대운');
    });

    it('사주 + 세운 + 대운 모두 양인살', () => {
      const result = analyzeYangInSalStrength('갑', ['묘', '인', '사', '미'], '묘', '묘');
      expect(result.count).toBe(3);
      expect(result.locations).toContain('년지');
      expect(result.locations).toContain('세운');
      expect(result.locations).toContain('대운');
      expect(result.strength).toBe('strong');
    });

    it('위치 정보가 올바름', () => {
      const result = analyzeYangInSalStrength('갑', ['자', '묘', '묘', '묘']);
      expect(result.locations).toContain('월지');
      expect(result.locations).toContain('일지');
      expect(result.locations).toContain('시지');
      expect(result.locations).not.toContain('년지');
    });

    it('warning 메시지가 적절함', () => {
      const noneResult = analyzeYangInSalStrength('갑', ['축', '인', '사', '미']);
      expect(noneResult.warning).toContain('없');

      const weakResult = analyzeYangInSalStrength('갑', ['묘', '인', '사', '미']);
      expect(weakResult.warning).toContain('추진력');

      const normalResult = analyzeYangInSalStrength('갑', ['묘', '묘', '사', '미']);
      expect(normalResult.warning).toContain('주의');

      const strongResult = analyzeYangInSalStrength('갑', ['묘', '묘', '묘', '미']);
      expect(strongResult.warning).toContain('사고');

      const veryStrongResult = analyzeYangInSalStrength('갑', ['묘', '묘', '묘', '묘']);
      expect(veryStrongResult.warning).toContain('각별');
    });
  });
});
