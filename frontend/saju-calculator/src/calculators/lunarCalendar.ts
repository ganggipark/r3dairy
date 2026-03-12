import KoreanLunarCalendar from 'korean-lunar-calendar';

export interface LunarDate {
  year: number
  month: number
  day: number
  isLeapMonth: boolean
  zodiac: string // 띠
  chineseYear: string // 간지
}

/**
 * 양력 날짜를 음력으로 변환
 */
export const solarToLunar = (date: Date): LunarDate => {
  try {
    const calendar = new KoreanLunarCalendar();

    calendar.setSolarDate(
      date.getFullYear(),
      date.getMonth() + 1, // JavaScript months are 0-indexed
      date.getDate(),
    );

    // lunarCalendar 속성에서 값 가져오기 (메서드가 아님)
    const lunar = (calendar as any).lunarCalendar;

    return {
      year: lunar.year || date.getFullYear(),
      month: lunar.month || date.getMonth() + 1,
      day: lunar.day || date.getDate(),
      isLeapMonth: lunar.intercalation || false,
      zodiac: '', // 띠 정보는 별도 계산 필요
      chineseYear: '', // 간지 정보는 별도 계산 필요
    };
  } catch (error) {
    console.error('Error converting solar to lunar:', error);
    // 에러 시 기본값 반환
    return {
      year: date.getFullYear(),
      month: date.getMonth() + 1,
      day: date.getDate(),
      isLeapMonth: false,
      zodiac: '',
      chineseYear: '',
    };
  }
};

/**
 * 음력 날짜를 양력으로 변환
 */
export const lunarToSolar = (year: number, month: number, day: number, isLeapMonth: boolean = false): Date => {
  try {
    const calendar = new KoreanLunarCalendar();

    calendar.setLunarDate(year, month, day, isLeapMonth);

    // solarCalendar 속성에서 값 가져오기 (메서드가 아님)
    const solar = (calendar as any).solarCalendar;

    return new Date(
      solar.year || year,
      (solar.month || month) - 1, // Convert to 0-indexed
      solar.day || day,
    );
  } catch (error) {
    console.error('Error converting lunar to solar:', error);
    // 에러 시 기본값 반환
    return new Date(year, month - 1, day);
  }
};

/**
 * 음력 날짜를 포맷팅된 문자열로 반환
 */
export const formatLunarDate = (date: Date, includeYear: boolean = false): string => {
  const lunar = solarToLunar(date);
  
  if (includeYear) {
    return `음 ${lunar.year}.${lunar.month}.${lunar.day}${lunar.isLeapMonth ? '(윤)' : ''}`;
  }
  
  return `음 ${lunar.month}.${lunar.day}${lunar.isLeapMonth ? '(윤)' : ''}`;
};

/**
 * 24절기 데이터 (양력 기준 근사값)
 */
const SOLAR_TERMS = {
  // 봄 (春)
  '입춘': { month: 2, day: 4 },   // 立春
  '우수': { month: 2, day: 19 },  // 雨水
  '경칩': { month: 3, day: 6 },   // 驚蟄
  '춘분': { month: 3, day: 21 },  // 春分
  '청명': { month: 4, day: 5 },   // 淸明
  '곡우': { month: 4, day: 20 },  // 穀雨

  // 여름 (夏)
  '입하': { month: 5, day: 6 },   // 立夏
  '소만': { month: 5, day: 21 },  // 小滿
  '망종': { month: 6, day: 6 },   // 芒種
  '하지': { month: 6, day: 21 },  // 夏至
  '소서': { month: 7, day: 7 },   // 小暑
  '대서': { month: 7, day: 23 },  // 大暑

  // 가을 (秋)
  '입추': { month: 8, day: 8 },   // 立秋
  '처서': { month: 8, day: 23 },  // 處暑
  '백로': { month: 9, day: 8 },   // 白露
  '추분': { month: 9, day: 23 },  // 秋分
  '한로': { month: 10, day: 8 },  // 寒露
  '상강': { month: 10, day: 23 }, // 霜降

  // 겨울 (冬)
  '입동': { month: 11, day: 8 },  // 立冬
  '소설': { month: 11, day: 22 }, // 小雪
  '대설': { month: 12, day: 7 },  // 大雪
  '동지': { month: 12, day: 22 }, // 冬至
  '소한': { month: 1, day: 6 },   // 小寒
  '대한': { month: 1, day: 20 },  // 大寒
};

/**
 * 24절기인지 확인
 */
export const getSolarTerm = (date: Date): string | null => {
  const month = date.getMonth() + 1; // JavaScript의 0-indexed month를 1-indexed로 변환
  const day = date.getDate();

  for (const [term, termDate] of Object.entries(SOLAR_TERMS)) {
    // 정확히 일치하는 날짜만 반환 (중복 표시 방지)
    if (termDate.month === month && termDate.day === day) {
      return term;
    }
  }

  return null;
};

/**
 * 특별한 음력 날짜인지 확인 (설날, 정월대보름, 추석 등)
 */
export const getSpecialLunarDay = (date: Date): string | null => {
  // 먼저 24절기인지 확인
  const solarTerm = getSolarTerm(date);
  if (solarTerm) {
    return solarTerm;
  }

  const lunar = solarToLunar(date);

  // 설날 (음력 1월 1일)
  if (lunar.month === 1 && lunar.day === 1) {
    return '설날';
  }

  // 정월대보름 (음력 1월 15일)
  if (lunar.month === 1 && lunar.day === 15) {
    return '정월대보름';
  }

  // 단오 (음력 5월 5일)
  if (lunar.month === 5 && lunar.day === 5) {
    return '단오';
  }

  // 칠석 (음력 7월 7일)
  if (lunar.month === 7 && lunar.day === 7) {
    return '칠석';
  }

  // 백중 (음력 7월 15일)
  if (lunar.month === 7 && lunar.day === 15) {
    return '백중';
  }

  // 추석 (음력 8월 15일)
  if (lunar.month === 8 && lunar.day === 15) {
    return '추석';
  }

  // 중양절 (음력 9월 9일)
  if (lunar.month === 9 && lunar.day === 9) {
    return '중양절';
  }

  return null;
};

/**
 * 음력 월의 한글 이름 반환
 */
export const getLunarMonthName = (month: number): string => {
  const monthNames = [
    '정월', '이월', '삼월', '사월', '오월', '유월',
    '칠월', '팔월', '구월', '시월', '동월', '섣달',
  ];
  
  return monthNames[month - 1] || `${month}월`;
};