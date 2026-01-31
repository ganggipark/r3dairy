"use strict";
/**
 * 완전한 사주 데이터 계산기
 *
 * 모든 사주 분석 데이터를 한 번에 계산하여 CompleteSajuData 구조로 반환
 *
 * @author SajuApp
 * @version 2.0.0
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.calculateCompleteSajuData = calculateCompleteSajuData;
const solarTermsCalculator_1 = require("./solarTermsCalculator");
const lunarCalendar_1 = require("./lunarCalendar");
const trueSolarTimeCalculator_1 = require("./trueSolarTimeCalculator");
// ============================================================
// 상수 정의
// ============================================================
const CHEON_GAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
const JI_JI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];
const SIXTY_CYCLE = [
    '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유',
    '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미',
    '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사',
    '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘',
    '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축',
    '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해',
];
const CHEON_GAN_OH_HAENG = {
    '갑': '목', '을': '목', '병': '화', '정': '화', '무': '토',
    '기': '토', '경': '금', '신': '금', '임': '수', '계': '수',
};
const JI_JI_OH_HAENG = {
    '인': '목', '묘': '목', '사': '화', '오': '화',
    '진': '토', '술': '토', '축': '토', '미': '토',
    '신': '금', '유': '금', '해': '수', '자': '수',
};
const JI_JI_ANIMAL = {
    '자': '쥐', '축': '소', '인': '호랑이', '묘': '토끼',
    '진': '용', '사': '뱀', '오': '말', '미': '양',
    '신': '원숭이', '유': '닭', '술': '개', '해': '돼지',
};
const JI_JI_SEASON = {
    '인': '봄', '묘': '봄', '진': '봄',
    '사': '여름', '오': '여름', '미': '여름',
    '신': '가을', '유': '가을', '술': '가을',
    '해': '겨울', '자': '겨울', '축': '겨울',
};
const TEN_GODS_RELATIONS = {
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
const HIDDEN_STEMS = {
    '자': ['계'], '축': ['기', '계', '신'], '인': ['갑', '병', '무'], '묘': ['을'],
    '진': ['무', '을', '계'], '사': ['병', '무', '경'], '오': ['정', '기'], '미': ['기', '정', '을'],
    '신': ['경', '임', '무'], '유': ['신'], '술': ['무', '신', '정'], '해': ['임', '갑'],
};
const JI_JI_CHUNG = {
    '자': '오', '오': '자', '축': '미', '미': '축',
    '인': '신', '신': '인', '묘': '유', '유': '묘',
    '진': '술', '술': '진', '사': '해', '해': '사',
};
const JI_JI_YUK_HAP = {
    '자': '축', '축': '자', '인': '해', '해': '인',
    '묘': '술', '술': '묘', '진': '유', '유': '진',
    '사': '신', '신': '사', '오': '미', '미': '오',
};
const CHEON_GAN_HAP = {
    '갑': '기', '기': '갑', '을': '경', '경': '을',
    '병': '신', '신': '병', '정': '임', '임': '정', '무': '계', '계': '무',
};
const DAY_MASTER_PERSONALITY = {
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
// 메인 계산 함수
// ============================================================
function calculateCompleteSajuData(input) {
    const { year, month, day, hour, minute = 0, gender, isLunar = false, isLeapMonth = false, useTrueSolarTime = true, birthPlace = '서울' } = input;
    const fourPillars = calculateFourPillars(year, month, day, hour, minute, isLunar, isLeapMonth, useTrueSolarTime, birthPlace);
    const ohHaeng = analyzeOhHaeng(fourPillars);
    const sipSung = analyzeSipSung(fourPillars);
    const gyeokGuk = analyzeGyeokGuk(fourPillars, ohHaeng);
    const yongSin = analyzeYongSin(gyeokGuk);
    const currentAge = new Date().getFullYear() - year;
    const daewoon = calculateDaewoon(fourPillars, year, gender, yongSin, currentAge);
    const currentYear = new Date().getFullYear();
    const currentYearSewoon = calculateSewoon(currentYear, currentAge, yongSin, daewoon);
    const nextYearSewoon = calculateSewoon(currentYear + 1, currentAge + 1, yongSin, daewoon);
    const sinsal = analyzeSinsal(fourPillars);
    const relations = analyzeRelations(fourPillars);
    const personality = analyzePersonality(fourPillars, sipSung);
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
        ohHaeng, sipSung, gyeokGuk, yongSin, daewoon,
        currentYearSewoon, nextYearSewoon,
        sinsal, relations, personality,
        ...legacyFields,
    };
}
// ============================================================
// 사주 팔자 계산
// ============================================================
function calculateFourPillars(year, month, day, hour, minute, isLunar, isLeapMonth, useTrueSolarTime, birthPlace) {
    let solarYear = year, solarMonth = month, solarDay = day;
    if (isLunar) {
        const solarDate = (0, lunarCalendar_1.lunarToSolar)(year, month, day, isLeapMonth);
        solarYear = solarDate.getFullYear();
        solarMonth = solarDate.getMonth() + 1;
        solarDay = solarDate.getDate();
    }
    let adjustedHour = hour;
    if (useTrueSolarTime) {
        const trueSolarResult = (0, trueSolarTimeCalculator_1.applyTrueSolarTimeByCity)(hour, minute, birthPlace);
        adjustedHour = trueSolarResult.adjustedHour;
    }
    let adjustedYear = solarYear;
    if (solarMonth === 1 || (solarMonth === 2 && solarDay < 4)) {
        adjustedYear -= 1;
    }
    const yearGanIndex = ((adjustedYear - 4) % 10 + 10) % 10;
    const yearJiIndex = ((adjustedYear - 4) % 12 + 12) % 12;
    const yearGan = CHEON_GAN[yearGanIndex];
    const yearJi = JI_JI[yearJiIndex];
    const solarMonthIndex = (0, solarTermsCalculator_1.getExactSolarMonth)(solarYear, solarMonth, solarDay, hour, minute);
    const monthJiIndex = (solarMonthIndex + 1) % 12;
    const monthJi = JI_JI[monthJiIndex];
    const monthGanBase = ((yearGanIndex % 5) * 2 + 2) % 10;
    const monthGanIndex = (monthGanBase + solarMonthIndex - 1) % 10;
    const monthGan = CHEON_GAN[monthGanIndex];
    const baseDate = Date.UTC(1900, 0, 1);
    const targetDate = Date.UTC(solarYear, solarMonth - 1, solarDay);
    const diffDays = Math.floor((targetDate - baseDate) / (1000 * 60 * 60 * 24));
    let dayCycleIndex = (10 + diffDays) % 60;
    if (dayCycleIndex < 0)
        dayCycleIndex += 60;
    const dayGanJi = SIXTY_CYCLE[dayCycleIndex];
    const dayGan = dayGanJi[0];
    const dayJi = dayGanJi[1];
    const dayGanIndex = dayCycleIndex % 10;
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
function createPillar(gan, ji) {
    return {
        gan, ji,
        ganJi: `${gan}${ji}`,
        ganOhHaeng: CHEON_GAN_OH_HAENG[gan],
        jiOhHaeng: JI_JI_OH_HAENG[ji],
    };
}
// ============================================================
// 오행 분석
// ============================================================
function analyzeOhHaeng(fourPillars) {
    const balance = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 };
    const pillars = [fourPillars.year, fourPillars.month, fourPillars.day, fourPillars.time];
    const weights = [15, 15, 20, 15];
    pillars.forEach((pillar, index) => {
        balance[pillar.ganOhHaeng] += weights[index];
        balance[pillar.jiOhHaeng] += weights[index] - 5;
        HIDDEN_STEMS[pillar.ji].forEach(stem => {
            balance[CHEON_GAN_OH_HAENG[stem]] += 5;
        });
    });
    const total = Object.values(balance).reduce((sum, v) => sum + v, 0);
    const normalized = { 목: 0, 화: 0, 토: 0, 금: 0, 수: 0 };
    for (const key of Object.keys(balance)) {
        normalized[key] = Math.round((balance[key] / total) * 100);
    }
    const entries = Object.entries(normalized);
    const sorted = entries.sort((a, b) => b[1] - a[1]);
    return {
        balance: normalized,
        dominant: sorted[0][0],
        weak: sorted[sorted.length - 1][0],
        dominantScore: sorted[0][1],
        weakScore: sorted[sorted.length - 1][1],
        isBalanced: sorted[0][1] - sorted[sorted.length - 1][1] < 15,
    };
}
// ============================================================
// 십성 분석
// ============================================================
function analyzeSipSung(fourPillars) {
    const dayGan = fourPillars.day.gan;
    const detail = {
        비견: 0, 겁재: 0, 식신: 0, 상관: 0,
        정재: 0, 편재: 0, 정관: 0, 편관: 0, 정인: 0, 편인: 0,
    };
    const pillars = [fourPillars.year, fourPillars.month, fourPillars.day, fourPillars.time];
    pillars.forEach((pillar, index) => {
        const weight = index === 2 ? 15 : 10;
        detail[TEN_GODS_RELATIONS[dayGan][pillar.gan]] += weight;
        HIDDEN_STEMS[pillar.ji].forEach(stem => {
            detail[TEN_GODS_RELATIONS[dayGan][stem]] += 5;
        });
    });
    const balance = {
        비겁: detail.비견 + detail.겁재,
        식상: detail.식신 + detail.상관,
        재성: detail.정재 + detail.편재,
        관성: detail.정관 + detail.편관,
        인성: detail.정인 + detail.편인,
    };
    const entries = Object.entries(balance);
    const sorted = entries.sort((a, b) => b[1] - a[1]);
    return { balance, detail, dominant: sorted[0][0], weak: sorted[sorted.length - 1][0] };
}
// ============================================================
// 격국 분석
// ============================================================
function analyzeGyeokGuk(fourPillars, ohHaeng) {
    const dayMaster = fourPillars.day.gan;
    const dayMasterOhHaeng = CHEON_GAN_OH_HAENG[dayMaster];
    const monthBranch = fourPillars.month.ji;
    const season = JI_JI_SEASON[monthBranch];
    const dayMasterScore = ohHaeng.balance[dayMasterOhHaeng];
    let strength;
    let gyeokGukType;
    let description;
    if (dayMasterScore >= 25) {
        strength = '신강';
        gyeokGukType = '신강격';
        description = '일간의 기운이 강하여 재성과 관성이 필요합니다.';
    }
    else if (dayMasterScore <= 15) {
        strength = '신약';
        gyeokGukType = '신약격';
        description = '일간의 기운이 약하여 인성과 비겁이 필요합니다.';
    }
    else {
        strength = '중화';
        gyeokGukType = '중화격';
        description = '일간의 기운이 균형잡혀 있어 식상과 재성이 유리합니다.';
    }
    return { dayMaster, dayMasterOhHaeng, strength, monthBranch, season, gyeokGukType, description };
}
// ============================================================
// 용신/기신 분석
// ============================================================
function analyzeYongSin(gyeokGuk) {
    const { dayMasterOhHaeng, strength } = gyeokGuk;
    const ohHaengOrder = ['목', '화', '토', '금', '수'];
    const index = ohHaengOrder.indexOf(dayMasterOhHaeng);
    const 생하는오행 = ohHaengOrder[(index + 4) % 5];
    const 내가생하는 = ohHaengOrder[(index + 1) % 5];
    const 극하는오행 = ohHaengOrder[(index + 3) % 5];
    const 내가극하는 = ohHaengOrder[(index + 2) % 5];
    let yongSin = [], giSin = [], huiSin = [];
    let yongSinReason = '', giSinReason = '';
    if (strength === '신강') {
        yongSin = [내가생하는, 내가극하는];
        giSin = [생하는오행, dayMasterOhHaeng];
        huiSin = [극하는오행];
        yongSinReason = '일간이 강하여 기운을 빼주는 오행이 필요합니다.';
        giSinReason = '일간을 더 강하게 하는 오행은 피해야 합니다.';
    }
    else if (strength === '신약') {
        yongSin = [생하는오행, dayMasterOhHaeng];
        giSin = [극하는오행, 내가극하는];
        huiSin = [내가생하는];
        yongSinReason = '일간이 약하여 기운을 보충해주는 오행이 필요합니다.';
        giSinReason = '일간을 더 약하게 하는 오행은 피해야 합니다.';
    }
    else {
        yongSin = [내가생하는, 내가극하는];
        giSin = [];
        huiSin = [생하는오행];
        yongSinReason = '일간이 균형잡혀 있어 활동성을 높이는 오행이 좋습니다.';
        giSinReason = '특별히 피해야 할 오행은 없습니다.';
    }
    const yongSinScore = { 목: 50, 화: 50, 토: 50, 금: 50, 수: 50 };
    yongSin.forEach(oh => { yongSinScore[oh] = 80; });
    huiSin.forEach(oh => { yongSinScore[oh] = 65; });
    giSin.forEach(oh => { yongSinScore[oh] = 30; });
    return { yongSin, giSin, huiSin, yongSinReason, giSinReason, yongSinScore };
}
// ============================================================
// 대운 계산
// ============================================================
function calculateDaewoon(fourPillars, birthYear, gender, yongSin, currentAge) {
    const yearGanIndex = ((birthYear - 4) % 10 + 10) % 10;
    const yearGan = CHEON_GAN[yearGanIndex];
    const isYangYear = ['갑', '병', '무', '경', '임'].includes(yearGan);
    const isForward = (gender === 'male' && isYangYear) || (gender === 'female' && !isYangYear);
    const direction = isForward ? '순행' : '역행';
    const startAge = 3;
    const monthGanIndex = CHEON_GAN.indexOf(fourPillars.month.gan);
    const monthJiIndex = JI_JI.indexOf(fourPillars.month.ji);
    const list = [];
    for (let i = 0; i < 10; i++) {
        let ganIndex, jiIndex;
        if (isForward) {
            ganIndex = (monthGanIndex + i + 1) % 10;
            jiIndex = (monthJiIndex + i + 1) % 12;
        }
        else {
            ganIndex = (monthGanIndex - i - 1 + 10) % 10;
            jiIndex = (monthJiIndex - i - 1 + 12) % 12;
        }
        const gan = CHEON_GAN[ganIndex];
        const ji = JI_JI[jiIndex];
        const ohHaeng = CHEON_GAN_OH_HAENG[gan];
        const jiOhHaeng = JI_JI_OH_HAENG[ji];
        const isYongSin = yongSin.yongSin.includes(ohHaeng);
        const isGiSin = yongSin.giSin.includes(ohHaeng);
        let score = 50;
        if (isYongSin)
            score += 30;
        if (isGiSin)
            score -= 20;
        if (yongSin.huiSin.includes(ohHaeng))
            score += 15;
        score = Math.max(20, Math.min(95, score));
        let description = '';
        if (isYongSin)
            description = `용신 대운! ${ohHaeng} 기운이 도와줍니다.`;
        else if (isGiSin)
            description = `기신 대운. ${ohHaeng} 기운에 주의하세요.`;
        else
            description = `${ohHaeng} 기운의 평범한 대운입니다.`;
        list.push({
            cycle: i + 1, startAge: startAge + i * 10, endAge: startAge + (i + 1) * 10 - 1,
            gan, ji, ganJi: `${gan}${ji}`, ohHaeng, jiOhHaeng, score, description, isYongSin, isGiSin,
        });
    }
    const current = list.find(d => currentAge >= d.startAge && currentAge <= d.endAge) || null;
    const sorted = [...list].sort((a, b) => b.score - a.score);
    return {
        startAge, direction, list, current, currentAge,
        bestPeriod: sorted[0], worstPeriod: sorted[sorted.length - 1],
    };
}
// ============================================================
// 세운 계산
// ============================================================
function calculateSewoon(year, age, yongSin, daewoon) {
    const ganIndex = ((year - 4) % 10 + 10) % 10;
    const jiIndex = ((year - 4) % 12 + 12) % 12;
    const gan = CHEON_GAN[ganIndex];
    const ji = JI_JI[jiIndex];
    const ohHaeng = CHEON_GAN_OH_HAENG[gan];
    const animal = JI_JI_ANIMAL[ji];
    const isYongSin = yongSin.yongSin.includes(ohHaeng);
    const isGiSin = yongSin.giSin.includes(ohHaeng);
    let score = 50;
    if (isYongSin)
        score += 25;
    if (isGiSin)
        score -= 15;
    if (yongSin.huiSin.includes(ohHaeng))
        score += 10;
    let daewoonInteraction = 0;
    const currentDaewoon = daewoon.list.find(d => age >= d.startAge && age <= d.endAge);
    if (currentDaewoon) {
        if (currentDaewoon.gan === gan)
            daewoonInteraction += 15;
        if (JI_JI_YUK_HAP[currentDaewoon.ji] === ji)
            daewoonInteraction += 10;
        if (JI_JI_CHUNG[currentDaewoon.ji] === ji)
            daewoonInteraction -= 20;
    }
    score = Math.max(20, Math.min(95, score + daewoonInteraction));
    let description = `${year}년은 ${gan}${ji}년(${animal}띠 해)입니다. `;
    if (isYongSin)
        description += `용신 오행(${ohHaeng})이 작용하여 유리한 해입니다.`;
    else if (isGiSin)
        description += `기신 오행(${ohHaeng})이 작용하여 주의가 필요한 해입니다.`;
    else
        description += `${ohHaeng} 기운이 작용하는 평범한 해입니다.`;
    return { year, age, gan, ji, ganJi: `${gan}${ji}`, ohHaeng, animal, score, description, isYongSin, daewoonInteraction };
}
// ============================================================
// 신살 분석
// ============================================================
function analyzeSinsal(fourPillars) {
    const dayGan = fourPillars.day.gan;
    const gilSin = [];
    const hyungSin = [];
    const guiInTable = {
        '갑': ['축', '미'], '을': ['자', '신'], '병': ['해', '유'], '정': ['해', '유'],
        '무': ['축', '미'], '기': ['자', '신'], '경': ['축', '미'], '신': ['인', '오'],
        '임': ['묘', '사'], '계': ['묘', '사'],
    };
    const hasCheonEulGuiIn = [fourPillars.year.ji, fourPillars.month.ji, fourPillars.time.ji].some(ji => guiInTable[dayGan].includes(ji));
    if (hasCheonEulGuiIn)
        gilSin.push('천을귀인');
    const hasMunChangGuiIn = false;
    const hasYeokMaSal = false;
    const hasDoHwaSal = false;
    const hasYangInSal = false;
    const hasGeopSal = false;
    const hasGongMang = false;
    let summary = '';
    if (gilSin.length > 0)
        summary += `길신: ${gilSin.join(', ')}. `;
    if (hyungSin.length > 0)
        summary += `흉신: ${hyungSin.join(', ')}. `;
    if (!summary)
        summary = '특별한 신살이 없습니다.';
    return {
        gilSin, hyungSin, hasCheonEulGuiIn, hasMunChangGuiIn,
        hasYeokMaSal, hasDoHwaSal, hasGongMang, hasYangInSal, hasGeopSal, summary,
    };
}
// ============================================================
// 관계 분석
// ============================================================
function analyzeRelations(fourPillars) {
    const cheonganHap = [], cheonganChung = [];
    const jijiYukHap = [], jijiChung = [];
    const jijiSamHap = [], jijiHyung = [];
    const jijiBan = [], jijiPa = [], jijiHae = [];
    const pillars = [
        { name: '년', pillar: fourPillars.year }, { name: '월', pillar: fourPillars.month },
        { name: '일', pillar: fourPillars.day }, { name: '시', pillar: fourPillars.time },
    ];
    for (let i = 0; i < pillars.length; i++) {
        for (let j = i + 1; j < pillars.length; j++) {
            const gan1 = pillars[i].pillar.gan, gan2 = pillars[j].pillar.gan;
            if (CHEON_GAN_HAP[gan1] === gan2)
                cheonganHap.push(`${pillars[i].name}${pillars[j].name} ${gan1}${gan2}합`);
            const ji1 = pillars[i].pillar.ji, ji2 = pillars[j].pillar.ji;
            if (JI_JI_YUK_HAP[ji1] === ji2)
                jijiYukHap.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}합`);
            if (JI_JI_CHUNG[ji1] === ji2)
                jijiChung.push(`${pillars[i].name}${pillars[j].name} ${ji1}${ji2}충`);
        }
    }
    const summaryParts = [];
    if (cheonganHap.length > 0)
        summaryParts.push(`천간합: ${cheonganHap.length}개`);
    if (jijiYukHap.length > 0)
        summaryParts.push(`지지합: ${jijiYukHap.length}개`);
    if (jijiChung.length > 0)
        summaryParts.push(`지지충: ${jijiChung.length}개`);
    return {
        cheonganHap, cheonganChung, jijiYukHap, jijiSamHap, jijiChung, jijiHyung, jijiBan, jijiPa, jijiHae,
        summary: summaryParts.length > 0 ? summaryParts.join(', ') : '특별한 합충 관계 없음',
    };
}
// ============================================================
// 성격/적성 분석
// ============================================================
function analyzePersonality(fourPillars, sipSung) {
    const dayMaster = fourPillars.day.gan;
    const dayMasterTraits = DAY_MASTER_PERSONALITY[dayMaster];
    const dominantSipsung = sipSung.dominant;
    const sipsungTraits = {
        비겁: ['독립심', '경쟁심', '자존심'],
        식상: ['창의성', '표현력', '자유로움'],
        재성: ['실용성', '현실감각', '재물관리'],
        관성: ['책임감', '조직력', '명예심'],
        인성: ['학습능력', '사고력', '자기계발'],
    };
    const careerByDominant = {
        비겁: ['개인사업', '스포츠', '영업'],
        식상: ['예술가', '작가', '강사'],
        재성: ['금융', '무역', '자영업'],
        관성: ['공무원', '관리자', '법조계'],
        인성: ['학자', '교육자', '연구원'],
    };
    const relationshipStyles = {
        비겁: '독립적이고 주도적인 관계를 선호합니다.',
        식상: '자유롭고 창의적인 소통을 즐깁니다.',
        재성: '실용적이고 현실적인 관계를 추구합니다.',
        관성: '책임감 있고 안정적인 관계를 중시합니다.',
        인성: '깊이 있고 지적인 교류를 선호합니다.',
    };
    return {
        dayMasterTraits,
        dominantSipsung: { type: dominantSipsung, traits: sipsungTraits[dominantSipsung] },
        careerAptitude: careerByDominant[dominantSipsung],
        relationshipStyle: relationshipStyles[dominantSipsung],
    };
}
// ============================================================
// 레거시 호환
// ============================================================
function createLegacyFields(fourPillars, ohHaeng, sipSung) {
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
            wood: ohHaeng.balance.목, fire: ohHaeng.balance.화,
            earth: ohHaeng.balance.토, metal: ohHaeng.balance.금, water: ohHaeng.balance.수,
        },
    };
}
//# sourceMappingURL=completeSajuCalculator.js.map