/**
 * 완전한 사주 데이터 계산기
 *
 * 모든 사주 분석 데이터를 한 번에 계산하여 CompleteSajuData 구조로 반환
 * Customer.saju_data에 저장될 데이터를 생성
 *
 * @author Claude Code
 * @version 2.0.0
 * @updated 2026-01-12 - 정확한 절기월 계산 적용, 윤달 파라미터 지원
 */

import type {
  CompleteSajuData,
  CheonGan,
  JiJi,
  OhHaeng,
  Gender,
  SajuPillar,
  FourPillars,
  OhHaengBalance,
  OhHaengAnalysis,
  SipSungBalance,
  SipSungDetail,
  SipSungAnalysis,
  GyeokGukAnalysis,
  YongSinAnalysis,
  DaewoonItem,
  DaewoonAnalysis,
  SewoonItem,
  SinsalAnalysis,
  PillarRelations,
  PersonalityAnalysis,
} from '../types/completeSajuData';
import { getExactSolarMonth } from './solarTermsCalculator';
import { lunarToSolar } from './lunarCalendar';
import { applyTrueSolarTimeByCity } from './trueSolarTimeCalculator';
import { calculateBodyStrength } from '../analysis/bodyStrength';
import { calculateDaeunStartAge } from '../analysis/daewoonAnalysis/daeunStartAge';
import { analyzeYongSinGiSin } from '../analysis/yongSinGiSin';
import { analyzeAllSinsal } from '../analysis/sinsal';
import { determineGeukGuk } from '../analysis/geukGuk';

// ============================================================
// 상수 정의
// ============================================================

const CHEON_GAN: CheonGan[] = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
const JI_JI: JiJi[] = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];

// 60갑자 배열 (일주 계산용)
const SIXTY_CYCLE: string[] = [
  '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유', // 0-9
  '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미', // 10-19
  '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사', // 20-29
  '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘', // 30-39
  '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축', // 40-49
  '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해', // 50-59
];

const CHEON_GAN_OH_HAENG: Record<CheonGan, OhHaeng> = {
  '갑': '목', '을': '목',
  '병': '화', '정': '화',
  '무': '토', '기': '토',
  '경': '금', '신': '금',
  '임': '수', '계': '수',
};

const JI_JI_OH_HAENG: Record<JiJi, OhHaeng> = {
  '인': '목', '묘': '목',
  '사': '화', '오': '화',
  '진': '토', '술': '토', '축': '토', '미': '토',
  '신': '금', '유': '금',
  '해': '수', '자': '수',
};

const JI_JI_ANIMAL: Record<JiJi, string> = {
  '자': '쥐', '축': '소', '인': '호랑이', '묘': '토끼',
  '진': '용', '사': '뱀', '오': '말', '미': '양',
  '신': '원숭이', '유': '닭', '술': '개', '해': '돼지',
};

const JI_JI_SEASON: Record<JiJi, '봄' | '여름' | '가을' | '겨울'> = {
  '인': '봄', '묘': '봄', '진': '봄',
  '사': '여름', '오': '여름', '미': '여름',
  '신': '가을', '유': '가을', '술': '가을',
  '해': '겨울', '자': '겨울', '축': '겨울',
};

// 십성 관계 테이블 (일간 기준)
const TEN_GODS_RELATIONS: Record<CheonGan, Record<CheonGan, keyof SipSungDetail>> = {
  '갑': { '갑': '비견', '을': '겁재', '병': '식신', '정': '상관', '무': '편재', '기': '정재', '경': '편관', '신': '정관', '임': '편인', '계': '정인' },
  '을': { '을': '비견', '갑': '겁재', '정': '식신', '병': '상관', '기': '편재', '무': '정재', '신': '편관', '경': '정관', '계': '편인', '임': '정인' },
  '병': { '병': '비견', '정': '겁재', '무': '식신', '기': '상관', '경': '편재', '신': '정재', '임': '편관', '계': '정관', '갑': '편인', '을': '정인' },
  '정': { '정': '비견', '병': '겁재', '기': '식신', '무': '상관', '신': '편재', '경': '정재', '계': '편관', '임': '정관', '을': '편인', '갑': '정인' },
  '무': { '무': '비견', '기': '겁재', '경': '식신', '신': '상관', '임': '편재', '계': '정재', '갑': '편관', '을': '정관', '병': '편인', '정': '정인' },
  '기': { '기': '비견', '무': '겁재', '신': '식신', '경': '상관', '계': '편재', '임': '정재', '을': '편관', '갑': '정관', '정': '편인', '병': '정인' },
  '경': { '경': '비견', '신': '겁재', '임': '식신', '계': '상관', '갑': '편재', '을': '정재', '병': '편관', '정': '정관', '무': '편인', '기': '정인' },
  '신': { '신': '비견', '경': '겁재', '계': '식신', '임': '상관', '을': '편재', '갑': '정재', '정': '편관', '병': '정관', '기': '편인', '무': '정인' },
  '임': { '임': '비견', '계': '겁재', '갑': '식신', '을': '상관', '병': '편재', '정': '정재', '무': '편관', '기': '정관', '경': '편인', '신': '정인' },
  '계': { '계': '비견', '임': '겁재', '을': '식신', '갑': '상관', '정': '편재', '병': '정재', '기': '편관', '무': '정관', '신': '편인', '경': '정인' },
};

// 장간 (지지에 숨은 천간)
const HIDDEN_STEMS: Record<JiJi, CheonGan[]> = {
  '자': ['계'],
  '축': ['기', '계', '신'],
  '인': ['갑', '병', '무'],
  '묘': ['을'],
  '진': ['무', '을', '계'],
  '사': ['병', '무', '경'],
  '오': ['정', '기'],
  '미': ['기', '정', '을'],
  '신': ['경', '임', '무'],
  '유': ['신'],
  '술': ['무', '신', '정'],
  '해': ['임', '갑'],
};

// 지지 충
const JI_JI_CHUNG: Record<JiJi, JiJi> = {
  '자': '오', '오': '자',
  '축': '미', '미': '축',
  '인': '신', '신': '인',
  '묘': '유', '유': '묘',
  '진': '술', '술': '진',
  '사': '해', '해': '사',
};

// 지지 육합
const JI_JI_YUK_HAP: Record<JiJi, JiJi> = {
  '자': '축', '축': '자',
  '인': '해', '해': '인',
  '묘': '술', '술': '묘',
  '진': '유', '유': '진',
  '사': '신', '신': '사',
  '오': '미', '미': '오',
};

// 천간 합
const CHEON_GAN_HAP: Record<CheonGan, CheonGan> = {
  '갑': '기', '기': '갑',
  '을': '경', '경': '을',
  '병': '신', '신': '병',
  '정': '임', '임': '정',
  '무': '계', '계': '무',
};

// 일간별 성격
const DAY_MASTER_PERSONALITY: Record<CheonGan, { keyword: string; strengths: string[]; weaknesses: string[]; advice: string }> = {
  '갑': { keyword: '큰 나무, 리더', strengths: ['리더십', '추진력', '정의감'], weaknesses: ['고집', '융통성 부족'], advice: '유연함을 기르세요' },
  '을': { keyword: '작은 풀, 적응력', strengths: ['유연함', '적응력', '섬세함'], weaknesses: ['우유부단', '의존적'], advice: '결단력을 키우세요' },
  '병': { keyword: '태양, 열정', strengths: ['낙관적', '사교적', '열정적'], weaknesses: ['성급함', '지속력 부족'], advice: '꾸준함을 기르세요' },
  '정': { keyword: '촛불, 따뜻함', strengths: ['배려심', '섬세함', '집중력'], weaknesses: ['소심함', '걱정 많음'], advice: '자신감을 키우세요' },
  '무': { keyword: '큰 산, 안정', strengths: ['신뢰감', '책임감', '포용력'], weaknesses: ['둔함', '고집'], advice: '변화에 열린 마음을 가지세요' },
  '기': { keyword: '땅, 실용적', strengths: ['실용적', '부드러움', '현실감각'], weaknesses: ['걱정 많음', '소극적'], advice: '적극성을 키우세요' },
  '경': { keyword: '강철, 결단력', strengths: ['결단력', '정직함', '실행력'], weaknesses: ['무뚝뚝함', '융통성 부족'], advice: '부드러움을 기르세요' },
  '신': { keyword: '보석, 완벽주의', strengths: ['꼼꼼함', '예리함', '미적 감각'], weaknesses: ['예민함', '비판적'], advice: '관대함을 기르세요' },
  '임': { keyword: '큰 바다, 지혜', strengths: ['지혜로움', '포용력', '창의성'], weaknesses: ['게으름', '우울함'], advice: '실행력을 키우세요' },
  '계': { keyword: '비/이슬, 직관', strengths: ['직관력', '감성', '적응력'], weaknesses: ['변덕', '감정기복'], advice: '안정감을 기르세요' },
};

// ============================================================
// 입력 타입
// ============================================================

export interface SajuCalculationInput {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
  gender: Gender;
  isLunar?: boolean;
  isLeapMonth?: boolean; // 윤달 여부 (음력일 때만)
  useTrueSolarTime?: boolean; // 진태양시 보정 적용 여부
  birthPlace?: string; // 출생 지역 (기본값: '서울')
}

// ============================================================
// 메인 계산 함수
// ============================================================

export function calculateCompleteSajuData(input: SajuCalculationInput): CompleteSajuData {
  const { year, month, day, hour, minute = 0, gender, isLunar = false, isLeapMonth = false, useTrueSolarTime = true, birthPlace = '서울' } = input;

  // 1. 사주 팔자 계산
  const fourPillars = calculateFourPillars(year, month, day, hour, minute, isLunar, isLeapMonth, useTrueSolarTime, birthPlace);

  // 2. 오행 분석
  const ohHaeng = analyzeOhHaeng(fourPillars);

  // 3. 십성 분석
  const sipSung = analyzeSipSung(fourPillars);

  // 4. 격국 분석
  const gyeokGuk = analyzeGyeokGuk(fourPillars, ohHaeng);

  // 5. 용신/기신 분석
  const yongSin = analyzeYongSin(gyeokGuk, ohHaeng, fourPillars);

  // 6. 대운 계산
  const currentAge = new Date().getFullYear() - year;
  const daewoon = calculateDaewoon(fourPillars, year, month, day, hour, minute, gender, yongSin, currentAge);

  // 7. 세운 계산 (올해/내년)
  const currentYear = new Date().getFullYear();
  const currentYearSewoon = calculateSewoon(currentYear, currentAge, fourPillars, yongSin, daewoon);
  const nextYearSewoon = calculateSewoon(currentYear + 1, currentAge + 1, fourPillars, yongSin, daewoon);

  // 8. 신살 분석
  const sinsal = analyzeSinsal(fourPillars);

  // 9. 관계 분석
  const relations = analyzeRelations(fourPillars);

  // 10. 성격/적성 분석
  const personality = analyzePersonality(fourPillars, sipSung);

  // 11. 레거시 호환 필드 생성
  const legacyFields = createLegacyFields(fourPillars, ohHaeng, sipSung);

  return {
    version: '1.0.0',
    calculatedAt: new Date().toISOString(),
    isComplete: true,

    birthInfo: {
      year, month, day, hour, minute, gender, isLunar,
      birthDateString: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`,
      birthTimeString: `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`,
    },

    fourPillars,
    fullSajuString: `${fourPillars.year.ganJi} ${fourPillars.month.ganJi} ${fourPillars.day.ganJi} ${fourPillars.time.ganJi}`,

    ohHaeng,
    sipSung,
    gyeokGuk,
    yongSin,
    daewoon,
    currentYearSewoon,
    nextYearSewoon,
    sinsal,
    relations,
    personality,

    ...legacyFields,
  };
}

// ============================================================
// 사주 팔자 계산
// ============================================================

function calculateFourPillars(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
  isLunar: boolean,
  isLeapMonth: boolean,
  useTrueSolarTime: boolean,
  birthPlace: string,
): FourPillars {
  // 음력 → 양력 변환 (윤달 지원)
  let solarYear = year;
  let solarMonth = month;
  let solarDay = day;

  if (isLunar) {
    const solarDate = lunarToSolar(year, month, day, isLeapMonth);
    solarYear = solarDate.getFullYear();
    solarMonth = solarDate.getMonth() + 1;
    solarDay = solarDate.getDate();
  }

  // 진태양시 보정 (시주 계산용)
  let adjustedHour = hour;
  let _adjustedMinute = minute;

  if (useTrueSolarTime) {
    const trueSolarResult = applyTrueSolarTimeByCity(hour, minute, birthPlace);
    adjustedHour = trueSolarResult.adjustedHour;
    _adjustedMinute = trueSolarResult.adjustedMinute;
  }

  // 절기월 계산 (정확한 시분 고려) ⭐ 핵심 개선!
  // 년주와 월주 모두에서 사용하므로 먼저 계산
  const solarMonthIndex = getExactSolarMonth(solarYear, solarMonth, solarDay, hour, minute);

  // 년주 계산 - 입춘(立春) 기준 적용
  // 입춘은 매년 2/3~2/5 사이에 변동하므로, getExactSolarMonth 결과를 사용하여 정확히 판단
  // solarMonthIndex가 12(축월)이면 아직 입춘 전이므로 전년도 간지 사용
  // 1월은 항상 입춘 전(축월 또는 자월)이므로 전년도
  let adjustedYear = solarYear;
  if (solarMonth <= 2 && solarMonthIndex === 12) {
    // 1월 전체 또는 2월 입춘 이전 → 축월(12)이므로 전년도 간지 사용
    adjustedYear -= 1;
  } else if (solarMonth === 1 && solarMonthIndex === 11) {
    // 1월 초(소한 이전) → 자월(11)이므로 역시 전년도 간지 사용
    adjustedYear -= 1;
  }
  const yearGanIndex = ((adjustedYear - 4) % 10 + 10) % 10;
  const yearJiIndex = ((adjustedYear - 4) % 12 + 12) % 12;
  const yearGan = CHEON_GAN[yearGanIndex];
  const yearJi = JI_JI[yearJiIndex];

  // 월주 계산 (절기월 기준)
  // solarMonthIndex: 1=인월, 2=묘월, ..., 12=축월
  // JI_JI 배열: [0]=자, [1]=축, [2]=인, [3]=묘, ...
  const monthJiIndex = (solarMonthIndex + 1) % 12; // 인월(1) → JI_JI[2], 축월(12) → JI_JI[1]
  const monthJi = JI_JI[monthJiIndex];

  // 년간에 따른 월간 결정 (오호십이법/五虎遁月法)
  // 甲己年: 丙寅始(2), 乙庚年: 戊寅始(4), 丙辛年: 庚寅始(6), 丁壬年: 壬寅始(8), 戊癸年: 甲寅始(0)
  const monthGanBase = ((yearGanIndex % 5) * 2 + 2) % 10;
  const monthGanIndex = (monthGanBase + solarMonthIndex - 1) % 10;
  const monthGan = CHEON_GAN[monthGanIndex];

  // 일주 계산 (1900년 1월 1일 = 갑술일, 60갑자 index 10)
  // 검증: 1971-11-17 → (10 + 26252) % 60 = 42 → SIXTY_CYCLE[42] = 병오 ✓
  const baseDate = Date.UTC(1900, 0, 1);
  const targetDate = Date.UTC(solarYear, solarMonth - 1, solarDay);
  const diffDays = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24));
  let dayCycleIndex = (10 + diffDays) % 60;
  if (dayCycleIndex < 0) dayCycleIndex += 60;
  const dayGanJi = SIXTY_CYCLE[dayCycleIndex];
  const dayGan = dayGanJi[0] as CheonGan;
  const dayJi = dayGanJi[1] as JiJi;
  const dayGanIndex = dayCycleIndex % 10; // 시주 계산용

  // 시주 계산 (진태양시 보정된 시간 사용)
  const timeJiIndex = Math.floor((adjustedHour + 1) / 2) % 12;
  const timeJi = JI_JI[timeJiIndex];
  const timeGanBase = (dayGanIndex % 5) * 2;
  const timeGanIndex = (timeGanBase + timeJiIndex) % 10;
  const timeGan = CHEON_GAN[timeGanIndex];

  return {
    year: createPillar(yearGan, yearJi),
    month: createPillar(monthGan, monthJi),
    day: createPillar(dayGan, dayJi),
    time: createPillar(timeGan, timeJi),
  };
}

function createPillar(gan: CheonGan, ji: JiJi): SajuPillar {
  return {
    gan,
    ji,
    ganJi: `${gan}${ji}`,
    ganOhHaeng: CHEON_GAN_OH_HAENG[gan],
    jiOhHaeng: JI_JI_OH_HAENG[ji],
  };
}

// ============================================================
// 오행 분석
// ============================================================

function analyzeOhHaeng(fourPillars: FourPillars): OhHaengAnalysis {
  const balance: OhHaengBalance = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 };

  // 각 기둥의 천간/지지 오행 점수 부여
  const pillars = [fourPillars.year, fourPillars.month, fourPillars.day, fourPillars.time];
  const weights = [15, 15, 20, 15]; // 일주 가중치 높게

  pillars.forEach((pillar, index) => {
    balance[pillar.ganOhHaeng] += weights[index];
    balance[pillar.jiOhHaeng] += weights[index] - 5;

    // 장간 추가
    const hiddenStems = HIDDEN_STEMS[pillar.ji];
    hiddenStems.forEach(stem => {
      balance[CHEON_GAN_OH_HAENG[stem]] += 5;
    });
  });

  // 정규화 (100점 만점)
  const total = Object.values(balance).reduce((sum, v) => sum + v, 0);
  const normalized: OhHaengBalance = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 };
  for (const key of Object.keys(balance) as OhHaeng[]) {
    normalized[key] = Math.round((balance[key] / total) * 100);
  }

  // 가장 강한/약한 오행 찾기
  const entries = Object.entries(normalized) as [OhHaeng, number][];
  const sorted = entries.sort((a, b) => b[1] - a[1]);
  const dominant = sorted[0][0];
  const weak = sorted[sorted.length - 1][0];

  return {
    balance: normalized,
    dominant,
    weak,
    dominantScore: sorted[0][1],
    weakScore: sorted[sorted.length - 1][1],
    isBalanced: sorted[0][1] - sorted[sorted.length - 1][1] < 15,
  };
}

// ============================================================
// 십성 분석
// ============================================================

function analyzeSipSung(fourPillars: FourPillars): SipSungAnalysis {
  const dayGan = fourPillars.day.gan;
  const detail: SipSungDetail = {
    비견: 0, 겁재: 0, 식신: 0, 상관: 0,
    정재: 0, 편재: 0, 정관: 0, 편관: 0,
    정인: 0, 편인: 0,
  };

  // 각 기둥의 천간과 장간 분석
  const pillars = [fourPillars.year, fourPillars.month, fourPillars.day, fourPillars.time];

  pillars.forEach((pillar, index) => {
    const weight = index === 2 ? 15 : 10; // 일주 가중치

    // 천간 십성
    const ganRelation = TEN_GODS_RELATIONS[dayGan][pillar.gan];
    detail[ganRelation] += weight;

    // 장간 십성
    const hiddenStems = HIDDEN_STEMS[pillar.ji];
    hiddenStems.forEach(stem => {
      const hiddenRelation = TEN_GODS_RELATIONS[dayGan][stem];
      detail[hiddenRelation] += 5;
    });
  });

  // 그룹별 합계
  const balance: SipSungBalance = {
    비겁: detail.비견 + detail.겁재,
    식상: detail.식신 + detail.상관,
    재성: detail.정재 + detail.편재,
    관성: detail.정관 + detail.편관,
    인성: detail.정인 + detail.편인,
  };

  // 가장 강한/약한 십성 그룹
  const entries = Object.entries(balance) as [keyof SipSungBalance, number][];
  const sorted = entries.sort((a, b) => b[1] - a[1]);

  return {
    balance,
    detail,
    dominant: sorted[0][0],
    weak: sorted[sorted.length - 1][0],
  };
}

// ============================================================
// 격국 분석
// ============================================================

function analyzeGyeokGuk(fourPillars: FourPillars, _ohHaeng: OhHaengAnalysis): GyeokGukAnalysis {
  const dayMaster = fourPillars.day.gan;
  const dayMasterOhHaeng = CHEON_GAN_OH_HAENG[dayMaster];
  const monthBranch = fourPillars.month.ji;
  const season = JI_JI_SEASON[monthBranch];

  // Calculate body strength using precision module (already integrated)
  const bodyStrengthInput = {
    dayGan: dayMaster,
    monthJi: monthBranch,
    fourPillarGan: [fourPillars.year.gan, fourPillars.month.gan, fourPillars.day.gan, fourPillars.time.gan],
    fourPillarJi: [fourPillars.year.ji, fourPillars.month.ji, fourPillars.day.ji, fourPillars.time.ji],
  };
  const bodyResult = calculateBodyStrength(bodyStrengthInput);

  // Map 5-grade to 3-grade for backward compatibility
  let strength: '신강' | '신약' | '중화';
  if (bodyResult.grade === '극신강' || bodyResult.grade === '신강') {
    strength = '신강';
  } else if (bodyResult.grade === '극신약' || bodyResult.grade === '신약') {
    strength = '신약';
  } else {
    strength = '중화';
  }

  // Use precision module for detailed geukguk determination
  const geukGukResult = determineGeukGuk({
    dayGan: dayMaster,
    monthJi: monthBranch,
    fourPillarGan: bodyStrengthInput.fourPillarGan,
    fourPillarJi: bodyStrengthInput.fourPillarJi,
  });

  // Extract geukguk type (use specific type from precision module)
  const gyeokGukType = geukGukResult.geukguk;

  // Generate description using precision module's explanation
  const strengthDescription = `일간이 ${strength === '신강' ? '강하므로' : strength === '신약' ? '약하므로' : '균형잡혀 있으므로'}`;
  const geukGukDescription = geukGukResult.description || '';
  const description = `${strengthDescription} ${geukGukDescription}`;

  return {
    dayMaster,
    dayMasterOhHaeng,
    strength,
    monthBranch,
    season,
    gyeokGukType,  // Now returns specific 격국 type (e.g., "편인격", "종재격")
    description,
    // Optional fields from bodyStrength module
    strengthDetail: bodyResult.grade,
    strengthScore: bodyResult.score,
    strengthGrade: bodyResult.grade,
  };
}

// ============================================================
// 용신/기신 분석
// ============================================================

function analyzeYongSin(
  gyeokGuk: GyeokGukAnalysis,
  _ohHaeng: OhHaengAnalysis,
  fourPillars: FourPillars,
): YongSinAnalysis {
  const dayGan = fourPillars.day.gan;
  const monthJi = fourPillars.month.ji;

  // Use precision module for comprehensive yongsin analysis
  const precisionResult = analyzeYongSinGiSin({
    dayGan,
    monthJi,
    bodyStrength: (gyeokGuk.strengthDetail || gyeokGuk.strength) as any,
    fourPillars: {
      year: { gan: fourPillars.year.gan, ji: fourPillars.year.ji },
      month: { gan: fourPillars.month.gan, ji: fourPillars.month.ji },
      day: { gan: fourPillars.day.gan, ji: fourPillars.day.ji },
      time: { gan: fourPillars.time.gan, ji: fourPillars.time.ji },
    },
  });

  // Convert to YongSinAnalysis format
  const yongSin = precisionResult.yongSin.primary;
  const giSin = precisionResult.giSin.primary;
  const huiSin = precisionResult.johu.yongSin || []; // 조후용신을 희신으로 매핑

  // Generate descriptions with johu and mediating info
  let yongSinReason = `용신은 ${yongSin.join(', ')}입니다.`;
  if (precisionResult.johu.necessity === '높음') {
    yongSinReason += ` ${precisionResult.johu.reason}`;
  }
  if (precisionResult.mediating) {
    yongSinReason += ` ${precisionResult.mediating.reason}`;
  }

  const giSinReason = giSin.length > 0
    ? `기신은 ${giSin.join(', ')}이므로 주의가 필요합니다.`
    : '특별한 기신은 없습니다.';

  // Create yongSinScore mapping (merge all beneficial elements)
  const yongSinScore: Record<OhHaeng, number> = { 목: 50, 화: 50, 토: 50, 금: 50, 수: 50 };

  // Primary yongsin gets highest score
  yongSin.forEach(oh => { yongSinScore[oh] = 80; });

  // Johu yongsin gets high score (slightly lower if different from primary)
  huiSin.forEach(oh => {
    if (!yongSin.includes(oh)) {
      yongSinScore[oh] = 70;
    }
  });

  // Mediating yongsin gets moderate score
  if (precisionResult.mediating) {
    precisionResult.mediating.yongSin.forEach(oh => {
      if (!yongSin.includes(oh) && !huiSin.includes(oh)) {
        yongSinScore[oh] = 65;
      }
    });
  }

  // Gisin gets low score
  giSin.forEach(oh => { yongSinScore[oh] = 30; });

  return {
    yongSin,
    giSin,
    huiSin,
    yongSinReason,
    giSinReason,
    yongSinScore,
  };
}

// ============================================================
// 대운 계산
// ============================================================

function calculateDaewoon(
  fourPillars: FourPillars,
  birthYear: number,
  birthMonth: number,
  birthDay: number,
  birthHour: number,
  birthMinute: number,
  gender: Gender,
  yongSin: YongSinAnalysis,
  currentAge: number,
): DaewoonAnalysis {
  // 년간 확인 (사주 4기둥의 년간 사용 - 입춘 기준)
  const actualYearGan = fourPillars.year.gan;

  // 양간/음간 판단
  const isYangYear = ['갑', '병', '무', '경', '임'].includes(actualYearGan);

  // 순행 여부
  const isForward = (gender === 'male' && isYangYear) || (gender === 'female' && !isYangYear);
  const direction: '순행' | '역행' = isForward ? '순행' : '역행';

  // 대운 시작 나이 (정밀 계산)
  const birthDate = new Date(birthYear, birthMonth - 1, birthDay);
  const birthTime = `${String(birthHour).padStart(2, '0')}:${String(birthMinute).padStart(2, '0')}`;
  const daeunResult = calculateDaeunStartAge({
    birthDate,
    birthTime,
    gender,
    yearGan: fourPillars.year.gan as any,
  });
  const startAge = daeunResult.startAge;

  // 월주 기준으로 대운 생성
  const monthGanIndex = CHEON_GAN.indexOf(fourPillars.month.gan);
  const monthJiIndex = JI_JI.indexOf(fourPillars.month.ji);

  const list: DaewoonItem[] = [];

  for (let i = 0; i < 10; i++) {
    let ganIndex: number;
    let jiIndex: number;

    if (isForward) {
      ganIndex = (monthGanIndex + i + 1) % 10;
      jiIndex = (monthJiIndex + i + 1) % 12;
    } else {
      ganIndex = (monthGanIndex - i - 1 + 10) % 10;
      jiIndex = (monthJiIndex - i - 1 + 12) % 12;
    }

    const gan = CHEON_GAN[ganIndex];
    const ji = JI_JI[jiIndex];
    const ohHaeng = CHEON_GAN_OH_HAENG[gan];
    const jiOhHaeng = JI_JI_OH_HAENG[ji];

    const isYongSin = yongSin.yongSin.includes(ohHaeng);
    const isGiSin = yongSin.giSin.includes(ohHaeng);

    // 점수 계산
    let score = 50;
    if (isYongSin) score += 30;
    if (isGiSin) score -= 20;
    if (yongSin.huiSin.includes(ohHaeng)) score += 15;
    score = Math.max(20, Math.min(95, score));

    // 설명 생성
    let description = '';
    if (isYongSin) {
      description = `용신 대운! ${ohHaeng} 기운이 도와줍니다.`;
    } else if (isGiSin) {
      description = `기신 대운. ${ohHaeng} 기운에 주의하세요.`;
    } else {
      description = `${ohHaeng} 기운의 평범한 대운입니다.`;
    }

    list.push({
      cycle: i + 1,
      startAge: startAge + i * 10,
      endAge: startAge + (i + 1) * 10 - 1,
      gan,
      ji,
      ganJi: `${gan}${ji}`,
      ohHaeng,
      jiOhHaeng,
      score,
      description,
      isYongSin,
      isGiSin,
    });
  }

  // 현재 대운 찾기
  const current = list.find(d => currentAge >= d.startAge && currentAge <= d.endAge) || null;

  // 최고/최악 대운
  const sorted = [...list].sort((a, b) => b.score - a.score);
  const bestPeriod = sorted[0];
  const worstPeriod = sorted[sorted.length - 1];

  return {
    startAge,
    direction,
    list,
    current,
    currentAge,
    bestPeriod,
    worstPeriod,
  };
}

// calculateDaewoonStartAge 함수는 정밀 계산 모듈로 대체됨
// (saju/daewoonAnalysis/daeunStartAge.ts의 calculateDaeunStartAge 사용)

// ============================================================
// 세운 계산
// ============================================================

function calculateSewoon(
  year: number,
  age: number,
  fourPillars: FourPillars,
  yongSin: YongSinAnalysis,
  daewoon: DaewoonAnalysis,
): SewoonItem {
  const ganIndex = ((year - 4) % 10 + 10) % 10;
  const jiIndex = ((year - 4) % 12 + 12) % 12;
  const gan = CHEON_GAN[ganIndex];
  const ji = JI_JI[jiIndex];
  const ohHaeng = CHEON_GAN_OH_HAENG[gan];
  const animal = JI_JI_ANIMAL[ji];

  const isYongSin = yongSin.yongSin.includes(ohHaeng);
  const isGiSin = yongSin.giSin.includes(ohHaeng);

  // 점수 계산
  let score = 50;
  if (isYongSin) score += 25;
  if (isGiSin) score -= 15;
  if (yongSin.huiSin.includes(ohHaeng)) score += 10;

  // 대운과의 상호작용
  let daewoonInteraction = 0;
  const currentDaewoon = daewoon.list.find(d => age >= d.startAge && age <= d.endAge);
  if (currentDaewoon) {
    if (currentDaewoon.gan === gan) daewoonInteraction += 15;
    if (JI_JI_YUK_HAP[currentDaewoon.ji] === ji) daewoonInteraction += 10;
    if (JI_JI_CHUNG[currentDaewoon.ji] === ji) daewoonInteraction -= 20;
  }

  score += daewoonInteraction;
  score = Math.max(20, Math.min(95, score));

  // 설명
  let description = `${year}년은 ${gan}${ji}년(${animal}띠 해)입니다. `;
  if (isYongSin) {
    description += `용신 오행(${ohHaeng})이 작용하여 유리한 해입니다.`;
  } else if (isGiSin) {
    description += `기신 오행(${ohHaeng})이 작용하여 주의가 필요한 해입니다.`;
  } else {
    description += `${ohHaeng} 기운이 작용하는 평범한 해입니다.`;
  }

  return {
    year,
    age,
    gan,
    ji,
    ganJi: `${gan}${ji}`,
    ohHaeng,
    animal,
    score,
    description,
    isYongSin,
    daewoonInteraction,
  };
}

// ============================================================
// 신살 분석
// ============================================================

function analyzeSinsal(fourPillars: FourPillars): SinsalAnalysis {
  const dayGan = fourPillars.day.gan;
  const yearJi = fourPillars.year.ji;
  const monthJi = fourPillars.month.ji;
  const dayJi = fourPillars.day.ji;
  const hourJi = fourPillars.time.ji;  // FIX: fourPillars uses 'time' not 'hour'

  // Use precision module for comprehensive sinsal analysis
  const precisionResult = analyzeAllSinsal({
    year: { gan: fourPillars.year.gan, ji: yearJi },
    month: { gan: fourPillars.month.gan, ji: monthJi },
    day: { gan: dayGan, ji: dayJi },
    time: { gan: fourPillars.time.gan, ji: hourJi },  // FIX: fourPillars uses 'time' not 'hour'
  });

  // Convert to SinsalAnalysis format
  const gilSin: string[] = [];
  const hyungSin: string[] = [];

  // Categorize sinsal into beneficial (gilSin) and harmful (hyungSin)
  const beneficialSinsal = ['천을귀인', '문창귀인', '천덕귀인', '월덕귀인', '장성', '화개'];
  const harmfulSinsal = ['역마살', '도화살', '양인살', '겁살', '공망', '귀문관살', '원진살', '백호살', '홍염살', '현침살', '삼재'];

  // Add from good/bad sinsal lists
  gilSin.push(...precisionResult.goodSinsal);
  hyungSin.push(...precisionResult.badSinsal);

  // Extract individual sinsal flags
  const hasCheonEulGuiIn = precisionResult.cheonEulGwiIn?.present || false;
  const hasMunChangGuiIn = precisionResult.twelveSinsalByYear.some(s =>
    s.name.includes('문창') && s.present
  ) || precisionResult.twelveSinsalByDay.some(s =>
    s.name.includes('문창') && s.present
  );
  const hasYeokMaSal = precisionResult.twelveSinsalByYear.some(s =>
    s.type === 'yeokMaSal' && s.present
  );
  const hasDoHwaSal = precisionResult.twelveSinsalByYear.some(s =>
    s.type === 'nyeonSal' && s.present
  );
  const hasYangInSal = precisionResult.yangInSal?.present || false;
  const hasGeopSal = precisionResult.twelveSinsalByYear.some(s =>
    s.type === 'geobSal' && s.present
  );

  // Extract gongmang status from precision result (FIX CRITICAL BUG)
  const hasGongMang = precisionResult.gongMang?.present || false;

  // Generate description from precision module's summary
  const summary = precisionResult.summaryText || '신살 분석이 완료되었습니다.';

  return {
    gilSin,
    hyungSin,
    hasCheonEulGuiIn,
    hasMunChangGuiIn,
    hasYeokMaSal,
    hasDoHwaSal,
    hasYangInSal,
    hasGeopSal,
    hasGongMang,  // Now uses actual precision calculation instead of hardcoded false
    hasGoeGangSal: false,  // TODO: Implement in future
    summary,
  };
}


// ============================================================
// 관계 분석
// ============================================================

function analyzeRelations(fourPillars: FourPillars): PillarRelations {
  const cheonganHap: string[] = [];
  const cheonganChung: string[] = [];
  const jijiYukHap: string[] = [];
  const jijiChung: string[] = [];
  const jijiSamHap: string[] = [];
  const jijiBanHap: string[] = [];
  const jijiHyung: string[] = [];
  const jijiPa: string[] = [];
  const jijiHae: string[] = [];

  const pillars = [
    { name: '년', pillar: fourPillars.year },
    { name: '월', pillar: fourPillars.month },
    { name: '일', pillar: fourPillars.day },
    { name: '시', pillar: fourPillars.time },
  ];

  const jijis: JiJi[] = pillars.map(p => p.pillar.ji);

  // 천간합/충 체크
  for (let i = 0; i < pillars.length; i++) {
    for (let j = i + 1; j < pillars.length; j++) {
      const gan1 = pillars[i].pillar.gan;
      const gan2 = pillars[j].pillar.gan;

      if (CHEON_GAN_HAP[gan1] === gan2) {
        cheonganHap.push(`${pillars[i].name}${pillars[j].name} ${gan1}${gan2}합`);
      }
    }
  }

  // 지지 육합/충 체크
  for (let i = 0; i < pillars.length; i++) {
    for (let j = i + 1; j < pillars.length; j++) {
      const ji1 = pillars[i].pillar.ji;
      const ji2 = pillars[j].pillar.ji;

      if (JI_JI_YUK_HAP[ji1] === ji2) {
        jijiYukHap.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}합`);
      }

      if (JI_JI_CHUNG[ji1] === ji2) {
        jijiChung.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}충`);
      }
    }
  }

  // ============================================================
  // 삼합(三合) 체크
  // ============================================================
  // 삼합 그룹: [첫째, 둘째, 셋째, 국명]
  const SAMHAP_GROUPS: [JiJi, JiJi, JiJi, string][] = [
    ['해', '묘', '미', '목국'],  // 해묘미 삼합 목국
    ['인', '오', '술', '화국'],  // 인오술 삼합 화국
    ['사', '유', '축', '금국'],  // 사유축 삼합 금국
    ['신', '자', '진', '수국'],  // 신자진 삼합 수국
  ];

  for (const [a, b, c, guk] of SAMHAP_GROUPS) {
    const hasA = jijis.includes(a);
    const hasB = jijis.includes(b);
    const hasC = jijis.includes(c);

    if (hasA && hasB && hasC) {
      // 완전삼합 (3개 모두 존재)
      jijiSamHap.push(`${a}${b}${c} 삼합 (${guk})`);
    } else {
      // 반합 (2개만 존재) - 모든 2개 조합 체크
      if (hasA && hasB) {
        jijiBanHap.push(`${a}${b} 반합 (${guk})`);
      }
      if (hasA && hasC) {
        jijiBanHap.push(`${a}${c} 반합 (${guk})`);
      }
      if (hasB && hasC) {
        jijiBanHap.push(`${b}${c} 반합 (${guk})`);
      }
    }
  }

  // ============================================================
  // 형(刑) 체크
  // ============================================================

  // 무례지형: 자↔묘
  const MURYE_HYUNG: [JiJi, JiJi][] = [['자', '묘']];

  // 무은지형 (삼형살): 인↔사, 사↔신, 인↔신
  const MUEUN_HYUNG: [JiJi, JiJi][] = [['인', '사'], ['사', '신'], ['인', '신']];

  // 지세지형 (삼형살): 축↔술, 술↔미, 축↔미
  const JISE_HYUNG: [JiJi, JiJi][] = [['축', '술'], ['술', '미'], ['축', '미']];

  // 자형(自刑): 같은 지지 2개
  const JAHYUNG: JiJi[] = ['진', '오', '유', '해'];

  // 무례지형 체크
  for (const [a, b] of MURYE_HYUNG) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        const ji1 = pillars[i].pillar.ji;
        const ji2 = pillars[j].pillar.ji;
        if ((ji1 === a && ji2 === b) || (ji1 === b && ji2 === a)) {
          jijiHyung.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}형 (무례지형)`);
        }
      }
    }
  }

  // 무은지형 체크
  for (const [a, b] of MUEUN_HYUNG) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        const ji1 = pillars[i].pillar.ji;
        const ji2 = pillars[j].pillar.ji;
        if ((ji1 === a && ji2 === b) || (ji1 === b && ji2 === a)) {
          jijiHyung.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}형 (무은지형)`);
        }
      }
    }
  }

  // 지세지형 체크
  for (const [a, b] of JISE_HYUNG) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        const ji1 = pillars[i].pillar.ji;
        const ji2 = pillars[j].pillar.ji;
        if ((ji1 === a && ji2 === b) || (ji1 === b && ji2 === a)) {
          jijiHyung.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}형 (지세지형)`);
        }
      }
    }
  }

  // 자형 체크 (같은 지지가 2개 이상)
  for (const jaJi of JAHYUNG) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        if (pillars[i].pillar.ji === jaJi && pillars[j].pillar.ji === jaJi) {
          jijiHyung.push(`${pillars[i].name}${pillars[j].name} ${jaJi}${jaJi}형 (자형)`);
        }
      }
    }
  }

  // ============================================================
  // 파(破) 체크
  // ============================================================
  const PA_PAIRS: [JiJi, JiJi][] = [
    ['자', '유'],  // 자유파
    ['오', '묘'],  // 오묘파
    ['축', '진'],  // 축진파
    ['인', '해'],  // 인해파
    ['사', '신'],  // 사신파
    ['술', '미'],  // 술미파
  ];

  for (const [a, b] of PA_PAIRS) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        const ji1 = pillars[i].pillar.ji;
        const ji2 = pillars[j].pillar.ji;
        if ((ji1 === a && ji2 === b) || (ji1 === b && ji2 === a)) {
          jijiPa.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}파`);
        }
      }
    }
  }

  // ============================================================
  // 해(害) 체크
  // ============================================================
  const HAE_PAIRS: [JiJi, JiJi][] = [
    ['자', '미'],  // 자미해
    ['축', '오'],  // 축오해
    ['인', '사'],  // 인사해
    ['묘', '진'],  // 묘진해
    ['신', '해'],  // 신해해
    ['유', '술'],  // 유술해
  ];

  for (const [a, b] of HAE_PAIRS) {
    for (let i = 0; i < pillars.length; i++) {
      for (let j = i + 1; j < pillars.length; j++) {
        const ji1 = pillars[i].pillar.ji;
        const ji2 = pillars[j].pillar.ji;
        if ((ji1 === a && ji2 === b) || (ji1 === b && ji2 === a)) {
          jijiHae.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}해`);
        }
      }
    }
  }

  // 요약 생성
  const summaryParts: string[] = [];
  if (cheonganHap.length > 0) summaryParts.push(`천간합: ${cheonganHap.length}개`);
  if (jijiYukHap.length > 0) summaryParts.push(`지지육합: ${jijiYukHap.length}개`);
  if (jijiSamHap.length > 0) summaryParts.push(`지지삼합: ${jijiSamHap.length}개`);
  if (jijiBanHap.length > 0) summaryParts.push(`지지반합: ${jijiBanHap.length}개`);
  if (jijiChung.length > 0) summaryParts.push(`지지충: ${jijiChung.length}개`);
  if (jijiHyung.length > 0) summaryParts.push(`지지형: ${jijiHyung.length}개`);
  if (jijiPa.length > 0) summaryParts.push(`지지파: ${jijiPa.length}개`);
  if (jijiHae.length > 0) summaryParts.push(`지지해: ${jijiHae.length}개`);

  return {
    cheonganHap,
    cheonganChung,
    jijiYukHap,
    jijiSamHap,
    jijiChung,
    jijiHyung,
    jijiBan: jijiBanHap,
    jijiPa,
    jijiHae,
    summary: summaryParts.length > 0 ? summaryParts.join(', ') : '특별한 합충 관계 없음',
  };
}

// ============================================================
// 성격/적성 분석
// ============================================================

function analyzePersonality(fourPillars: FourPillars, sipSung: SipSungAnalysis): PersonalityAnalysis {
  const dayMaster = fourPillars.day.gan;
  const dayMasterTraits = DAY_MASTER_PERSONALITY[dayMaster];

  const dominantSipsung = sipSung.dominant;
  const sipsungTraits: Record<keyof SipSungBalance, string[]> = {
    비겁: ['독립심', '경쟁심', '자존심'],
    식상: ['창의성', '표현력', '자유로움'],
    재성: ['실용성', '현실감각', '재물관리'],
    관성: ['책임감', '조직력', '명예심'],
    인성: ['학습능력', '사고력', '자기계발'],
  };

  const careerByDominant: Record<keyof SipSungBalance, string[]> = {
    비겁: ['개인사업', '스포츠', '영업'],
    식상: ['예술가', '작가', '강사'],
    재성: ['금융', '무역', '자영업'],
    관성: ['공무원', '관리자', '법조계'],
    인성: ['학자', '교육자', '연구원'],
  };

  return {
    dayMasterTraits,
    dominantSipsung: {
      type: dominantSipsung,
      traits: sipsungTraits[dominantSipsung],
    },
    careerAptitude: careerByDominant[dominantSipsung],
    relationshipStyle: getRelationshipStyle(dayMaster, sipSung),
  };
}

function getRelationshipStyle(dayMaster: CheonGan, sipSung: SipSungAnalysis): string {
  const dominant = sipSung.dominant;
  const styles: Record<keyof SipSungBalance, string> = {
    비겁: '독립적이고 주도적인 관계를 선호합니다.',
    식상: '자유롭고 창의적인 소통을 즐깁니다.',
    재성: '실용적이고 현실적인 관계를 추구합니다.',
    관성: '책임감 있고 안정적인 관계를 중시합니다.',
    인성: '깊이 있고 지적인 교류를 선호합니다.',
  };
  return styles[dominant];
}

// ============================================================
// 레거시 호환 필드 생성
// ============================================================

function createLegacyFields(fourPillars: FourPillars, ohHaeng: OhHaengAnalysis, sipSung: SipSungAnalysis) {
  return {
    year: { gan: fourPillars.year.gan, ji: fourPillars.year.ji },
    month: { gan: fourPillars.month.gan, ji: fourPillars.month.ji },
    day: { gan: fourPillars.day.gan, ji: fourPillars.day.ji },
    time: { gan: fourPillars.time.gan, ji: fourPillars.time.ji },
    ohHaengBalance: ohHaeng.balance,
    sipSungBalance: sipSung.balance,
    fullSaju: `${fourPillars.year.ganJi} ${fourPillars.month.ganJi} ${fourPillars.day.ganJi} ${fourPillars.time.ganJi}`,
    tenGods: sipSung.detail,
    fiveElements: {
      wood: ohHaeng.balance.목,
      fire: ohHaeng.balance.화,
      earth: ohHaeng.balance.토,
      metal: ohHaeng.balance.금,
      water: ohHaeng.balance.수,
    },
  };
}

// ============================================================
// Export
// ============================================================

export { calculateFourPillars, analyzeOhHaeng, analyzeSipSung, analyzeGyeokGuk, analyzeYongSin };
