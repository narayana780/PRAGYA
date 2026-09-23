'use client';

import React, { useState } from 'react';
import {
  CheckCircle2,
  Clock,
  FileText,
  ChevronRight,
} from 'lucide-react';

interface CourseReadingViewerProps {
  readingId?: string;
  title: string;
  durationDisplay?: string;
  contentMarkdown: string;
  isCompleted?: boolean;
  onMarkComplete: () => void;
}

export function CourseReadingViewer({
  title,
  durationDisplay = '5 min read',
  contentMarkdown,
  isCompleted = false,
  onMarkComplete,
}: CourseReadingViewerProps) {
  const [completed, setCompleted] = useState(isCompleted);

  const handleComplete = () => {
    setCompleted(true);
    onMarkComplete();
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/95 p-6 md:p-8 space-y-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 flex items-center gap-1">
              <FileText className="w-3 h-3" />
              <span>OFFICIAL STUDY MATERIAL</span>
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {durationDisplay}
            </span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">{title}</h3>
        </div>

        {completed ? (
          <div className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shrink-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Completed & Verified</span>
          </div>
        ) : (
          <button
            onClick={handleComplete}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/40 shrink-0"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Mark as Read & Completed</span>
          </button>
        )}
      </div>

      {/* Content Rendering */}
      <div className="prose prose-invert max-w-none text-xs md:text-sm text-slate-300 leading-relaxed space-y-4">
        {contentMarkdown.split('\n\n').map((paragraph, idx) => {
          if (paragraph.startsWith('# ')) {
            return (
              <h2 key={idx} className="text-base md:text-lg font-bold text-white pt-2 border-b border-slate-800 pb-1">
                {paragraph.replace('# ', '')}
              </h2>
            );
          }
          if (paragraph.startsWith('## ')) {
            return (
              <h3 key={idx} className="text-sm md:text-base font-bold text-indigo-300 pt-2 flex items-center gap-2">
                <ChevronRight className="w-4 h-4 text-indigo-400" />
                <span>{paragraph.replace('## ', '')}</span>
              </h3>
            );
          }
          if (paragraph.startsWith('### ')) {
            return (
              <h4 key={idx} className="text-xs md:text-sm font-semibold text-amber-300 pt-1">
                {paragraph.replace('### ', '')}
              </h4>
            );
          }
          if (paragraph.startsWith('- ')) {
            const items = paragraph.split('\n');
            return (
              <ul key={idx} className="space-y-1 pl-4 list-disc marker:text-indigo-400">
                {items.map((it, i) => (
                  <li key={i} className="text-slate-300">
                    {it.replace('- ', '')}
                  </li>
                ))}
              </ul>
            );
          }
          return (
            <p key={idx} className="text-slate-300 leading-relaxed">
              {paragraph}
            </p>
          );
        })}
      </div>

      {/* Completion Confirmation Footer */}
      <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Source: National Academy of Statistical Administration (NSSTA) Training Compendium
        </span>
        {!completed && (
          <button
            onClick={handleComplete}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/40"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Confirm Reading Completed</span>
          </button>
        )}
      </div>
    </div>
  );
}
