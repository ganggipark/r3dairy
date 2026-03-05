'use client'

export type PaperSize = 'A4' | 'B4' | 'A5' | 'B5' | 'Letter'

export const PAPER_SIZES: Record<PaperSize, { width: string; height: string; label: string; widthMm: number; heightMm: number }> = {
  A4:     { width: '210mm',  height: '297mm', label: 'A4 (210×297)',    widthMm: 210, heightMm: 297 },
  B4:     { width: '257mm',  height: '364mm', label: 'B4 (257×364)',    widthMm: 257, heightMm: 364 },
  A5:     { width: '148mm',  height: '210mm', label: 'A5 (148×210)',    widthMm: 148, heightMm: 210 },
  B5:     { width: '182mm',  height: '257mm', label: 'B5 (182×257)',    widthMm: 182, heightMm: 257 },
  Letter: { width: '216mm',  height: '279mm', label: 'Letter (216×279)', widthMm: 216, heightMm: 279 },
}

interface PaperSizeSelectorProps {
  paperSize: PaperSize
  onChange: (size: PaperSize) => void
}

export default function PaperSizeSelector({ paperSize, onChange }: PaperSizeSelectorProps) {
  return (
    <select
      value={paperSize}
      onChange={(e) => onChange(e.target.value as PaperSize)}
      className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
    >
      {Object.entries(PAPER_SIZES).map(([key, val]) => (
        <option key={key} value={key}>{val.label}</option>
      ))}
    </select>
  )
}
