/**
 * 기문둔갑(奇門遁甲) 완전 구현 모듈
 * 
 * 8문(八門), 9궁(九宮), 9성(九星), 8신(八神) 완전 계산
 * 천반(天盤), 지반(地盤), 인반(人盤), 신반(神盤) 4층 구조
 */

import { CheonGan, JiJi } from '../core/types';

// ============================================================
// 타입 정의
// ============================================================

/**
 * 기문둔갑 궁(宮) 정보
 */
export interface QimenPalace {
  palaceNum: number;          // 궁 번호 (1-9)
  directionKo: string;        // 한국어 방위
  directionEn: string;        // 영문 코드
  gate: string;               // 8문
  star: string;               // 9성
  deity: string;              // 8신
  earthlyPlateGan: CheonGan;  // 지반 천간
  heavenlyPlateGan: CheonGan; // 천반 천간
  qualityScore: number;       // 종합 점수 (0-100)
}

/**
 * 완전한 기문둔갑 결과
 */
export interface CompleteQimenResult {
  hourStart: number;          // 시작 시각 (0-23)
  hourEnd: number;            // 종료 시각
  hourBranch: JiJi;          // 시지
  palaces: QimenPalace[];     // 9개 궁
  bestPalace: QimenPalace;    // 최적 궁
  avoidPalace: QimenPalace;   // 회피 궁
  overallQuality: 'excellent' | 'good' | 'neutral' | 'bad';
  userGuidance: string;       // 사용자 가이드
}

/**
 * 일일 기문둔갑 요약
 */
export interface QimenDailySummary {
  bestHour: string;
  bestDirection: string;
  avoidHour: string;
  avoidDirection: string;
  luckyGates: string[];
  luckyStars: string[];
  dailyQuality: string;
  guidance: string;
}

// ============================================================
// 상수: 낙서(洛書) 9궁 배치
// ============================================================

const LUOSHU_PALACE: Record<number, {
  pos: [number, number];
  dirKo: string;
  dirEn: string;
  element: string;
}> = {
  1: { pos: [0, -1], dirKo: '북', dirEn: 'N', element: '水' },
  2: { pos: [-1, -1], dirKo: '남서', dirEn: 'SW', element: '土' },
  3: { pos: [1, 0], dirKo: '동', dirEn: 'E', element: '木' },
  4: { pos: [1, -1], dirKo: '남동', dirEn: 'SE', element: '木' },
  5: { pos: [0, 0], dirKo: '중앙', dirEn: 'C', element: '土' },
  6: { pos: [-1, 1], dirKo: '북서', dirEn: 'NW', element: '金' },
  7: { pos: [-1, 0], dirKo: '서', dirEn: 'W', element: '金' },
  8: { pos: [1, 1], dirKo: '북동', dirEn: 'NE', element: '土' },
  9: { pos: [0, 1], dirKo: '남', dirEn: 'S', element: '火' },
};

// ============================================================
// 상수: 8문(八門)
// ============================================================

const EIGHT_GATES: Record<string, {
  quality: number;
  element: string;
  label: string;
}> = {
  휴문: { quality: 90, element: '水', label: '휴식과 회복의 문' },
  생문: { quality: 95, element: '土', label: '생기와 발전의 문' },
  상문: { quality: 30, element: '金', label: '상처와 손실의 문' },
  두문: { quality: 50, element: '木', label: '은둔과 숨김의 문' },
  경문: { quality: 70, element: '金', label: '경치와 학문의 문' },
  사문: { quality: 20, element: '土', label: '죽음과 종말의 문' },
  경문2: { quality: 25, element: '火', label: '놀람과 변화의 문' },
  개문: { quality: 85, element: '金', label: '시작과 개척의 문' },
};

const GATE_NAMES = ['휴문', '생문', '상문', '두문', '경문', '사문', '경문2', '개문'];

// ============================================================
// 상수: 9성(九星)
// ============================================================

const NINE_STARS: Record<string, {
  quality: number;
  element: string;
  label: string;
}> = {
  천봉: { quality: 95, element: '土', label: '리더십의 별' },
  천임: { quality: 90, element: '土', label: '책임과 신뢰의 별' },
  천충: { quality: 40, element: '木', label: '충돌과 도전의 별' },
  천보: { quality: 80, element: '木', label: '도움과 보조의 별' },
  천심: { quality: 85, element: '金', label: '지혜와 통찰의 별' },
  천주: { quality: 60, element: '金', label: '기둥과 지지의 별' },
  천예: { quality: 30, element: '火', label: '날카로운 비판의 별' },
  천영: { quality: 75, element: '火', label: '명예와 영광의 별' },
  천임2: { quality: 70, element: '水', label: '유연한 적응의 별' },
};

const STAR_NAMES = ['천봉', '천임', '천충', '천보', '천심', '천주', '천예', '천영', '천임2'];

// ============================================================
// 상수: 8신(八神)
// ============================================================

const EIGHT_DEITIES_YANG = ['직부', '등사', '태음', '육합', '백호', '현무', '구지', '구천'];
const EIGHT_DEITIES_YIN = ['직부', '등사', '태음', '육합', '구천', '구지', '현무', '백호'];

const DEITY_QUALITIES: Record<string, number> = {
  직부: 95,  // 주신, 최고 길신
  등사: 35,  // 변화와 속임
  태음: 80,  // 은밀과 비밀
  육합: 85,  // 화합과 인연
  백호: 25,  // 살기와 투쟁
  현무: 40,  // 도둑과 손실
  구지: 50,  // 안정과 정착
  구천: 70,  // 상승과 발전
};

// ============================================================
// 상수: 천간, 지지
// ============================================================

const HEAVENLY_STEMS: CheonGan[] = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
const EARTHLY_BRANCHES: JiJi[] = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];

const STEM_ELEMENT: Record<CheonGan, string> = {
  갑: '木', 을: '木',
  병: '火', 정: '火',
  무: '土', 기: '土',
  경: '金', 신: '金',
  임: '水', 계: '水',
};

const BRANCH_ELEMENT: Record<JiJi, string> = {
  자: '水', 축: '土', 인: '木', 묘: '木',
  진: '土', 사: '火', 오: '火', 미: '土',
  신: '金', 유: '金', 술: '土', 해: '水',
};

// 기준일: 1900-01-31 = 갑자일
const JIAZI_DATE = new Date(1900, 0, 31);

// ============================================================
// 내부 계산 함수
// ============================================================

/**
 * 날짜의 일간지 계산
 */
function getDayStemBranch(date: Date): [CheonGan, JiJi] {
  const diffDays = Math.floor((date.getTime() - JIAZI_DATE.getTime()) / (1000 * 60 * 60 * 24));
  const stemIdx = diffDays % 10;
  const branchIdx = diffDays % 12;
  
  return [HEAVENLY_STEMS[stemIdx], EARTHLY_BRANCHES[branchIdx]];
}

/**
 * 시간의 시간지 계산
 */
function getHourStemBranch(dayStem: CheonGan, hour: number): [CheonGan, JiJi] {
  // 시지 결정
  const branchIdx = Math.floor((hour + 1) / 2) % 12;
  const hourBranch = EARTHLY_BRANCHES[branchIdx];
  
  // 일간에 따른 시간 결정 (五鼠遁)
  const dayStemIdx = HEAVENLY_STEMS.indexOf(dayStem);
  const hourStemStartMap: Record<number, number> = {
    0: 0,  // 갑일 → 갑자시부터
    1: 2,  // 을일 → 병자시부터
    2: 4,  // 병일 → 무자시부터
    3: 6,  // 정일 → 경자시부터
    4: 8,  // 무일 → 임자시부터
    5: 0,  // 기일 → 갑자시부터
    6: 2,  // 경일 → 병자시부터
    7: 4,  // 신일 → 무자시부터
    8: 6,  // 임일 → 경자시부터
    9: 8,  // 계일 → 임자시부터
  };
  
  const stemStart = hourStemStartMap[(dayStemIdx % 5) * 2];
  const stemIdx = (stemStart + branchIdx) % 10;
  const hourStem = HEAVENLY_STEMS[stemIdx];
  
  return [hourStem, hourBranch];
}

/**
 * 양둔/음둔 결정
 */
function determineYangYinDun(date: Date): boolean {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  
  // 간단한 월별 판정 (실제는 절기 정밀 계산 필요)
  if (month === 12 && day >= 22) return true;
  if (month >= 1 && month <= 5) return true;
  if (month === 6 && day < 21) return true;
  
  return false;
}

/**
 * 局數 계산
 */
function calculateJuNumber(
  dayStem: CheonGan,
  dayBranch: JiJi,
  isYangDun: boolean,
  date: Date
): number {
  const stems = HEAVENLY_STEMS;
  const branches = EARTHLY_BRANCHES;
  
  const stemIdx = stems.indexOf(dayStem);
  const branchIdx = branches.indexOf(dayBranch);
  
  // 旬首 계산
  const sunHeadIdx = (branchIdx - stemIdx + 12) % 12;
  const sunHeads = ['자', '술', '신', '오', '진', '인'];
  const sunIndex = sunHeads.indexOf(branches[sunHeadIdx]) || 0;
  
  // 상원/중원/하원 결정
  const dayInMonth = date.getDate();
  const yuan = Math.floor((dayInMonth - 1) / 5) % 3;
  
  const yangJuTable = [
    [1, 7, 4], [2, 8, 5], [3, 9, 6],
    [4, 1, 7], [5, 2, 8], [6, 3, 9]
  ];
  const yinJuTable = [
    [9, 3, 6], [8, 2, 5], [7, 1, 4],
    [6, 9, 3], [5, 8, 2], [4, 7, 1]
  ];
  
  return isYangDun ? yangJuTable[sunIndex][yuan] : yinJuTable[sunIndex][yuan];
}

/**
 * 8문 배치
 */
function arrangeGates(juNumber: number, isYangDun: boolean): Map<number, string> {
  const palaceOrderYang = [1, 8, 3, 4, 9, 2, 7, 6];
  const palaceOrderYin = [1, 6, 7, 2, 9, 4, 3, 8];
  const palaceOrder = isYangDun ? palaceOrderYang : palaceOrderYin;
  
  const startIdx = (juNumber - 1) % 8;
  const gatesRotated = [...GATE_NAMES.slice(startIdx), ...GATE_NAMES.slice(0, startIdx)];
  
  const gateMap = new Map<number, string>();
  palaceOrder.forEach((palace, i) => {
    gateMap.set(palace, gatesRotated[i]);
  });
  
  // 5궁은 2궁의 문 사용
  gateMap.set(5, gateMap.get(2) || '');
  
  return gateMap;
}

/**
 * 9성 배치
 */
function arrangeStars(hourStem: CheonGan): Map<number, string> {
  const stemToPalace: Record<CheonGan, number> = {
    갑: 1, 을: 2, 병: 3, 정: 4, 무: 5,
    기: 6, 경: 7, 신: 8, 임: 9, 계: 1
  };
  
  const tianpengPalace = stemToPalace[hourStem] || 1;
  const palaceOrder = [1, 2, 3, 4, 5, 6, 7, 8, 9];
  const startIdx = tianpengPalace - 1;
  const palacesRotated = [...palaceOrder.slice(startIdx), ...palaceOrder.slice(0, startIdx)];
  
  const starMap = new Map<number, string>();
  palacesRotated.forEach((palace, i) => {
    starMap.set(palace, STAR_NAMES[i]);
  });
  
  return starMap;
}

/**
 * 8신 배치
 */
function arrangeDeities(hourBranch: JiJi, isYangDun: boolean): Map<number, string> {
  const deities = isYangDun ? EIGHT_DEITIES_YANG : EIGHT_DEITIES_YIN;
  
  const branchToPalace: Record<JiJi, number> = {
    자: 1, 축: 8, 인: 3, 묘: 3, 진: 4, 사: 9,
    오: 9, 미: 2, 신: 7, 유: 7, 술: 6, 해: 1
  };
  
  const zhifuPalace = branchToPalace[hourBranch] || 1;
  const palaceOrderYang = [1, 8, 3, 4, 9, 2, 7, 6];
  const palaceOrderYin = [1, 6, 7, 2, 9, 4, 3, 8];
  const palaceOrder = isYangDun ? palaceOrderYang : palaceOrderYin;
  
  const startIdx = palaceOrder.indexOf(zhifuPalace);
  const palacesRotated = [...palaceOrder.slice(startIdx), ...palaceOrder.slice(0, startIdx)];
  
  const deityMap = new Map<number, string>();
  palacesRotated.forEach((palace, i) => {
    if (i < 8) {
      deityMap.set(palace, deities[i]);
    }
  });
  
  // 5궁은 2궁의 신 사용
  deityMap.set(5, deityMap.get(2) || '직부');
  
  return deityMap;
}

/**
 * 천간 배치 (지반과 천반)
 */
function arrangeStemsOnPlates(
  juNumber: number,
  hourStem: CheonGan
): { earthPlate: Map<number, CheonGan>; heavenPlate: Map<number, CheonGan> } {
  const earthPlateStemsBase: CheonGan[] = ['무', '기', '경', '신', '임', '계', '정', '병', '을'];
  
  // 지반 배치
  const earthPlate = new Map<number, CheonGan>();
  const palaceOrder = [juNumber];
  for (let i = 1; i < 9; i++) {
    palaceOrder.push(((juNumber + i - 1) % 9) + 1);
  }
  
  palaceOrder.forEach((palace, i) => {
    if (palace === 5) {
      earthPlate.set(5, earthPlate.get(2) || '무');
    } else if (i < 9) {
      earthPlate.set(palace, earthPlateStemsBase[i]);
    }
  });
  
  // 천반: 시간에 따라 회전
  const hourStemIdx = HEAVENLY_STEMS.indexOf(hourStem);
  const rotation = hourStemIdx % 9;
  
  const heavenPlate = new Map<number, CheonGan>();
  for (let palace = 1; palace <= 9; palace++) {
    const earthStem = earthPlate.get(palace) || '무';
    const earthIdx = earthPlateStemsBase.indexOf(earthStem);
    const heavenIdx = (earthIdx + rotation) % 9;
    heavenPlate.set(palace, earthPlateStemsBase[heavenIdx]);
  }
  
  return { earthPlate, heavenPlate };
}

/**
 * 궁의 종합 점수 계산
 */
function calculatePalaceQuality(
  palace: QimenPalace,
  yongSinScore?: Record<string, number>
): number {
  let score = 50;
  
  // 문의 길흉
  const gateQuality = EIGHT_GATES[palace.gate]?.quality || 50;
  score = Math.floor((score + gateQuality) / 2);
  
  // 별의 길흉
  const starQuality = NINE_STARS[palace.star]?.quality || 50;
  score = Math.floor((score + starQuality) / 2);
  
  // 신의 길흉
  const deityQuality = DEITY_QUALITIES[palace.deity] || 50;
  score = Math.floor((score + deityQuality) / 2);
  
  // 천간 상생상극
  const earthElem = STEM_ELEMENT[palace.earthlyPlateGan] || '土';
  const heavenElem = STEM_ELEMENT[palace.heavenlyPlateGan] || '土';
  
  const shengMap: Record<string, string> = {
    木: '火', 火: '土', 土: '金', 金: '水', 水: '木'
  };
  const keMap: Record<string, string> = {
    木: '土', 土: '水', 水: '火', 火: '金', 金: '木'
  };
  
  if (shengMap[earthElem] === heavenElem || shengMap[heavenElem] === earthElem) {
    score += 10;
  } else if (keMap[earthElem] === heavenElem) {
    score -= 15;
  } else if (keMap[heavenElem] === earthElem) {
    score -= 5;
  }
  
  // 특수 조합
  if (palace.gate === '생문' && palace.star === '천봉' && palace.deity === '직부') {
    score = 100;
  }
  if (palace.gate === '사문' && palace.star === '천예' && palace.deity === '백호') {
    score = 10;
  }
  
  // ===== M21: 사주 용신 기반 개인화 보정 =====
  if (yongSinScore) {
    const KO_TO_HAN: Record<string, string> = {목:'木',화:'火',토:'土',금:'金',수:'水'};
    const HAN_TO_KO: Record<string, string> = {木:'목',火:'화',土:'토',金:'금',水:'수'};
    const lookupYS = (e: string): number => {
      if (yongSinScore[e] !== undefined) return yongSinScore[e];
      if (yongSinScore[KO_TO_HAN[e]] !== undefined) return yongSinScore[KO_TO_HAN[e]];
      if (yongSinScore[HAN_TO_KO[e]] !== undefined) return yongSinScore[HAN_TO_KO[e]];
      return 50;
    };
    const heavenWeight = lookupYS(heavenElem);
    const earthWeight = lookupYS(earthElem);
    // 0-100 → -20 ~ +20 범위 보정
    const personalAdjust = ((heavenWeight + earthWeight) / 2 - 50) * 0.4;
    score = score + personalAdjust;
  }

  return Math.max(0, Math.min(100, Math.round(score)));
}

// ============================================================
// 공개 함수
// ============================================================

/**
 * 완전한 기문둔갑 계산
 */
export function calculateCompleteQimen(
  birthDate: Date,
  targetDate: Date,
  targetHour: number,
  yongSinScore?: Record<string, number>
): CompleteQimenResult {
  // 1. 일간지와 시간지 계산
  const [dayStem, dayBranch] = getDayStemBranch(targetDate);
  const [hourStem, hourBranch] = getHourStemBranch(dayStem, targetHour);
  
  // 2. 양둔/음둔 결정
  const isYangDun = determineYangYinDun(targetDate);
  
  // 3. 局數 계산
  const juNumber = calculateJuNumber(dayStem, dayBranch, isYangDun, targetDate);
  
  // 4. 각 요소 배치
  const gateMap = arrangeGates(juNumber, isYangDun);
  const starMap = arrangeStars(hourStem);
  const deityMap = arrangeDeities(hourBranch, isYangDun);
  const { earthPlate, heavenPlate } = arrangeStemsOnPlates(juNumber, hourStem);
  
  // 5. 9궁 정보 생성
  const palaces: QimenPalace[] = [];
  
  for (let palaceNum = 1; palaceNum <= 9; palaceNum++) {
    const palaceInfo = LUOSHU_PALACE[palaceNum];
    
    const palace: QimenPalace = {
      palaceNum,
      directionKo: palaceInfo.dirKo,
      directionEn: palaceInfo.dirEn,
      gate: gateMap.get(palaceNum) || '',
      star: starMap.get(palaceNum) || '',
      deity: deityMap.get(palaceNum) || '',
      earthlyPlateGan: earthPlate.get(palaceNum) || '무',
      heavenlyPlateGan: heavenPlate.get(palaceNum) || '무',
      qualityScore: 0
    };
    
    palace.qualityScore = calculatePalaceQuality(palace, yongSinScore);
    palaces.push(palace);
  }
  
  // 6. 최적/회피 궁 결정
  const bestPalace = palaces.reduce((best, current) => 
    current.qualityScore > best.qualityScore ? current : best
  );
  const avoidPalace = palaces.reduce((worst, current) => 
    current.qualityScore < worst.qualityScore ? current : worst
  );
  
  // 7. 전체 품질 판정
  const avgScore = palaces.reduce((sum, p) => sum + p.qualityScore, 0) / 9;
  let overallQuality: CompleteQimenResult['overallQuality'];
  
  if (avgScore >= 70) overallQuality = 'excellent';
  else if (avgScore >= 50) overallQuality = 'good';
  else if (avgScore >= 30) overallQuality = 'neutral';
  else overallQuality = 'bad';
  
  // 8. 사용자 가이드 생성
  const hourIdx = Math.floor((targetHour + 1) / 2) % 12;
  const currentHourBranch = EARTHLY_BRANCHES[hourIdx];
  
  let guidance = `${targetHour.toString().padStart(2, '0')}시(${currentHourBranch}시)는 `;
  
  switch (overallQuality) {
    case 'excellent':
      guidance += `매우 좋은 시간입니다. ${bestPalace.directionKo}쪽이 특히 유리합니다.`;
      break;
    case 'good':
      guidance += `좋은 시간입니다. ${bestPalace.directionKo}쪽을 활용하세요.`;
      break;
    case 'neutral':
      guidance += `평범한 시간입니다. ${avoidPalace.directionKo}쪽은 피하는 것이 좋습니다.`;
      break;
    default:
      guidance += `주의가 필요한 시간입니다. 중요한 일은 피하고 ${bestPalace.directionKo}쪽에서 휴식을 취하세요.`;
  }
  
  // 시작/종료 시간
  let hourStart: number, hourEnd: number;
  if (hourIdx === 0) {  // 자시
    hourStart = 23;
    hourEnd = 1;
  } else {
    hourStart = (hourIdx * 2 - 1) % 24;
    hourEnd = (hourIdx * 2 + 1) % 24;
  }
  
  return {
    hourStart,
    hourEnd,
    hourBranch: currentHourBranch,
    palaces,
    bestPalace,
    avoidPalace,
    overallQuality,
    userGuidance: guidance
  };
}

/**
 * 하루 전체 기문둔갑 분석
 */
export function getDailyCompleteQimen(
  birthDate: Date,
  targetDate: Date,
  yongSinScore?: Record<string, number>
): CompleteQimenResult[] {
  const results: CompleteQimenResult[] = [];

  for (let hourIdx = 0; hourIdx < 12; hourIdx++) {
    const targetHour = hourIdx === 0 ? 23 : hourIdx * 2 - 1;
    const result = calculateCompleteQimen(birthDate, targetDate, targetHour, yongSinScore);
    results.push(result);
  }

  return results;
}

/**
 * M22: 하루 12시진 중 본인에게 가장 길한 시진의 기문 결과 반환.
 * yongSinScore가 있으면 사주 가중치 적용 → 사람마다 best hour 달라짐.
 */
export function getDailyBestQimen(
  birthDate: Date,
  targetDate: Date,
  yongSinScore?: Record<string, number>
): CompleteQimenResult {
  const all = getDailyCompleteQimen(birthDate, targetDate, yongSinScore);
  return all.reduce((best, cur) =>
    cur.bestPalace.qualityScore > best.bestPalace.qualityScore ? cur : best
  );
}

/**
 * 일일 기문둔갑 요약
 */
export function getQimenSummary(
  birthDate: Date,
  targetDate: Date
): QimenDailySummary {
  const dailyResults = getDailyCompleteQimen(birthDate, targetDate);
  
  // 최고/최악 시간 찾기
  const bestHour = dailyResults.reduce((best, current) =>
    current.bestPalace.qualityScore > best.bestPalace.qualityScore ? current : best
  );
  const worstHour = dailyResults.reduce((worst, current) =>
    current.bestPalace.qualityScore < worst.bestPalace.qualityScore ? current : worst
  );
  
  // 길한 문과 별 수집
  const luckyGates = new Set<string>();
  const luckyStars = new Set<string>();
  let totalScore = 0;
  
  dailyResults.forEach(result => {
    result.palaces.forEach(palace => {
      if (palace.qualityScore >= 70) {
        if (palace.gate) luckyGates.add(palace.gate);
        if (palace.star) luckyStars.add(palace.star);
      }
    });
    totalScore += result.bestPalace.qualityScore;
  });
  
  const avgScore = totalScore / 12;
  
  let dailyQuality: string;
  let guidance: string;
  
  if (avgScore >= 70) {
    dailyQuality = 'excellent';
    guidance = '오늘은 매우 좋은 날입니다. 적극적으로 활동하세요.';
  } else if (avgScore >= 50) {
    dailyQuality = 'good';
    guidance = '오늘은 전반적으로 좋은 날입니다. 계획한 일을 추진하기 좋습니다.';
  } else if (avgScore >= 30) {
    dailyQuality = 'neutral';
    guidance = '오늘은 평범한 날입니다. 무리하지 말고 차분히 진행하세요.';
  } else {
    dailyQuality = 'caution';
    guidance = '오늘은 신중함이 필요한 날입니다. 중요한 결정은 미루는 것이 좋습니다.';
  }
  
  const formatHour = (result: CompleteQimenResult) => {
    const endStr = result.hourEnd === 1 ? '01' : result.hourEnd.toString().padStart(2, '0');
    return `${result.hourStart.toString().padStart(2, '0')}-${endStr}시 (${result.hourBranch}시)`;
  };
  
  return {
    bestHour: formatHour(bestHour),
    bestDirection: bestHour.bestPalace.directionKo,
    avoidHour: formatHour(worstHour),
    avoidDirection: worstHour.avoidPalace.directionKo,
    luckyGates: Array.from(luckyGates).slice(0, 3),
    luckyStars: Array.from(luckyStars).slice(0, 3),
    dailyQuality,
    guidance
  };
}

