'use client';

import React, { useState, useRef } from 'react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/layout/page-header';
import { PageContainer } from '@/components/layout/page-container';
import { GlassCard } from '@/components/ui/glass-card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Modal } from '@/components/ui/modal';
import { EmptyState } from '@/components/ui/empty-state';
import { LoadingState } from '@/components/ui/loading-state';
import { ToastContainer, type ToastItem } from '@/components/ui/toast';
import {
  useMaterials,
  useMaterialChunks,
  useUploadMaterial,
  useDeleteMaterial,
} from '@/hooks/use-materials';
import { useRAGSearch } from '@/hooks/use-rag';
import type {
  UploadedMaterial,
  DocumentChunk,
  RAGSearchResultItem,
  RAGSearchResponse,
} from '@pragya/types';
import {
  Upload,
  FileText,
  FileCode,
  Trash2,
  Eye,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Cpu,
  RefreshCw,
  AlertTriangle,
  FileCheck,
  Hash,
  BookOpen,
} from 'lucide-react';

const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB
const ALLOWED_EXTENSIONS = ['.pdf', '.ppt', '.pptx', '.txt'];

export default function EmployeeMaterialsPage() {
  const [activeTab, setActiveTab] = useState<'materials' | 'rag'>('materials');
  const [selectedMaterialForChunks, setSelectedMaterialForChunks] = useState<UploadedMaterial | null>(null);
  const [isChunkModalOpen, setIsChunkModalOpen] = useState(false);
  const [deleteConfirmMaterial, setDeleteConfirmMaterial] = useState<UploadedMaterial | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // RAG Search State
  const [searchQuery, setSearchQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [selectedDocFilter, setSelectedDocFilter] = useState<string>('all');
  const [ragResponse, setRagResponse] = useState<RAGSearchResponse | null>(null);

  // Queries & Mutations
  const { data: materialsData, isLoading: isLoadingMaterials, refetch: refetchMaterials } = useMaterials();
  const uploadMutation = useUploadMaterial();
  const deleteMutation = useDeleteMaterial();
  const ragSearchMutation = useRAGSearch();

  // Chunks Query for the currently selected material
  const { data: chunksData, isLoading: isLoadingChunks } = useMaterialChunks(
    selectedMaterialForChunks?.id
  );

  const materials = materialsData?.items || [];
  const totalCount = materialsData?.total || 0;
  const processedCount = materials.filter((m) => m.status === 'PROCESSED').length;
  const processingCount = materials.filter(
    (m) => m.status === 'PROCESSING' || m.status === 'UPLOADED'
  ).length;

  const addToast = (type: ToastItem['type'], title: string, message?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Handle file selection and validation
  const handleFile = async (file: File) => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      addToast(
        'danger',
        'Unsupported File Format',
        `File "${file.name}" is not supported. Allowed formats: PDF, PPT, PPTX, TXT.`
      );
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      addToast(
        'danger',
        'File Size Exceeded',
        `File size (${(file.size / (1024 * 1024)).toFixed(1)} MB) exceeds the 25 MB limit.`
      );
      return;
    }

    try {
      await uploadMutation.mutateAsync(file);
      addToast(
        'success',
        'Upload Successful',
        `"${file.name}" uploaded. Processing pipeline initiated.`
      );
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to upload document.';
      addToast('danger', 'Upload Failed', errorMsg);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirmMaterial) return;
    try {
      await deleteMutation.mutateAsync(deleteConfirmMaterial.id);
      addToast(
        'success',
        'Material Deleted',
        `"${deleteConfirmMaterial.original_filename}" removed.`
      );
      setIsDeleteModalOpen(false);
      setDeleteConfirmMaterial(null);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete material.';
      addToast('danger', 'Delete Failed', errorMsg);
    }
  };

  const handleOpenChunks = (material: UploadedMaterial) => {
    setSelectedMaterialForChunks(material);
    setIsChunkModalOpen(true);
  };

  const handleExecuteSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      const res = await ragSearchMutation.mutateAsync({
        query: searchQuery.trim(),
        top_k: topK,
        document_id: selectedDocFilter !== 'all' ? selectedDocFilter : null,
      });
      setRagResponse(res);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Search failed.';
      addToast('danger', 'Retrieval Failed', errorMsg);
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getDocTypeIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return <FileText className="w-5 h-5 text-red-400" />;
    if (ext === 'ppt' || ext === 'pptx') return <FileCode className="w-5 h-5 text-amber-400" />;
    return <FileText className="w-5 h-5 text-cyan-400" />;
  };

  const getStatusBadge = (status: UploadedMaterial['status']) => {
    switch (status) {
      case 'PROCESSED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border bg-emerald-500/10 text-emerald-300 border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_#10B981]" />
            Indexed & Ready
          </span>
        );
      case 'PROCESSING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border bg-cyan-500/10 text-cyan-300 border-cyan-500/30 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin text-cyan-400" />
            Processing Pipeline...
          </span>
        );
      case 'UPLOADED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border bg-amber-500/10 text-amber-300 border-amber-500/30">
            <Clock className="w-3 h-3 text-amber-400" />
            Queued
          </span>
        );
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border bg-red-500/10 text-red-300 border-red-500/30">
            <AlertCircle className="w-3 h-3 text-red-400" />
            Extraction Failed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border bg-slate-500/10 text-slate-300 border-slate-500/30">
            {status}
          </span>
        );
    }
  };

  return (
    <AppShell role="EMPLOYEE" pageTitle="Document Intelligence & Materials">
      <PageContainer>
        <PageHeader
          title="Document Intelligence & Vector Retrieval"
          subtitle="Multi-format document ingestion, semantic chunking, and grounded vector retrieval for verified officer learning."
          breadcrumbs={[
            { label: 'Learner Workspace', href: '/employee' },
            { label: 'Document Intelligence' },
          ]}
        />

        {/* Global Key Metrics Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <GlassCard className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Total Ingested
              </p>
              <h3 className="text-2xl font-bold text-white mt-1">{totalCount}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Uploaded materials</p>
            </div>
            <div className="w-11 h-11 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Layers className="w-5 h-5" />
            </div>
          </GlassCard>

          <GlassCard className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Indexed Documents
              </p>
              <h3 className="text-2xl font-bold text-emerald-400 mt-1">{processedCount}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Ready for retrieval</p>
            </div>
            <div className="w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </GlassCard>

          <GlassCard className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                In Pipeline
              </p>
              <h3 className="text-2xl font-bold text-amber-400 mt-1">{processingCount}</h3>
              <p className="text-[11px] text-slate-500 mt-0.5">Extracting & embedding</p>
            </div>
            <div className="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Cpu className="w-5 h-5" />
            </div>
          </GlassCard>

          <GlassCard className="p-4 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                Engine Status
              </p>
              <h3 className="text-sm font-semibold text-white mt-1.5 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_#06B6D4]" />
                Hybrid Lexical + Vector
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">Dimension: 384 (MiniLM-L6)</p>
            </div>
            <div className="w-11 h-11 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-400">
              <FileCheck className="w-5 h-5" />
            </div>
          </GlassCard>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-3 border-b border-white/10 pb-3 mb-6">
          <button
            type="button"
            onClick={() => setActiveTab('materials')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'materials'
                ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
            }`}
          >
            <Upload className="w-4 h-4" />
            <span>Document Ingestion & Repository</span>
            <Badge variant={activeTab === 'materials' ? 'primary' : 'outline'} className="text-[10px] ml-1">
              {totalCount}
            </Badge>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('rag')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'rag'
                ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 shadow-[0_0_15px_rgba(6,182,212,0.15)]'
                : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
            }`}
          >
            <Search className="w-4 h-4" />
            <span>Evidence Retrieval Preview (RAG)</span>
            <span className="px-1.5 py-0.5 rounded text-[10px] bg-violet-500/20 text-violet-300 font-mono border border-violet-500/30">
              Retrieval Only
            </span>
          </button>
        </div>

        {/* TAB 1: Document Ingestion & Materials */}
        {activeTab === 'materials' && (
          <div className="space-y-6">
            {/* Upload Zone */}
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                dragActive
                  ? 'border-cyan-400 bg-cyan-500/10 shadow-[0_0_30px_rgba(6,182,212,0.2)]'
                  : 'border-white/10 hover:border-cyan-500/30 bg-slate-900/30'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.ppt,.pptx,.txt"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFile(e.target.files[0]);
                  }
                }}
                className="hidden"
                id="material-upload-input"
              />

              <div className="flex flex-col items-center justify-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                  <Upload className="w-7 h-7" />
                </div>

                <div>
                  <h3 className="text-base font-semibold text-white">
                    Drop your learning documents here, or{' '}
                    <label
                      htmlFor="material-upload-input"
                      className="text-cyan-400 hover:text-cyan-300 underline cursor-pointer font-medium"
                    >
                      browse files
                    </label>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                    Supported formats: PDF manuals (PyMuPDF), PPT/PPTX slide decks (python-pptx), and safe plain text files. Maximum file size: 25 MB.
                  </p>
                </div>

                {/* Badges for Supported Formats */}
                <div className="flex flex-wrap items-center justify-center gap-2 mt-2">
                  <span className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-red-500/10 border border-red-500/20 text-red-300">
                    PDF (PyMuPDF)
                  </span>
                  <span className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-amber-500/10 border border-amber-500/20 text-amber-300">
                    PPT / PPTX (python-pptx)
                  </span>
                  <span className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-cyan-500/10 border border-cyan-500/20 text-cyan-300">
                    TXT (Safe UTF-8)
                  </span>
                  <span className="px-2 py-0.5 rounded-md text-[11px] font-mono bg-violet-500/10 border border-violet-500/20 text-violet-300">
                    Max 25 MB
                  </span>
                </div>

                {uploadMutation.isPending && (
                  <div className="flex items-center gap-2 mt-3 text-cyan-400 text-xs font-medium animate-pulse">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Uploading and verifying document integrity...</span>
                  </div>
                )}
              </div>
            </div>

            {/* Pipeline Stage Architecture Tracker */}
            <GlassCard className="p-4 border border-white/5">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
                Automated Document Intelligence Pipeline
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">STAGE 1</span>
                  <p className="text-xs font-medium text-white mt-1">Validation & Storage</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">SHA-256 deduplication & MIME inspection</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">STAGE 2</span>
                  <p className="text-xs font-medium text-white mt-1">Multi-Format Extraction</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">PyMuPDF pages & PPTX shapes/slides</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">STAGE 3</span>
                  <p className="text-xs font-medium text-white mt-1">Semantic Chunking</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">400–700 tokens with 80-token overlap</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">STAGE 4</span>
                  <p className="text-xs font-medium text-white mt-1">Embeddings & Vectors</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">384-dimensional vector indexing</p>
                </div>
                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/5">
                  <span className="text-[10px] font-mono text-cyan-400 font-semibold">STAGE 5</span>
                  <p className="text-xs font-medium text-white mt-1">Grounded Retrieval</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">Cosine evidence lookup & citations</p>
                </div>
              </div>
            </GlassCard>

            {/* Ingested Materials List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
                  <span>Ingested Learning Documents</span>
                  <span className="text-xs text-slate-400 font-normal">
                    ({materials.length} of {totalCount})
                  </span>
                </h3>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => refetchMaterials()}
                  className="text-xs"
                >
                  <RefreshCw className="w-3.5 h-3.5 mr-1" />
                  Refresh
                </Button>
              </div>

              {isLoadingMaterials ? (
                <LoadingState message="Loading ingested materials..." />
              ) : materials.length === 0 ? (
                <EmptyState
                  icon={<BookOpen className="w-8 h-8 text-slate-500" />}
                  title="No Documents Uploaded Yet"
                  description="Upload your operational manuals, survey methodologies, or training presentations to enable grounded evidence retrieval."
                />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {materials.map((mat) => {
                    const doc = mat.documents?.[0];
                    return (
                      <GlassCard
                        key={mat.id}
                        className="p-5 flex flex-col justify-between hover:border-cyan-500/30 transition-all"
                      >
                        <div>
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <div className="flex items-center gap-2.5">
                              {getDocTypeIcon(mat.original_filename)}
                              <h4
                                className="text-sm font-medium text-white truncate max-w-[220px]"
                                title={mat.original_filename}
                              >
                                {mat.original_filename}
                              </h4>
                            </div>
                            {getStatusBadge(mat.status)}
                          </div>

                          {/* File Details */}
                          <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 mt-3 pt-3 border-t border-white/5">
                            <div>
                              <span className="text-slate-500">File Size:</span>{' '}
                              <span className="text-slate-300 font-mono">
                                {formatBytes(mat.file_size)}
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500">Checksum:</span>{' '}
                              <span className="text-slate-300 font-mono">
                                {mat.checksum_sha256.substring(0, 8)}...
                              </span>
                            </div>
                            {doc && (
                              <>
                                <div>
                                  <span className="text-slate-500">Type:</span>{' '}
                                  <span className="text-slate-300 font-mono font-medium">
                                    {doc.document_type}
                                  </span>
                                </div>
                                <div>
                                  <span className="text-slate-500">Extent:</span>{' '}
                                  <span className="text-slate-300">
                                    {doc.page_count
                                      ? `${doc.page_count} Pages`
                                      : doc.slide_count
                                      ? `${doc.slide_count} Slides`
                                      : 'Structured Text'}
                                  </span>
                                </div>
                              </>
                            )}
                            <div className="col-span-2">
                              <span className="text-slate-500">Uploaded:</span>{' '}
                              <span className="text-slate-300">
                                {new Date(mat.created_at).toLocaleString()}
                              </span>
                            </div>
                          </div>

                          {mat.error_code && (
                            <div className="mt-3 p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-[11px] flex items-center gap-2">
                              <AlertCircle className="w-3.5 h-3.5 shrink-0 text-red-400" />
                              <span>Error Code: {mat.error_code}</span>
                            </div>
                          )}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center justify-between gap-2 mt-4 pt-3 border-t border-white/5">
                          {mat.status === 'PROCESSED' ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleOpenChunks(mat)}
                              className="text-xs flex items-center gap-1 text-cyan-300 hover:text-cyan-200 border-cyan-500/30"
                            >
                              <Eye className="w-3.5 h-3.5" />
                              Inspect Chunks
                            </Button>
                          ) : (
                            <span className="text-[11px] text-slate-500 italic">
                              {mat.status === 'FAILED' ? 'Extraction failed' : 'Pipeline running...'}
                            </span>
                          )}

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setDeleteConfirmMaterial(mat);
                              setIsDeleteModalOpen(true);
                            }}
                            className="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </GlassCard>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: Evidence Retrieval Preview (RAG) */}
        {activeTab === 'rag' && (
          <div className="space-y-6">
            {/* Search Controls */}
            <GlassCard className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-semibold text-white flex items-center gap-2">
                    <Search className="w-4 h-4 text-cyan-400" />
                    Semantic Evidence Retrieval
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Query against your ingested learning materials for exact, citation-grounded evidence chunks.
                  </p>
                </div>
                <div className="px-2.5 py-1 rounded-full text-[11px] font-mono bg-violet-500/10 border border-violet-500/20 text-violet-300">
                  Strict Evidence Only (No LLM answers)
                </div>
              </div>

              <form onSubmit={handleExecuteSearch} className="space-y-4">
                <div className="flex flex-col sm:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="e.g., minimum wage revision guidelines, sampling methods, labour inspection..."
                      className="w-full bg-slate-900/80 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
                    />
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    disabled={ragSearchMutation.isPending || !searchQuery.trim()}
                    className="shrink-0"
                  >
                    {ragSearchMutation.isPending ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="w-4 h-4 mr-2" />
                        Retrieve Evidence
                      </>
                    )}
                  </Button>
                </div>

                {/* Filters: Top-K and Document Scope */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 pt-2 border-t border-white/5">
                  <div className="flex items-center gap-2">
                    <span>Top-K Results:</span>
                    <select
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="bg-slate-900 border border-white/10 rounded-lg px-2 py-1 text-white text-xs focus:outline-none focus:border-cyan-400"
                    >
                      <option value={3}>3 Chunks</option>
                      <option value={5}>5 Chunks (Default)</option>
                      <option value={10}>10 Chunks</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <span>Document Filter:</span>
                    <select
                      value={selectedDocFilter}
                      onChange={(e) => setSelectedDocFilter(e.target.value)}
                      className="bg-slate-900 border border-white/10 rounded-lg px-2 py-1 text-white text-xs focus:outline-none focus:border-cyan-400 max-w-[200px] truncate"
                    >
                      <option value="all">All Ingested Documents</option>
                      {materials
                        .filter((m) => m.status === 'PROCESSED')
                        .map((m) => (
                          <option key={m.id} value={m.documents?.[0]?.id || m.id}>
                            {m.original_filename}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>
              </form>
            </GlassCard>

            {/* Status Banner: Vector Search Active or Fallback Notice */}
            {ragResponse?.retrieval_mode === 'vector' && !ragResponse?.warning && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-3 text-left">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-semibold text-emerald-300">
                      Vector search active
                    </h4>
                    <span className="px-1.5 py-0.5 text-[10px] font-mono rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      pgvector 0.8.6
                    </span>
                  </div>
                  <p className="text-[11px] text-emerald-200/80 mt-0.5 leading-relaxed">
                    Native PostgreSQL pgvector extension is active with 384-dimensional cosine distance retrieval.
                  </p>
                </div>
              </div>
            )}

            {(ragResponse?.retrieval_mode === 'development_lexical_fallback' ||
              ragResponse?.warning) && (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-left">
                <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-semibold text-amber-300">
                    Vector search unavailable in current environment.
                  </h4>
                  <p className="text-[11px] text-amber-200/80 mt-0.5 leading-relaxed">
                    PostgreSQL pgvector extension is not compiled in this native Windows database environment.
                    The platform is operating with the official <strong>Development Lexical Similarity Fallback</strong>{' '}
                    (calculating exact cosine similarity in-memory with lexical boosting).
                  </p>
                </div>
              </div>
            )}

            {/* Search Results Display */}
            {ragSearchMutation.isPending ? (
              <LoadingState message="Retrieving semantic evidence chunks from vector repository..." />
            ) : ragResponse ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-white flex items-center gap-2">
                    <span>Retrieved Evidence</span>
                    <Badge variant="primary" className="text-xs font-mono">
                      {ragResponse.results.length} Chunks
                    </Badge>
                  </h4>

                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
                    Mode: {ragResponse.retrieval_mode === 'vector' ? (
                      <span className="text-emerald-400 font-medium">pgvector (cosine)</span>
                    ) : (
                      <span className="text-amber-400">{ragResponse.retrieval_mode}</span>
                    )}
                  </span>
                </div>

                {ragResponse.results.length === 0 || ragResponse.status === 'INSUFFICIENT_EVIDENCE' ? (
                  <EmptyState
                    icon={<Search className="w-8 h-8 text-slate-500" />}
                    title="No sufficiently relevant evidence found."
                    description={
                      ragResponse.message ||
                      `No sufficiently relevant evidence was found for "${ragResponse.query}". Try a broader query or upload more learning materials.`
                    }
                  />
                ) : (
                  <div className="space-y-3">
                    {ragResponse.results.map((result: RAGSearchResultItem, idx: number) => (
                      <GlassCard
                        key={result.chunk_id || idx}
                        className="p-5 border border-white/10 hover:border-cyan-500/30 transition-all text-left"
                      >
                        {/* Citation Header */}
                        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                          <div className="flex items-center gap-2">
                            <span className="w-6 h-6 rounded-md bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold flex items-center justify-center">
                              #{idx + 1}
                            </span>
                            <span className="text-sm font-semibold text-white">
                              {result.document_title}
                            </span>
                          </div>

                          <div className="flex items-center gap-2">
                            {result.page_number && (
                              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-white/5 border border-white/10 text-slate-300">
                                Page {result.page_number}
                              </span>
                            )}
                            {result.slide_number && (
                              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-amber-500/10 border border-amber-500/20 text-amber-300">
                                Slide {result.slide_number}
                              </span>
                            )}
                            {result.section_title && (
                              <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300">
                                {result.section_title}
                              </span>
                            )}
                            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                              Score: {(result.score * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>

                        {/* Text Excerpt */}
                        <div className="p-3.5 rounded-xl bg-slate-950/80 border border-white/5 font-sans text-xs text-slate-200 leading-relaxed">
                          <p className="whitespace-pre-wrap">{result.text}</p>
                        </div>

                        {/* Provenance Footer */}
                        <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 mt-2.5">
                          <span>Chunk ID: {result.chunk_id.substring(0, 16)}...</span>
                          <span className="text-cyan-400/70">Verified Officer Document Chunk</span>
                        </div>
                      </GlassCard>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Guided Prompt State */
              <GlassCard className="p-8 text-center border-white/5">
                <Search className="w-10 h-10 text-cyan-400/40 mx-auto mb-3" />
                <h4 className="text-sm font-semibold text-white">
                  Evidence Retrieval Query Console
                </h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                  Type an inquiry above to search across your indexed documents. Grounded citations and similarity scores will be displayed without generative synthesis.
                </p>
                <div className="flex flex-wrap items-center justify-center gap-2 mt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery('minimum wages revision and enforcement procedure');
                    }}
                    className="px-2.5 py-1 rounded-lg text-xs bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors"
                  >
                    💡 &quot;minimum wages revision...&quot;
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery('sampling methodology for labour statistics survey');
                    }}
                    className="px-2.5 py-1 rounded-lg text-xs bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors"
                  >
                    💡 &quot;sampling methodology...&quot;
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSearchQuery('field inspection checklist and verification');
                    }}
                    className="px-2.5 py-1 rounded-lg text-xs bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 transition-colors"
                  >
                    💡 &quot;field inspection checklist...&quot;
                  </button>
                </div>
              </GlassCard>
            )}
          </div>
        )}

        {/* Modal: Inspect Extracted Chunks */}
        <Modal
          isOpen={isChunkModalOpen}
          onClose={() => {
            setIsChunkModalOpen(false);
            setSelectedMaterialForChunks(null);
          }}
          title={selectedMaterialForChunks?.original_filename || 'Extracted Document Chunks'}
          description="Direct view of normalized, semantically bounded text chunks indexed in the vector store."
          size="lg"
        >
          <div className="space-y-4 max-h-[65vh] overflow-y-auto pr-1">
            {isLoadingChunks ? (
              <LoadingState message="Loading indexed chunks..." />
            ) : !chunksData || chunksData.length === 0 ? (
              <EmptyState
                icon={<Layers className="w-6 h-6 text-slate-500" />}
                title="No Chunks Available"
                description="This document has not produced chunks or is still being processed."
              />
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400 pb-2 border-b border-white/10">
                  <span>Total Chunks: <strong>{chunksData.length}</strong></span>
                  <span>Target Bound: ~400–700 tokens</span>
                </div>

                {chunksData.map((chunk: DocumentChunk) => (
                  <div
                    key={chunk.id}
                    className="p-3.5 rounded-xl bg-slate-900/90 border border-white/5 space-y-2 text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                          Chunk #{chunk.chunk_index + 1}
                        </span>
                        {chunk.page_number && (
                          <span className="text-[11px] text-slate-400 font-mono">
                            Page {chunk.page_number}
                          </span>
                        )}
                        {chunk.slide_number && (
                          <span className="text-[11px] text-amber-300 font-mono">
                            Slide {chunk.slide_number}
                          </span>
                        )}
                      </div>

                      <div className="flex items-center gap-2">
                        {chunk.token_count && (
                          <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                            <Hash className="w-3 h-3" />
                            {chunk.token_count} tokens
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 whitespace-pre-wrap leading-relaxed font-sans">
                      {chunk.text}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Modal>

        {/* Modal: Confirm Material Deletion */}
        <Modal
          isOpen={isDeleteModalOpen}
          onClose={() => {
            setIsDeleteModalOpen(false);
            setDeleteConfirmMaterial(null);
          }}
          title="Delete Learning Material"
          description="Are you sure you want to permanently delete this material? All associated extracted chunks and vector embeddings will also be deleted."
          size="sm"
        >
          <div className="space-y-4 text-left">
            <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300">
              <p className="font-semibold text-white">
                {deleteConfirmMaterial?.original_filename}
              </p>
              <p className="mt-1 text-slate-400">
                This action cannot be undone. Evidence retrieval will no longer match chunks from this file.
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setIsDeleteModalOpen(false);
                  setDeleteConfirmMaterial(null);
                }}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="bg-red-600 hover:bg-red-700 text-white"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete Material'}
              </Button>
            </div>
          </div>
        </Modal>

        <ToastContainer toasts={toasts} onDismiss={removeToast} />
      </PageContainer>
    </AppShell>
  );
}
