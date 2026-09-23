'use client';

import React from 'react';
import { FileText, Bookmark } from 'lucide-react';

export interface SourceCitationProps {
  documentTitle: string;
  pageNumber?: number | string;
  chunkId?: string;
  snippet?: string;
  className?: string;
}

export function SourceCitation({
  documentTitle,
  pageNumber,
  chunkId,
  snippet,
  className = '',
}: SourceCitationProps) {
  return (
    <div className={`p-3 rounded-lg bg-slate-900/70 border border-white/5 text-left text-xs ${className}`}>
      <div className="flex items-center justify-between gap-2 mb-1">
        <div className="flex items-center gap-1.5 font-medium text-cyan-300 truncate">
          <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="truncate">{documentTitle}</span>
        </div>
        {pageNumber && (
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400 shrink-0">
            P. {pageNumber}
          </span>
        )}
      </div>

      {snippet && <p className="text-[11px] text-slate-400 italic line-clamp-2 mt-1 leading-relaxed">&ldquo;{snippet}&rdquo;</p>}

      {chunkId && (
        <div className="mt-1.5 text-[9px] font-mono text-slate-500 flex items-center gap-1">
          <Bookmark className="w-2.5 h-2.5" />
          <span>Chunk: {chunkId}</span>
        </div>
      )}
    </div>
  );
}
