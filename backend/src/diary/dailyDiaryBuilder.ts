/**
 * 일일 다이어리 빌더
 * 
 * 사주 엔진과 기문둔갑 엔진을 활용하여 하루치 다이어리 표준 JSON 생성
 */

import * as path from 'path';
import * as fs from 'fs';
import {
  DailyDiaryPayload,
  CalendarInfo,
  SajuInfo,
  QimenInfo,
  NlpContent,
  BuilderInput,
  FourPillars,
  Pillar,
  SajuSummary,
  SajuDomains,
  DomainAnalysis,
  QimenDailySummary,
  HourlyQimen,
  Activity,
  MindsetGuide,
  ActionGuide,
  LunarDateInfo,
  LeftPage,
  RightPage,
  BottomPanel,
  TimeSlot
} from './types';

// Import real engines - using absolute paths for reliability
const sajuCalculator = require('../../saju-calculator/dist/calculators/completeSajuCalculator');
const lunarCalc = require('../../saju-calculator/dist/calculators/lunarCalendar');
const { calculateCompleteSajuData } = sajuCalculator;
const { solarToLunar } = lunarCalc;

// 타입 정의
interface CompleteSajuData {
  fourPillars: any;
  [key: string]: any;
}

interface SajuCalculationInput {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  gender: 'male' | 'female';
  isLunar: boolean;
  useTrueSolarTime: boolean;
  birthPlace: string;
}

// ============================================================
// 헬퍼 함수
// ============================================================

/**
 * 날짜에서 요일 추출
 */
function getWeekday(dateStr: string): string {
  const weekdays = ['일', '월', '화', '수', '목', '금', '토'];
  const date = new Date(dateStr);
  return weekdays[date.getDay()];
}

/**
 * TypeScript 사주 계산기 호출 (직접 import 방식)
 */
function callSajuCalculator(date: string, birth?: BuilderInput['birth']): CompleteSajuData | null {
  try {
    // 생년월일 정보 준비
    const birthInfo = birth || {
      year: 1971,
      month: 11,
      day: 17,
      hour: 4,
      minute: 0,
      isLunar: false
    };
    
    // 사주 계산 입력 데이터
    const sajuInput: SajuCalculationInput = {
      year: birthInfo.year,
      month: birthInfo.month,
      day: birthInfo.day,
      hour: birthInfo.hour || 0,
      minute: birthInfo.minute || 0,
      gender: 'male', // 기본값
      isLunar: birthInfo.isLunar || false,
      useTrueSolarTime: true,
      birthPlace: birthInfo.birthPlace || '서울'
    };
    
    // 직접 함수 호출
    const result = calculateCompleteSajuData(sajuInput);
    return result;
  } catch (error) {
    console.error('사주 계산 오류:', error);
    return null;
  }
}

/**
 * Python 기문둔갑 계산기 호출 (파일 기반 실행)
 */
async function callQimenCalculator(date: string, birth?: BuilderInput['birth']): Promise<any> {
  try {
    // Backend 루트 경로 계산  
    const backendRoot = 'C:/Users/USER/dev/diary-PJ/backend';
    
    // Python 스크립트 내용 준비
    const pythonScript = `
import sys
import json
from datetime import date

# 경로 추가 - backend 루트로 설정
sys.path.insert(0, r'${backendRoot}')

from src.rhythm.qimen_complete import get_qimen_summary, get_daily_complete_qimen

birth_date = date(${birth?.year || 1971}, ${birth?.month || 11}, ${birth?.day || 17})
target_date = date.fromisoformat('${date}')

summary = get_qimen_summary(birth_date, target_date)
hourly = get_daily_complete_qimen(birth_date, target_date)

# summary가 dataclass인 경우 처리
summary_dict = {}
if hasattr(summary, '__dict__'):
    summary_dict = summary.__dict__
else:
    # dataclass 필드 추출
    summary_dict = {
        'best_hour': getattr(summary, 'best_hour', '09-11시'),
        'best_direction': getattr(summary, 'best_direction', '동'),
        'avoid_hour': getattr(summary, 'avoid_hour', '15-17시'),
        'avoid_direction': getattr(summary, 'avoid_direction', '서'),
        'daily_quality': getattr(summary, 'daily_quality', 'good'),
        'guidance': getattr(summary, 'user_guidance', '오늘의 기문둔갑 운세입니다')
    }

result = {
    'summary': summary_dict,
    'hourly': [
        {
            'hour_start': h.hour_start,
            'hour_end': h.hour_end,
            'hour_branch': h.hour_branch,
            'quality': h.overall_quality,
            'best_direction': h.best_palace.direction_ko if h.best_palace else '중앙',
            'energy': h.best_palace.quality_score if h.best_palace else 50,
            'guidance': h.user_guidance
        }
        for h in hourly
    ]
}

print(json.dumps(result, ensure_ascii=False))
`;
    
    // 임시 파일을 backend 디렉토리에 저장
    const tempFile = path.join(backendRoot, 'temp_qimen.py');
    fs.writeFileSync(tempFile, pythonScript);
    
    // Python 실행 - backend 디렉토리에서 실행
    const { exec } = await import('child_process');
    const { promisify } = await import('util');
    const execAsync = promisify(exec);
    
    const { stdout, stderr } = await execAsync(`cd "${backendRoot}" && python temp_qimen.py`);
    
    // 임시 파일 삭제
    fs.unlinkSync(tempFile);
    
    if (stderr) {
      console.error('기문둔갑 계산 경고:', stderr);
    }
    
    return JSON.parse(stdout);
  } catch (error) {
    console.error('기문둔갑 계산 오류:', error);
    return null;
  }
}

/**
 * 음력 날짜 계산
 */
function calculateLunarDate(dateStr: string): LunarDateInfo | null {
  try {
    const date = new Date(dateStr);
    const lunar = solarToLunar(date);
    
    return {
      year: lunar.year,
      month: lunar.month,
      day: lunar.day,
      isLeapMonth: lunar.isLeapMonth || false,
      displayText: `음력 ${lunar.month}월 ${lunar.day}일${lunar.isLeapMonth ? ' (윤달)' : ''}`
    };
  } catch (error) {
    console.error('음력 계산 오류:', error);
    return null;
  }
}

// ============================================================
// 섹션별 빌더 함수
// ============================================================

/**
 * Calendar 섹션 생성
 */
function buildCalendarSection(dateStr: string): CalendarInfo {
  const lunarDate = calculateLunarDate(dateStr);
  
  return {
    solarDate: dateStr,
    weekday: getWeekday(dateStr),
    lunarDate
  };
}

/**
 * Saju 섹션 생성
 */
function buildSajuSection(date: string, birth?: BuilderInput['birth']): SajuInfo {
  const sajuData = callSajuCalculator(date, birth);
  
  // 기본값 구조
  const defaultSaju: SajuInfo = {
    pillars: {
      year: null,
      month: null,
      day: {
        heavenlyStem: '갑',
        earthlyBranch: '자',
        combined: '갑자',
        element: '목'
      },
      hour: null
    },
    dayMaster: '갑',
    summary: {
      mainCharacteristics: ['안정적', '신중함', '계획적'],
      elementBalance: {
        wood: 2,
        fire: 1,
        earth: 2,
        metal: 1,
        water: 2
      },
      dayMasterStrength: 'balanced'
    },
    domains: {
      health: {
        score: 75,
        status: 'good',
        advice: '규칙적인 생활 리듬을 유지하세요'
      },
      wealth: {
        score: 70,
        status: 'good',
        advice: '재물운이 안정적입니다'
      },
      relationship: {
        score: 80,
        status: 'good',
        advice: '인간관계가 원만합니다'
      },
      career: {
        score: 75,
        status: 'good',
        advice: '업무 진행이 순조롭습니다'
      }
    },
    fortuneLayers: null
  };
  
  if (!sajuData) {
    return defaultSaju;
  }
  
  // 실제 사주 데이터 매핑
  try {
    const pillars: FourPillars = {
      year: sajuData.fourPillars?.year ? {
        heavenlyStem: sajuData.fourPillars.year.gan,
        earthlyBranch: sajuData.fourPillars.year.ji,
        combined: sajuData.fourPillars.year.ganJi,
        element: sajuData.fourPillars.year.ganOhHaeng
      } : null,
      month: sajuData.fourPillars?.month ? {
        heavenlyStem: sajuData.fourPillars.month.gan,
        earthlyBranch: sajuData.fourPillars.month.ji,
        combined: sajuData.fourPillars.month.ganJi,
        element: sajuData.fourPillars.month.ganOhHaeng
      } : null,
      day: {
        heavenlyStem: sajuData.fourPillars?.day?.gan || '갑',
        earthlyBranch: sajuData.fourPillars?.day?.ji || '자',
        combined: sajuData.fourPillars?.day?.ganJi || '갑자',
        element: sajuData.fourPillars?.day?.ganOhHaeng || '목'
      },
      hour: sajuData.fourPillars?.time ? {
        heavenlyStem: sajuData.fourPillars.time.gan,
        earthlyBranch: sajuData.fourPillars.time.ji,
        combined: sajuData.fourPillars.time.ganJi,
        element: sajuData.fourPillars.time.ganOhHaeng
      } : null
    };
    
    return {
      pillars,
      dayMaster: sajuData.fourPillars?.day?.gan || '갑',
      summary: {
        mainCharacteristics: defaultSaju.summary.mainCharacteristics,
        elementBalance: defaultSaju.summary.elementBalance, // 일단 기본값 사용
        dayMasterStrength: 'balanced'
      },
      domains: defaultSaju.domains,
      fortuneLayers: null // 추후 구현
    };
  } catch (error) {
    console.error('사주 데이터 매핑 오류:', error);
    return defaultSaju;
  }
}

/**
 * QiMen 섹션 생성
 */
async function buildQimenSection(date: string, birth?: BuilderInput['birth']): Promise<QimenInfo> {
  const qimenData = await callQimenCalculator(date, birth);
  
  // 기본값 구조
  const defaultQimen: QimenInfo = {
    dailySummary: {
      bestHour: '09-11시',
      bestDirection: '동',
      avoidHour: '15-17시',
      avoidDirection: '서',
      overallQuality: 'good',
      guidance: '오늘은 전반적으로 좋은 날입니다'
    },
    hourlyAnalysis: [],
    bestActivities: [
      {
        type: '중요한 결정',
        description: '오전 시간을 활용하세요',
        priority: 1
      }
    ],
    avoidActivities: [
      {
        type: '새로운 시작',
        description: '오후 3시 이후는 피하세요',
        priority: 1
      }
    ]
  };
  
  if (!qimenData) {
    return defaultQimen;
  }
  
  try {
    // 실제 기문둔갑 데이터 매핑
    const dailySummary: QimenDailySummary = {
      bestHour: qimenData.summary.best_hour || '09-11시',
      bestDirection: qimenData.summary.best_direction || '동',
      avoidHour: qimenData.summary.avoid_hour || '15-17시',
      avoidDirection: qimenData.summary.avoid_direction || '서',
      overallQuality: qimenData.summary.daily_quality === 'excellent' ? 'excellent' :
                      qimenData.summary.daily_quality === 'good' ? 'good' :
                      qimenData.summary.daily_quality === 'caution' ? 'caution' : 'neutral',
      guidance: qimenData.summary.guidance || '오늘의 기문둔갑 운세입니다'
    };
    
    const hourlyAnalysis: HourlyQimen[] = qimenData.hourly.map((h: any) => ({
      timeSlot: `${String(h.hour_start).padStart(2, '0')}-${String(h.hour_end).padStart(2, '0')}시`,
      branch: h.hour_branch || '자',
      quality: h.quality === 'excellent' || h.quality === 'good' ? 'good' :
               h.quality === 'bad' || h.quality === 'caution' ? 'avoid' : 'neutral',
      direction: h.best_direction || '중앙',
      energyLevel: Math.round(h.energy / 10) || 5,
      description: h.guidance || '평범한 시간대입니다'
    }));
    
    return {
      dailySummary,
      hourlyAnalysis: hourlyAnalysis.slice(0, 12), // 12시진만
      bestActivities: defaultQimen.bestActivities,
      avoidActivities: defaultQimen.avoidActivities
    };
  } catch (error) {
    console.error('기문둔갑 데이터 매핑 오류:', error);
    return defaultQimen;
  }
}

/**
 * NLP 섹션 생성
 */
function buildNlpSection(saju: SajuInfo, qimen: QimenInfo): NlpContent {
  // 사주와 기문둔갑 정보를 기반으로 NLP 콘텐츠 생성
  const quality = qimen.dailySummary.overallQuality;
  
  const themes: Record<string, string> = {
    excellent: '도약과 성취의 날',
    good: '안정과 성장의 날',
    neutral: '균형과 조화의 날',
    caution: '신중과 내실의 날'
  };
  
  const messages: Record<string, string> = {
    excellent: '오늘은 모든 일이 순조롭게 풀리는 날입니다. 적극적으로 도전하세요.',
    good: '좋은 기운이 함께하는 날입니다. 계획한 일을 추진하기 좋습니다.',
    neutral: '평온한 하루가 예상됩니다. 일상의 루틴을 충실히 하세요.',
    caution: '조심스럽게 행동해야 하는 날입니다. 중요한 결정은 신중히 하세요.'
  };
  
  return {
    dailyTheme: themes[quality],
    coreMessage: messages[quality],
    mindset: {
      focusEmotion: quality === 'excellent' || quality === 'good' ? '자신감' : '차분함',
      cautionEmotion: quality === 'caution' ? '조급함' : '나태함',
      emotionTip: '감정의 균형을 유지하며 하루를 보내세요'
    },
    actionGuides: [
      {
        timeOfDay: 'morning',
        recommendation: `${qimen.dailySummary.bestHour}에 중요한 일을 처리하세요`,
        reason: `${qimen.dailySummary.bestDirection}쪽 방향의 에너지가 좋습니다`
      },
      {
        timeOfDay: 'afternoon',
        recommendation: '점심 후 가벼운 산책으로 에너지를 충전하세요',
        reason: '오후의 에너지 밸런스를 맞추기 위함입니다'
      },
      {
        timeOfDay: 'evening',
        recommendation: '하루를 정리하며 내일을 준비하세요',
        reason: '저녁 시간은 성찰과 계획에 적합합니다'
      }
    ],
    reflectionQuestions: [
      '오늘 가장 감사한 일은 무엇인가요?',
      '내일을 위해 준비할 것은 무엇인가요?',
      '오늘의 경험에서 배운 점은 무엇인가요?'
    ],
    dailyQuote: {
      text: '매일 조금씩 나아가는 것이 큰 변화를 만든다',
      author: '동양 격언'
    }
  };
}

// ============================================================
// 메인 빌더 함수
// ============================================================

/**
 * 일일 다이어리 페이로드 생성
 */
export async function buildDailyDiaryPayload(input: BuilderInput): Promise<DailyDiaryPayload> {
  const { date, birth, options = {} } = input;
  
  // 날짜 유효성 검증
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) {
    throw new Error(`Invalid date format: ${date}`);
  }
  
  // Calendar와 Saju는 동기, QiMen은 비동기
  const calendar = buildCalendarSection(date);
  const saju = options.includeSaju !== false ? buildSajuSection(date, birth) : buildSajuSection(date, undefined);
  const qimen = await (options.includeQimen !== false ? buildQimenSection(date, birth) : buildQimenSection(date, undefined));
  
  // NLP 콘텐츠 생성
  const nlp = options.includeNlp !== false ? buildNlpSection(saju, qimen) : buildNlpSection(saju, qimen);
  
  // Page Layout 매핑
  const leftPage = mapToLeftPage(saju, qimen);
  const rightPage = mapToRightPage(qimen);
  const bottomPanel = mapToBottomPanel(nlp);
  
  // 최종 페이로드 구성
  const payload: DailyDiaryPayload = {
    date,
    generatedAt: new Date().toISOString(),
    version: '1.0.0',
    calendar,
    leftPage,
    rightPage,
    bottomPanel,
    metadata: {
      generationMethod: 'realtime',
      cacheExpiry: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24시간 후
    }
  };
  
  return payload;
}

// ============================================================
// Page Layout Mappers
// ============================================================

/**
 * LeftPage 생성
 */
function mapToLeftPage(saju: SajuInfo, qimen: QimenInfo): LeftPage {
  // 주의사항 생성
  const cautions: string[] = [];
  if (qimen.dailySummary.avoidHour) {
    cautions.push(`${qimen.dailySummary.avoidHour}에는 중요한 결정을 피하세요`);
  }
  if (qimen.dailySummary.avoidDirection) {
    cautions.push(`${qimen.dailySummary.avoidDirection}쪽 방향은 오늘 피하는 것이 좋습니다`);
  }
  // 운세가 caution일 경우 추가 주의사항
  if (qimen.dailySummary.overallQuality === 'caution') {
    cautions.push('오늘은 전반적으로 신중한 행동이 필요합니다');
  }
  
  // 권장사항 생성
  const recommendations: string[] = [];
  if (qimen.dailySummary.bestHour) {
    recommendations.push(`${qimen.dailySummary.bestHour}에 중요한 일을 진행하세요`);
  }
  if (qimen.dailySummary.bestDirection) {
    recommendations.push(`${qimen.dailySummary.bestDirection}쪽 방향이 오늘 좋습니다`);
  }
  // 도메인 기반 권장사항
  Object.entries(saju.domains).forEach(([domain, analysis]) => {
    if (analysis.score >= 80) {
      recommendations.push(analysis.advice);
    }
  });
  
  return {
    sajuSummary: saju.summary,
    fortuneLayers: saju.fortuneLayers,
    lifeAreas: saju.domains,
    cautions: cautions.slice(0, 3), // 최대 3개
    recommendations: recommendations.slice(0, 3) // 최대 3개
  };
}

/**
 * RightPage 생성
 */
function mapToRightPage(qimen: QimenInfo): RightPage {
  // TimeSlots 생성 (2시간 단위)
  const timeSlots: TimeSlot[] = [];
  const hours = ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'];
  
  hours.forEach((hour, index) => {
    const hourNum = parseInt(hour);
    const label = `${hour.substring(0, 2)}-${String(hourNum + 2).padStart(2, '0')}시`;
    
    // 해당 시간대의 기문 정보 찾기
    const qimenHour = qimen.hourlyAnalysis.find(h => 
      h.timeSlot.startsWith(hour.substring(0, 2))
    );
    
    timeSlots.push({
      time: hour,
      label: label,
      qimenLabel: qimenHour ? 
        (qimenHour.quality === 'good' ? '길' : 
         qimenHour.quality === 'avoid' ? '흉' : '평') : '평',
      note: ''
    });
  });
  
  // 좋은/나쁜 시간대 추출
  const goodHours: string[] = [];
  const badHours: string[] = [];
  
  qimen.hourlyAnalysis.forEach(hour => {
    if (hour.quality === 'good') {
      goodHours.push(hour.timeSlot);
    } else if (hour.quality === 'avoid') {
      badHours.push(hour.timeSlot);
    }
  });
  
  // 좋은/나쁜 방향
  const goodDirections: string[] = qimen.dailySummary.bestDirection ? 
    [qimen.dailySummary.bestDirection] : [];
  const badDirections: string[] = qimen.dailySummary.avoidDirection ? 
    [qimen.dailySummary.avoidDirection] : [];
  
  return {
    timeSlots,
    goodHours: goodHours.slice(0, 3),
    badHours: badHours.slice(0, 3),
    goodDirections,
    badDirections
  };
}

/**
 * BottomPanel 생성
 */
function mapToBottomPanel(nlp: NlpContent): BottomPanel {
  return {
    mindset: nlp.mindset,
    journalPrompt: nlp.reflectionQuestions,
    affirmation: nlp.dailyQuote ? 
      `${nlp.dailyQuote.text} - ${nlp.dailyQuote.author}` : 
      nlp.coreMessage
  };
}

// ============================================================
// Export
// ============================================================

export default buildDailyDiaryPayload;
export * from './types';