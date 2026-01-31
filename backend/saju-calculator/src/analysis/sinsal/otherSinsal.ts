/**
 * 기타 신살 계산 모듈
 * - 천을귀인 (天乙貴人)
 * - 문창귀인 (文昌貴人)
 * - 홍염살 (紅艶煞)
 * - 백호살 (白虎煞)
 * - 현침살 (懸針煞)
 */

import type { CheonGan, JiJi } from '../../types/saju';
import type { SinsalResult } from './types';

/**
 * ==========================================
 * 천을귀인 (天乙貴人) - 가장 큰 귀인
 * ==========================================
 * 계산 원리: 일간을 기준으로 특정 지지가 귀인
 */
const CHEON_EUL_GWI_IN_TABLE: Record<CheonGan, JiJi[]> = {
  '갑': ['축', '미'],  // 갑일은 축, 미가 귀인
  '을': ['자', '신'],  // 을일은 자, 신이 귀인
  '병': ['해', '유'],  // 병일은 해, 유가 귀인
  '정': ['해', '유'],  // 정일은 해, 유가 귀인
  '무': ['축', '미'],  // 무일은 축, 미가 귀인
  '기': ['자', '신'],  // 기일은 자, 신이 귀인
  '경': ['축', '미'],  // 경일은 축, 미가 귀인
  '신': ['인', '오'],  // 신일은 인, 오가 귀인
  '임': ['묘', '사'],  // 임일은 묘, 사가 귀인
  '계': ['묘', '사'],  // 계일은 묘, 사가 귀인
};

export function calculateCheonEulGwiIn(dayGan: CheonGan): JiJi[] {
  return CHEON_EUL_GWI_IN_TABLE[dayGan];
}

export function hasCheonEulGwiIn(dayGan: CheonGan, targetJijis: JiJi[]): boolean {
  const gwiInJijis = CHEON_EUL_GWI_IN_TABLE[dayGan];
  return gwiInJijis.some(ji => targetJijis.includes(ji));
}

export function analyzeCheonEulGwiIn(
  dayGan: CheonGan,
  targetJijis: JiJi[],
): SinsalResult {
  const gwiInJijis = CHEON_EUL_GWI_IN_TABLE[dayGan];
  const foundJijis = gwiInJijis.filter(ji => targetJijis.includes(ji));
  const present = foundJijis.length > 0;

  return {
    name: '천을귀인(天乙貴人)',
    type: 'cheonEulGwiIn',
    present,
    triggerJiji: foundJijis[0],
    description: present
      ? `귀인의 도움을 받는 길성 (${foundJijis.join(', ')})`
      : `천을귀인 지지(${gwiInJijis.join(', ')})가 사주에 없음`,
    effect: 'good',
    detailedMeaning: present
      ? '천을귀인은 가장 큰 귀인성으로, 어려울 때 귀인의 도움을 받습니다. 위기를 기회로 바꾸는 힘이 있고, 사회적으로 존경받는 위치에 오를 수 있습니다. 관직이나 학업에서 좋은 성과를 거두기 쉽습니다.'
      : '천을귀인이 없어도 다른 귀인이나 좋은 운에서 도움을 받을 수 있습니다.',
  };
}

/**
 * ==========================================
 * 문창귀인 (文昌貴人) - 학문, 시험운
 * ==========================================
 */
const MUN_CHANG_GWI_IN_TABLE: Record<CheonGan, JiJi> = {
  '갑': '사',  // 갑일은 사가 문창
  '을': '오',  // 을일은 오가 문창
  '병': '신',  // 병일은 신이 문창
  '정': '유',  // 정일은 유가 문창
  '무': '신',  // 무일은 신이 문창
  '기': '유',  // 기일은 유가 문창
  '경': '해',  // 경일은 해가 문창
  '신': '자',  // 신일은 자가 문창
  '임': '인',  // 임일은 인이 문창
  '계': '묘',  // 계일은 묘가 문창
};

export function calculateMunChangGwiIn(dayGan: CheonGan): JiJi {
  return MUN_CHANG_GWI_IN_TABLE[dayGan];
}

export function analyzeMunChangGwiIn(
  dayGan: CheonGan,
  targetJijis: JiJi[],
): SinsalResult {
  const munChangJi = MUN_CHANG_GWI_IN_TABLE[dayGan];
  const present = targetJijis.includes(munChangJi);

  return {
    name: '문창귀인(文昌貴人)',
    type: 'munChangGwiIn',
    present,
    triggerJiji: munChangJi,
    description: present
      ? '학문, 시험, 문서운이 좋음'
      : `문창귀인 지지(${munChangJi})가 사주에 없음`,
    effect: 'good',
    detailedMeaning: present
      ? '문창귀인은 학문의 별로, 총명하고 문서를 잘 다룹니다. 시험운이 좋아 공무원, 자격증 등에 유리하며, 글쓰기나 연구 분야에서 두각을 나타냅니다.'
      : '문창귀인이 없어도 노력으로 학업 성취가 가능합니다.',
  };
}

/**
 * ==========================================
 * 홍염살 (紅艶煞) - 이성운, 매력
 * ==========================================
 */
const HONG_YEOM_SAL_TABLE: Record<CheonGan, JiJi> = {
  '갑': '오',
  '을': '신',
  '병': '인',
  '정': '미',
  '무': '진',
  '기': '진',
  '경': '술',
  '신': '유',
  '임': '자',
  '계': '신',
};

export function calculateHongYeomSal(dayGan: CheonGan): JiJi {
  return HONG_YEOM_SAL_TABLE[dayGan];
}

export function analyzeHongYeomSal(
  dayGan: CheonGan,
  targetJijis: JiJi[],
): SinsalResult {
  const hongYeomJi = HONG_YEOM_SAL_TABLE[dayGan];
  const present = targetJijis.includes(hongYeomJi);

  return {
    name: '홍염살(紅艶煞)',
    type: 'hongYeomSal',
    present,
    triggerJiji: hongYeomJi,
    description: present
      ? '이성에게 매력적, 연애운 활발'
      : `홍염살 지지(${hongYeomJi})가 사주에 없음`,
    effect: 'neutral',
    detailedMeaning: present
      ? '홍염살은 붉은 꽃처럼 이성을 끄는 매력을 의미합니다. 연애운이 활발하고 인기가 많지만, 과하면 색정 문제나 복잡한 이성 관계에 빠질 수 있습니다. 연예인이나 서비스업에 유리합니다.'
      : '홍염살이 없어 이성 문제로 인한 복잡함이 적습니다.',
  };
}

/**
 * ==========================================
 * 백호살 (白虎煞) - 사고, 수술
 * ==========================================
 * 일지가 특정 지지일 때 해당 연도에 백호살
 */
const BAEK_HO_SAL_YEARS: Record<JiJi, JiJi[]> = {
  '자': ['인', '묘'],  // 자일지는 인묘년에 백호
  '축': ['인', '묘'],
  '인': ['사', '오'],
  '묘': ['사', '오'],
  '진': ['사', '오'],
  '사': ['신', '유'],
  '오': ['신', '유'],
  '미': ['신', '유'],
  '신': ['해', '자'],
  '유': ['해', '자'],
  '술': ['해', '자'],
  '해': ['인', '묘'],
};

export function isBaekHoSalYear(dayJi: JiJi, yearJi: JiJi): boolean {
  const badYears = BAEK_HO_SAL_YEARS[dayJi] || [];
  return badYears.includes(yearJi);
}

export function analyzeBaekHoSal(
  dayJi: JiJi,
  currentYearJi: JiJi,
): SinsalResult {
  const present = isBaekHoSalYear(dayJi, currentYearJi);
  const badYears = BAEK_HO_SAL_YEARS[dayJi] || [];

  return {
    name: '백호살(白虎煞)',
    type: 'baekHoSal',
    present,
    description: present
      ? '올해 사고, 수술, 부상에 주의'
      : `백호살 해당 연도(${badYears.join(', ')}년)가 아님`,
    effect: present ? 'bad' : 'neutral',
    detailedMeaning: present
      ? '백호살은 흰 호랑이처럼 갑작스러운 위험을 의미합니다. 올해는 교통사고, 수술, 부상에 특히 주의해야 합니다. 위험한 활동은 자제하고, 건강검진을 받아보세요.'
      : '올해는 백호살이 작용하지 않아 큰 사고 위험이 낮습니다.',
  };
}

/**
 * ==========================================
 * 현침살 (懸針煞) - 날카로움, 수술
 * ==========================================
 * 甲, 申, 卯, 辛 글자에 세로획이 관통하는 형상
 * 사주에 甲申, 卯辛이 함께 있을 때
 */
export function hasHyeonChimSal(
  sajuGans: CheonGan[],
  sajuJis: JiJi[],
): boolean {
  // 甲申(갑신)이 함께 있거나
  const hasGapSin = sajuGans.includes('갑') && sajuJis.includes('신');
  // 辛卯(신묘)가 함께 있으면 현침살
  const hasSinMyo = sajuGans.includes('신') && sajuJis.includes('묘');

  return hasGapSin || hasSinMyo;
}

export function analyzeHyeonChimSal(
  sajuGans: CheonGan[],
  sajuJis: JiJi[],
): SinsalResult {
  const present = hasHyeonChimSal(sajuGans, sajuJis);

  return {
    name: '현침살(懸針煞)',
    type: 'hyeonChimSal',
    present,
    description: present
      ? '바늘처럼 날카로운 기운, 수술/침술과 인연'
      : '현침살이 사주에 없음',
    effect: present ? 'neutral' : 'neutral',
    detailedMeaning: present
      ? '현침살은 매달린 바늘처럼 날카로운 기운입니다. 예리한 판단력과 비판 능력이 있으나, 말이 날카로워 대인관계에서 갈등이 생길 수 있습니다. 의사, 침술사, 재단사 등 날카로운 도구를 다루는 직업과 인연이 있습니다.'
      : '현침살이 없어 날카로운 기운의 영향이 적습니다.',
  };
}

/**
 * ==========================================
 * 원진살 (元辰煞) - 불안정한 기운
 * ==========================================
 * 원진(元辰): 원래의 진(辰) 위치에서 충(沖)하는 지지
 * 사주에서 불편하고 불안정한 기운을 나타냄
 * 인간관계 갈등, 건강 문제, 정신적 불안 암시
 */
const WON_JIN_SAL_TABLE: Record<JiJi, JiJi> = {
  '자': '미',  // 자일지/년지는 미가 원진
  '축': '신',  // 축일지/년지는 신이 원진
  '인': '유',  // 인일지/년지는 유가 원진
  '묘': '술',  // 묘일지/년지는 술이 원진
  '진': '해',  // 진일지/년지는 해가 원진
  '사': '자',  // 사일지/년지는 자가 원진
  '오': '축',  // 오일지/년지는 축이 원진
  '미': '인',  // 미일지/년지는 인이 원진
  '신': '묘',  // 신일지/년지는 묘가 원진
  '유': '진',  // 유일지/년지는 진이 원진
  '술': '사',  // 술일지/년지는 사가 원진
  '해': '오',  // 해일지/년지는 오가 원진
};

/**
 * 원진살 계산 (일지 기준)
 * @param dayJi 일지
 * @returns 원진살 지지
 */
export function calculateWonJinSal(dayJi: JiJi): JiJi {
  return WON_JIN_SAL_TABLE[dayJi];
}

/**
 * 원진살 분석
 * 일지-년지, 일지-월지, 일지-시지 조합을 검사
 * @param dayJi 일지
 * @param yearJi 년지
 * @param monthJi 월지
 * @param hourJi 시지
 * @returns 원진살 분석 결과
 */
export function analyzeWonJinSal(
  dayJi: JiJi,
  yearJi: JiJi,
  monthJi: JiJi,
  hourJi: JiJi,
): SinsalResult {
  const wonJinJi = WON_JIN_SAL_TABLE[dayJi];

  // 일지 기준으로 년지, 월지, 시지에서 원진살 검사
  const foundInYear = yearJi === wonJinJi;
  const foundInMonth = monthJi === wonJinJi;
  const foundInHour = hourJi === wonJinJi;

  const present = foundInYear || foundInMonth || foundInHour;

  // 어디서 발견되었는지 기록
  const locations: string[] = [];
  if (foundInYear) locations.push('년지');
  if (foundInMonth) locations.push('월지');
  if (foundInHour) locations.push('시지');

  return {
    name: '원진살(元辰煞)',
    type: 'gongMang', // 타입 임시 사용 (기타 신살)
    present,
    triggerJiji: present ? wonJinJi : undefined,
    description: present
      ? `원진살 발견: ${locations.join(', ')}에 ${wonJinJi}가 있음`
      : `원진살 지지(${wonJinJi})가 사주에 없음`,
    effect: present ? 'bad' : 'neutral',
    detailedMeaning: present
      ? `원진살은 불안정하고 불편한 기운을 나타냅니다. 인간관계에서 갈등이 생기기 쉽고, 정신적으로 불안하거나 초조함을 느낄 수 있습니다. 건강 문제나 예상치 못한 변수에 주의가 필요합니다. 감정 조절과 안정적인 생활 리듬 유지가 중요합니다.`
      : '원진살이 없어 불안정한 기운의 영향이 적습니다.',
  };
}

/**
 * ==========================================
 * 삼재 (三災) 계산
 * ==========================================
 * 12년 주기로 3년간 삼재 기간
 */
const SAM_JAE_TABLE: Record<JiJi, JiJi[]> = {
  // 인오술 삼합: 신유술년이 삼재
  '인': ['신', '유', '술'],
  '오': ['신', '유', '술'],
  '술': ['신', '유', '술'],
  // 사유축 삼합: 해자축년이 삼재
  '사': ['해', '자', '축'],
  '유': ['해', '자', '축'],
  '축': ['해', '자', '축'],
  // 신자진 삼합: 인묘진년이 삼재
  '신': ['인', '묘', '진'],
  '자': ['인', '묘', '진'],
  '진': ['인', '묘', '진'],
  // 해묘미 삼합: 사오미년이 삼재
  '해': ['사', '오', '미'],
  '묘': ['사', '오', '미'],
  '미': ['사', '오', '미'],
};

export function getSamJaeYears(yearJi: JiJi): JiJi[] {
  return SAM_JAE_TABLE[yearJi] || [];
}

export function isSamJaeYear(birthYearJi: JiJi, currentYearJi: JiJi): {
  isSamJae: boolean;
  type: 'entering' | 'staying' | 'leaving' | null;
} {
  const samJaeYears = SAM_JAE_TABLE[birthYearJi];
  if (!samJaeYears) return { isSamJae: false, type: null };

  const index = samJaeYears.indexOf(currentYearJi);
  if (index === -1) return { isSamJae: false, type: null };

  const types: ('entering' | 'staying' | 'leaving')[] = ['entering', 'staying', 'leaving'];
  return { isSamJae: true, type: types[index] };
}

export function analyzeSamJae(
  birthYearJi: JiJi,
  currentYearJi: JiJi,
): SinsalResult {
  const result = isSamJaeYear(birthYearJi, currentYearJi);
  const samJaeYears = SAM_JAE_TABLE[birthYearJi];

  const typeNames = {
    entering: '들삼재 (시작)',
    staying: '눌삼재 (중간, 가장 강함)',
    leaving: '날삼재 (끝)',
  };

  return {
    name: '삼재(三災)',
    type: 'gongMang', // 타입 임시 사용
    present: result.isSamJae,
    description: result.isSamJae
      ? `${typeNames[result.type!]} - 주의 필요`
      : `삼재 기간(${samJaeYears.join(', ')}년)이 아님`,
    effect: result.isSamJae ? 'bad' : 'neutral',
    detailedMeaning: result.isSamJae
      ? `현재 삼재 기간입니다 (${typeNames[result.type!]}). 삼재는 12년 주기로 3년간 지속되며, 예상치 못한 어려움이 생길 수 있습니다. 무리한 투자나 변화는 자제하고, 건강과 안전에 유의하세요. 삼재 기간에는 부적을 지니거나 삼재풀이를 하기도 합니다.`
      : '현재 삼재 기간이 아니므로 삼재의 영향은 없습니다.',
  };
}
