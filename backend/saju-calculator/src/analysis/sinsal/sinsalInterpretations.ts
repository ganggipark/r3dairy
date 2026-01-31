/**
 * 신살 상세 해석 데이터베이스
 *
 * 각 신살의 의미, 영향, 조언을 포함
 */

export interface SinsalInterpretation {
  name: string;
  koreanName: string;
  category: 'gilSin' | 'hyungSin';
  meaning: string;
  influence: string;
  advice: string;
  keywords: string[];
}

export const SINSAL_INTERPRETATIONS: Record<string, SinsalInterpretation> = {
  // 길신 (6종)
  '천을귀인': {
    name: 'CheonEulGuiIn',
    koreanName: '천을귀인',
    category: 'gilSin',
    meaning: '하늘이 내린 귀인으로, 어려울 때 도움을 주는 존재가 나타남',
    influence: '위기 상황에서 구원자가 나타나고, 귀인의 도움으로 성공 가능',
    advice: '타인을 도우면 그 복이 돌아오니 선행을 실천하세요',
    keywords: ['귀인', '도움', '행운', '위기 극복'],
  },
  '천덕귀인': {
    name: 'CheonDeokGuiIn',
    koreanName: '천덕귀인',
    category: 'gilSin',
    meaning: '하늘의 덕으로 복을 받는 길신',
    influence: '재난을 피하고 복을 받으며, 주변의 존경을 받음',
    advice: '덕을 베풀면 더 큰 복이 돌아옵니다',
    keywords: ['복덕', '재난 회피', '존경'],
  },
  '월덕귀인': {
    name: 'WolDeokGuiIn',
    koreanName: '월덕귀인',
    category: 'gilSin',
    meaning: '달의 덕으로 순탄한 운을 받는 길신',
    influence: '매사가 순조롭고 큰 어려움 없이 진행됨',
    advice: '감사하는 마음으로 현재를 즐기세요',
    keywords: ['순탄', '평화', '안정'],
  },
  '문창귀인': {
    name: 'MunChangGuiIn',
    koreanName: '문창귀인',
    category: 'gilSin',
    meaning: '학문과 글에 뛰어난 재능을 부여하는 길신',
    influence: '시험, 학업, 자격증에서 좋은 성과를 얻음',
    advice: '꾸준히 공부하고 자기계발에 힘쓰세요',
    keywords: ['학업', '시험', '문서', '자격증'],
  },
  '학당귀인': {
    name: 'HakDangGuiIn',
    koreanName: '학당귀인',
    category: 'gilSin',
    meaning: '배움의 전당에서 빛나는 길신',
    influence: '교육 분야에서 성공하고 가르치는 재능이 있음',
    advice: '배운 것을 나누면 더 큰 지혜가 생깁니다',
    keywords: ['교육', '가르침', '지혜'],
  },
  '천의성': {
    name: 'CheonUiSung',
    koreanName: '천의성',
    category: 'gilSin',
    meaning: '하늘의 의술로 치유 능력을 부여하는 길신',
    influence: '건강 회복이 빠르고 의료/치유 분야에 적성',
    advice: '건강 관리에 관심을 갖고, 타인의 아픔을 돌보세요',
    keywords: ['건강', '치유', '의료', '회복'],
  },

  // 흉신 (11종)
  '역마살': {
    name: 'YeokMaSal',
    koreanName: '역마살',
    category: 'hyungSin',
    meaning: '끊임없이 움직이고 이동해야 하는 운',
    influence: '잦은 이사, 출장, 여행이 많으며 한 곳에 정착하기 어려움',
    advice: '움직임을 직업으로 활용하면 오히려 길함 (영업, 무역, 여행업)',
    keywords: ['이동', '여행', '변화', '불안정'],
  },
  '도화살': {
    name: 'DoHwaSal',
    koreanName: '도화살',
    category: 'hyungSin',
    meaning: '이성에게 매력적으로 보이는 살',
    influence: '연애운은 좋으나 바람기나 유혹에 빠지기 쉬움',
    advice: '매력을 예술이나 서비스업에 활용하면 성공',
    keywords: ['매력', '연애', '유혹', '이성'],
  },
  '양인살': {
    name: 'YangInSal',
    koreanName: '양인살',
    category: 'hyungSin',
    meaning: '칼날같이 날카로운 기운',
    influence: '사고, 수술, 분쟁 주의가 필요하며 성격이 급함',
    advice: '결단력과 추진력으로 전환하면 리더십 발휘 가능',
    keywords: ['사고', '수술', '분쟁', '결단력'],
  },
  '겁살': {
    name: 'GeopSal',
    koreanName: '겁살',
    category: 'hyungSin',
    meaning: '강탈당할 수 있는 운',
    influence: '재물 손실, 도난, 사기 주의가 필요함',
    advice: '중요한 계약이나 투자는 신중하게 검토하세요',
    keywords: ['손실', '도난', '사기', '주의'],
  },
  '망신살': {
    name: 'MangSinSal',
    koreanName: '망신살',
    category: 'hyungSin',
    meaning: '명예가 손상될 수 있는 운',
    influence: '구설수, 소문, 스캔들에 휘말릴 수 있음',
    advice: '언행을 조심하고 겸손한 태도를 유지하세요',
    keywords: ['구설', '명예', '소문', '조심'],
  },
  '백호살': {
    name: 'BaekHoSal',
    koreanName: '백호살',
    category: 'hyungSin',
    meaning: '흰 호랑이의 맹렬한 기운',
    influence: '급작스러운 재난, 사고, 질병 주의',
    advice: '안전에 신경 쓰고 무리한 모험은 피하세요',
    keywords: ['사고', '재난', '질병', '안전'],
  },
  '귀문관살': {
    name: 'GwiMunGwanSal',
    koreanName: '귀문관살',
    category: 'hyungSin',
    meaning: '귀신이 드나드는 문의 살',
    influence: '정신적 불안, 악몽, 신경쇠약 주의',
    advice: '명상, 운동으로 정신 건강을 챙기세요',
    keywords: ['정신', '불안', '신경', '명상'],
  },
  '천라': {
    name: 'CheonRa',
    koreanName: '천라',
    category: 'hyungSin',
    meaning: '하늘의 그물에 걸리는 운',
    influence: '법적 문제, 소송, 관재 주의',
    advice: '법과 규칙을 철저히 준수하세요',
    keywords: ['법', '소송', '관재', '규칙'],
  },
  '지망': {
    name: 'JiMang',
    koreanName: '지망',
    category: 'hyungSin',
    meaning: '땅의 그물에 걸리는 운',
    influence: '부동산 문제, 이사 불리, 토지 분쟁',
    advice: '부동산 거래 시 전문가 조언을 받으세요',
    keywords: ['부동산', '이사', '토지', '분쟁'],
  },
  '원진살': {
    name: 'WonJinSal',
    koreanName: '원진살',
    category: 'hyungSin',
    meaning: '원망과 질투의 기운',
    influence: '대인관계 갈등, 오해, 배신 주의',
    advice: '오해가 생기면 빨리 대화로 풀어가세요',
    keywords: ['갈등', '오해', '배신', '관계'],
  },
  '화개살': {
    name: 'HwaGaeSal',
    koreanName: '화개살',
    category: 'hyungSin',
    meaning: '꽃 덮개 아래 고독한 운',
    influence: '예술적 재능이 있으나 외로움을 느끼기 쉬움',
    advice: '예술, 종교, 학문에서 성취감을 찾으세요',
    keywords: ['예술', '고독', '종교', '학문'],
  },
  '괴강살': {
    name: 'GoeGangSal',
    koreanName: '괴강살',
    category: 'hyungSin',
    meaning: '하늘의 강직한 별 기운',
    influence: '강인하고 결단력 있으나 고집이 세고 극단적 성향',
    advice: '유연성을 기르고 타협하는 법을 배우세요. 리더십 발휘 가능',
    keywords: ['강인', '결단력', '고집', '리더십'],
  },
};

/**
 * 신살 이름으로 해석 가져오기
 */
export function getSinsalInterpretation(sinsalName: string): SinsalInterpretation | undefined {
  return SINSAL_INTERPRETATIONS[sinsalName];
}

/**
 * 카테고리별 신살 목록 가져오기
 */
export function getSinsalByCategory(category: 'gilSin' | 'hyungSin'): SinsalInterpretation[] {
  return Object.values(SINSAL_INTERPRETATIONS).filter(s => s.category === category);
}

/**
 * 신살 목록에 대한 종합 해석 생성
 */
export function generateComprehensiveSinsalSummary(gilSin: string[], hyungSin: string[]): string {
  const gilInterpretations = gilSin.map(s => SINSAL_INTERPRETATIONS[s]).filter(Boolean);
  const hyungInterpretations = hyungSin.map(s => SINSAL_INTERPRETATIONS[s]).filter(Boolean);

  const parts: string[] = [];

  if (gilInterpretations.length > 0) {
    parts.push(`길신 ${gilInterpretations.length}개 (${gilSin.join(', ')})가 있어 복이 있습니다.`);
  }

  if (hyungInterpretations.length > 0) {
    const warnings = hyungInterpretations.slice(0, 2).map(s => s.advice);
    parts.push(`흉신 ${hyungInterpretations.length}개 (${hyungSin.join(', ')}) 주의가 필요합니다. ${warnings.join(' ')}`);
  }

  return parts.join(' ');
}
