/**
 * 기간별 다이어리 PDF 묶음 렌더러
 * 
 * PeriodDiaryResult를 사용하여 전체 기간의 인쇄용 다이어리 PDF 생성
 * 1개월/3개월/6개월/1년 모든 기간 지원
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';
import { DailyDiaryPayload } from './types';
import { PeriodDiaryResult } from './periodDiaryGenerator';

// ============================================================
// Type Definitions
// ============================================================

export interface PeriodPdfInput {
  period: PeriodDiaryResult;
  outputPath?: string;
  includeTableOfContents?: boolean;
  mode?: 'standard' | 'large';
  ownerLabel?: string;
  productTitle?: string;
}

export interface PeriodPdfResult {
  success: boolean;
  outputPath?: string;
  pageCount: number;
  error?: string;
}

// ============================================================
// PDF Bundle Template Constants
// ============================================================

const BUNDLE_TEMPLATE_START = `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R³ 다이어리 - {{startDate}} to {{endDate}}</title>
    <style>
        @page {
            size: A4;
            margin: {{page_margin}};
        }
        
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
            font-size: {{body_font_size}};
            line-height: {{line_height}};
            margin: 0;
            padding: 0;
            color: #333;
        }
        
        /* Page Break */
        .page-break {
            page-break-after: always;
        }
        
        /* Cover Page */
        .cover-page {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            page-break-after: always;
            text-align: center;
            background: #fff;
            padding: {{section_padding}};
            border: 3px solid #2c5aa0;
            margin: 5mm;
        }
        
        .cover-header {
            margin-top: {{section_padding}};
        }
        
        .cover-page .main-title {
            font-size: {{cover_title_size}};
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: {{section_padding}};
            text-shadow: 1px 1px 2px rgba(44, 90, 160, 0.1);
        }
        
        .cover-page .subtitle {
            font-size: {{cover_subtitle_size}};
            color: #4a5568;
            margin-bottom: {{section_padding}};
            font-weight: 300;
        }
        
        .cover-page .concept-line {
            font-size: {{small_font_size}};
            color: #718096;
            font-style: italic;
            margin: {{section_padding}} 0;
            border-top: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            padding: {{item_padding}} 0;
        }
        
        .cover-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 100%;
        }
        
        .period-info-box {
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: {{section_padding}};
            margin: {{section_padding}} 0;
        }
        
        .period-info-box .period-title {
            font-size: {{subheader_font_size}};
            font-weight: bold;
            color: #2d3748;
            margin-bottom: {{item_padding}};
        }
        
        .period-details {
            font-size: {{body_font_size}};
            color: #4a5568;
            line-height: {{line_height}};
        }
        
        .owner-section {
            margin: {{section_padding}} 0;
            padding: {{section_padding}};
            border: 1px dashed #cbd5e0;
            border-radius: 5px;
        }
        
        .owner-label {
            font-size: {{small_font_size}};
            color: #718096;
            margin-bottom: 8mm;
        }
        
        .owner-line {
            border-bottom: 1px solid #2c5aa0;
            height: 8mm;
            width: 60%;
            margin: 0 auto;
        }
        
        .cover-footer {
            margin-bottom: {{item_padding}};
        }
        
        .brand-footer {
            font-size: {{small_font_size}};
            color: #a0aec0;
            border-top: 1px solid #e2e8f0;
            padding-top: {{item_padding}};
        }
        
        /* Daily Page */
        .daily-page {
            height: 100vh;
            display: flex;
            flex-direction: column;
            page-break-after: always;
        }
        
        .daily-page:last-child {
            page-break-after: auto;
        }
        
        /* Daily Page Header */
        .daily-header {
            text-align: center;
            border-bottom: 1px solid #333;
            padding-bottom: 2mm;
            margin-bottom: 3mm;
        }
        
        .daily-header h2 {
            font-size: 14pt;
            margin: 0 0 1mm 0;
            color: #2c5aa0;
        }
        
        .daily-header .date-info {
            font-size: 10pt;
            margin: 0;
        }
        
        /* Main Content Layout */
        .daily-content {
            display: flex;
            flex: 1;
            gap: 3mm;
        }
        
        .left-panel {
            flex: 0.45;
            padding: 2mm;
            border: 1px solid #ccc;
            overflow: hidden;
        }
        
        .right-panel {
            flex: 0.55;
            padding: 2mm;
            border: 1px solid #ccc;
            overflow: hidden;
        }
        
        .left-panel {
            background-color: #f9f9f9;
        }
        
        .right-panel {
            background-color: #fff;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 10pt;
            font-weight: bold;
            color: #2c5aa0;
            border-bottom: 1px solid #2c5aa0;
            padding-bottom: 0.5mm;
            margin: 0 0 2mm 0;
        }
        
        /* Content Blocks */
        .content-block {
            margin-bottom: 2mm;
        }
        
        .content-block h3 {
            font-size: 9pt;
            font-weight: bold;
            color: #555;
            margin: 0 0 1mm 0;
        }
        
        .content-block p {
            font-size: 8pt;
            margin: 0 0 1mm 0;
            line-height: 1.2;
        }
        
        .content-block ul {
            margin: 0;
            padding-left: 3mm;
        }
        
        .content-block li {
            font-size: 8pt;
            margin-bottom: 0.5mm;
            line-height: 1.2;
        }
        
        /* Bottom Panel */
        .bottom-panel {
            border-top: 1px solid #ccc;
            padding-top: 3mm;
            margin-top: 3mm;
        }
        
        /* User Recording Section */
        .user-recording {
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 1mm;
            padding: 2mm;
            margin-top: 3mm;
        }
        
        .user-recording h3 {
            font-size: 9pt;
            color: #2c5aa0;
            margin: 0 0 2mm 0;
            border-bottom: 1px solid #cbd5e0;
            padding-bottom: 1mm;
        }
        
        .recording-section {
            margin-bottom: 2mm;
        }
        
        .recording-section h4 {
            font-size: 8pt;
            color: #4a5568;
            margin: 0 0 1mm 0;
            font-weight: bold;
        }
        
        .recording-line {
            border-bottom: 1px solid #cbd5e0;
            min-height: 4mm;
            margin-bottom: 1mm;
        }
        
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 2mm;
            margin: 1mm 0;
        }
        
        .checkbox-item {
            display: flex;
            align-items: center;
            font-size: 8pt;
        }
        
        .checkbox {
            width: 2.5mm;
            height: 2.5mm;
            border: 1px solid #4a5568;
            margin-right: 1mm;
            display: inline-block;
        }
        
        /* Keywords */
        .keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5mm;
            margin-bottom: 1mm;
        }
        
        .keyword-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.5mm 1mm;
            border-radius: 0.5mm;
            font-size: 7pt;
            font-weight: bold;
        }
        
        /* Time Schedule Table */
        .time-slots {
            width: 100%;
            border-collapse: collapse;
            font-size: 7pt;
        }
        
        .time-slots th,
        .time-slots td {
            border: 1px solid #ddd;
            padding: 0.5mm 1mm;
            text-align: left;
            line-height: 1.1;
        }
        
        .time-slots th {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        
        /* Good/Bad Info */
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2mm;
            margin-top: 3mm;
            font-size: 8pt;
        }
        
        .info-item {
            padding: 2mm;
            border: 1px solid #ddd;
            border-radius: 1mm;
        }
        
        .info-item.good {
            background-color: #e8f5e9;
        }
        
        .info-item.bad {
            background-color: #ffebee;
        }
        
        /* Utilities */
        .text-small { font-size: 8pt; }
        .text-bold { font-weight: bold; }
        .text-center { text-align: center; }
        
        /* Month Divider Page */
        .month-divider {
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            page-break-after: always;
            background: linear-gradient(to bottom, #f7fafc 0%, #e2e8f0 100%);
        }
        
        .month-divider h1 {
            font-size: 48pt;
            margin-bottom: 10mm;
            color: #2c5aa0;
        }
        
        .month-divider .month-info {
            font-size: 14pt;
            color: #4a5568;
            margin: 5mm 0;
        }
        
        .month-divider .month-stats {
            margin-top: 15mm;
            padding: 8mm;
            border: 1px solid #cbd5e0;
            border-radius: 3mm;
            background: white;
        }
        
        /* Monthly Summary Page */
        .monthly-summary {
            height: 100vh;
            padding: 10mm;
            page-break-after: always;
        }
        
        .monthly-summary h2 {
            font-size: 20pt;
            color: #2c5aa0;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 3mm;
            margin-bottom: 10mm;
        }
        
        .monthly-summary .summary-section {
            margin-bottom: 10mm;
        }
        
        .monthly-summary .summary-section h3 {
            font-size: 12pt;
            color: #4a5568;
            margin-bottom: 5mm;
        }
        
        .monthly-summary .summary-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 5mm;
        }
        
        .monthly-summary .summary-item {
            padding: 5mm;
            border: 1px solid #e2e8f0;
            border-radius: 2mm;
            background: #f7fafc;
        }
        
        /* Weekly Summary Page */
        .weekly-summary {
            padding: 8mm;
            page-break-after: always;
        }
        
        .weekly-summary h3 {
            font-size: 16pt;
            color: #2c5aa0;
            border-bottom: 1px solid #2c5aa0;
            padding-bottom: 2mm;
            margin-bottom: 8mm;
        }
        
        .weekly-summary .week-info {
            font-size: 11pt;
            color: #4a5568;
            margin-bottom: 8mm;
        }
        
        .weekly-summary .summary-row {
            display: flex;
            gap: 10mm;
            margin-bottom: 8mm;
        }
        
        .weekly-summary .summary-col {
            flex: 1;
        }
        
        .weekly-summary .summary-col h4 {
            font-size: 10pt;
            color: #2c5aa0;
            margin-bottom: 3mm;
        }
        
        .weekly-summary .checkpoint-list {
            padding-left: 4mm;
            margin-top: 5mm;
        }
        
        .weekly-summary .checkpoint-list li {
            margin-bottom: 2mm;
            font-size: 9pt;
        }
        
        /* Weekly Reflection Page */
        .weekly-reflection {
            padding: 10mm;
            page-break-after: always;
        }
        
        .weekly-reflection h3 {
            font-size: 16pt;
            color: #2c5aa0;
            border-bottom: 2px solid #2c5aa0;
            padding-bottom: 3mm;
            margin-bottom: 8mm;
            text-align: center;
        }
        
        .weekly-reflection .reflection-section {
            margin-bottom: 8mm;
        }
        
        .weekly-reflection .reflection-section h4 {
            font-size: 11pt;
            color: #4a5568;
            margin-bottom: 3mm;
            font-weight: bold;
        }
        
        .weekly-reflection .reflection-item {
            margin-bottom: 5mm;
        }
        
        .weekly-reflection .reflection-label {
            font-size: 9pt;
            color: #4a5568;
            margin-bottom: 1mm;
        }
        
        .weekly-reflection .writing-line {
            border-bottom: 1px solid #cbd5e0;
            min-height: 5mm;
            margin-bottom: 2mm;
        }
        
        .weekly-reflection .memo-box {
            border: 1px solid #cbd5e0;
            min-height: 50mm;
            background: #fafafa;
            padding: 3mm;
        }
    </style>
</head>
<body>
`;

const BUNDLE_TEMPLATE_END = `
</body>
</html>`;

// ============================================================
// Main Renderer Class
// ============================================================

export class PeriodDiaryPdfRenderer {
  private outputDir: string;
  private mode: 'standard' | 'large';
  
  constructor(outputDir: string = './test_output', mode: 'standard' | 'large' = 'standard') {
    this.outputDir = outputDir;
    this.mode = mode;
    // 출력 디렉토리 생성
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }
  
  /**
   * 모드에 따른 스타일 값 반환
   */
  private getStyleValues() {
    if (this.mode === 'large') {
      return {
        page_margin: '15mm',
        body_font_size: '12pt',
        line_height: '1.5',
        header_font_size: '18pt',
        subheader_font_size: '14pt',
        small_font_size: '10pt',
        checkbox_size: '5mm',
        recording_line_height: '8mm',
        section_padding: '4mm',
        panel_padding: '5mm',
        cover_title_size: '42pt',
        cover_subtitle_size: '16pt',
        item_padding: '3mm'
      };
    } else {
      // standard mode
      return {
        page_margin: '10mm',
        body_font_size: '10pt',
        line_height: '1.3',
        header_font_size: '14pt',
        subheader_font_size: '11pt',
        small_font_size: '8pt',
        checkbox_size: '3mm',
        recording_line_height: '5mm',
        section_padding: '2.5mm',
        panel_padding: '3mm',
        cover_title_size: '36pt',
        cover_subtitle_size: '14pt',
        item_padding: '2mm'
      };
    }
  }

  /**
   * 기간별 다이어리 PDF 생성
   */
  async renderPdf(input: PeriodPdfInput): Promise<PeriodPdfResult> {
    const { period, outputPath, includeTableOfContents = false, mode = 'standard', ownerLabel, productTitle } = input;
    
    // Update mode if provided
    this.mode = mode;
    
    try {
      // 1. HTML 생성
      const html = this.generateBundleHtml(period, includeTableOfContents, ownerLabel, productTitle);
      
      // 2. HTML 파일 저장
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const htmlPath = path.join(
        this.outputDir,
        `period_${period.durationType}_${timestamp}.html`
      );
      fs.writeFileSync(htmlPath, html, 'utf-8');
      
      // 3. JSON 파일 저장 (Python converter용)
      const jsonPath = htmlPath.replace('.html', '.json');
      fs.writeFileSync(jsonPath, JSON.stringify(period, null, 2), 'utf-8');
      console.log(`[PeriodDiaryPdfRenderer] JSON saved: ${jsonPath}`);
      
      // 4. PDF 변환
      const pdfPath = outputPath || htmlPath.replace('.html', '.pdf');
      await this.convertHtmlToPdf(htmlPath, pdfPath);
      
      // 5. 임시 HTML 파일 삭제 (옵션)
      // fs.unlinkSync(htmlPath);
      // fs.unlinkSync(jsonPath);
      
      // 6. 페이지 수 계산 (Cover + Month dividers + Monthly summaries + Weekly summaries + Daily pages)
      const monthGroups = this.groupEntriesByMonth(period.entries);
      const monthCount = monthGroups.size;
      const monthlySummaryPages = period.totalDays > 30 ? monthCount : 0;
      
      // Count weekly summaries and reflections
      let weeklySummaryCount = 0;
      let weeklyReflectionCount = 0;
      if (period.totalDays > 7) {
        monthGroups.forEach((monthData) => {
          const weekGroups = this.groupEntriesByWeek(monthData.entries);
          weeklySummaryCount += weekGroups.size;
          weeklyReflectionCount += weekGroups.size; // Same count as summaries
        });
      }
      
      const indexPageCount = Math.ceil(period.entries.length / 25); // ~25 entries per index page
      const pageCount = 1 + indexPageCount + monthCount + monthlySummaryPages + weeklySummaryCount + weeklyReflectionCount + period.entries.length;
      
      return {
        success: true,
        outputPath: pdfPath,
        pageCount
      };
    } catch (error) {
      console.error('PDF 생성 실패:', error);
      return {
        success: false,
        pageCount: 0,
        error: String(error)
      };
    }
  }
  
  /**
   * HTML 묶음 생성
   */
  private generateBundleHtml(period: PeriodDiaryResult, includeTableOfContents: boolean, ownerLabel?: string, productTitle?: string): string {
    // Get style values
    const styleVals = this.getStyleValues();
    
    // Start with template
    let html = BUNDLE_TEMPLATE_START;
    
    // Replace all style variables
    Object.entries(styleVals).forEach(([key, value]) => {
      html = html.replace(new RegExp(`{{${key}}}`, 'g'), String(value));
    });
    
    // Replace content variables
    html = html
      .replace('{{startDate}}', period.startDate)
      .replace('{{endDate}}', period.endDate);
    
    // Cover Page
    html += this.generateCoverPage(period, ownerLabel, productTitle);
    
    // Calculate page numbers for index
    const pageMap = this.calculatePageNumbers(period);
    
    // Index Pages (always included)
    html += this.generateIndexPages(period, pageMap);
    
    // Table of Contents (옵션)
    if (includeTableOfContents && period.totalDays > 30) {
      html += this.generateTableOfContents(period);
    }
    
    // Group entries by month
    const monthGroups = this.groupEntriesByMonth(period.entries);
    
    // Render each month section
    monthGroups.forEach((monthData, monthKey) => {
      // Month Divider Page
      html += this.generateMonthDivider(monthKey, monthData.entries, period);
      
      // Monthly Summary Page (optional)
      if (period.totalDays > 30) { // Only for multi-month periods
        html += this.generateMonthlySummary(monthKey, monthData.entries);
      }
      
      // Group month's entries by week and render with weekly summaries
      const weekGroups = this.groupEntriesByWeek(monthData.entries);
      
      weekGroups.forEach((weekData, weekKey) => {
        // Daily Pages for this week
        weekData.entries.forEach((entry) => {
          const globalIndex = period.entries.indexOf(entry) + 1;
          html += this.generateDailyPage(entry, globalIndex, period.totalDays);
        });
        
        // Weekly Summary Page (after each week)
        if (period.totalDays > 7) { // Only for periods longer than a week
          html += this.generateWeeklySummary(weekKey, weekData.entries);
          // Add Weekly Reflection Page after Weekly Summary
          html += this.generateWeeklyReflection(weekKey, weekData.entries);
        }
      });
    });
    
    html += BUNDLE_TEMPLATE_END;
    
    return html;
  }
  
  /**
   * Group entries by month
   */
  private groupEntriesByMonth(entries: DailyDiaryPayload[]): Map<string, {entries: DailyDiaryPayload[]}> {
    const groups = new Map<string, {entries: DailyDiaryPayload[]}>();
    
    entries.forEach(entry => {
      const monthKey = entry.date.substring(0, 7); // YYYY-MM
      if (!groups.has(monthKey)) {
        groups.set(monthKey, {entries: []});
      }
      groups.get(monthKey)!.entries.push(entry);
    });
    
    return groups;
  }
  
  /**
   * Cover Page 생성
   */
  private generateCoverPage(period: PeriodDiaryResult, ownerLabel?: string, productTitle?: string): string {
    const durationLabels = {
      '1m': '1개월',
      '3m': '3개월', 
      '6m': '6개월',
      '1y': '1년'
    };
    
    const formatDate = (dateStr: string) => {
      const [year, month, day] = dateStr.split('-');
      return `${year}년 ${month}월 ${day}일`;
    };
    
    // 기본값 처리
    const mainTitle = productTitle || '라이프 리듬 다이어리';
    const ownerName = ownerLabel || '';
    
    return `
    <div class="cover-page">
        <div class="cover-header">
            <div class="main-title">${mainTitle}</div>
            <div class="subtitle">사주·기문둔갑 기반 개인화 일일 관리 다이어리</div>
            <div class="concept-line">"나만의 리듬을 찾아 성장하는 시간"</div>
        </div>
        
        <div class="cover-content">
            <div class="period-info-box">
                <div class="period-title">${durationLabels[period.durationType]} 다이어리</div>
                <div class="period-details">
                    <div><strong>사용 기간:</strong> ${formatDate(period.startDate)} ~ ${formatDate(period.endDate)}</div>
                    <div><strong>총 일수:</strong> ${period.totalDays}일</div>
                    <div><strong>생성일:</strong> ${formatDate(new Date().toISOString().split('T')[0])}</div>
                </div>
            </div>
            
            <div class="owner-section">
                <div class="owner-label">소유자 / Owner</div>
                ${ownerName ? 
                  `<div style="text-align: center; font-size: 14pt; font-weight: bold; margin-top: 5mm; color: #2c5aa0;">${ownerName}</div>` : 
                  '<div class="owner-line"></div>'
                }
            </div>
        </div>
        
        <div class="cover-footer">
            <div class="brand-footer">Powered by R³ System (Rhythm → Response → Recode)</div>
        </div>
    </div>
    `;
  }
  
  /**
   * Table of Contents 생성 (선택사항)
   */
  private generateTableOfContents(period: PeriodDiaryResult): string {
    const months = new Map<string, DailyDiaryPayload[]>();
    
    // 월별로 그룹화
    period.entries.forEach(entry => {
      const monthKey = entry.date.substring(0, 7); // YYYY-MM
      if (!months.has(monthKey)) {
        months.set(monthKey, []);
      }
      months.get(monthKey)!.push(entry);
    });
    
    let tocHtml = `
    <div class="page-break">
        <h2 class="text-center">목차</h2>
        <div style="margin-top: 10mm;">
    `;
    
    months.forEach((entries, monthKey) => {
      tocHtml += `
        <div style="margin-bottom: 5mm;">
            <h3>${monthKey}</h3>
            <ul>
      `;
      entries.forEach(entry => {
        tocHtml += `<li>${entry.date} (${entry.calendar.weekday})</li>`;
      });
      tocHtml += `
            </ul>
        </div>
      `;
    });
    
    tocHtml += `
        </div>
    </div>
    `;
    
    return tocHtml;
  }
  
  /**
   * Daily Page 생성
   */
  private generateDailyPage(
    payload: DailyDiaryPayload,
    pageNumber: number,
    totalPages: number
  ): string {
    // 키워드 생성
    const keywords = payload.leftPage.sajuSummary.mainCharacteristics
      .slice(0, 4)
      .map(k => `<span class="keyword-tag">${k}</span>`)
      .join('');
    
    // 생활 영역 콘텐츠
    const lifeAreas = this.generateLifeAreas(payload.leftPage.lifeAreas);
    
    // 권장사항/주의사항 리스트
    const recommendations = payload.leftPage.recommendations
      .map(r => `<li>${r}</li>`)
      .join('');
    const cautions = payload.leftPage.cautions
      .map(c => `<li>${c}</li>`)
      .join('');
    
    // 시간표 생성
    const timeSlots = this.generateTimeSlots(payload.rightPage.timeSlots);
    
    return `
    <div class="daily-page">
        <div class="daily-header">
            <h2>Day ${pageNumber} / ${totalPages}</h2>
            <div class="date-info">
                ${payload.calendar.solarDate} (${payload.calendar.weekday})
                ${payload.calendar.lunarDate?.displayText || ''}
            </div>
        </div>
        
        <div class="daily-content">
            <!-- Left Panel -->
            <div class="left-panel">
                <div class="section-header">오늘의 안내</div>
                
                <div class="content-block">
                    <h3>오늘의 키워드</h3>
                    <div class="keywords">${keywords}</div>
                </div>
                
                <div class="content-block">
                    <h3>생활 영역</h3>
                    ${lifeAreas}
                </div>
                
                <div class="content-block">
                    <h3>권장사항</h3>
                    <ul>${recommendations}</ul>
                </div>
                
                <div class="content-block">
                    <h3>주의사항</h3>
                    <ul>${cautions}</ul>
                </div>
            </div>
            
            <!-- Right Panel -->
            <div class="right-panel">
                <div class="section-header">기록 공간</div>
                
                <div class="content-block">
                    <h3>시간별 일정</h3>
                    ${timeSlots}
                </div>
                
                <div class="info-grid">
                    <div class="info-item good">
                        <div class="text-bold">좋은 시간</div>
                        <div>${payload.rightPage.goodHours.join(', ') || 'N/A'}</div>
                    </div>
                    <div class="info-item bad">
                        <div class="text-bold">주의 시간</div>
                        <div>${payload.rightPage.badHours.join(', ') || 'N/A'}</div>
                    </div>
                    <div class="info-item good">
                        <div class="text-bold">좋은 방향</div>
                        <div>${payload.rightPage.goodDirections.join(', ') || 'N/A'}</div>
                    </div>
                    <div class="info-item bad">
                        <div class="text-bold">나쁜 방향</div>
                        <div>${payload.rightPage.badDirections.join(', ') || 'N/A'}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- User Recording Section -->
        <div class="user-recording">
            <h3>사용자 기록 및 자기관리</h3>
            
            <div class="recording-section">
                <h4>A. 오늘의 기록</h4>
                <div style="margin-bottom: 2mm;">
                    <span style="font-size: 8pt; color: #4a5568;">가장 중요한 1가지:</span>
                    <div class="recording-line"></div>
                </div>
                <div style="margin-bottom: 2mm;">
                    <span style="font-size: 8pt; color: #4a5568;">잘한 점:</span>
                    <div class="recording-line"></div>
                    <div class="recording-line"></div>
                </div>
                <div>
                    <span style="font-size: 8pt; color: #4a5568;">개선 필요:</span>
                    <div class="recording-line"></div>
                    <div class="recording-line"></div>
                </div>
            </div>
            
            <div class="recording-section">
                <h4>B. 감정 체크</h4>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 안정
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 집중
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 피로
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 불안
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 만족
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 긴장
                    </div>
                </div>
            </div>
            
            <div class="recording-section">
                <h4>C. 실행 체크</h4>
                <div class="checkbox-group">
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 계획 실행
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 미루지 않음
                    </div>
                    <div class="checkbox-item">
                        <span class="checkbox"></span> 중요한 일 완료
                    </div>
                </div>
            </div>
            
            <div class="bottom-panel" style="margin-top: 2mm; padding-top: 1mm; border-top: 1px solid #cbd5e0;">
                <div class="text-small" style="color: #718096; font-size: 7pt;">
                    <strong>마음가짐:</strong> 
                    ${payload.bottomPanel.mindset.focusEmotion} / ${payload.bottomPanel.mindset.cautionEmotion}
                </div>
            </div>
        </div>
            </div>
        </div>
    </div>
    `;
  }
  
  /**
   * Group entries by week (Monday to Sunday)
   */
  private groupEntriesByWeek(entries: DailyDiaryPayload[]): Map<string, {entries: DailyDiaryPayload[]}> {
    const groups = new Map<string, {entries: DailyDiaryPayload[]}>();
    
    entries.forEach(entry => {
      // Calculate week start date (Monday)
      const entryDate = new Date(entry.date);
      const dayOfWeek = entryDate.getDay();
      const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Sunday is 0, we want Monday as start
      const weekStart = new Date(entryDate);
      weekStart.setDate(weekStart.getDate() + daysToMonday);
      const weekKey = weekStart.toISOString().split('T')[0]; // YYYY-MM-DD of Monday
      
      if (!groups.has(weekKey)) {
        groups.set(weekKey, {entries: []});
      }
      groups.get(weekKey)!.entries.push(entry);
    });
    
    return groups;
  }
  
  /**
   * Weekly Summary Page 생성
   */
  private generateWeeklySummary(weekKey: string, entries: DailyDiaryPayload[]): string {
    const firstDate = entries[0].date;
    const lastDate = entries[entries.length - 1].date;
    
    // Analyze weekly data
    const analysis = this.analyzeWeeklyData(entries);
    
    return `
    <div class="weekly-summary">
        <h3>주간 요약</h3>
        <div class="week-info">
            ${firstDate} ~ ${lastDate} (${entries.length}일)
        </div>
        
        <div class="summary-row">
            <div class="summary-col">
                <h4>🧭 좋은 방향 Top 3</h4>
                <ul>
                    ${analysis.goodDirections.slice(0, 3).map(([dir, count]: [string, number]) => 
                      `<li>${dir} (${count}회)</li>`
                    ).join('')}
                </ul>
            </div>
            
            <div class="summary-col">
                <h4>⏰ 주의 시간대 Top 3</h4>
                <ul>
                    ${analysis.badHours.slice(0, 3).map(([hour, count]: [string, number]) => 
                      `<li>${hour} (${count}일)</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
        
        <div class="summary-row">
            <div class="summary-col">
                <h4>🔑 주요 키워드</h4>
                <div style="padding: 3mm; background: #f7fafc; border-radius: 2mm;">
                    ${analysis.topKeywords.slice(0, 6).map((kw: string) => 
                      `<span style="display: inline-block; margin: 1mm; padding: 1mm 3mm; background: white; border: 1px solid #cbd5e0; border-radius: 1mm; font-size: 9pt;">${kw}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="summary-col">
                <h4>💭 마음가짐</h4>
                <div style="padding: 3mm; font-size: 9pt;">
                    <div>집중: ${analysis.focusEmotions.slice(0, 2).join(', ')}</div>
                    <div>주의: ${analysis.cautionEmotions.slice(0, 2).join(', ')}</div>
                </div>
            </div>
        </div>
        
        <div>
            <h4>✅ 이번 주 체크포인트</h4>
            <ul class="checkpoint-list">
                ${analysis.checkpoints.map((point: string) => 
                  `<li>${point}</li>`
                ).join('')}
            </ul>
        </div>
    </div>
    `;
  }
  
  /**
   * Generate Weekly Reflection Page
   */
  private generateWeeklyReflection(weekKey: string, entries: DailyDiaryPayload[]): string {
    const firstDate = entries[0].date;
    const lastDate = entries[entries.length - 1].date;
    
    return `
    <div class="weekly-reflection">
        <h3>주간 회고</h3>
        <div style="text-align: center; margin-bottom: 10mm; color: #718096; font-size: 10pt;">
            ${firstDate} ~ ${lastDate}
        </div>
        
        <!-- Section A: 이번 주 돌아보기 -->
        <div class="reflection-section">
            <h4>A. 이번 주 돌아보기</h4>
            
            <div class="reflection-item">
                <div class="reflection-label">이번 주 가장 잘한 점:</div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">이번 주 가장 아쉬운 점:</div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">이번 주 배운 점:</div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
            </div>
        </div>
        
        <!-- Section B: 감정 회고 -->
        <div class="reflection-section">
            <h4>B. 감정 회고</h4>
            
            <div class="reflection-item">
                <div class="reflection-label">이번 주 나의 주된 감정:</div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">감정 변화의 원인:</div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">다음 주에 조절할 점:</div>
                <div class="writing-line"></div>
            </div>
        </div>
        
        <!-- Section C: 실행 점검 -->
        <div class="reflection-section">
            <h4>C. 실행 점검</h4>
            
            <div class="reflection-item">
                <div class="reflection-label">완료한 중요한 일 3가지:</div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">미룬 일 / 놓친 일:</div>
                <div class="writing-line"></div>
            </div>
            
            <div class="reflection-item">
                <div class="reflection-label">다음 주 가장 중요한 1가지:</div>
                <div class="writing-line"></div>
            </div>
        </div>
        
        <!-- Section D: 자유 메모 -->
        <div class="reflection-section">
            <h4>D. 자유 메모</h4>
            <div class="memo-box"></div>
        </div>
    </div>
    `;
  }

  /**
   * Analyze weekly data for summary
   */
  private analyzeWeeklyData(entries: DailyDiaryPayload[]): any {
    // Count good directions
    const directionCounts = new Map<string, number>();
    entries.forEach(entry => {
      entry.rightPage.goodDirections?.forEach(dir => {
        directionCounts.set(dir, (directionCounts.get(dir) || 0) + 1);
      });
    });
    
    // Count bad hours
    const hourCounts = new Map<string, number>();
    entries.forEach(entry => {
      entry.rightPage.badHours?.forEach(hour => {
        hourCounts.set(hour, (hourCounts.get(hour) || 0) + 1);
      });
    });
    
    // Collect keywords
    const keywordSet = new Set<string>();
    entries.forEach(entry => {
      entry.leftPage.sajuSummary.mainCharacteristics?.forEach(kw => keywordSet.add(kw));
    });
    
    // Collect mindset emotions
    const focusEmotionSet = new Set<string>();
    const cautionEmotionSet = new Set<string>();
    entries.forEach(entry => {
      if (entry.bottomPanel?.mindset?.focusEmotion) {
        focusEmotionSet.add(entry.bottomPanel.mindset.focusEmotion);
      }
      if (entry.bottomPanel?.mindset?.cautionEmotion) {
        cautionEmotionSet.add(entry.bottomPanel.mindset.cautionEmotion);
      }
    });
    
    // Generate checkpoints based on week data
    const checkpoints: string[] = [];
    
    // Checkpoint 1: Most important days
    const importantDays = entries
      .filter(e => e.leftPage.sajuSummary.mainCharacteristics?.includes('중요') || 
                   e.leftPage.sajuSummary.mainCharacteristics?.includes('집중'))
      .map(e => e.calendar.weekday);
    if (importantDays.length > 0) {
      checkpoints.push(`${importantDays[0]}에 중요한 일 처리하기`);
    } else {
      checkpoints.push('주중에 중요한 결정 신중히 하기');
    }
    
    // Checkpoint 2: Good time utilization
    if (directionCounts.size > 0) {
      const bestDirection = Array.from(directionCounts.entries())[0][0];
      checkpoints.push(`${bestDirection} 방향 활용하여 성과 내기`);
    } else {
      checkpoints.push('좋은 시간대 활용하여 효율 높이기');
    }
    
    // Checkpoint 3: Emotional balance
    if (cautionEmotionSet.size > 0) {
      const firstCaution = Array.from(cautionEmotionSet)[0];
      checkpoints.push(`${firstCaution} 감정 관리에 주의하기`);
    } else {
      checkpoints.push('감정 균형 유지하며 안정적인 한 주 보내기');
    }
    
    return {
      goodDirections: Array.from(directionCounts.entries()).sort((a, b) => b[1] - a[1]),
      badHours: Array.from(hourCounts.entries()).sort((a, b) => b[1] - a[1]),
      topKeywords: Array.from(keywordSet).slice(0, 10),
      focusEmotions: Array.from(focusEmotionSet),
      cautionEmotions: Array.from(cautionEmotionSet),
      checkpoints
    };
  }
  
  /**
   * Month Divider Page 생성
   */
  private generateMonthDivider(monthKey: string, entries: DailyDiaryPayload[], period: PeriodDiaryResult): string {
    const [year, month] = monthKey.split('-');
    const monthNames = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const monthName = monthNames[parseInt(month)];
    
    // Calculate start and end dates for this month within the period
    const firstEntry = entries[0];
    const lastEntry = entries[entries.length - 1];
    
    return `
    <div class="month-divider">
        <h1>${year}년 ${monthName}</h1>
        
        <div class="month-info">
            <div>기간 내 일수: ${entries.length}일</div>
        </div>
        
        <div class="month-stats">
            <div class="text-bold">${firstEntry.date} ~ ${lastEntry.date}</div>
            <div style="margin-top: 5mm;">
                <div>총 ${entries.length}개 페이지</div>
                <div>주중: ${entries.filter(e => !['토', '일'].includes(e.calendar.weekday)).length}일</div>
                <div>주말: ${entries.filter(e => ['토', '일'].includes(e.calendar.weekday)).length}일</div>
            </div>
        </div>
    </div>
    `;
  }
  
  /**
   * Calculate page numbers for all entries
   */
  private calculatePageNumbers(period: PeriodDiaryResult): Map<string, number> {
    const pageMap = new Map<string, number>();
    let currentPage = 1; // Start with cover page
    
    // Cover page
    currentPage++;
    
    // Index pages (calculated based on entry count)
    const indexPageCount = Math.ceil(period.entries.length / 25); // ~25 entries per index page
    currentPage += indexPageCount;
    
    // Group by month first
    const monthGroups = this.groupEntriesByMonth(period.entries);
    
    // Process each month
    monthGroups.forEach((monthData, monthKey) => {
      // Month divider
      currentPage++;
      
      // Monthly summary (for periods > 30 days)
      if (period.totalDays > 30) {
        currentPage++;
      }
      
      // Group by week within month
      const weekGroups = this.groupEntriesByWeek(monthData.entries);
      
      weekGroups.forEach((weekData, weekKey) => {
        // Daily pages for this week
        weekData.entries.forEach(entry => {
          pageMap.set(entry.date, currentPage);
          currentPage++;
        });
        
        // Weekly summary (for periods > 7 days)
        if (period.totalDays > 7) {
          currentPage++;
        }
      });
    });
    
    return pageMap;
  }
  
  /**
   * Generate index pages
   */
  private generateIndexPages(period: PeriodDiaryResult, pageMap: Map<string, number>): string {
    let indexHtml = '<div class="index-page">\n';
    indexHtml += '  <h2>날짜별 인덱스</h2>\n';
    indexHtml += '  <table class="index-table">\n';
    
    // Group by month for better organization
    const monthGroups = this.groupEntriesByMonth(period.entries);
    let currentMonth = '';
    
    period.entries.forEach((entry, idx) => {
      const monthKey = entry.date.substring(0, 7);
      
      // Add month header if changed
      if (monthKey !== currentMonth) {
        const [year, month] = monthKey.split('-');
        const monthNames = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
        const monthName = monthNames[parseInt(month)];
        
        indexHtml += `    <tr>\n      <td colspan="4" class="index-month-header">${year}년 ${monthName}</td>\n    </tr>\n`;
        currentMonth = monthKey;
      }
      
      const pageNum = pageMap.get(entry.date) || 0;
      const keywords = entry.leftPage.sajuSummary.mainCharacteristics?.slice(0, 2).join(', ') || '';
      
      indexHtml += '    <tr>\n';
      indexHtml += `      <td class="date-col">${entry.date}</td>\n`;
      indexHtml += `      <td class="weekday-col">${entry.calendar.weekday}</td>\n`;
      indexHtml += `      <td class="page-col">p.${pageNum}</td>\n`;
      indexHtml += `      <td class="memo-col">${keywords}</td>\n`;
      indexHtml += '    </tr>\n';
      
      // Add page break every 25 entries
      if ((idx + 1) % 25 === 0 && idx < period.entries.length - 1) {
        indexHtml += '  </table>\n';
        indexHtml += '</div>\n';
        indexHtml += '<div class="index-page">\n';
        indexHtml += '  <h2>날짜별 인덱스 (계속)</h2>\n';
        indexHtml += '  <table class="index-table">\n';
      }
    });
    
    indexHtml += '  </table>\n';
    indexHtml += '</div>\n';
    
    return indexHtml;
  }

  /**
   * Monthly Summary Page 생성
   */
  private generateMonthlySummary(monthKey: string, entries: DailyDiaryPayload[]): string {
    const [year, month] = monthKey.split('-');
    const monthNames = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const monthName = monthNames[parseInt(month)];
    
    // Analyze monthly data
    const analysis = this.analyzeMonthlyData(entries);
    
    return `
    <div class="monthly-summary">
        <h2>${year}년 ${monthName} 요약</h2>
        
        <div class="summary-section">
            <h3>📊 월간 통계</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="text-bold">총 일수</div>
                    <div>${entries.length}일</div>
                </div>
                <div class="summary-item">
                    <div class="text-bold">페이지 수</div>
                    <div>${entries.length}페이지</div>
                </div>
            </div>
        </div>
        
        <div class="summary-section">
            <h3>🧭 좋은 방향 빈도</h3>
            <div class="summary-grid">
                ${analysis.goodDirections.slice(0, 4).map(([dir, count]: [string, number]) => `
                    <div class="summary-item">
                        <div class="text-bold">${dir}</div>
                        <div>${count}회 등장</div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="summary-section">
            <h3>⏰ 주의 시간대 빈도</h3>
            <div class="summary-grid">
                ${analysis.badHours.slice(0, 4).map(([hour, count]: [string, number]) => `
                    <div class="summary-item">
                        <div class="text-bold">${hour}</div>
                        <div>${count}일 주의</div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="summary-section">
            <h3>🔑 주요 키워드</h3>
            <div style="padding: 5mm; background: #f7fafc; border-radius: 2mm;">
                ${analysis.topKeywords.slice(0, 10).map((kw: string) => 
                  `<span style="display: inline-block; margin: 2mm; padding: 2mm 4mm; background: white; border: 1px solid #cbd5e0; border-radius: 2mm;">${kw}</span>`
                ).join('')}
            </div>
        </div>
        
        <div class="summary-section">
            <h3>💭 마음가짐 키워드</h3>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="text-bold">집중 감정</div>
                    <div>${analysis.focusEmotions.slice(0, 3).join(', ')}</div>
                </div>
                <div class="summary-item">
                    <div class="text-bold">주의 감정</div>
                    <div>${analysis.cautionEmotions.slice(0, 3).join(', ')}</div>
                </div>
            </div>
        </div>
    </div>
    `;
  }
  
  /**
   * Analyze monthly data for summary
   */
  private analyzeMonthlyData(entries: DailyDiaryPayload[]): any {
    // Count good directions
    const directionCounts = new Map<string, number>();
    entries.forEach(entry => {
      entry.rightPage.goodDirections?.forEach(dir => {
        directionCounts.set(dir, (directionCounts.get(dir) || 0) + 1);
      });
    });
    
    // Count bad hours
    const hourCounts = new Map<string, number>();
    entries.forEach(entry => {
      entry.rightPage.badHours?.forEach(hour => {
        hourCounts.set(hour, (hourCounts.get(hour) || 0) + 1);
      });
    });
    
    // Collect keywords
    const keywordSet = new Set<string>();
    entries.forEach(entry => {
      entry.leftPage.sajuSummary.mainCharacteristics?.forEach(kw => keywordSet.add(kw));
    });
    
    // Collect mindset emotions
    const focusEmotionSet = new Set<string>();
    const cautionEmotionSet = new Set<string>();
    entries.forEach(entry => {
      if (entry.bottomPanel?.mindset?.focusEmotion) {
        focusEmotionSet.add(entry.bottomPanel.mindset.focusEmotion);
      }
      if (entry.bottomPanel?.mindset?.cautionEmotion) {
        cautionEmotionSet.add(entry.bottomPanel.mindset.cautionEmotion);
      }
    });
    
    return {
      goodDirections: Array.from(directionCounts.entries()).sort((a, b) => b[1] - a[1]),
      badHours: Array.from(hourCounts.entries()).sort((a, b) => b[1] - a[1]),
      topKeywords: Array.from(keywordSet).slice(0, 20),
      focusEmotions: Array.from(focusEmotionSet),
      cautionEmotions: Array.from(cautionEmotionSet)
    };
  }
  
  /**
   * 생활 영역 HTML 생성
   */
  private generateLifeAreas(lifeAreas: any): string {
    const areas = [
      { key: 'health', name: '건강' },
      { key: 'wealth', name: '재물' },
      { key: 'relationship', name: '관계' },
      { key: 'career', name: '사업' }
    ];
    
    return areas.map(area => {
      const data = lifeAreas[area.key];
      if (!data) return '';
      
      return `
        <div style="margin-bottom: 2mm;">
          <strong>${area.name}:</strong> ${data.description || 'N/A'}
          <span class="text-small">(${data.score || 0}점)</span>
        </div>
      `;
    }).join('');
  }
  
  /**
   * 시간표 HTML 생성
   */
  private generateTimeSlots(timeSlots: any[]): string {
    if (!timeSlots || timeSlots.length === 0) {
      return '<div class="text-small">시간대별 정보가 없습니다.</div>';
    }
    
    const rows = timeSlots.slice(0, 8).map(slot => `
      <tr>
        <td>${slot.time || ''}</td>
        <td>${slot.label || ''}</td>
        <td>${slot.qimenLabel || ''}</td>
        <td style="width: 40%;"></td>
      </tr>
    `).join('');
    
    return `
      <table class="time-slots">
        <thead>
          <tr>
            <th>시간</th>
            <th>시간대</th>
            <th>운</th>
            <th>메모</th>
          </tr>
        </thead>
        <tbody>
          ${rows}
        </tbody>
      </table>
    `;
  }
  
  /**
   * HTML을 PDF로 변환 (Python converter 사용)
   */
  private async convertHtmlToPdf(htmlPath: string, pdfPath: string): Promise<void> {
    try {
      // Python PDF converter 사용
      // 먼저 period data를 JSON으로 저장 (이미 renderPdf에서 처리됨)
      const jsonPath = htmlPath.replace('.html', '.json');
      
      // Python converter 실행
      const pythonScript = path.join(__dirname, 'simplePdfConverter.py');
      const command = `python "${pythonScript}" --convert-period "${jsonPath}" --output "${pdfPath}"`;
      
      try {
        execSync(command, { 
          stdio: 'pipe',
          encoding: 'utf-8'
        });
        console.log(`PDF 생성 완료 (Python ReportLab): ${pdfPath}`);
      } catch (error) {
        // Python converter 실행 실패 시 경고만 출력
        console.warn('Python PDF converter 실행 실패:', error);
        console.log('HTML 파일은 생성되었습니다:', htmlPath);
        throw new Error('PDF 변환 실패. Python과 reportlab이 설치되어 있는지 확인해주세요.');
      }
    } catch (error) {
      console.error('PDF 변환 중 오류 발생:', error);
      throw error;
    }
  }
}

// ============================================================
// Export Functions
// ============================================================

/**
 * 기간별 다이어리 PDF 렌더링 (함수 형태)
 */
export async function renderPeriodDiaryPdf(input: {
  period: PeriodDiaryResult;
  outputPath?: string;
  mode?: 'standard' | 'large';
  ownerLabel?: string;
  productTitle?: string;
}): Promise<{
  success: boolean;
  outputPath?: string;
  pageCount: number;
}> {
  const renderer = new PeriodDiaryPdfRenderer('./test_output', input.mode || 'standard');
  return renderer.renderPdf({
    period: input.period,
    outputPath: input.outputPath,
    includeTableOfContents: input.period.totalDays > 30,
    mode: input.mode || 'standard',
    ownerLabel: input.ownerLabel,
    productTitle: input.productTitle
  });
}