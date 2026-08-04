# Architecture

> **Placeholder (Fase 0).** Diisi pada Fase 10, dirangkum dari blueprint bagian 16 (C4 diagrams)
> dan 46 (ADR). Sumber kebenaran: [INSIGHTULASAN_BLUEPRINT.md](reference/INSIGHTULASAN_BLUEPRINT.md).

## 1. System Context (C4 Level 1)
_Diisi dari blueprint bagian 15._

## 2. Container Diagram (C4 Level 2)
_Diisi dari blueprint bagian 16.1._

## 3. Component Diagram — Backend API (C4 Level 3)
_Diisi dari blueprint bagian 16.2._

## 4. Deployment Diagram
_Diisi dari blueprint bagian 16.3._

## 5. Data Flow & Lineage
_Diisi dari blueprint bagian 16.4–16.5._

## 6. AI Tool Orchestration
_Diisi dari blueprint bagian 16.6 dan 27.3 (10 tool contracts)._

## 7. Architecture Decision Records (ringkasan)
_Empat belas ADR pada blueprint bagian 46 dirangkum di sini, dengan status implementasi aktual._

| ADR | Keputusan | Status implementasi |
| --- | --- | --- |
| ADR-001 | Local-first, bukan commercial API | belum diimplementasikan |
| ADR-002 | IndoBERT-base sebagai model teks primary | belum diimplementasikan |
| ADR-003 | CLIP ViT-B/32 sebagai vision model primary | belum diimplementasikan |
| ADR-004 | Frozen zero-shot visual, bukan trained classifier | belum diimplementasikan |
| ADR-005 | BGE-M3 sebagai embedding primary | belum diimplementasikan |
| ADR-006 | SEA-LION quantized sebagai orchestrator | belum diimplementasikan |
| ADR-007 | Chroma embedded sebagai vector store | belum diimplementasikan |
| ADR-008 | FastAPI, satu service, service layer modular | belum diimplementasikan |
| ADR-009 | React + Vite untuk competition MVP | belum diimplementasikan |
| ADR-010 | Temporary storage session-only, tanpa DB persisten | belum diimplementasikan |
| ADR-011 | Skor deterministic, LLM hanya menyusun narasi | belum diimplementasikan |
| ADR-012 | Benchmark precomputed aggregate | belum diimplementasikan |
| ADR-013 | Tidak ada eksekusi tindakan bisnis otomatis | belum diimplementasikan |
| ADR-014 | FALLBACK MODE deterministic template wajib | belum diimplementasikan |
