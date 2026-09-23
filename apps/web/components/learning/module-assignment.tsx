'use client';

import React, { useState } from 'react';
import {
  FileCode2,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  RotateCcw,
  Loader2,
  Building2,
} from 'lucide-react';
import type { AssignmentResultResponse } from '@pragya/types';

interface AssignmentFieldOption {
  value: string;
  label: string;
}

interface AssignmentField {
  name: string;
  label: string;
  options: AssignmentFieldOption[];
}

interface StratumInfo {
  name?: string;
  households?: number;
  estimated_std_dev?: number;
  description?: string;
}

interface AssignmentScenario {
  district_name?: string;
  total_households?: number;
  budgeted_sample_size?: number;
  stratum_a?: StratumInfo;
  stratum_b?: StratumInfo;
}

interface AssignmentData {
  title?: string;
  instructions?: string;
  scenario?: AssignmentScenario;
  fields?: AssignmentField[];
}

interface RubricItem {
  submitted: string;
  correct: string;
  is_correct: boolean;
  points: number;
  feedback: string;
}

interface ModuleAssignmentProps {
  moduleId: number;
  assignmentData?: AssignmentData | null;
  isAlreadyPassed?: boolean;
  onAssignmentSubmit: (payload: {
    sampling_method: string;
    allocation_strategy: string;
    non_response_buffer: string;
    justification_code: string;
  }) => Promise<AssignmentResultResponse>;
}

export function ModuleAssignment({
  moduleId,
  assignmentData,
  isAlreadyPassed = false,
  onAssignmentSubmit,
}: ModuleAssignmentProps) {
  const [formData, setFormData] = useState({
    sampling_method: '',
    allocation_strategy: '',
    non_response_buffer: '',
    justification_code: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<AssignmentResultResponse | null>(null);

  const scenario = assignmentData?.scenario;
  const fields = assignmentData?.fields || [];

  const handleFieldChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    if (
      !formData.sampling_method ||
      !formData.allocation_strategy ||
      !formData.non_response_buffer ||
      !formData.justification_code
    ) {
      alert('Please select a decision for all methodological configuration fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await onAssignmentSubmit(formData);
      setResult(res);
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'Failed to submit assignment. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormComplete =
    formData.sampling_method &&
    formData.allocation_strategy &&
    formData.non_response_buffer &&
    formData.justification_code;

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A]/95 p-6 md:p-8 space-y-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 border border-violet-500/20 flex items-center gap-1">
              <FileCode2 className="w-3 h-3" />
              <span>MODULE {moduleId} PRACTICAL ASSIGNMENT</span>
            </span>
            <span className="text-xs text-slate-400">Pass Threshold: 75% Score</span>
          </div>
          <h3 className="text-lg font-bold text-white tracking-tight">
            {assignmentData?.title || 'District Household Survey Stratification & Allocation Design'}
          </h3>
        </div>

        {isAlreadyPassed && !result && (
          <div className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 shrink-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Assignment Passed & Credited</span>
          </div>
        )}
      </div>

      {/* Scenario Context Card */}
      {scenario && (
        <div className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
              <Building2 className="w-4 h-4" />
              <span>Administrative Scenario Brief</span>
            </div>
            <span className="font-mono text-[11px] text-slate-400">
              Budgeted Sample n = {scenario.budgeted_sample_size} Households
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            You are tasked with planning the socioeconomic sample survey for <strong>{scenario.district_name}</strong> ({scenario.total_households?.toLocaleString() ?? '100,000'} households). Notice the high variance heterogeneity between the two sub-strata:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-200">
                <span>{scenario.stratum_a?.name}</span>
                <span className="font-mono text-indigo-400">σ = ₹{scenario.stratum_a?.estimated_std_dev?.toLocaleString()}</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                {scenario.stratum_a?.households?.toLocaleString()} households. {scenario.stratum_a?.description}.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-1.5">
              <div className="flex justify-between font-semibold text-slate-200">
                <span>{scenario.stratum_b?.name}</span>
                <span className="font-mono text-cyan-400">σ = ₹{scenario.stratum_b?.estimated_std_dev?.toLocaleString()}</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                {scenario.stratum_b?.households?.toLocaleString()} households. {scenario.stratum_b?.description}.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Result Card if submitted */}
      {result && (
        <div
          className={`p-5 rounded-2xl border transition-all ${
            result.passed
              ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-200'
              : 'bg-rose-950/20 border-rose-500/30 text-rose-200'
          } space-y-3`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-sm">
              {result.passed ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span className="text-white">Practical Design Validated & Passed!</span>
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-rose-400" />
                  <span className="text-white">Design Score: {result.score}/100 — Needs Review</span>
                </>
              )}
            </div>
            <span className="font-mono text-xs font-bold px-3 py-1 rounded-lg bg-slate-900 border border-slate-700">
              Score: {result.score} / {result.max_score} ({result.percentage}%)
            </span>
          </div>

          <p className="text-xs leading-relaxed text-slate-300">{result.feedback}</p>

          {/* Rubric Breakdown */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 text-[11px]">
            {Object.entries(result.rubric_breakdown || {}).map(([key, value]) => {
              const rb = value as RubricItem;
              return (
                <div
                  key={key}
                  className={`p-2.5 rounded-lg border ${
                    rb.is_correct ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300' : 'bg-rose-950/30 border-rose-500/40 text-rose-300'
                  }`}
                >
                  <div className="flex justify-between font-semibold">
                    <span className="capitalize">{key.replace('_', ' ')}</span>
                    <span>{rb.points} pts</span>
                  </div>
                  <p className="text-[10px] opacity-90 leading-tight pt-1">{rb.feedback}</p>
                </div>
              );
            })}
          </div>

          {result.evidence_id && (
            <div className="mt-2 text-[11px] font-mono text-emerald-400 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Competency Evidence Logged: #{result.evidence_id.slice(0, 8)}</span>
            </div>
          )}

          {!result.passed && (
            <button
              onClick={() => setResult(null)}
              className="mt-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold flex items-center gap-2 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Modify and Re-evaluate Design</span>
            </button>
          )}
        </div>
      )}

      {/* Decision Fields Form */}
      {(!result || !result.passed) && (
        <div className="space-y-6">
          <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            Methodological Decision Configuration
          </div>

          {fields.map((fld: AssignmentField) => (
            <div key={fld.name} className="p-5 rounded-xl bg-slate-950/50 border border-slate-800 space-y-3">
              <label className="text-xs font-semibold text-white block">
                {fld.label}
              </label>

              <div className="space-y-2">
                {fld.options.map((opt: AssignmentFieldOption) => {
                  const isChecked = formData[fld.name as keyof typeof formData] === opt.value;
                  return (
                    <label
                      key={opt.value}
                      className={`flex items-start gap-3 p-3 rounded-xl border text-xs cursor-pointer transition ${
                        isChecked
                          ? 'border-indigo-500 bg-indigo-950/30 text-indigo-200 font-semibold'
                          : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name={fld.name}
                        value={opt.value}
                        checked={isChecked}
                        onChange={() => handleFieldChange(fld.name, opt.value)}
                        className="mt-0.5 accent-indigo-500"
                      />
                      <span className="leading-relaxed">{opt.label}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          ))}

          <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              {isFormComplete ? 'All 4 decisions configured' : 'Configure all 4 parameters to submit'}
            </span>

            <button
              onClick={handleSubmit}
              disabled={!isFormComplete || isSubmitting}
              className="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs transition flex items-center gap-2 shadow-lg shadow-indigo-950/50"
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle2 className="w-4 h-4" />
              )}
              <span>Submit & Validate Design</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
