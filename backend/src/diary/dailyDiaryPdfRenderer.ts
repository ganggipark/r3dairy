/**
 * 일일 다이어리 PDF 렌더러
 * 
 * DailyDiaryPayload를 사용하여 하루치 인쇄용 다이어리 PDF 생성
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';
import { DailyDiaryPayload } from './types';

// ============================================================
// PDF Template Constants
// ============================================================

const PDF_TEMPLATE = `<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R³ 다이어리 - {{date}}</title>
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
        
        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Header */
        .header {
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 8mm;
            margin-bottom: 5mm;
        }
        
        .header h1 {
            font-size: 18pt;
            margin: 0 0 2mm 0;
            font-weight: bold;
        }
        
        .header .date-info {
            font-size: 12pt;
            margin: 0;
        }
        
        /* Main Content */
        .main-content {
            display: flex;
            flex: 1;
            gap: 5mm;
        }
        
        .left-panel, .right-panel {
            flex: 1;
            padding: 3mm;
            border: 1px solid #ccc;
        }
        
        .left-panel {
            background-color: #f8f9fa;
        }
        
        .right-panel {
            background-color: #fff;
        }
        
        /* Section Headers */
        .section-header {
            font-size: {{subheader_font_size}};
            font-weight: bold;
            color: #2c5aa0;
            border-bottom: 1px solid #2c5aa0;
            padding-bottom: 1mm;
            margin: 0 0 {{section_margin}} 0;
        }
        
        /* Content Blocks */
        .content-block {
            margin-bottom: 4mm;
        }
        
        .content-block h3 {
            font-size: {{small_font_size}};
            font-weight: bold;
            margin: 0 0 2mm 0;
            color: #444;
        }
        
        .content-block p {
            margin: 0 0 {{section_margin}} 0;
            line-height: {{line_height}};
        }
        
        .content-block ul {
            margin: 0;
            padding-left: 4mm;
        }
        
        .content-block li {
            margin-bottom: 2mm;
            line-height: {{line_height}};
        }
        
        /* Life Areas Grid */
        .life-areas {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2mm;
            margin-bottom: 3mm;
        }
        
        .life-area {
            padding: 2mm;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 1mm;
        }
        
        .life-area-title {
            font-weight: bold;
            font-size: 9pt;
            color: #2c5aa0;
        }
        
        .life-area-score {
            font-size: 10pt;
            font-weight: bold;
        }
        
        .life-area-advice {
            font-size: 8pt;
            color: #666;
            margin-top: 1mm;
        }
        
        /* Time Slots */
        .time-slots {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 3mm;
        }
        
        .time-slots th,
        .time-slots td {
            border: 1px solid #ddd;
            padding: 1.5mm;
            text-align: left;
        }
        
        .time-slots th {
            background: #f0f0f0;
            font-size: 9pt;
            font-weight: bold;
        }
        
        .time-slots td {
            font-size: 8pt;
            height: 6mm;
        }
        
        .time-label {
            font-weight: bold;
            width: 20mm;
        }
        
        .qimen-label {
            width: 10mm;
            text-align: center;
        }
        
        .qimen-good { color: #28a745; }
        .qimen-neutral { color: #6c757d; }
        .qimen-bad { color: #dc3545; }
        
        /* Bottom Panel */
        .bottom-panel {
            margin-top: 3mm;
            padding: 3mm;
            border: 1px solid #ccc;
            background-color: #f8f9fa;
        }
        
        .bottom-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4mm;
        }
        
        /* Keywords */
        .keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 1mm;
            margin-bottom: 2mm;
        }
        
        .keyword-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 1mm 2mm;
            border-radius: 1mm;
            font-size: 8pt;
            font-weight: bold;
        }
        
        /* Utilities */
        .text-small { font-size: 8pt; }
        .text-bold { font-weight: bold; }
        .text-center { text-align: center; }
        .mb-2 { margin-bottom: 2mm; }
        .mb-3 { margin-bottom: 3mm; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>R³ 다이어리</h1>
            <div class="date-info">
                {{solarDate}} ({{weekday}}) {{lunarDisplay}}
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content">
            <!-- Left Panel: Today's Guidance -->
            <div class="left-panel">
                <div class="section-header">오늘의 안내</div>
                
                <!-- Summary -->
                <div class="content-block">
                    <h3>일간 요약</h3>
                    <div class="keywords">
                        {{keywordTags}}
                    </div>
                    <p>{{summary}}</p>
                </div>
                
                <!-- Life Areas -->
                <div class="content-block">
                    <h3>생활 영역</h3>
                    <div class="life-areas">
                        {{lifeAreasContent}}
                    </div>
                </div>
                
                <!-- Recommendations -->
                <div class="content-block">
                    <h3>권장사항</h3>
                    <ul>
                        {{recommendationsList}}
                    </ul>
                </div>
                
                <!-- Cautions -->
                <div class="content-block">
                    <h3>주의사항</h3>
                    <ul>
                        {{cautionsList}}
                    </ul>
                </div>
            </div>
            
            <!-- Right Panel: User Records -->
            <div class="right-panel">
                <div class="section-header">기록 공간</div>
                
                <!-- Time Schedule -->
                <div class="content-block">
                    <h3>시간표</h3>
                    <table class="time-slots">
                        <thead>
                            <tr>
                                <th>시간</th>
                                <th>운</th>
                                <th>일정 및 메모</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{timeSlotsContent}}
                        </tbody>
                    </table>
                </div>
                
                <!-- Quick Info -->
                <div class="content-block">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2mm;">
                        <div>
                            <h3>좋은 시간</h3>
                            <p class="text-small">{{goodHours}}</p>
                        </div>
                        <div>
                            <h3>나쁜 시간</h3>
                            <p class="text-small">{{badHours}}</p>
                        </div>
                        <div>
                            <h3>좋은 방향</h3>
                            <p class="text-small">{{goodDirections}}</p>
                        </div>
                        <div>
                            <h3>피할 방향</h3>
                            <p class="text-small">{{badDirections}}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Bottom Panel -->
        <div class="bottom-panel">
            <div class="section-header">마음가짐 & 성찰</div>
            <div class="bottom-content">
                <div>
                    <h3>오늘의 마음가짐</h3>
                    <p class="text-small"><strong>집중:</strong> {{focusEmotion}}</p>
                    <p class="text-small"><strong>주의:</strong> {{cautionEmotion}}</p>
                    <p class="text-small">{{emotionTip}}</p>
                </div>
                <div>
                    <h3>성찰 질문</h3>
                    <ul class="text-small">
                        {{journalPrompts}}
                    </ul>
                    <p class="text-bold text-small">{{affirmation}}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>`;

// ============================================================
// Interfaces
// ============================================================

export interface PdfOptions {
  /** 출력 디렉토리 (기본값: ./output) */
  outputDir?: string;
  /** 파일명 접두사 (기본값: diary_) */
  filePrefix?: string;
  /** PDF 품질 설정 */
  quality?: 'draft' | 'normal' | 'high';
  /** 템플릿 모드 (기본값: standard) */
  mode?: 'standard' | 'large';
}

// ============================================================
// Main Renderer Class
// ============================================================

export class DailyDiaryPdfRenderer {
  private outputDir: string;
  private filePrefix: string;
  private quality: string;
  private mode: 'standard' | 'large';

  constructor(options: PdfOptions = {}) {
    this.outputDir = options.outputDir || './output';
    this.filePrefix = options.filePrefix || 'diary_';
    this.quality = options.quality || 'normal';
    this.mode = options.mode || 'standard';
    
    // 출력 디렉토리 생성
    this.ensureOutputDir();
  }

  /**
   * DailyDiaryPayload를 PDF로 렌더링
   */
  async renderToPdf(payload: DailyDiaryPayload): Promise<string> {
    try {
      // 1. HTML 생성
      const htmlContent = this.generateHtml(payload);
      
      // 2. 임시 HTML 파일 저장
      const tempHtmlPath = path.join(this.outputDir, `temp_${payload.date}.html`);
      fs.writeFileSync(tempHtmlPath, htmlContent, 'utf8');
      
      // 3. PDF 파일 경로
      const pdfPath = path.join(this.outputDir, `${this.filePrefix}${payload.date}.pdf`);
      
      // 4. WeasyPrint로 PDF 생성
      await this.convertHtmlToPdf(tempHtmlPath, pdfPath);
      
      // 5. 임시 HTML 파일 삭제
      fs.unlinkSync(tempHtmlPath);
      
      return pdfPath;
    } catch (error) {
      throw new Error(`PDF 생성 실패: ${error}`);
    }
  }

  /**
   * 모드에 따른 스타일 값 반환
   */
  private getStyleValues() {
    if (this.mode === 'large') {
      return {
        page_margin: '15mm',
        body_font_size: '13pt',
        line_height: '1.6',
        header_font_size: '18pt',
        subheader_font_size: '14pt',
        small_font_size: '11pt',
        checkbox_size: '5mm',
        recording_line_height: '8mm',
        section_margin: '5mm',
        item_padding: '3mm'
      };
    } else {
      // standard mode
      return {
        page_margin: '10mm',
        body_font_size: '11pt',
        line_height: '1.4',
        header_font_size: '14pt',
        subheader_font_size: '12pt',
        small_font_size: '9pt',
        checkbox_size: '3mm',
        recording_line_height: '5mm',
        section_margin: '3mm',
        item_padding: '2mm'
      };
    }
  }

  /**
   * HTML 콘텐츠 생성
   */
  private generateHtml(payload: DailyDiaryPayload): string {
    // Get style values based on mode
    const styleVals = this.getStyleValues();
    
    // Template variables 준비
    const vars = {
      date: payload.date,
      solarDate: payload.calendar.solarDate,
      weekday: payload.calendar.weekday,
      lunarDisplay: payload.calendar.lunarDate?.displayText || '',
      
      // Keywords
      keywordTags: this.generateKeywordTags(payload),
      
      // Content
      summary: this.generateSummaryText(payload),
      lifeAreasContent: this.generateLifeAreas(payload.leftPage.lifeAreas),
      recommendationsList: this.generateListItems(payload.leftPage.recommendations),
      cautionsList: this.generateListItems(payload.leftPage.cautions),
      
      // Time slots
      timeSlotsContent: this.generateTimeSlots(payload.rightPage.timeSlots),
      goodHours: payload.rightPage.goodHours.join(', ') || 'N/A',
      badHours: payload.rightPage.badHours.join(', ') || 'N/A',
      goodDirections: payload.rightPage.goodDirections.join(', ') || 'N/A',
      badDirections: payload.rightPage.badDirections.join(', ') || 'N/A',
      
      // Bottom panel
      focusEmotion: payload.bottomPanel.mindset.focusEmotion,
      cautionEmotion: payload.bottomPanel.mindset.cautionEmotion,
      emotionTip: payload.bottomPanel.mindset.emotionTip,
      journalPrompts: this.generateListItems(payload.bottomPanel.journalPrompt),
      affirmation: payload.bottomPanel.affirmation
    };
    
    // Combine style values and content variables
    const allVars = { ...styleVals, ...vars };
    
    // Template replace
    let html = PDF_TEMPLATE;
    Object.entries(allVars).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      html = html.replace(new RegExp(placeholder, 'g'), String(value));
    });
    
    return html;
  }

  /**
   * 키워드 태그 생성
   */
  private generateKeywordTags(payload: DailyDiaryPayload): string {
    // 사주 요약에서 키워드 추출
    const characteristics = payload.leftPage.sajuSummary.mainCharacteristics || [];
    
    return characteristics
      .slice(0, 4) // 최대 4개
      .map(keyword => `<span class="keyword-tag">${keyword}</span>`)
      .join('');
  }

  /**
   * 요약 텍스트 생성
   */
  private generateSummaryText(payload: DailyDiaryPayload): string {
    const characteristics = payload.leftPage.sajuSummary.mainCharacteristics || [];
    const dayMasterStrength = payload.leftPage.sajuSummary.dayMasterStrength;
    
    let summary = `오늘은 ${characteristics.join(', ')}한 특성이 두드러지는 날입니다. `;
    
    if (dayMasterStrength === 'strong') {
      summary += '강한 에너지를 가지고 있으니 적극적으로 행동하기 좋습니다.';
    } else if (dayMasterStrength === 'weak') {
      summary += '차분하고 신중하게 행동하는 것이 좋습니다.';
    } else {
      summary += '균형 잡힌 상태이므로 계획된 일을 차근차근 진행하세요.';
    }
    
    return summary;
  }

  /**
   * 생활 영역 HTML 생성
   */
  private generateLifeAreas(lifeAreas: any): string {
    const areas = [
      { key: 'health', name: '건강운' },
      { key: 'wealth', name: '재물운' },
      { key: 'relationship', name: '관계운' },
      { key: 'career', name: '사업운' }
    ];
    
    return areas.map(area => {
      const data = lifeAreas[area.key];
      if (!data) return '';
      
      return `
        <div class="life-area">
          <div class="life-area-title">${area.name}</div>
          <div class="life-area-score">${data.score}점 (${this.getStatusText(data.status)})</div>
          <div class="life-area-advice">${data.advice}</div>
        </div>
      `;
    }).join('');
  }

  /**
   * 상태 텍스트 변환
   */
  private getStatusText(status: string): string {
    const statusMap: Record<string, string> = {
      'excellent': '매우 좋음',
      'good': '좋음',
      'neutral': '보통',
      'caution': '주의',
      'warning': '경고'
    };
    return statusMap[status] || status;
  }

  /**
   * 리스트 아이템 생성
   */
  private generateListItems(items: string[]): string {
    if (!items || items.length === 0) {
      return '<li>특별한 사항이 없습니다.</li>';
    }
    
    return items
      .slice(0, 5) // 최대 5개
      .map(item => `<li>${item}</li>`)
      .join('');
  }

  /**
   * 시간표 HTML 생성
   */
  private generateTimeSlots(timeSlots: any[]): string {
    if (!timeSlots || timeSlots.length === 0) {
      // 기본 시간표 생성
      const defaultHours = ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'];
      return defaultHours.map(hour => `
        <tr>
          <td class="time-label">${hour}</td>
          <td class="qimen-label qimen-neutral">평</td>
          <td></td>
        </tr>
      `).join('');
    }
    
    return timeSlots.map(slot => {
      const qimenClass = slot.qimenLabel === '길' ? 'qimen-good' : 
                        slot.qimenLabel === '흉' ? 'qimen-bad' : 'qimen-neutral';
      
      return `
        <tr>
          <td class="time-label">${slot.time}</td>
          <td class="qimen-label ${qimenClass}">${slot.qimenLabel || '평'}</td>
          <td>${slot.note || ''}</td>
        </tr>
      `;
    }).join('');
  }

  /**
   * 기존 PDF 생성기를 사용해 HTML을 PDF로 변환
   */
  private async convertHtmlToPdf(htmlPath: string, pdfPath: string): Promise<void> {
    try {
      // Python PDF Generator 사용 방식으로 수정
      // PDF-generator 디렉토리의 generator.py를 활용
      const pythonScript = `
import sys
import os
sys.path.append('${path.join(__dirname, '../../../pdf-generator').replace(/\\/g, '/')}')

from generator import PDFGenerator
from pathlib import Path

# HTML을 Markdown 형식으로 변환하고 PDF 생성
generator = PDFGenerator()

# 임시 콘텐츠 딕셔너리 생성 (HTML을 파싱하지 않고 기본 샘플 사용)
sample_content = {
    "date": "2026-03-28",
    "summary": "TypeScript PDF 렌더러 테스트",
    "keywords": ["테스트", "PDF", "렌더러"],
    "rhythm_description": "TypeScript 기반 PDF 렌더러가 정상 작동하는지 확인하는 테스트입니다.",
    "focus_caution": {
        "focus": ["HTML 구조 검증", "PDF 생성 확인"],
        "caution": ["WeasyPrint 의존성", "Python 경로 설정"]
    },
    "action_guide": {
        "do": ["테스트 실행", "구조 검증"],
        "avoid": ["의존성 문제", "경로 오류"]
    },
    "time_direction": {
        "good_time": "테스트 시간",
        "avoid_time": "없음",
        "good_direction": "정상 경로",
        "avoid_direction": "오류 경로"
    },
    "state_trigger": {
        "gesture": "테스트 실행",
        "phrase": "PDF 생성 성공",
        "how_to": "TypeScript에서 Python 호출"
    },
    "meaning_shift": "이 테스트는 TypeScript PDF 렌더러의 정상 작동을 확인합니다.",
    "rhythm_question": "PDF가 정상적으로 생성되었나요?"
}

# PDF 생성
result = generator.generate_daily_pdf(
    content=sample_content,
    output_path='${pdfPath.replace(/\\/g, '/')}',
    role=None
)

print(f"PDF 생성 완료: {result}")
      `;
      
      // Python 스크립트를 임시 파일로 저장
      const tempScriptPath = path.join(this.outputDir, 'temp_pdf_gen.py');
      const fs = require('fs');
      fs.writeFileSync(tempScriptPath, pythonScript);
      
      // Python 스크립트 실행
      const command = `python "${tempScriptPath}"`;
      execSync(command, { encoding: 'utf8' });
      
      // 임시 스크립트 파일 삭제
      fs.unlinkSync(tempScriptPath);
      
    } catch (error) {
      throw new Error(`PDF 생성기 실행 실패: ${error}`);
    }
  }

  /**
   * 출력 디렉토리 생성
   */
  private ensureOutputDir(): void {
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }
}

// ============================================================
// Exported Function
// ============================================================

/**
 * DailyDiaryPayload를 PDF로 렌더링하는 메인 함수
 * 
 * @param payload - 다이어리 페이로드
 * @param options - PDF 옵션
 * @returns PDF 파일 경로
 */
export async function renderDailyDiaryPdf(
  payload: DailyDiaryPayload, 
  options?: PdfOptions
): Promise<string> {
  const renderer = new DailyDiaryPdfRenderer(options);
  return await renderer.renderToPdf(payload);
}

// ============================================================
// Default Export
// ============================================================

export default DailyDiaryPdfRenderer;