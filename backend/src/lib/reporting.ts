import ExcelJS from 'exceljs';
import PDFDocument from 'pdfkit';
import { Readable } from 'node:stream';

export async function createCsvReport(rows: Record<string, unknown>[]) {
  if (!rows.length) return 'category,metric,value\n';
  const headers = Object.keys(rows[0]);
  const lines = [headers.join(',')];
  rows.forEach((row) => {
    const values = headers.map((header) => {
      const value = row[header];
      const text = value == null ? '' : String(value).replace(/,/g, ';');
      return `"${text}"`;
    });
    lines.push(values.join(','));
  });
  return lines.join('\n') + '\n';
}

export async function createExcelReport(rows: Record<string, unknown>[]) {
  const workbook = new ExcelJS.Workbook();
  const sheet = workbook.addWorksheet('Report');
  if (rows.length) {
    sheet.addRow(Object.keys(rows[0]));
    rows.forEach((row) => sheet.addRow(Object.values(row)));
  }
  const buffer = await workbook.xlsx.writeBuffer();
  return Buffer.from(buffer);
}

export async function createPdfReport(title: string, rows: Record<string, unknown>[]) {
  return new Promise<Buffer>((resolve, reject) => {
    const doc = new PDFDocument({ margin: 40 });
    const chunks: Buffer[] = [];

    doc.on('data', (chunk) => chunks.push(Buffer.from(chunk)));
    doc.on('end', () => resolve(Buffer.concat(chunks)));
    doc.on('error', reject);

    doc.fontSize(20).text(title, { align: 'center' });
    doc.moveDown();

    if (rows.length) {
      const headers = Object.keys(rows[0]);
      const rowWidth = 500 / headers.length;
      let currentY = doc.y;
      headers.forEach((key, index) => {
        doc.rect(40 + index * rowWidth, currentY, rowWidth, 20).stroke();
        doc.text(key, 45 + index * rowWidth, currentY + 5, { width: rowWidth - 10 });
      });

      rows.forEach((row) => {
        currentY += 25;
        headers.forEach((key, index) => {
          const cellText = String(row[key] ?? '');
          doc.rect(40 + index * rowWidth, currentY, rowWidth, 20).stroke();
          doc.text(cellText, 45 + index * rowWidth, currentY + 5, { width: rowWidth - 10 });
        });
      });
    }

    doc.end();
  });
}

export function getReportMimeType(format: string) {
  switch (format) {
    case 'csv':
      return 'text/csv';
    case 'xlsx':
      return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
    case 'pdf':
      return 'application/pdf';
    default:
      return 'application/octet-stream';
  }
}
