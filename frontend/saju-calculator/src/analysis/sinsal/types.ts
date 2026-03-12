/**
 * 신살(神煞) 타입 정의
 * 전통 명리학 기반 정확한 계산을 위한 타입
 */

import type { CheonGan, JiJi } from '../../types/saju';

// 오행 타입
export type OhHaeng = '목' | '화' | '토' | '금' | '수';

// 삼합 그룹 타입
export type SamhapGroup = '인오술' | '사유축' | '신자진' | '해묘미';

// 12신살 종류
export type TwelveSinsalType =
  | 'geobSal'      // 겁살 (劫煞)
  | 'jaeSal'       // 재살 (災煞)
  | 'cheonSal'     // 천살 (天煞)
  | 'jiSal'        // 지살 (地煞)
  | 'nyeonSal'     // 년살 (年煞) = 도화살
  | 'wolSal'       // 월살 (月煞)
  | 'mangSinSal'   // 망신살 (亡身煞)
  | 'jangSeongSal' // 장성살 (將星煞)
  | 'banAnSal'     // 반안살 (攀鞍煞)
  | 'yeokMaSal'    // 역마살 (驛馬煞)
  | 'yukHaeSal'    // 육해살 (六害煞)
  | 'hwaGaeSal';   // 화개살 (華蓋煞)

// 기타 신살 종류
export type OtherSinsalType =
  | 'yangInSal'      // 양인살 (羊刃煞)
  | 'guiMunGwanSal'  // 귀문관살 (鬼門關煞)
  | 'gongMang'       // 공망 (空亡)
  | 'cheonEulGwiIn'  // 천을귀인 (天乙貴人)
  | 'munChangGwiIn'  // 문창귀인 (文昌貴人)
  | 'hakDangGwiIn'   // 학당귀인 (學堂貴人)
  | 'hongYeomSal'    // 홍염살 (紅艶煞)
  | 'baekHoSal'      // 백호살 (白虎煞)
  | 'hyeonChimSal';  // 현침살 (懸針煞)

// 신살 결과
export interface SinsalResult {
  name: string;           // 한글 이름
  type: TwelveSinsalType | OtherSinsalType;
  present: boolean;       // 해당 신살 존재 여부
  triggerJiji?: JiJi;     // 해당 신살을 발동시키는 지지
  description: string;    // 간단 설명
  effect: 'good' | 'bad' | 'neutral'; // 길흉 여부
  detailedMeaning: string; // 상세 의미
}

// 12신살 테이블 (삼합별)
export interface TwelveSinsalTable {
  geobSal: JiJi;      // 겁살
  jaeSal: JiJi;       // 재살
  cheonSal: JiJi;     // 천살
  jiSal: JiJi;        // 지살
  nyeonSal: JiJi;     // 년살 (도화살)
  wolSal: JiJi;       // 월살
  mangSinSal: JiJi;   // 망신살
  jangSeongSal: JiJi; // 장성살
  banAnSal: JiJi;     // 반안살
  yeokMaSal: JiJi;    // 역마살
  yukHaeSal: JiJi;    // 육해살
  hwaGaeSal: JiJi;    // 화개살
}

// 신살 분석 전체 결과
export interface SinsalAnalysis {
  // 기준 정보
  yearJiji: JiJi;
  dayJiji: JiJi;
  dayGan: CheonGan;

  // 12신살 결과 (년지 기준)
  twelveSinsalByYear: SinsalResult[];

  // 12신살 결과 (일지 기준)
  twelveSinsalByDay: SinsalResult[];

  // 기타 신살
  yangInSal: SinsalResult | null;      // 양인살 (일간 기준)
  guiMunGwanSal: SinsalResult | null;  // 귀문관살
  wonJinSal: SinsalResult | null;      // 원진살
  gongMang: SinsalResult | null;       // 공망
  cheonEulGwiIn: SinsalResult | null;  // 천을귀인

  // 요약
  goodSinsal: string[];   // 길한 신살 목록
  badSinsal: string[];    // 흉한 신살 목록
  neutralSinsal: string[]; // 중립 신살 목록

  // AI 해석용 텍스트
  summaryText: string;
}

// 택일용 신살 분석
export interface DateSinsalAnalysis {
  date: Date;
  dayPillar: { gan: CheonGan; ji: JiJi };

  // 해당 날짜에 해당되는 신살
  activeSinsal: SinsalResult[];

  // 길흉 판정
  isGoodDay: boolean;
  isBadDay: boolean;
  score: number; // 0-100

  // 추천 여부
  recommendFor: string[]; // ['이사', '결혼', '개업' 등]
  avoidFor: string[];     // ['큰 결정', '계약' 등]
}
