import { jsPDF } from 'jspdf'
import 'jspdf-autotable'

export function useExportReports() {
  /**
   * Generates and downloads a clean CSV file of all detection/audit events.
   */
  const exportToCSV = (records = []) => {
    if (!records || records.length === 0) {
      alert('No detection records available to export.')
      return
    }

    const headers = [
      'Incident ID',
      'Timestamp',
      'Plate Number',
      'Vehicle Type',
      'Observed Color',
      'OCR Confidence',
      'Risk Score',
      'Risk Level',
      'Audit Reason'
    ]

    const rows = records.map(r => [
      r.alert_id || r.detection_id || r.id || 'N/A',
      `"${r.timestamp || new Date().toISOString()}"`,
      `"${(r.plate_number || 'UNKNOWN').toUpperCase()}"`,
      `"${(r.observed_type || r.vehicle_type || 'N/A').toUpperCase()}"`,
      `"${(r.observed_color || r.color || 'N/A').toUpperCase()}"`,
      `"${Math.round((r.ocr_confidence || 0.95) * 100)}%"`,
      `"${typeof r.risk_score === 'number' ? r.risk_score.toFixed(1) : '0.0'}"`,
      `"${(r.risk_level || (r.risk_score > 60 ? 'RED' : (r.risk_score > 30 ? 'YELLOW' : 'GREEN'))).toUpperCase()}"`,
      `"${(r.reason || 'Routine Verification Pass').replace(/"/g, '""')}"`
    ])

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
    link.setAttribute('href', url)
    link.setAttribute('download', `AVNIT_Incident_Audit_Log_${timestamp}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * Generates and downloads an Executive Law Enforcement PDF Audit Dossier.
   * STRICTLY ZERO BLUE: Employs slate-900, dark charcoal, emerald, amber, and crimson.
   */
  const exportToPDF = (records = [], stats = {}) => {
    if (!records || records.length === 0) {
      alert('No detection records available to export to PDF.')
      return
    }

    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const pageWidth = doc.internal.pageSize.getWidth()
    const nowStr = new Date().toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })

    // 1. Official Header Top Bar (Dark Charcoal / Slate-900 - ZERO BLUE)
    doc.setFillColor(24, 24, 27) // #18181b onyx
    doc.rect(0, 0, pageWidth, 26, 'F')

    // System Title & Subtitle
    doc.setTextColor(255, 255, 255)
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(16)
    doc.text('A.V.N.I.T. | LAW ENFORCEMENT AUDIT DOSSIER', 14, 12)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8.5)
    doc.setTextColor(212, 212, 216) // zinc-300
    doc.text('Automated Verification of Number Plate & Identity Tampering Detection System', 14, 19)

    doc.setFontSize(8)
    doc.setTextColor(161, 161, 170) // zinc-400
    doc.text(`Generated: ${nowStr}`, pageWidth - 14, 19, { align: 'right' })

    // 2. Executive Summary KPI Grid (Neutral warm boxes)
    const validCount = records.filter(r => (r.risk_score || 0) < 30 || r.risk_level === 'GREEN').length
    const tamperCount = records.filter(r => (r.risk_score || 0) >= 60 || r.risk_level === 'RED').length
    const warningCount = records.length - validCount - tamperCount

    const boxY = 32
    const boxWidth = (pageWidth - 28 - 9) / 4
    const boxHeight = 16

    const kpiCards = [
      { label: 'TOTAL SCANNED', value: records.length.toString(), bg: [244, 244, 245], text: [24, 24, 27] },
      { label: 'VALID PASSES', value: validCount.toString(), bg: [236, 253, 245], text: [5, 150, 105] }, // emerald
      { label: 'MODERATE VARIANCE', value: warningCount.toString(), bg: [254, 243, 199], text: [217, 119, 6] }, // amber
      { label: 'TAMPER ALERTS', value: tamperCount.toString(), bg: [255, 228, 230], text: [225, 29, 72] } // rose/crimson
    ]

    kpiCards.forEach((card, idx) => {
      const cardX = 14 + idx * (boxWidth + 3)
      doc.setFillColor(card.bg[0], card.bg[1], card.bg[2])
      doc.roundedRect(cardX, boxY, boxWidth, boxHeight, 2, 2, 'F')
      doc.setDrawColor(228, 228, 231)
      doc.roundedRect(cardX, boxY, boxWidth, boxHeight, 2, 2, 'S')

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(7)
      doc.setTextColor(113, 113, 122)
      doc.text(card.label, cardX + 4, boxY + 5.5)

      doc.setFontSize(13)
      doc.setTextColor(card.text[0], card.text[1], card.text[2])
      doc.text(card.value, cardX + 4, boxY + 12.5)
    })

    // 3. Tabular Audit Feed
    const tableBody = records.map(r => {
      const score = typeof r.risk_score === 'number' ? r.risk_score : 0
      let verdict = 'VERIFIED'
      if (score >= 60 || r.risk_level === 'RED') verdict = 'TAMPER ALERT'
      else if (score >= 30 || r.risk_level === 'YELLOW') verdict = 'VARIANCE'

      return [
        (r.plate_number || 'UNKNOWN').toUpperCase(),
        (r.observed_type || r.vehicle_type || 'CAR').toUpperCase(),
        (r.observed_color || r.color || 'N/A').toUpperCase(),
        `${Math.round((r.ocr_confidence || 0.95) * 100)}%`,
        `${score.toFixed(1)}%`,
        verdict,
        (r.reason || 'Identity Verified against Registry').slice(0, 55),
        (r.timestamp || nowStr).slice(11, 19)
      ]
    })

    doc.autoTable({
      startY: 53,
      head: [['PLATE', 'TYPE', 'COLOR', 'OCR CONF', 'RISK', 'VERDICT', 'INVESTIGATION FINDING', 'TIME']],
      body: tableBody,
      theme: 'grid',
      styles: {
        fontSize: 7.5,
        cellPadding: 2.2,
        textColor: [39, 39, 42],
        lineColor: [228, 228, 231],
        lineWidth: 0.1
      },
      headStyles: {
        fillColor: [39, 39, 42], // Charcoal
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        fontSize: 7.5
      },
      alternateRowStyles: {
        fillColor: [250, 250, 250]
      },
      columnStyles: {
        0: { fontStyle: 'bold', font: 'courier', cellWidth: 26 },
        1: { cellWidth: 16 },
        2: { cellWidth: 16 },
        3: { cellWidth: 16 },
        4: { cellWidth: 14, fontStyle: 'bold' },
        5: { cellWidth: 24, fontStyle: 'bold' },
        6: { cellWidth: 54 },
        7: { cellWidth: 16 }
      },
      didParseCell: (data) => {
        if (data.section === 'body' && data.column.index === 5) {
          if (data.cell.raw === 'TAMPER ALERT') {
            data.cell.styles.textColor = [225, 29, 72] // Crimson
          } else if (data.cell.raw === 'VARIANCE') {
            data.cell.styles.textColor = [217, 119, 6] // Amber
          } else {
            data.cell.styles.textColor = [5, 150, 105] // Emerald
          }
        }
      }
    })

    // 4. Footer Watermark & Sign-off
    const pageCount = doc.internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFont('helvetica', 'normal')
      doc.setFontSize(7.5)
      doc.setTextColor(161, 161, 170)
      doc.text(
        'CONFIDENTIAL & PROPRIETARY — LAW ENFORCEMENT & HIGHWAY TRAFFIC CONTROL EVIDENCE RECORD',
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 8,
        { align: 'center' }
      )
      doc.text(`Page ${i} of ${pageCount}`, pageWidth - 14, doc.internal.pageSize.getHeight() - 8, { align: 'right' })
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
    doc.save(`AVNIT_Audit_Dossier_${timestamp}.pdf`)
  }

  return {
    exportToCSV,
    exportToPDF
  }
}
