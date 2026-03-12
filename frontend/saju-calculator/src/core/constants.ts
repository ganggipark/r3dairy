/**
 * 사주 계산 핵심 상수 (CANONICAL DATA)
 *
 * 모든 사주 모듈에서 사용하는 단일 진실 출처 (Single Source of Truth)
 * 특히 지장간(支藏干) 순서와 가중치는 반드시 이 파일을 참조할 것
 *
 * @module core/constants
 * @version 2.0.0
 */

import type { CheonGan, JiJi } from './types';

/**
 * 천간(天干) 배열
 * 갑을병정무기경신임계 (10개)
 */
export const CHEONGAN_LIST: readonly CheonGan[] = [
  '갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'
] as const;

/**
 * 지지(地支) 배열
 * 자축인묘진사오미신유술해 (12개)
 */
export const JIJI_LIST: readonly JiJi[] = [
  '자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'
] as const;

/**
 * 오행(五行) 타입
 */
export type OhHaeng = '목' | '화' | '토' | '금' | '수';

/**
 * 천간 → 오행 매핑
 *
 * 갑을목(甲乙木), 병정화(丙丁火), 무기토(戊己土),
 * 경신금(庚辛金), 임계수(壬癸水)
 */
export const CHEONGAN_TO_OHHAENG: Record<CheonGan, OhHaeng> = {
  '갑': '목', '을': '목',
  '병': '화', '정': '화',
  '무': '토', '기': '토',
  '경': '금', '신': '금',
  '임': '수', '계': '수',
} as const;

/**
 * 천간 음양 (陰陽)
 * true = 양(陽), false = 음(陰)
 *
 * 양: 갑병무경임 (홀수 인덱스)
 * 음: 을정기신계 (짝수 인덱스)
 */
export const CHEONGAN_YINYANG: Record<CheonGan, boolean> = {
  '갑': true,  '을': false,
  '병': true,  '정': false,
  '무': true,  '기': false,
  '경': true,  '신': false,
  '임': true,  '계': false,
} as const;

/**
 * 지지 → 오행 매핑
 *
 * 인묘목(寅卯木), 사오화(巳午火), 신유금(申酉金), 해자수(亥子水)
 * 축진미술토(丑辰未戌土)
 */
export const JIJI_TO_OHHAENG: Record<JiJi, OhHaeng> = {
  '자': '수', '축': '토',
  '인': '목', '묘': '목',
  '진': '토', '사': '화',
  '오': '화', '미': '토',
  '신': '금', '유': '금',
  '술': '토', '해': '수',
} as const;

/**
 * 지지 음양
 *
 * 양지: 자인진오신술 (홀수 인덱스)
 * 음지: 축묘사미유해 (짝수 인덱스)
 */
export const JIJI_YINYANG: Record<JiJi, boolean> = {
  '자': true,  '축': false,
  '인': true,  '묘': false,
  '진': true,  '사': false,
  '오': true,  '미': false,
  '신': true,  '유': false,
  '술': true,  '해': false,
} as const;

/**
 * 지장간(支藏干) 데이터 - 가중치 포함
 *
 * ⚠️ 순서 중요: [여기(餘氣), 중기(中氣), 본기(本氣)]
 *
 * 규칙:
 * - 왕지(旺支) 2개: 자묘오유 - 여기(0.33) + 본기(0.67)
 * - 오(午)는 예외 3개: 병(0.33) + 기(0.33) + 정(0.33)
 * - 생지(生支) 3개: 인사신해 - 여기(0.23) + 중기(0.23) + 본기(0.54)
 * - 고지(庫支) 4개: 축진미술 - 여기(0.30) + 중기(0.10) + 본기(0.60)
 *
 * @example
 * JIJANGGAN['인'] // [{ stem: '무', weight: 0.23 }, { stem: '병', weight: 0.23 }, { stem: '갑', weight: 0.54 }]
 */
export const JIJANGGAN: Record<JiJi, Array<{ stem: CheonGan; weight: number }>> = {
  // 왕지(旺支) - 2개
  '자': [
    { stem: '임', weight: 0.33 },  // 여기
    { stem: '계', weight: 0.67 },  // 본기
  ],
  '묘': [
    { stem: '갑', weight: 0.33 },  // 여기
    { stem: '을', weight: 0.67 },  // 본기
  ],
  '유': [
    { stem: '경', weight: 0.33 },  // 여기
    { stem: '신', weight: 0.67 },  // 본기
  ],

  // 오(午) - 왕지 예외 3개 균등
  '오': [
    { stem: '병', weight: 0.33 },
    { stem: '기', weight: 0.33 },
    { stem: '정', weight: 0.33 },
  ],

  // 생지(生支) - 3개
  '인': [
    { stem: '무', weight: 0.23 },  // 여기
    { stem: '병', weight: 0.23 },  // 중기
    { stem: '갑', weight: 0.54 },  // 본기
  ],
  '사': [
    { stem: '무', weight: 0.23 },  // 여기
    { stem: '경', weight: 0.23 },  // 중기
    { stem: '병', weight: 0.54 },  // 본기
  ],
  '신': [
    { stem: '무', weight: 0.23 },  // 여기
    { stem: '임', weight: 0.23 },  // 중기
    { stem: '경', weight: 0.54 },  // 본기
  ],
  '해': [
    { stem: '무', weight: 0.23 },  // 여기
    { stem: '갑', weight: 0.23 },  // 중기
    { stem: '임', weight: 0.54 },  // 본기
  ],

  // 고지(庫支) - 3개
  '축': [
    { stem: '계', weight: 0.30 },  // 여기
    { stem: '신', weight: 0.10 },  // 중기
    { stem: '기', weight: 0.60 },  // 본기
  ],
  '진': [
    { stem: '을', weight: 0.30 },  // 여기
    { stem: '계', weight: 0.10 },  // 중기
    { stem: '무', weight: 0.60 },  // 본기
  ],
  '미': [
    { stem: '정', weight: 0.30 },  // 여기
    { stem: '을', weight: 0.10 },  // 중기
    { stem: '기', weight: 0.60 },  // 본기
  ],
  '술': [
    { stem: '신', weight: 0.30 },  // 여기
    { stem: '정', weight: 0.10 },  // 중기
    { stem: '무', weight: 0.60 },  // 본기
  ],
} as const;

/**
 * 지장간 단순 배열 (가중치 없이 순서만)
 *
 * 레거시 코드 호환용
 */
export const JIJANGGAN_SIMPLE: Record<JiJi, readonly CheonGan[]> = {
  '자': ['임', '계'],
  '축': ['계', '신', '기'],
  '인': ['무', '병', '갑'],
  '묘': ['갑', '을'],
  '진': ['을', '계', '무'],
  '사': ['무', '경', '병'],
  '오': ['병', '기', '정'],
  '미': ['정', '을', '기'],
  '신': ['무', '임', '경'],
  '유': ['경', '신'],
  '술': ['신', '정', '무'],
  '해': ['무', '갑', '임'],
} as const;

/**
 * 본기(本氣) 추출 함수
 *
 * 지장간의 마지막 천간이 본기(가장 강한 기운)
 *
 * @param ji - 지지
 * @returns 본기 천간
 *
 * @example
 * getMainJijanggan('인') // '갑'
 * getMainJijanggan('축') // '기'
 */
export function getMainJijanggan(ji: JiJi): CheonGan {
  const stems = JIJANGGAN[ji];
  return stems[stems.length - 1].stem;
}

/**
 * 오행 상생(相生) 관계
 *
 * 수생목(水生木), 목생화(木生火), 화생토(火生土),
 * 토생금(土生金), 금생수(金生水)
 *
 * @example
 * SANG_SAENG['목'] // '화' (목생화)
 */
export const SANG_SAENG: Record<OhHaeng, OhHaeng> = {
  '목': '화',  // 목생화
  '화': '토',  // 화생토
  '토': '금',  // 토생금
  '금': '수',  // 금생수
  '수': '목',  // 수생목
} as const;

/**
 * 오행 상극(相剋) 관계
 *
 * 목극토(木剋土), 토극수(土剋水), 수극화(水剋火),
 * 화극금(火剋金), 금극목(金剋木)
 *
 * @example
 * SANG_GEUK['목'] // '토' (목극토)
 */
export const SANG_GEUK: Record<OhHaeng, OhHaeng> = {
  '목': '토',  // 목극토
  '토': '수',  // 토극수
  '수': '화',  // 수극화
  '화': '금',  // 화극금
  '금': '목',  // 금극목
} as const;

/**
 * 60갑자(甲子) 배열
 *
 * 갑자부터 계해까지 순환하는 60개 간지 조합
 * 천간 10개 × 지지 12개 = 최소공배수 60
 */
export const SIXTY_GAPJA: readonly string[] = [
  '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유',
  '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미',
  '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사',
  '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘',
  '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축',
  '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해',
] as const;

/**
 * 60갑자 Set (O(1) 검증용)
 */
export const SIXTY_GAPJA_SET = new Set(SIXTY_GAPJA);

/**
 * 60갑자 → 인덱스 매핑 (O(1) 조회)
 */
export const SIXTY_GAPJA_INDEX: ReadonlyMap<string, number> = new Map(
  SIXTY_GAPJA.map((gapja, index) => [gapja, index])
);

/**
 * 유효한 갑자인지 검증
 *
 * @param gapja - 간지 문자열 (예: '갑자', '을축')
 * @returns 유효 여부
 *
 * @example
 * isValidGapja('갑자') // true
 * isValidGapja('갑축') // false (천간-지지 조합 불가)
 */
export function isValidGapja(gapja: string): boolean {
  return SIXTY_GAPJA_SET.has(gapja);
}

/**
 * 갑자 인덱스 조회 (0-59)
 *
 * @param gapja - 간지 문자열
 * @returns 인덱스 (0-59), 유효하지 않으면 -1
 *
 * @example
 * getGapjaIndex('갑자') // 0
 * getGapjaIndex('을축') // 1
 * getGapjaIndex('계해') // 59
 * getGapjaIndex('갑축') // -1 (무효)
 */
export function getGapjaIndex(gapja: string): number {
  return SIXTY_GAPJA_INDEX.get(gapja) ?? -1;
}

/**
 * 인덱스로 갑자 조회
 *
 * @param index - 0-59 사이 인덱스
 * @returns 간지 문자열, 범위 밖이면 undefined
 *
 * @example
 * getGapjaByIndex(0) // '갑자'
 * getGapjaByIndex(59) // '계해'
 * getGapjaByIndex(60) // undefined
 */
export function getGapjaByIndex(index: number): string | undefined {
  if (index < 0 || index >= 60) return undefined;
  return SIXTY_GAPJA[index];
}

/**
 * 갑자 순환 계산 (연월일시 계산용)
 *
 * @param startIndex - 시작 인덱스 (0-59)
 * @param offset - 오프셋 (양수/음수 모두 가능)
 * @returns 순환된 인덱스 (0-59)
 *
 * @example
 * cycleGapjaIndex(0, 1) // 1 (갑자 → 을축)
 * cycleGapjaIndex(59, 1) // 0 (계해 → 갑자, 순환)
 * cycleGapjaIndex(0, -1) // 59 (갑자 → 계해, 역순환)
 */
export function cycleGapjaIndex(startIndex: number, offset: number): number {
  const result = (startIndex + offset) % 60;
  return result < 0 ? result + 60 : result;
}

/**
 * 천간-지지 조합이 유효한지 검증 (음양 일치 규칙)
 *
 * 천간과 지지의 음양이 반드시 일치해야 함
 * 양간(갑병무경임) + 양지(자인진오신술)
 * 음간(을정기신계) + 음지(축묘사미유해)
 *
 * @param gan - 천간
 * @param ji - 지지
 * @returns 유효한 조합 여부
 *
 * @example
 * isValidGanJiPair('갑', '자') // true (양+양)
 * isValidGanJiPair('갑', '축') // false (양+음)
 * isValidGanJiPair('을', '축') // true (음+음)
 */
export function isValidGanJiPair(gan: CheonGan, ji: JiJi): boolean {
  return CHEONGAN_YINYANG[gan] === JIJI_YINYANG[ji];
}

/**
 * 다음 갑자 계산
 *
 * @param currentGapja - 현재 간지
 * @returns 다음 간지, 유효하지 않으면 undefined
 *
 * @example
 * getNextGapja('갑자') // '을축'
 * getNextGapja('계해') // '갑자' (순환)
 */
export function getNextGapja(currentGapja: string): string | undefined {
  const index = getGapjaIndex(currentGapja);
  if (index === -1) return undefined;
  return getGapjaByIndex((index + 1) % 60);
}

/**
 * 이전 갑자 계산
 *
 * @param currentGapja - 현재 간지
 * @returns 이전 간지, 유효하지 않으면 undefined
 *
 * @example
 * getPreviousGapja('을축') // '갑자'
 * getPreviousGapja('갑자') // '계해' (역순환)
 */
export function getPreviousGapja(currentGapja: string): string | undefined {
  const index = getGapjaIndex(currentGapja);
  if (index === -1) return undefined;
  return getGapjaByIndex(index === 0 ? 59 : index - 1);
}
