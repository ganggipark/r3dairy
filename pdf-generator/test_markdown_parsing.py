"""
Test script for Markdown parsing logic (without PDF generation)
"""
from pathlib import Path
import sys
import json
import io

# Set stdout to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add generator module to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock the dependencies
class MockHTML:
    def __init__(self, *args, **kwargs):
        pass
    def write_pdf(self, *args, **kwargs):
        pass

class MockCSS:
    def __init__(self, *args, **kwargs):
        pass

# Mock weasyprint
sys.modules['weasyprint'] = type('module', (), {
    'HTML': MockHTML,
    'CSS': MockCSS
})()

# Now we can import generator
from generator import PDFGenerator


def test_markdown_parsing():
    """Test Markdown parsing to dictionary"""
    generator = PDFGenerator()

    # Load markdown file
    md_file = Path(__file__).parent.parent / "backend" / "daily" / "2026-01-31_new_format.md"

    if not md_file.exists():
        print(f"❌ Markdown file not found: {md_file}")
        return

    print(f"📄 Loading markdown file: {md_file}")

    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print(f"📏 Content length: {len(md_content)} characters\n")

    try:
        # Parse markdown to dict
        print(f"🔨 Parsing markdown to dictionary...")
        parsed_content = generator._parse_markdown_to_dict(md_content)

        print(f"✅ Parsing successful!\n")
        print("=" * 60)
        print("PARSED CONTENT:")
        print("=" * 60)

        # Display key sections
        print(f"\n📅 Date: {parsed_content.get('date', 'NOT FOUND')}")
        print(f"\n📝 Summary:\n{parsed_content.get('summary', 'NOT FOUND')[:150]}...")

        print(f"\n🏷️ Keywords ({len(parsed_content.get('keywords', []))}):")
        print(f"  {', '.join(parsed_content.get('keywords', []))}")

        print(f"\n🎵 Rhythm Description:")
        print(f"  {parsed_content.get('rhythm_description', 'NOT FOUND')[:150]}...")

        print(f"\n🎯 Focus Points ({len(parsed_content.get('focus_caution', {}).get('focus', []))}):")
        for item in parsed_content.get('focus_caution', {}).get('focus', [])[:3]:
            print(f"  - {item}")

        print(f"\n⚠️ Caution Points ({len(parsed_content.get('focus_caution', {}).get('caution', []))}):")
        for item in parsed_content.get('focus_caution', {}).get('caution', [])[:3]:
            print(f"  - {item}")

        print(f"\n✅ Do Actions ({len(parsed_content.get('action_guide', {}).get('do', []))}):")
        for item in parsed_content.get('action_guide', {}).get('do', [])[:3]:
            print(f"  - {item}")

        print(f"\n🚫 Avoid Actions ({len(parsed_content.get('action_guide', {}).get('avoid', []))}):")
        for item in parsed_content.get('action_guide', {}).get('avoid', [])[:3]:
            print(f"  - {item}")

        print(f"\n⏰ Time/Direction:")
        td = parsed_content.get('time_direction', {})
        print(f"  Good Time: {td.get('good_time', 'NOT FOUND')}")
        print(f"  Avoid Time: {td.get('avoid_time', 'NOT FOUND')}")
        print(f"  Good Direction: {td.get('good_direction', 'NOT FOUND')}")
        print(f"  Avoid Direction: {td.get('avoid_direction', 'NOT FOUND')}")

        print(f"\n🔄 State Trigger:")
        st = parsed_content.get('state_trigger', {})
        print(f"  Gesture: {st.get('gesture', 'NOT FOUND')}")
        print(f"  Phrase: {st.get('phrase', 'NOT FOUND')}")
        print(f"  How To: {st.get('how_to', 'NOT FOUND')}")

        print(f"\n💭 Meaning Shift:")
        print(f"  {parsed_content.get('meaning_shift', 'NOT FOUND')[:150]}...")

        print(f"\n❓ Rhythm Question:")
        print(f"  {parsed_content.get('rhythm_question', 'NOT FOUND')}")

        # Save parsed JSON for inspection
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        json_output = output_dir / "parsed_content.json"

        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(parsed_content, f, ensure_ascii=False, indent=2)

        print(f"\n📁 Full parsed content saved to: {json_output}")

    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_markdown_parsing()
