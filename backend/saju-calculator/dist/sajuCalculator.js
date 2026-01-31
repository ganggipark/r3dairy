"use strict";
/**
 * 사주 계산 모듈 (만세력)
 *
 * 정확한 사주(四柱) 계산:
 * - 년주: 입춘 기준 60갑자 순환
 * - 월주: 절기 기준 월간 계산
 * - 일주: 1900년 1월 1일 갑술 기준
 * - 시주: 야자시(夜子時) 규칙 + 진태양시 보정
 *
 * @author SajuApp
 * @version 1.0.0
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.SIXTY_CYCLE = exports.EARTHLY_BRANCHES = exports.HEAVENLY_STEMS = void 0;
exports.calculateDayPillar = calculateDayPillar;
exports.calculateFourPillars = calculateFourPillars;
exports.formatFourPillars = formatFourPillars;
exports.calculateFiveElements = calculateFiveElements;
exports.getDayMaster = getDayMaster;
exports.getZodiac = getZodiac;
const lunarCalendar_1 = require("./lunarCalendar");
// ============================================================
// 상수 정의
// ============================================================
/** 천간(天干) - 10개 */
exports.HEAVENLY_STEMS = [
    '갑', '을', '병', '정', '무', '기', '경', '신', '임', '계',
];
/** 지지(地支) - 12개 */
exports.EARTHLY_BRANCHES = [
    '자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해',
];
/** 60갑자 순환표 */
exports.SIXTY_CYCLE = [
    '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유',
    '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미',
    '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사',
    '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘',
    '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축',
    '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해',
];
/** 월주 계산용 - 년간에 따른 월간 */
const MONTHLY_STEMS = {
    '갑': ['병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유', '갑술', '을해', '병자', '정축'],
    '을': ['무인', '기묘', '경진', '신사', '임오', '계미', '갑신', '을유', '병술', '정해', '무자', '기축'],
    '병': ['경인', '신묘', '임진', '계사', '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축'],
    '정': ['임인', '계묘', '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축'],
    '무': ['갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해', '갑자', '을축'],
    '기': ['병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유', '갑술', '을해', '병자', '정축'],
    '경': ['무인', '기묘', '경진', '신사', '임오', '계미', '갑신', '을유', '병술', '정해', '무자', '기축'],
    '신': ['경인', '신묘', '임진', '계사', '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축'],
    '임': ['임인', '계묘', '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축'],
    '계': ['갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해', '갑자', '을축'],
};
/** 시주 계산용 - 일간에 따른 시간 */
const HOURLY_STEMS = {
    '갑': ['갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유', '갑술', '을해'],
    '을': ['병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미', '갑신', '을유', '병술', '정해'],
    '병': ['무자', '기축', '경인', '신묘', '임진', '계사', '갑오', '을미', '병신', '정유', '무술', '기해'],
    '정': ['경자', '신축', '임인', '계묘', '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해'],
    '무': ['임자', '계축', '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해'],
    '기': ['갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유', '갑술', '을해'],
    '경': ['병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미', '갑신', '을유', '병술', '정해'],
    '신': ['무자', '기축', '경인', '신묘', '임진', '계사', '갑오', '을미', '병신', '정유', '무술', '기해'],
    '임': ['경자', '신축', '임인', '계묘', '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해'],
    '계': ['임자', '계축', '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해'],
};
/** 주요 도시 경도 데이터 */
const CITY_LONGITUDES = {
    '서울': 126.978, '부산': 129.076, '인천': 126.705,
    '대구': 128.601, '대전': 127.385, '광주': 126.853,
    '울산': 129.311, '평양': 125.763, '기본': 126.978,
};
const KST_STANDARD_LONGITUDE = 135.0;
/**
 * 진태양시 보정
 */
function applyTrueSolarTime(hour, minute, cityName = '서울') {
    const longitude = CITY_LONGITUDES[cityName] || CITY_LONGITUDES['기본'];
    const correctionMinutes = (longitude - KST_STANDARD_LONGITUDE) * 4;
    let totalMinutes = hour * 60 + minute + correctionMinutes;
    while (totalMinutes < 0)
        totalMinutes += 24 * 60;
    while (totalMinutes >= 24 * 60)
        totalMinutes -= 24 * 60;
    return {
        adjustedHour: Math.floor(totalMinutes / 60),
        adjustedMinute: Math.floor(totalMinutes % 60),
    };
}
// ============================================================
// 계산 함수
// ============================================================
/**
 * 년주 계산 - 입춘(立春) 기준
 */
function calculateYearPillar(year, month, day) {
    let adjustedYear = year;
    if (month === 1 || (month === 2 && day < 4)) {
        adjustedYear -= 1;
    }
    const baseYear = 1924;
    const yearDiff = adjustedYear - baseYear;
    let cycleIndex = yearDiff % 60;
    if (cycleIndex < 0) {
        cycleIndex += 60;
    }
    const combined = exports.SIXTY_CYCLE[cycleIndex];
    return {
        heavenly: combined[0],
        earthly: combined[1],
        combined,
    };
}
/**
 * 절기 기준 월 계산 (근사값)
 */
function getSolarMonth(month, day) {
    if (month === 1)
        return day >= 6 ? 12 : 11;
    if (month === 2)
        return day >= 4 ? 1 : 12;
    if (month === 3)
        return day >= 6 ? 2 : 1;
    if (month === 4)
        return day >= 5 ? 3 : 2;
    if (month === 5)
        return day >= 6 ? 4 : 3;
    if (month === 6)
        return day >= 6 ? 5 : 4;
    if (month === 7)
        return day >= 7 ? 6 : 5;
    if (month === 8)
        return day >= 8 ? 7 : 6;
    if (month === 9)
        return day >= 8 ? 8 : 7;
    if (month === 10)
        return day >= 8 ? 9 : 8;
    if (month === 11)
        return day >= 7 ? 10 : 9;
    if (month === 12)
        return day >= 7 ? 11 : 10;
    return month;
}
/**
 * 월주 계산
 */
function calculateMonthPillar(year, month, day) {
    const yearPillar = calculateYearPillar(year, month, day);
    const yearStem = yearPillar.heavenly;
    const solarMonth = getSolarMonth(month, day);
    const monthIndex = solarMonth - 1;
    const monthStems = MONTHLY_STEMS[yearStem];
    if (!monthStems) {
        return { heavenly: '갑', earthly: '자', combined: '갑자' };
    }
    const monthStem = monthStems[monthIndex];
    if (!monthStem) {
        return { heavenly: '갑', earthly: '자', combined: '갑자' };
    }
    return {
        heavenly: monthStem[0],
        earthly: monthStem[1],
        combined: monthStem,
    };
}
/**
 * 일주 계산
 * 기준일: 1900년 1월 1일 = 갑술(甲戌, index 10)
 */
function calculateDayPillar(year, month, day) {
    const baseDate = Date.UTC(1900, 0, 1);
    const targetDate = Date.UTC(year, month - 1, day);
    const dayDiff = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24));
    let cycleIndex = (10 + dayDiff) % 60;
    if (cycleIndex < 0) {
        cycleIndex += 60;
    }
    const combined = exports.SIXTY_CYCLE[cycleIndex];
    return {
        heavenly: combined[0],
        earthly: combined[1],
        combined,
    };
}
/**
 * 시주 계산 (야자시 적용)
 */
function calculateHourPillar(year, month, day, hour, minute = 0) {
    const time = hour + minute / 60;
    let actualYear = year;
    let actualMonth = month;
    let actualDay = day;
    if (time >= 23) {
        const nextDate = new Date(year, month - 1, day + 1);
        actualYear = nextDate.getFullYear();
        actualMonth = nextDate.getMonth() + 1;
        actualDay = nextDate.getDate();
    }
    const dayPillar = calculateDayPillar(actualYear, actualMonth, actualDay);
    const dayStem = dayPillar.heavenly;
    let hourIndex;
    if (time >= 23 || time < 1)
        hourIndex = 0;
    else if (time < 3)
        hourIndex = 1;
    else if (time < 5)
        hourIndex = 2;
    else if (time < 7)
        hourIndex = 3;
    else if (time < 9)
        hourIndex = 4;
    else if (time < 11)
        hourIndex = 5;
    else if (time < 13)
        hourIndex = 6;
    else if (time < 15)
        hourIndex = 7;
    else if (time < 17)
        hourIndex = 8;
    else if (time < 19)
        hourIndex = 9;
    else if (time < 21)
        hourIndex = 10;
    else
        hourIndex = 11;
    const hourStems = HOURLY_STEMS[dayStem];
    if (!hourStems) {
        return { heavenly: '갑', earthly: '자', combined: '갑자' };
    }
    const combined = hourStems[hourIndex];
    return {
        heavenly: combined[0],
        earthly: combined[1],
        combined,
    };
}
// ============================================================
// 메인 API
// ============================================================
/**
 * 사주팔자 계산 (메인 함수)
 */
function calculateFourPillars(birthInfo, useTrueSolarTime = true, birthPlace = '서울') {
    let { year, month, day, hour, minute = 0 } = birthInfo;
    if (birthInfo.isLunar) {
        try {
            const solarDate = (0, lunarCalendar_1.lunarToSolar)(year, month, day, birthInfo.isLeapMonth || false);
            year = solarDate.getFullYear();
            month = solarDate.getMonth() + 1;
            day = solarDate.getDate();
        }
        catch (error) {
            console.error('음력 변환 오류:', error);
        }
    }
    let adjustedHour = hour;
    let adjustedMinute = minute;
    if (useTrueSolarTime) {
        const trueSolarResult = applyTrueSolarTime(hour, minute, birthPlace);
        adjustedHour = trueSolarResult.adjustedHour;
        adjustedMinute = trueSolarResult.adjustedMinute;
    }
    return {
        year: calculateYearPillar(year, month, day),
        month: calculateMonthPillar(year, month, day),
        day: calculateDayPillar(year, month, day),
        hour: calculateHourPillar(year, month, day, adjustedHour, adjustedMinute),
    };
}
/**
 * 사주 결과를 문자열로 포맷팅
 */
function formatFourPillars(pillars) {
    return `${pillars.year.combined}년 ${pillars.month.combined}월 ${pillars.day.combined}일 ${pillars.hour.combined}시`;
}
/**
 * 오행 균형 계산
 */
function calculateFiveElements(pillars) {
    const elements = { wood: 0, fire: 0, earth: 0, metal: 0, water: 0 };
    const elementMap = {
        '갑': 'wood', '을': 'wood', '인': 'wood', '묘': 'wood',
        '병': 'fire', '정': 'fire', '사': 'fire', '오': 'fire',
        '무': 'earth', '기': 'earth', '진': 'earth', '술': 'earth', '축': 'earth', '미': 'earth',
        '경': 'metal', '신': 'metal', '유': 'metal',
        '임': 'water', '계': 'water', '해': 'water', '자': 'water',
    };
    const allChars = [
        pillars.year.heavenly, pillars.year.earthly,
        pillars.month.heavenly, pillars.month.earthly,
        pillars.day.heavenly, pillars.day.earthly,
        pillars.hour.heavenly, pillars.hour.earthly,
    ];
    allChars.forEach(char => {
        const element = elementMap[char];
        if (element) {
            elements[element] += 12.5;
        }
    });
    return elements;
}
/**
 * 일간(日干) 추출
 */
function getDayMaster(pillars) {
    return pillars.day.heavenly;
}
/**
 * 띠(12지신) 반환
 */
function getZodiac(year) {
    const zodiacNames = [
        '쥐', '소', '호랑이', '토끼', '용', '뱀',
        '말', '양', '원숭이', '닭', '개', '돼지'
    ];
    const baseYear = 1924;
    let index = (year - baseYear) % 12;
    if (index < 0)
        index += 12;
    return zodiacNames[index];
}
//# sourceMappingURL=sajuCalculator.js.map