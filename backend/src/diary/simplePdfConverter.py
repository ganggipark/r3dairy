"""
Simple PDF Converter for Diary System using ReportLab
No external dependencies required - pure Python solution
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import re


class SimplePdfConverter:
    """Convert diary data to PDF using ReportLab"""
    
    def __init__(self, mode='standard'):
        self.output_dir = Path(__file__).parent / "test_output"
        self.output_dir.mkdir(exist_ok=True)
        self.mode = mode
        self.styles = self._create_styles()
        
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles based on mode"""
        base_styles = getSampleStyleSheet()
        
        # Set font sizes based on mode
        if self.mode == 'large':
            title_size = 24
            h1_size = 18
            h2_size = 14
            body_size = 12
            small_size = 10
            line_height = 18
        else:  # standard mode
            title_size = 20
            h1_size = 14
            h2_size = 11
            body_size = 10
            small_size = 8
            line_height = 14
        
        custom_styles = {
            'Title': ParagraphStyle(
                'Title',
                parent=base_styles['Title'],
                fontSize=title_size,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=colors.HexColor('#2D3748')
            ),
            'Heading1': ParagraphStyle(
                'Heading1',
                parent=base_styles['Heading1'],
                fontSize=14,
                spaceAfter=8,
                textColor=colors.HexColor('#2D3748'),
                borderWidth=0,
                borderPadding=0,
                borderColor=colors.HexColor('#E2E8F0'),
                borderRadius=0
            ),
            'Heading2': ParagraphStyle(
                'Heading2',
                parent=base_styles['Heading2'],
                fontSize=11,
                spaceAfter=6,
                textColor=colors.HexColor('#4A5568')
            ),
            'Body': ParagraphStyle(
                'Body',
                parent=base_styles['BodyText'],
                fontSize=body_size,
                leading=line_height,
                alignment=TA_JUSTIFY,
                spaceAfter=6
            ),
            'Bullet': ParagraphStyle(
                'Bullet',
                parent=base_styles['BodyText'],
                fontSize=8,
                leftIndent=15,
                bulletIndent=8,
                spaceAfter=3
            ),
            'Date': ParagraphStyle(
                'Date',
                parent=base_styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#718096')
            ),
            'Keyword': ParagraphStyle(
                'Keyword',
                parent=base_styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#5A67D8'),
                backColor=colors.HexColor('#EDF2F7')
            ),
            'CoverTitle': ParagraphStyle(
                'CoverTitle',
                parent=base_styles['Title'],
                fontSize=title_size * 1.8,
                alignment=TA_CENTER,
                spaceAfter=20,
                textColor=colors.HexColor('#2D3748')
            ),
            'CoverSubtitle': ParagraphStyle(
                'CoverSubtitle',
                parent=base_styles['Normal'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=40,
                textColor=colors.HexColor('#4A5568')
            )
        }
        
        return custom_styles
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
        return text.strip()
    
    def convert_daily_json_to_pdf(self, json_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert daily diary JSON to PDF
        
        Args:
            json_path: Path to JSON file with DailyDiaryPayload
            output_path: Optional output path for PDF
            
        Returns:
            Result dictionary with success status and file path
        """
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                return {
                    "success": False,
                    "error": f"JSON file not found: {json_path}"
                }
            
            # Load JSON content
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate output path if not provided
            if not output_path:
                output_path = str(json_file.with_suffix('.pdf'))
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=2*cm,
                bottomMargin=2*cm,
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            
            # Build content
            story = self._build_daily_content(data)
            
            # Generate PDF
            doc.build(story)
            
            return {
                "success": True,
                "outputPath": output_path,
                "fileSize": os.path.getsize(output_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def convert_period_json_to_pdf(self, json_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert period diary JSON bundle to PDF
        
        Args:
            json_path: Path to JSON file with PeriodDiaryResult
            output_path: Optional output path for PDF
            
        Returns:
            Result dictionary with success status and file path
        """
        try:
            json_file = Path(json_path)
            if not json_file.exists():
                return {
                    "success": False,
                    "error": f"JSON file not found: {json_path}"
                }
            
            # Load JSON content
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Generate output path if not provided
            if not output_path:
                output_path = str(json_file.with_suffix('.pdf'))
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=2*cm,
                bottomMargin=2*cm,
                leftMargin=2*cm,
                rightMargin=2*cm
            )
            
            # Build content
            story = []
            
            # Add cover page
            story.extend(self._build_cover_page(data))
            story.append(PageBreak())
            
            # Calculate page numbers for index
            entries = data.get('entries', [])
            total_days = data.get('totalDays', len(entries))
            page_map = self._calculate_page_numbers(data)
            
            # Add index pages
            story.extend(self._build_index_pages(data, page_map))
            story.append(PageBreak())
            
            # Group entries by month and add month dividers
            month_groups = self._group_by_month(entries)
            
            for month_key, month_entries in month_groups.items():
                # Add month divider
                story.extend(self._build_month_divider(month_key, month_entries))
                story.append(PageBreak())
                
                # Add monthly summary (only for multi-month periods)
                if total_days > 30:
                    story.extend(self._build_monthly_summary(month_key, month_entries))
                    story.append(PageBreak())
                
                # Group month entries by week and add weekly summaries
                week_groups = self._group_by_week(month_entries)
                
                for week_key, week_entries in week_groups.items():
                    # Add daily pages for this week
                    for entry in week_entries:
                        story.extend(self._build_daily_content(entry))
                        story.append(PageBreak())
                    
                    # Add weekly summary (only for periods longer than a week)
                    if total_days > 7:
                        story.extend(self._build_weekly_summary(week_key, week_entries))
                        story.append(PageBreak())
                        # Add weekly reflection page after summary
                        story.extend(self._build_weekly_reflection(week_key, week_entries))
                        # Add page break except after the very last entry
                        if not (month_key == list(month_groups.keys())[-1] and 
                                week_key == list(week_groups.keys())[-1]):
                            story.append(PageBreak())
            
            # Generate PDF
            doc.build(story)
            
            # Calculate page count
            month_count = len(month_groups)
            monthly_summary_pages = month_count if total_days > 30 else 0
            
            # Count weekly summaries
            weekly_summary_count = 0
            if total_days > 7:
                for month_entries in month_groups.values():
                    week_groups = self._group_by_week(month_entries)
                    weekly_summary_count += len(week_groups)
            
            page_count = 1 + month_count + monthly_summary_pages + weekly_summary_count + len(entries)
            
            return {
                "success": True,
                "outputPath": output_path,
                "fileSize": os.path.getsize(output_path),
                "pageCount": page_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _group_by_month(self, entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group entries by month"""
        from collections import OrderedDict
        
        groups = OrderedDict()
        for entry in entries:
            month_key = entry.get('date', '')[:7]  # YYYY-MM
            if month_key not in groups:
                groups[month_key] = []
            groups[month_key].append(entry)
        
        return groups
    
    def _build_month_divider(self, month_key: str, entries: List[Dict[str, Any]]) -> List:
        """Build month divider page"""
        story = []
        
        year, month = month_key.split('-')
        month_names = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        month_name = month_names[int(month)]
        
        # Month title
        story.append(Spacer(1, 5*cm))
        story.append(Paragraph(f"{year}년 {month_name}", self.styles['CoverTitle']))
        story.append(Spacer(1, 2*cm))
        
        # Month info
        first_date = entries[0].get('date', '')
        last_date = entries[-1].get('date', '')
        
        story.append(Paragraph(f"기간: {first_date} ~ {last_date}", self.styles['Date']))
        story.append(Paragraph(f"총 {len(entries)}일", self.styles['Date']))
        
        return story
    
    def _build_monthly_summary(self, month_key: str, entries: List[Dict[str, Any]]) -> List:
        """Build monthly summary page"""
        story = []
        
        year, month = month_key.split('-')
        month_names = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        month_name = month_names[int(month)]
        
        story.append(Paragraph(f"{year}년 {month_name} 요약", self.styles['Heading1']))
        story.append(Spacer(1, 0.5*cm))
        
        # Basic stats
        story.append(Paragraph("📊 월간 통계", self.styles['Heading2']))
        story.append(Paragraph(f"• 총 일수: {len(entries)}일", self.styles['Body']))
        story.append(Paragraph(f"• 페이지 수: {len(entries)}페이지", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        
        # Analyze good directions
        direction_counts = {}
        for entry in entries:
            content = entry.get('content', {})
            time_dir = content.get('timeDirection', {})
            good_dir = time_dir.get('good_direction', '')
            if good_dir:
                direction_counts[good_dir] = direction_counts.get(good_dir, 0) + 1
        
        if direction_counts:
            story.append(Paragraph("🧭 좋은 방향 빈도", self.styles['Heading2']))
            sorted_dirs = sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for dir_name, count in sorted_dirs:
                story.append(Paragraph(f"• {dir_name}: {count}회", self.styles['Body']))
            story.append(Spacer(1, 0.3*cm))
        
        # Collect keywords
        all_keywords = []
        for entry in entries:
            content = entry.get('content', {})
            keywords = content.get('keywords', [])
            all_keywords.extend(keywords)
        
        if all_keywords:
            unique_keywords = list(set(all_keywords))[:10]
            story.append(Paragraph("🔑 주요 키워드", self.styles['Heading2']))
            story.append(Paragraph(", ".join(unique_keywords), self.styles['Body']))
        
        return story
    
    def _group_by_week(self, entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group entries by week (Monday to Sunday)"""
        from collections import OrderedDict
        from datetime import datetime, timedelta
        
        groups = OrderedDict()
        for entry in entries:
            entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
            # Calculate week start (Monday)
            days_since_monday = entry_date.weekday()
            week_start = entry_date - timedelta(days=days_since_monday)
            week_key = week_start.strftime('%Y-%m-%d')
            
            if week_key not in groups:
                groups[week_key] = []
            groups[week_key].append(entry)
        
        return groups
    
    def _calculate_page_numbers(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate page numbers for all entries"""
        page_map = {}
        current_page = 1  # Start with cover page
        
        # Cover page
        current_page += 1
        
        # Index pages (based on entry count)
        entries = data.get('entries', [])
        index_page_count = max(1, len(entries) // 25 + (1 if len(entries) % 25 else 0))
        current_page += index_page_count
        
        # Group by month
        month_groups = self._group_by_month(entries)
        total_days = data.get('totalDays', len(entries))
        
        for month_key, month_entries in month_groups.items():
            # Month divider
            current_page += 1
            
            # Monthly summary (for periods > 30 days)
            if total_days > 30:
                current_page += 1
            
            # Group by week within month
            week_groups = self._group_by_week(month_entries)
            
            for week_key, week_entries in week_groups.items():
                # Daily pages for this week
                for entry in week_entries:
                    page_map[entry['date']] = current_page
                    current_page += 1
                
                # Weekly summary (for periods > 7 days)
                if total_days > 7:
                    current_page += 1
        
        return page_map
    
    def _build_index_pages(self, data: Dict[str, Any], page_map: Dict[str, int]) -> List:
        """Build index pages with date and page number mapping"""
        story = []
        entries = data.get('entries', [])
        
        # Index header
        story.append(Paragraph("날짜별 인덱스", self.styles['Title']))
        story.append(Spacer(1, 0.5*cm))
        
        # Build index table data
        table_data = []
        current_month = ''
        
        for entry in entries:
            date = entry['date']
            month_key = date[:7]  # YYYY-MM
            
            # Add month header if changed
            if month_key != current_month:
                year, month = month_key.split('-')
                month_names = ['', '1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
                month_name = month_names[int(month)]
                table_data.append([
                    Paragraph(f"<b>{year}년 {month_name}</b>", self.styles['Heading2']),
                    '', '', ''
                ])
                current_month = month_key
            
            # Add entry row
            calendar = entry.get('calendar', {})
            weekday = calendar.get('weekday', '')
            page_num = page_map.get(date, 0)
            keywords = ', '.join(entry.get('leftPage', {}).get('sajuSummary', {}).get('mainCharacteristics', [])[:2])
            
            table_data.append([
                Paragraph(date, self.styles['Body']),
                Paragraph(weekday, self.styles['Body']),
                Paragraph(f"p.{page_num}", self.styles['Body']),
                Paragraph(keywords, self.styles['Bullet'])
            ])
        
        # Create table
        if table_data:
            col_widths = [3.5*cm, 2*cm, 2*cm, 8*cm]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F4F8')),
                ('SPAN', (0, 0), (3, 0))  # Span month header rows
            ]))
            story.append(table)
        
        return story
    
    def _build_weekly_reflection(self, week_key: str, entries: List[Dict[str, Any]]) -> List:
        """Build weekly reflection page for user to fill in"""
        story = []
        
        first_date = entries[0].get('date', '')
        last_date = entries[-1].get('date', '')
        
        # Title
        story.append(Paragraph("주간 회고", self.styles['Title']))
        story.append(Paragraph(f"{first_date} ~ {last_date}", self.styles['Date']))
        story.append(Spacer(1, 0.5*cm))
        
        # Section A: 이번 주 돌아보기
        story.append(Paragraph("<b>A. 이번 주 돌아보기</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*cm))
        
        story.append(Paragraph("이번 주 가장 잘한 점:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("이번 주 가장 아쉬운 점:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("이번 주 배운 점:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.5*cm))
        
        # Section B: 감정 회고
        story.append(Paragraph("<b>B. 감정 회고</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*cm))
        
        story.append(Paragraph("이번 주 나의 주된 감정:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("감정 변화의 원인:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("다음 주에 조절할 점:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.5*cm))
        
        # Section C: 실행 점검
        story.append(Paragraph("<b>C. 실행 점검</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.2*cm))
        
        story.append(Paragraph("완료한 중요한 일 3가지:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("1. " + "_" * 55, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("2. " + "_" * 55, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("3. " + "_" * 55, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("미룬 일 / 놓친 일:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.4*cm))
        
        story.append(Paragraph("다음 주 가장 중요한 1가지:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.5*cm))
        
        # Section D: 자유 메모
        story.append(Paragraph("<b>D. 자유 메모</b>", self.styles['Heading1']))
        story.append(Spacer(1, 0.3*cm))
        
        # Create a bordered box for memo
        memo_data = [["" for _ in range(1)] for _ in range(8)]  # 8 rows for memo space
        memo_table = Table(memo_data, colWidths=[15*cm], rowHeights=[0.8*cm]*8)
        memo_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
        ]))
        story.append(memo_table)
        
        return story
    
    def _build_weekly_summary(self, week_key: str, entries: List[Dict[str, Any]]) -> List:
        """Build weekly summary page"""
        story = []
        
        first_date = entries[0].get('date', '')
        last_date = entries[-1].get('date', '')
        
        story.append(Paragraph("주간 요약", self.styles['Heading1']))
        story.append(Paragraph(f"{first_date} ~ {last_date} ({len(entries)}일)", self.styles['Date']))
        story.append(Spacer(1, 0.3*cm))
        
        # Analyze good directions
        direction_counts = {}
        for entry in entries:
            content = entry.get('content', {})
            time_dir = content.get('timeDirection', {})
            good_dir = time_dir.get('good_direction', '')
            if good_dir:
                direction_counts[good_dir] = direction_counts.get(good_dir, 0) + 1
        
        if direction_counts:
            story.append(Paragraph("🧭 좋은 방향 Top 3", self.styles['Heading2']))
            sorted_dirs = sorted(direction_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for dir_name, count in sorted_dirs:
                story.append(Paragraph(f"• {dir_name}: {count}회", self.styles['Body']))
            story.append(Spacer(1, 0.2*cm))
        
        # Analyze bad hours
        hour_counts = {}
        for entry in entries:
            content = entry.get('content', {})
            time_dir = content.get('timeDirection', {})
            bad_time = time_dir.get('avoid_time', '')
            if bad_time:
                hour_counts[bad_time] = hour_counts.get(bad_time, 0) + 1
        
        if hour_counts:
            story.append(Paragraph("⏰ 주의 시간대 Top 3", self.styles['Heading2']))
            sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            for hour_name, count in sorted_hours:
                story.append(Paragraph(f"• {hour_name}: {count}일", self.styles['Body']))
            story.append(Spacer(1, 0.2*cm))
        
        # Collect keywords
        all_keywords = []
        for entry in entries:
            content = entry.get('content', {})
            keywords = content.get('keywords', [])
            all_keywords.extend(keywords)
        
        if all_keywords:
            unique_keywords = list(set(all_keywords))[:6]
            story.append(Paragraph("🔑 주요 키워드", self.styles['Heading2']))
            story.append(Paragraph(", ".join(unique_keywords), self.styles['Body']))
            story.append(Spacer(1, 0.2*cm))
        
        # Add checkpoints
        story.append(Paragraph("✅ 이번 주 체크포인트", self.styles['Heading2']))
        checkpoints = [
            "주중 중요한 결정 신중히 하기",
            "좋은 시간대 활용하여 효율 높이기",
            "감정 균형 유지하며 안정적인 한 주 보내기"
        ]
        for checkpoint in checkpoints:
            story.append(Paragraph(f"• {checkpoint}", self.styles['Bullet']))
        
        return story
    
    def _build_cover_page(self, period_data: Dict[str, Any]) -> List:
        """Build professional cover page content"""
        story = []
        
        # Border frame
        from reportlab.platypus import Table, TableStyle
        
        # Main title
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("라이프 리듬 다이어리", self.styles['CoverTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'CoverSubtitle2',
            parent=self.styles['CoverSubtitle'],
            fontSize=self.styles['CoverSubtitle'].fontSize * 0.8,
            textColor=colors.HexColor('#4a5568')
        )
        story.append(Paragraph("사주·기문둔갑 기반 개인화 일일 관리 다이어리", subtitle_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Concept line
        concept_style = ParagraphStyle(
            'ConceptLine',
            parent=self.styles['Small'],
            fontSize=self.styles['Small'].fontSize,
            textColor=colors.HexColor('#718096'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
        story.append(Paragraph('"나만의 리듬을 찾아 성장하는 시간"', concept_style))
        story.append(Spacer(1, 1.5*cm))
        
        # Period info box
        start_date = period_data.get('startDate', '')
        end_date = period_data.get('endDate', '')
        duration = period_data.get('durationType', '')
        total_days = period_data.get('totalDays', 0)
        
        duration_map = {
            '1m': '1개월',
            '3m': '3개월', 
            '6m': '6개월',
            '1y': '1년'
        }
        duration_text = duration_map.get(duration, duration)
        
        def format_date(date_str):
            if not date_str:
                return ''
            parts = date_str.split('-')
            if len(parts) == 3:
                return f"{parts[0]}년 {parts[1]}월 {parts[2]}일"
            return date_str
        
        # Period info table
        info_data = [
            [f"{duration_text} 다이어리"],
            [f"사용 기간: {format_date(start_date)} ~ {format_date(end_date)}"],
            [f"총 일수: {total_days}일"],
            [f"생성일: {format_date(datetime.now().strftime('%Y-%m-%d'))}"]
        ]
        
        period_table = Table(info_data, colWidths=[12*cm])
        period_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('FONTSIZE', (0, 0), (-1, 0), self.styles['Heading2'].fontSize),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')])
        ]))
        
        story.append(period_table)
        story.append(Spacer(1, 2*cm))
        
        # Owner section
        owner_style = ParagraphStyle(
            'OwnerLabel',
            parent=self.styles['Small'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096')
        )
        story.append(Paragraph("소유자 / Owner", owner_style))
        story.append(Spacer(1, 0.3*cm))
        
        # Owner line (using a simple line)
        from reportlab.platypus import Drawing
        from reportlab.graphics.shapes import Line
        
        drawing = Drawing(400, 20)
        drawing.add(Line(100, 10, 300, 10, strokeColor=colors.HexColor('#2c5aa0'), strokeWidth=1))
        story.append(drawing)
        story.append(Spacer(1, 2*cm))
        
        # Brand footer
        footer_style = ParagraphStyle(
            'BrandFooter',
            parent=self.styles['Small'],
            fontSize=self.styles['Small'].fontSize * 0.9,
            textColor=colors.HexColor('#a0aec0'),
            alignment=TA_CENTER
        )
        story.append(Paragraph("Powered by R³ System (Rhythm → Response → Recode)", footer_style))
        
        return story
    
    def _build_daily_content(self, data: Dict[str, Any]) -> List:
        """Build daily page content"""
        story = []
        content = data.get('content', {})
        
        # Date header
        date = data.get('date', '')
        story.append(Paragraph(f"📅 {date}", self.styles['Title']))
        story.append(Spacer(1, 0.5*cm))
        
        # Summary
        summary = content.get('summary', '')
        if summary:
            story.append(Paragraph("📝 요약", self.styles['Heading1']))
            story.append(Paragraph(self._clean_html(summary), self.styles['Body']))
            story.append(Spacer(1, 0.3*cm))
        
        # Keywords
        keywords = content.get('keywords', [])
        if keywords:
            story.append(Paragraph("🏷️ 키워드", self.styles['Heading1']))
            keyword_text = " • ".join(keywords)
            story.append(Paragraph(keyword_text, self.styles['Body']))
            story.append(Spacer(1, 0.3*cm))
        
        # Rhythm Description
        rhythm_desc = content.get('rhythmDescription', '')
        if rhythm_desc:
            story.append(Paragraph("🎵 리듬 해설", self.styles['Heading1']))
            story.append(Paragraph(self._clean_html(rhythm_desc), self.styles['Body']))
            story.append(Spacer(1, 0.3*cm))
        
        # Focus/Caution
        focus_caution = content.get('focusCaution', {})
        if focus_caution:
            story.append(Paragraph("⚡ 집중/주의 포인트", self.styles['Heading1']))
            
            focus_items = focus_caution.get('focus', [])
            if focus_items:
                story.append(Paragraph("집중:", self.styles['Heading2']))
                for item in focus_items:
                    story.append(Paragraph(f"• {self._clean_html(item)}", self.styles['Bullet']))
            
            caution_items = focus_caution.get('caution', [])
            if caution_items:
                story.append(Paragraph("주의:", self.styles['Heading2']))
                for item in caution_items:
                    story.append(Paragraph(f"• {self._clean_html(item)}", self.styles['Bullet']))
            
            story.append(Spacer(1, 0.3*cm))
        
        # Action Guide
        action_guide = content.get('actionGuide', {})
        if action_guide:
            story.append(Paragraph("📋 행동 가이드", self.styles['Heading1']))
            
            do_items = action_guide.get('do', [])
            if do_items:
                story.append(Paragraph("권장:", self.styles['Heading2']))
                for item in do_items:
                    story.append(Paragraph(f"• {self._clean_html(item)}", self.styles['Bullet']))
            
            avoid_items = action_guide.get('avoid', [])
            if avoid_items:
                story.append(Paragraph("지양:", self.styles['Heading2']))
                for item in avoid_items:
                    story.append(Paragraph(f"• {self._clean_html(item)}", self.styles['Bullet']))
            
            story.append(Spacer(1, 0.3*cm))
        
        # Time/Direction
        time_dir = content.get('timeDirection', {})
        if time_dir:
            story.append(Paragraph("🕐 시간/방향", self.styles['Heading1']))
            
            if time_dir.get('good_time'):
                story.append(Paragraph(f"좋은 시간: {self._clean_html(time_dir['good_time'])}", self.styles['Body']))
            if time_dir.get('avoid_time'):
                story.append(Paragraph(f"피할 시간: {self._clean_html(time_dir['avoid_time'])}", self.styles['Body']))
            if time_dir.get('good_direction'):
                story.append(Paragraph(f"좋은 방향: {self._clean_html(time_dir['good_direction'])}", self.styles['Body']))
            if time_dir.get('avoid_direction'):
                story.append(Paragraph(f"피할 방향: {self._clean_html(time_dir['avoid_direction'])}", self.styles['Body']))
            
            story.append(Spacer(1, 0.3*cm))
        
        # Rhythm Question
        rhythm_question = content.get('rhythmQuestion', '')
        if rhythm_question:
            story.append(Paragraph("❓ 오늘의 질문", self.styles['Heading1']))
            story.append(Paragraph(self._clean_html(rhythm_question), self.styles['Body']))
            story.append(Spacer(1, 0.3*cm))
        
        # User Recording Section
        story.append(Paragraph("📝 사용자 기록 및 자기관리", self.styles['Heading1']))
        
        # A. Today's Record
        story.append(Paragraph("<b>A. 오늘의 기록</b>", self.styles['Heading2']))
        
        # Most important thing (1 line)
        story.append(Paragraph("가장 중요한 1가지:", self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.2*cm))
        
        # Things done well (2 lines)
        story.append(Paragraph("잘한 점:", self.styles['Body']))
        for i in range(2):
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.2*cm))
        
        # Things to improve (2 lines)
        story.append(Paragraph("개선 필요:", self.styles['Body']))
        for i in range(2):
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph("_" * 60, self.styles['Body']))
        story.append(Spacer(1, 0.3*cm))
        
        # B. Emotion Check
        story.append(Paragraph("<b>B. 감정 체크</b>", self.styles['Heading2']))
        
        # Create checkbox table
        emotion_data = [
            ['☐ 안정', '☐ 집중', '☐ 피로'],
            ['☐ 불안', '☐ 만족', '☐ 긴장']
        ]
        emotion_table = Table(emotion_data, colWidths=[5*cm, 5*cm, 5*cm])
        emotion_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(emotion_table)
        story.append(Spacer(1, 0.3*cm))
        
        # C. Execution Check
        story.append(Paragraph("<b>C. 실행 체크</b>", self.styles['Heading2']))
        
        execution_data = [
            ['☐ 계획 실행', '☐ 미루지 않음', '☐ 중요한 일 완료']
        ]
        execution_table = Table(execution_data, colWidths=[5*cm, 5*cm, 5*cm])
        execution_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(execution_table)
        
        return story


def main():
    """Test the simple PDF converter"""
    converter = SimplePdfConverter()
    
    # Create sample data for testing
    sample_daily = {
        "date": "2026-03-28",
        "metadata": {
            "role": "student",
            "generatedAt": datetime.now().isoformat()
        },
        "content": {
            "summary": "오늘은 집중력이 높은 날입니다. 중요한 학습과 과제를 진행하기에 적합합니다.",
            "keywords": ["집중", "학습", "정리", "계획"],
            "rhythmDescription": "안정적인 흐름이 이어지며, 특히 오전 시간대의 에너지가 강합니다.",
            "focusCaution": {
                "focus": ["중요한 과제 완성", "복습 시간 확보", "계획 수립"],
                "caution": ["과도한 스트레스", "늦은 밤 공부", "산만한 환경"]
            },
            "actionGuide": {
                "do": ["오전 시간 활용", "계획적인 학습", "충분한 휴식"],
                "avoid": ["미루기", "산만한 환경", "과도한 목표"]
            },
            "timeDirection": {
                "good_time": "오전 9-11시",
                "avoid_time": "오후 3-5시",
                "good_direction": "북쪽",
                "avoid_direction": "남서쪽"
            },
            "rhythmQuestion": "오늘 가장 집중하고 싶은 한 가지는 무엇인가요?"
        }
    }
    
    # Test 1: Single daily PDF
    print("Test 1: Generating single daily PDF...")
    daily_json_path = converter.output_dir / "test_daily.json"
    with open(daily_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_daily, f, ensure_ascii=False, indent=2)
    
    result = converter.convert_daily_json_to_pdf(str(daily_json_path))
    if result["success"]:
        print(f"[SUCCESS] Daily PDF generated: {result['outputPath']}")
        print(f"   File size: {result['fileSize']} bytes")
    else:
        print(f"[ERROR] Failed: {result['error']}")
    
    # Test 2: Period bundle PDF
    print("\nTest 2: Generating period bundle PDF...")
    sample_period = {
        "startDate": "2026-03-01",
        "endDate": "2026-03-07",
        "durationType": "1m",
        "totalDays": 7,
        "entries": [
            {**sample_daily, "date": f"2026-03-{i:02d}"}
            for i in range(1, 8)
        ]
    }
    
    period_json_path = converter.output_dir / "test_period.json"
    with open(period_json_path, 'w', encoding='utf-8') as f:
        json.dump(sample_period, f, ensure_ascii=False, indent=2)
    
    result = converter.convert_period_json_to_pdf(str(period_json_path))
    if result["success"]:
        print(f"[SUCCESS] Period PDF generated: {result['outputPath']}")
        print(f"   File size: {result['fileSize']} bytes")
        print(f"   Page count: {result['pageCount']}")
    else:
        print(f"[ERROR] Failed: {result['error']}")
    
    print("\n[DONE] All tests completed! Check the test_output directory for PDF files.")


if __name__ == "__main__":
    import sys
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--convert-period" and len(sys.argv) >= 3:
            # Convert period JSON to PDF
            json_path = sys.argv[2]
            output_path = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--output" else None
            mode = 'standard'
            
            # Check for mode argument
            for i, arg in enumerate(sys.argv):
                if arg == '--mode' and i + 1 < len(sys.argv):
                    mode = sys.argv[i + 1]
            
            converter = SimplePdfConverter(mode=mode)
            result = converter.convert_period_json_to_pdf(json_path, output_path)
            
            if result["success"]:
                print(f"[SUCCESS] PDF generated: {result['outputPath']}")
                sys.exit(0)
            else:
                print(f"[ERROR] {result['error']}")
                sys.exit(1)
        
        elif sys.argv[1] == "--convert-daily" and len(sys.argv) >= 3:
            # Convert daily JSON to PDF
            json_path = sys.argv[2]
            output_path = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--output" else None
            
            converter = SimplePdfConverter()
            result = converter.convert_daily_json_to_pdf(json_path, output_path)
            
            if result["success"]:
                print(f"[SUCCESS] PDF generated: {result['outputPath']}")
                sys.exit(0)
            else:
                print(f"[ERROR] {result['error']}")
                sys.exit(1)
        else:
            print("Usage:")
            print("  python simplePdfConverter.py --convert-period <json_path> [--output <pdf_path>]")
            print("  python simplePdfConverter.py --convert-daily <json_path> [--output <pdf_path>]")
            sys.exit(1)
    else:
        # Run test if no arguments
        main()