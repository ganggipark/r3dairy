/**
 * 기타 신살 테스트
 */

import { describe, it, expect } from 'vitest';
import {
  calculateCheonEulGwiIn,
  hasCheonEulGwiIn,
  analyzeCheonEulGwiIn,
  calculateMunChangGwiIn,
  analyzeMunChangGwiIn,
  calculateHongYeomSal,
  analyzeHongYeomSal,
  isBaekHoSalYear,
  analyzeBaekHoSal,
  hasHyeonChimSal,
  analyzeHyeonChimSal,
  getSamJaeYears,
  isSamJaeYear,
  analyzeSamJae,
} from './otherSinsal';
import type { CheonGan, JiJi } from '@/types/saju';

describe('otherSinsal', () => {
  describe('천을귀인 (天乙貴人)', () => {
    describe('calculateCheonEulGwiIn', () => {
      it('갑일은 축, 미가 귀인', () => {
        expect(calculateCheonEulGwiIn('갑')).toEqual(['축', '미']);
      });

      it('을일은 자, 신이 귀인', () => {
        expect(calculateCheonEulGwiIn('을')).toEqual(['자', '신']);
      });

      it('병일은 해, 유가 귀인', () => {
        expect(calculateCheonEulGwiIn('병')).toEqual(['해', '유']);
      });

      it('정일은 해, 유가 귀인', () => {
        expect(calculateCheonEulGwiIn('정')).toEqual(['해', '유']);
      });

      it('무일은 축, 미가 귀인', () => {
        expect(calculateCheonEulGwiIn('무')).toEqual(['축', '미']);
      });

      it('기일은 자, 신이 귀인', () => {
        expect(calculateCheonEulGwiIn('기')).toEqual(['자', '신']);
      });

      it('경일은 축, 미가 귀인', () => {
        expect(calculateCheonEulGwiIn('경')).toEqual(['축', '미']);
      });

      it('신일은 인, 오가 귀인', () => {
        expect(calculateCheonEulGwiIn('신')).toEqual(['인', '오']);
      });

      it('임일은 묘, 사가 귀인', () => {
        expect(calculateCheonEulGwiIn('임')).toEqual(['묘', '사']);
      });

      it('계일은 묘, 사가 귀인', () => {
        expect(calculateCheonEulGwiIn('계')).toEqual(['묘', '사']);
      });
    });

    describe('hasCheonEulGwiIn', () => {
      it('귀인 지지가 있으면 true', () => {
        expect(hasCheonEulGwiIn('갑', ['축', '인', '묘'])).toBe(true);
        expect(hasCheonEulGwiIn('갑', ['미', '신', '유'])).toBe(true);
      });

      it('귀인 지지가 없으면 false', () => {
        expect(hasCheonEulGwiIn('갑', ['인', '묘', '진'])).toBe(false);
      });
    });

    describe('analyzeCheonEulGwiIn', () => {
      it('귀인이 있으면 present가 true', () => {
        const result = analyzeCheonEulGwiIn('갑', ['축', '인', '묘']);
        expect(result.present).toBe(true);
        expect(result.name).toBe('천을귀인(天乙貴人)');
        expect(result.effect).toBe('good');
        expect(result.triggerJiji).toBe('축');
      });

      it('귀인이 없으면 present가 false', () => {
        const result = analyzeCheonEulGwiIn('갑', ['인', '묘', '진']);
        expect(result.present).toBe(false);
        expect(result.description).toContain('축');
        expect(result.description).toContain('미');
      });
    });
  });

  describe('문창귀인 (文昌貴人)', () => {
    describe('calculateMunChangGwiIn', () => {
      it('갑일은 사가 문창', () => {
        expect(calculateMunChangGwiIn('갑')).toBe('사');
      });

      it('을일은 오가 문창', () => {
        expect(calculateMunChangGwiIn('을')).toBe('오');
      });

      it('병일은 신이 문창', () => {
        expect(calculateMunChangGwiIn('병')).toBe('신');
      });

      it('정일은 유가 문창', () => {
        expect(calculateMunChangGwiIn('정')).toBe('유');
      });

      it('무일은 신이 문창', () => {
        expect(calculateMunChangGwiIn('무')).toBe('신');
      });

      it('기일은 유가 문창', () => {
        expect(calculateMunChangGwiIn('기')).toBe('유');
      });

      it('경일은 해가 문창', () => {
        expect(calculateMunChangGwiIn('경')).toBe('해');
      });

      it('신일은 자가 문창', () => {
        expect(calculateMunChangGwiIn('신')).toBe('자');
      });

      it('임일은 인이 문창', () => {
        expect(calculateMunChangGwiIn('임')).toBe('인');
      });

      it('계일은 묘가 문창', () => {
        expect(calculateMunChangGwiIn('계')).toBe('묘');
      });
    });

    describe('analyzeMunChangGwiIn', () => {
      it('문창귀인이 있으면 present가 true', () => {
        const result = analyzeMunChangGwiIn('갑', ['사', '오', '미']);
        expect(result.present).toBe(true);
        expect(result.name).toBe('문창귀인(文昌貴人)');
        expect(result.effect).toBe('good');
        expect(result.triggerJiji).toBe('사');
      });

      it('문창귀인이 없으면 present가 false', () => {
        const result = analyzeMunChangGwiIn('갑', ['자', '축', '인']);
        expect(result.present).toBe(false);
      });
    });
  });

  describe('홍염살 (紅艶煞)', () => {
    describe('calculateHongYeomSal', () => {
      it('갑일은 오가 홍염', () => {
        expect(calculateHongYeomSal('갑')).toBe('오');
      });

      it('을일은 신이 홍염', () => {
        expect(calculateHongYeomSal('을')).toBe('신');
      });

      it('병일은 인이 홍염', () => {
        expect(calculateHongYeomSal('병')).toBe('인');
      });

      it('정일은 미가 홍염', () => {
        expect(calculateHongYeomSal('정')).toBe('미');
      });

      it('무일은 진이 홍염', () => {
        expect(calculateHongYeomSal('무')).toBe('진');
      });

      it('기일은 진이 홍염', () => {
        expect(calculateHongYeomSal('기')).toBe('진');
      });

      it('경일은 술이 홍염', () => {
        expect(calculateHongYeomSal('경')).toBe('술');
      });

      it('신일은 유가 홍염', () => {
        expect(calculateHongYeomSal('신')).toBe('유');
      });

      it('임일은 자가 홍염', () => {
        expect(calculateHongYeomSal('임')).toBe('자');
      });

      it('계일은 신이 홍염', () => {
        expect(calculateHongYeomSal('계')).toBe('신');
      });
    });

    describe('analyzeHongYeomSal', () => {
      it('홍염살이 있으면 present가 true', () => {
        const result = analyzeHongYeomSal('갑', ['오', '미', '신']);
        expect(result.present).toBe(true);
        expect(result.name).toBe('홍염살(紅艶煞)');
        expect(result.effect).toBe('neutral');
      });

      it('홍염살이 없으면 present가 false', () => {
        const result = analyzeHongYeomSal('갑', ['자', '축', '인']);
        expect(result.present).toBe(false);
      });
    });
  });

  describe('백호살 (白虎煞)', () => {
    describe('isBaekHoSalYear', () => {
      it('자일지는 인묘년에 백호살', () => {
        expect(isBaekHoSalYear('자', '인')).toBe(true);
        expect(isBaekHoSalYear('자', '묘')).toBe(true);
        expect(isBaekHoSalYear('자', '진')).toBe(false);
      });

      it('인일지는 사오년에 백호살', () => {
        expect(isBaekHoSalYear('인', '사')).toBe(true);
        expect(isBaekHoSalYear('인', '오')).toBe(true);
        expect(isBaekHoSalYear('인', '미')).toBe(false);
      });

      it('사일지는 신유년에 백호살', () => {
        expect(isBaekHoSalYear('사', '신')).toBe(true);
        expect(isBaekHoSalYear('사', '유')).toBe(true);
        expect(isBaekHoSalYear('사', '술')).toBe(false);
      });

      it('신일지는 해자년에 백호살', () => {
        expect(isBaekHoSalYear('신', '해')).toBe(true);
        expect(isBaekHoSalYear('신', '자')).toBe(true);
        expect(isBaekHoSalYear('신', '축')).toBe(false);
      });
    });

    describe('analyzeBaekHoSal', () => {
      it('백호살 해당 연도면 present가 true', () => {
        const result = analyzeBaekHoSal('자', '인');
        expect(result.present).toBe(true);
        expect(result.name).toBe('백호살(白虎煞)');
        expect(result.effect).toBe('bad');
      });

      it('백호살 비해당 연도면 present가 false', () => {
        const result = analyzeBaekHoSal('자', '진');
        expect(result.present).toBe(false);
        expect(result.effect).toBe('neutral');
      });
    });
  });

  describe('현침살 (懸針煞)', () => {
    describe('hasHyeonChimSal', () => {
      it('갑신(甲申)이 있으면 현침살', () => {
        const gans: CheonGan[] = ['갑', '병', '무', '경'];
        const jis: JiJi[] = ['자', '신', '오', '유'];
        expect(hasHyeonChimSal(gans, jis)).toBe(true);
      });

      it('신묘(辛卯)가 있으면 현침살', () => {
        const gans: CheonGan[] = ['을', '신', '무', '경'];
        const jis: JiJi[] = ['자', '묘', '오', '유'];
        expect(hasHyeonChimSal(gans, jis)).toBe(true);
      });

      it('갑신/신묘 모두 없으면 현침살 아님', () => {
        const gans: CheonGan[] = ['을', '병', '무', '경'];
        const jis: JiJi[] = ['자', '축', '오', '유'];
        expect(hasHyeonChimSal(gans, jis)).toBe(false);
      });

      it('갑이 있어도 신이 없으면 현침살 아님', () => {
        const gans: CheonGan[] = ['갑', '병', '무', '경'];
        const jis: JiJi[] = ['자', '축', '오', '유'];
        expect(hasHyeonChimSal(gans, jis)).toBe(false);
      });
    });

    describe('analyzeHyeonChimSal', () => {
      it('현침살이 있으면 present가 true', () => {
        const gans: CheonGan[] = ['갑', '병', '무', '경'];
        const jis: JiJi[] = ['자', '신', '오', '유'];
        const result = analyzeHyeonChimSal(gans, jis);
        expect(result.present).toBe(true);
        expect(result.name).toBe('현침살(懸針煞)');
        expect(result.effect).toBe('neutral');
      });

      it('현침살이 없으면 present가 false', () => {
        const gans: CheonGan[] = ['을', '병', '무', '경'];
        const jis: JiJi[] = ['자', '축', '오', '유'];
        const result = analyzeHyeonChimSal(gans, jis);
        expect(result.present).toBe(false);
      });
    });
  });

  describe('삼재 (三災)', () => {
    describe('getSamJaeYears', () => {
      it('인오술 삼합은 신유술년이 삼재', () => {
        expect(getSamJaeYears('인')).toEqual(['신', '유', '술']);
        expect(getSamJaeYears('오')).toEqual(['신', '유', '술']);
        expect(getSamJaeYears('술')).toEqual(['신', '유', '술']);
      });

      it('사유축 삼합은 해자축년이 삼재', () => {
        expect(getSamJaeYears('사')).toEqual(['해', '자', '축']);
        expect(getSamJaeYears('유')).toEqual(['해', '자', '축']);
        expect(getSamJaeYears('축')).toEqual(['해', '자', '축']);
      });

      it('신자진 삼합은 인묘진년이 삼재', () => {
        expect(getSamJaeYears('신')).toEqual(['인', '묘', '진']);
        expect(getSamJaeYears('자')).toEqual(['인', '묘', '진']);
        expect(getSamJaeYears('진')).toEqual(['인', '묘', '진']);
      });

      it('해묘미 삼합은 사오미년이 삼재', () => {
        expect(getSamJaeYears('해')).toEqual(['사', '오', '미']);
        expect(getSamJaeYears('묘')).toEqual(['사', '오', '미']);
        expect(getSamJaeYears('미')).toEqual(['사', '오', '미']);
      });
    });

    describe('isSamJaeYear', () => {
      it('들삼재 판정', () => {
        const result = isSamJaeYear('인', '신');
        expect(result.isSamJae).toBe(true);
        expect(result.type).toBe('entering');
      });

      it('눌삼재 판정', () => {
        const result = isSamJaeYear('인', '유');
        expect(result.isSamJae).toBe(true);
        expect(result.type).toBe('staying');
      });

      it('날삼재 판정', () => {
        const result = isSamJaeYear('인', '술');
        expect(result.isSamJae).toBe(true);
        expect(result.type).toBe('leaving');
      });

      it('삼재 아닌 해', () => {
        const result = isSamJaeYear('인', '해');
        expect(result.isSamJae).toBe(false);
        expect(result.type).toBeNull();
      });
    });

    describe('analyzeSamJae', () => {
      it('삼재 기간이면 present가 true', () => {
        const result = analyzeSamJae('인', '신');
        expect(result.present).toBe(true);
        expect(result.name).toBe('삼재(三災)');
        expect(result.effect).toBe('bad');
        expect(result.description).toContain('들삼재');
      });

      it('눌삼재는 가장 강함 설명 포함', () => {
        const result = analyzeSamJae('인', '유');
        expect(result.description).toContain('눌삼재');
        expect(result.description).toContain('가장 강함');
      });

      it('날삼재는 끝 설명 포함', () => {
        const result = analyzeSamJae('인', '술');
        expect(result.description).toContain('날삼재');
        expect(result.description).toContain('끝');
      });

      it('삼재 아닌 기간이면 present가 false', () => {
        const result = analyzeSamJae('인', '해');
        expect(result.present).toBe(false);
        expect(result.effect).toBe('neutral');
      });
    });
  });
});
