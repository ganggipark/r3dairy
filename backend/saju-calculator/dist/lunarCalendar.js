/**
 * 음양력 변환 모듈
 *
 * 의존성: korean-lunar-calendar 패키지 필요
 * npm install korean-lunar-calendar
 *
 * @author SajuApp
 * @version 1.0.0
 */
import KoreanLunarCalendar from 'korean-lunar-calendar';
/**
 * 양력 날짜를 음력으로 변환
 * @param date 양력 Date 객체
 * @returns 음력 날짜 정보
 */
export function solarToLunar(date) {
    try {
        const calendar = new KoreanLunarCalendar();
        calendar.setSolarDate(date.getFullYear(), date.getMonth() + 1, date.getDate());
        const lunar = calendar.lunarCalendar;
        return {
            year: lunar.year || date.getFullYear(),
            month: lunar.month || date.getMonth() + 1,
            day: lunar.day || date.getDate(),
            isLeapMonth: lunar.intercalation || false,
        };
    }
    catch (error) {
        console.error('Error converting solar to lunar:', error);
        return {
            year: date.getFullYear(),
            month: date.getMonth() + 1,
            day: date.getDate(),
            isLeapMonth: false,
        };
    }
}
/**
 * 음력 날짜를 양력으로 변환
 * @param year 음력 연도
 * @param month 음력 월
 * @param day 음력 일
 * @param isLeapMonth 윤달 여부
 * @returns 양력 Date 객체
 */
export function lunarToSolar(year, month, day, isLeapMonth = false) {
    try {
        const calendar = new KoreanLunarCalendar();
        calendar.setLunarDate(year, month, day, isLeapMonth);
        const solar = calendar.solarCalendar;
        return new Date(solar.year || year, (solar.month || month) - 1, solar.day || day);
    }
    catch (error) {
        console.error('Error converting lunar to solar:', error);
        return new Date(year, month - 1, day);
    }
}
/**
 * 음력 날짜를 포맷팅된 문자열로 반환
 */
export function formatLunarDate(date, includeYear = false) {
    const lunar = solarToLunar(date);
    if (includeYear) {
        return `음 ${lunar.year}.${lunar.month}.${lunar.day}${lunar.isLeapMonth ? '(윤)' : ''}`;
    }
    return `음 ${lunar.month}.${lunar.day}${lunar.isLeapMonth ? '(윤)' : ''}`;
}
/**
 * 24절기 데이터 (양력 기준 근사값)
 */
export const SOLAR_TERMS = {
    '입춘': { month: 2, day: 4 },
    '우수': { month: 2, day: 19 },
    '경칩': { month: 3, day: 6 },
    '춘분': { month: 3, day: 21 },
    '청명': { month: 4, day: 5 },
    '곡우': { month: 4, day: 20 },
    '입하': { month: 5, day: 6 },
    '소만': { month: 5, day: 21 },
    '망종': { month: 6, day: 6 },
    '하지': { month: 6, day: 21 },
    '소서': { month: 7, day: 7 },
    '대서': { month: 7, day: 23 },
    '입추': { month: 8, day: 8 },
    '처서': { month: 8, day: 23 },
    '백로': { month: 9, day: 8 },
    '추분': { month: 9, day: 23 },
    '한로': { month: 10, day: 8 },
    '상강': { month: 10, day: 23 },
    '입동': { month: 11, day: 8 },
    '소설': { month: 11, day: 22 },
    '대설': { month: 12, day: 7 },
    '동지': { month: 12, day: 22 },
    '소한': { month: 1, day: 6 },
    '대한': { month: 1, day: 20 },
};
/**
 * 24절기인지 확인
 */
export function getSolarTerm(date) {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    for (const [term, termDate] of Object.entries(SOLAR_TERMS)) {
        if (termDate.month === month && termDate.day === day) {
            return term;
        }
    }
    return null;
}
/**
 * 특별한 음력 날짜인지 확인 (명절)
 */
export function getSpecialLunarDay(date) {
    const solarTerm = getSolarTerm(date);
    if (solarTerm)
        return solarTerm;
    const lunar = solarToLunar(date);
    if (lunar.month === 1 && lunar.day === 1)
        return '설날';
    if (lunar.month === 1 && lunar.day === 15)
        return '정월대보름';
    if (lunar.month === 5 && lunar.day === 5)
        return '단오';
    if (lunar.month === 7 && lunar.day === 7)
        return '칠석';
    if (lunar.month === 7 && lunar.day === 15)
        return '백중';
    if (lunar.month === 8 && lunar.day === 15)
        return '추석';
    if (lunar.month === 9 && lunar.day === 9)
        return '중양절';
    return null;
}
/**
 * 음력 월의 한글 이름 반환
 */
export function getLunarMonthName(month) {
    const monthNames = [
        '정월', '이월', '삼월', '사월', '오월', '유월',
        '칠월', '팔월', '구월', '시월', '동월', '섣달',
    ];
    return monthNames[month - 1] || `${month}월`;
}
//# sourceMappingURL=lunarCalendar.js.map