"""
Test script for Markdown PDF generation
"""
from pathlib import Path
from generator import PDFGenerator

def test_markdown_pdf():
    """Test PDF generation from Markdown file"""
    generator = PDFGenerator()

    # Load markdown file
    md_file = Path(__file__).parent.parent / "backend" / "daily" / "2026-01-31_new_format.md"

    if not md_file.exists():
        print(f"❌ Markdown file not found: {md_file}")
        return

    print(f"📄 Loading markdown file: {md_file}")

    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Output path
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "test_daily_2026-01-31.pdf"

    print(f"🔨 Generating PDF...")

    try:
        # Generate PDF
        result = generator.generate_daily_pdf(
            content=md_content,
            output_path=str(output_path),
            role=None,
            is_markdown=True
        )

        print(f"✅ PDF generated successfully: {result}")
        print(f"📁 File size: {Path(result).stat().st_size / 1024:.2f} KB")

    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_markdown_pdf()
