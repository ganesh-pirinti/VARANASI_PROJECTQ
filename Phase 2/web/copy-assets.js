/**
 * Build-preparation script for VARANASI Quantum Optimization Studio.
 * Copies authoritative presentation, report, and table files from Phase 2
 * into web/public/assets/ so they are included in the Vite production build.
 * Pure Node.js (runs on Vercel Node 22.x without external dependencies).
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const projectRoot = path.resolve(__dirname, '..');
const targetDir = path.resolve(__dirname, 'public', 'assets');

const filesToCopy = [
  {
    src: path.join(projectRoot, 'presentation', 'VARANASI_Pitch_Deck.pdf'),
    destName: 'VARANASI_Pitch_Deck.pdf'
  },
  {
    src: path.join(projectRoot, 'presentation', 'VARANASI_Pitch_Deck.pptx'),
    destName: 'VARANASI_Pitch_Deck.pptx'
  },
  {
    src: path.join(projectRoot, 'docs', 'VARANASI_RESEARCH_AND_IMPLEMENTATION_REPORT.md'),
    destName: 'VARANASI_RESEARCH_AND_IMPLEMENTATION_REPORT.md'
  },
  {
    src: path.join(projectRoot, 'results', 'tables', 'results.csv'),
    destName: 'results.csv'
  },
  {
    src: path.join(projectRoot, 'results', 'tables', 'bell.csv'),
    destName: 'bell.csv'
  },
  {
    src: path.join(projectRoot, 'dist', 'VARANASI_PS-O1_Phase2_Submission.zip'),
    destName: 'VARANASI_PS-O1_Phase2_Submission.zip'
  }
];

// Ensure target directory exists
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

let copiedCount = 0;
filesToCopy.forEach(({ src, destName }) => {
  const destPath = path.join(targetDir, destName);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, destPath);
    const stat = fs.statSync(destPath);
    console.log(`[copy-assets] Copied: ${destName} (${stat.size.toLocaleString()} bytes)`);
    copiedCount++;
  } else {
    console.warn(`[copy-assets] WARNING: Source file not found: ${src}`);
  }
});

console.log(`[copy-assets] Completed: ${copiedCount}/${filesToCopy.length} assets ready in public/assets/`);
