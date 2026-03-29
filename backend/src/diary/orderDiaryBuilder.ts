/**
 * 주문형 인쇄 제작 파이프라인
 * 
 * 하나의 주문 입력으로 기간별 다이어리 PDF를 생성하는 통합 빌더
 */

import * as path from 'path';
import * as fs from 'fs';
import { buildPeriodDiary, PeriodDiaryInput, DurationType } from './periodDiaryGenerator';
import { renderPeriodDiaryPdf } from './periodDiaryPdfRenderer';

// ============================================================
// Type Definitions
// ============================================================

export type CalendarType = "solar" | "lunar";
export type Gender = "male" | "female";
export type RenderMode = "standard" | "large";

export interface OrderInput {
  /** 고객 이름 (필수) */
  customerName: string;
  /** 소유자 라벨 (선택, 기본값: customerName) */
  ownerLabel?: string;
  /** 제품 타이틀 (선택, 기본값: 기존 브랜드 타이틀) */
  productTitle?: string;
  /** 달력 타입 (metadata용, 향후 확장) */
  calendarType: CalendarType;
  /** 성별 (metadata용, 향후 확장) */
  gender: Gender;
  /** 출생 정보 (필수) */
  birth: {
    year: number;
    month: number;
    day: number;
    hour?: number;
    minute?: number;
  };
  /** 시작 날짜 (필수, YYYY-MM-DD) */
  startDate: string;
  /** 기간 타입 (필수) */
  durationType: DurationType;
  /** 렌더링 모드 (선택, 기본값: standard) */
  renderMode?: RenderMode;
}

export interface OrderBuildResult {
  /** 성공 여부 */
  success: boolean;
  /** 주문 요약 */
  orderSummary: {
    customerName: string;
    startDate: string;
    endDate: string;
    durationType: DurationType;
    totalDays: number;
    totalPages: number;
  };
  /** 생성된 파일들 */
  files: {
    pdfPath?: string;
    htmlPath?: string;
  };
  /** 메타데이터 */
  metadata: {
    generatedAt: string;
    renderMode: RenderMode;
    calendarType: CalendarType;
  };
  /** 오류 메시지 (실패 시) */
  error?: string;
}

// ============================================================
// Helper Functions
// ============================================================

/**
 * 파일 안전한 고객명 생성
 */
function sanitizeCustomerName(name: string): string {
  // 파일 시스템에 안전한 문자로 변환
  const safeChars = name
    .replace(/[<>:"/\\|?*]/g, '_')  // 윈도우 금지 문자
    .replace(/\s+/g, '_')           // 공백을 언더스코어로
    .replace(/_{2,}/g, '_')         // 연속 언더스코어 제거
    .replace(/^_+|_+$/g, '');       // 앞뒤 언더스코어 제거
  
  // 한글은 유지하되 최대 20자로 제한
  return safeChars.substring(0, 20) || 'customer';
}

/**
 * 자동 파일명 생성
 * 규칙: YYYYMMDD_customerSafe_duration_mode.pdf
 */
function generateFileName(input: OrderInput): string {
  const dateStr = input.startDate.replace(/-/g, '');
  const customerSafe = sanitizeCustomerName(input.customerName);
  const mode = input.renderMode || 'standard';
  
  return `${dateStr}_${customerSafe}_${input.durationType}_${mode}`;
}

/**
 * OrderInput 유효성 검증
 */
function validateOrderInput(input: OrderInput): string | null {
  // 필수 필드 체크
  if (!input.customerName?.trim()) {
    return '고객명(customerName)이 필요합니다';
  }
  
  if (!input.birth) {
    return '출생 정보(birth)가 필요합니다';
  }
  
  if (!input.birth.year || !input.birth.month || !input.birth.day) {
    return '출생 년월일(birth.year/month/day)이 필요합니다';
  }
  
  if (!input.startDate?.trim()) {
    return '시작 날짜(startDate)가 필요합니다';
  }
  
  if (!input.durationType) {
    return '기간 타입(durationType)이 필요합니다';
  }
  
  // 날짜 형식 검증
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(input.startDate)) {
    return 'startDate는 YYYY-MM-DD 형식이어야 합니다';
  }
  
  const startDate = new Date(input.startDate);
  if (isNaN(startDate.getTime())) {
    return '유효하지 않은 시작 날짜입니다';
  }
  
  // 출생일 유효성
  const currentYear = new Date().getFullYear();
  if (input.birth.year < 1900 || input.birth.year > currentYear) {
    return '출생 연도가 유효하지 않습니다 (1900-현재)';
  }
  
  if (input.birth.month < 1 || input.birth.month > 12) {
    return '출생 월이 유효하지 않습니다 (1-12)';
  }
  
  if (input.birth.day < 1 || input.birth.day > 31) {
    return '출생 일이 유효하지 않습니다 (1-31)';
  }
  
  // 기간 타입 검증
  const validDurations: DurationType[] = ['1m', '3m', '6m', '1y'];
  if (!validDurations.includes(input.durationType)) {
    return '기간 타입은 1m, 3m, 6m, 1y 중 하나여야 합니다';
  }
  
  return null; // 유효함
}

// ============================================================
// Main Function
// ============================================================

/**
 * 주문형 다이어리 생성
 * 
 * @param input 주문 입력 정보
 * @returns 주문 결과
 */
export async function buildOrderDiary(input: OrderInput): Promise<OrderBuildResult> {
  const startTime = new Date();
  
  // 1. 입력 검증
  const validationError = validateOrderInput(input);
  if (validationError) {
    return {
      success: false,
      orderSummary: {
        customerName: input.customerName || 'Unknown',
        startDate: input.startDate || 'Invalid',
        endDate: 'Unknown',
        durationType: input.durationType || '1m',
        totalDays: 0,
        totalPages: 0
      },
      files: {},
      metadata: {
        generatedAt: startTime.toISOString(),
        renderMode: input.renderMode || 'standard',
        calendarType: input.calendarType
      },
      error: `주문 입력 검증 실패: ${validationError}`
    };
  }
  
  console.log(`[OrderDiaryBuilder] 주문 처리 시작: ${input.customerName} (${input.durationType})`);
  
  try {
    // 2. 기간별 다이어리 생성
    console.log('[OrderDiaryBuilder] 다이어리 데이터 생성 중...');
    const periodInput: PeriodDiaryInput = {
      startDate: input.startDate,
      durationType: input.durationType,
      birth: {
        year: input.birth.year,
        month: input.birth.month,
        day: input.birth.day,
        hour: input.birth.hour,
        minute: input.birth.minute,
        isLunar: input.calendarType === 'lunar',
        birthPlace: '서울' // 기본값, 향후 확장 가능
      }
    };
    
    const periodResult = await buildPeriodDiary(periodInput);
    console.log(`[OrderDiaryBuilder] 다이어리 생성 완료: ${periodResult.entries.length}일`);
    
    // 3. PDF 파일 생성
    console.log('[OrderDiaryBuilder] PDF 생성 중...');
    const outputDir = './order_output';
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const fileName = generateFileName(input);
    const pdfPath = path.join(outputDir, `${fileName}.pdf`);
    const htmlPath = path.join(outputDir, `${fileName}.html`);
    
    const renderResult = await renderPeriodDiaryPdf({
      period: periodResult,
      outputPath: pdfPath,
      mode: input.renderMode || 'standard',
      ownerLabel: input.ownerLabel || input.customerName,
      productTitle: input.productTitle
    });
    
    if (!renderResult.success) {
      throw new Error(`PDF 생성 실패: ${renderResult.error || 'Unknown error'}`);
    }
    
    console.log(`[OrderDiaryBuilder] PDF 생성 완료: ${renderResult.outputPath}`);
    
    // 4. 성공 결과 반환
    const endTime = new Date();
    const processingTime = endTime.getTime() - startTime.getTime();
    
    console.log(`[OrderDiaryBuilder] 주문 완료: ${input.customerName} (${processingTime}ms)`);
    
    // 페이지 수 추정 (표지 1페이지 + 일간 페이지들 + 인덱스 등)
    const estimatedPages = 1 + periodResult.totalDays + Math.ceil(periodResult.totalDays / 7); // 표지 + 일간 + 주간 요약
    
    return {
      success: true,
      orderSummary: {
        customerName: input.customerName,
        startDate: periodResult.startDate,
        endDate: periodResult.endDate,
        durationType: periodResult.durationType,
        totalDays: periodResult.totalDays,
        totalPages: renderResult.pageCount || estimatedPages
      },
      files: {
        pdfPath: renderResult.outputPath,
        htmlPath: fs.existsSync(htmlPath) ? htmlPath : undefined
      },
      metadata: {
        generatedAt: startTime.toISOString(),
        renderMode: input.renderMode || 'standard',
        calendarType: input.calendarType
      }
    };
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`[OrderDiaryBuilder] 주문 처리 실패: ${errorMessage}`);
    
    return {
      success: false,
      orderSummary: {
        customerName: input.customerName,
        startDate: input.startDate,
        endDate: 'Error',
        durationType: input.durationType,
        totalDays: 0,
        totalPages: 0
      },
      files: {},
      metadata: {
        generatedAt: startTime.toISOString(),
        renderMode: input.renderMode || 'standard',
        calendarType: input.calendarType
      },
      error: `주문 처리 중 오류 발생: ${errorMessage}`
    };
  }
}

// ============================================================
// Export
// ============================================================

export {
  buildPeriodDiary,
  renderPeriodDiaryPdf
};