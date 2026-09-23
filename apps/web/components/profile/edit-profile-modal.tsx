'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import type { Employee } from '@pragya/types';
import { useJobRoles } from '@/hooks/use-organization';
import { useUpdateEmployee } from '@/hooks/use-employee';

const SUPPORTED_LANGUAGES = [
  'English',
  'Hindi',
  'Bengali',
  'Marathi',
  'Telugu',
  'Tamil',
  'Gujarati',
  'Urdu',
  'Kannada',
  'Odia',
  'Malayalam',
  'Punjabi',
  'Assamese',
] as const;

const profileEditSchema = z.object({
  current_assignment: z
    .string()
    .min(2, 'Current assignment must be at least 2 characters')
    .max(255, 'Assignment exceeds maximum length'),
  education: z
    .string()
    .min(2, 'Education qualification is required')
    .max(255, 'Education exceeds maximum length'),
  experience_years: z
    .number()
    .min(0, 'Experience cannot be negative')
    .max(50, 'Experience cannot exceed 50 years'),
  preferred_language: z.string().min(1, 'Please select a supported official language'),
  target_role_id: z.string().optional().nullable(),
});

interface ProfileEditFormValues {
  current_assignment: string;
  education: string;
  experience_years: number;
  preferred_language: string;
  target_role_id?: string | null;
}

interface EditProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  employee: Employee;
}

export function EditProfileModal({
  isOpen,
  onClose,
  employee,
}: EditProfileModalProps) {
  const { data: jobRoles = [] } = useJobRoles();
  const updateMutation = useUpdateEmployee();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ProfileEditFormValues>({
    resolver: zodResolver(profileEditSchema),
    defaultValues: {
      current_assignment: employee.current_assignment || '',
      education: employee.education || '',
      experience_years: employee.experience_years,
      preferred_language: employee.preferred_language || 'English',
      target_role_id: employee.target_role_id || '',
    },
  });

  // Re-sync form defaults if employee prop changes
  React.useEffect(() => {
    if (isOpen) {
      reset({
        current_assignment: employee.current_assignment || '',
        education: employee.education || '',
        experience_years: employee.experience_years,
        preferred_language: employee.preferred_language || 'English',
        target_role_id: employee.target_role_id || '',
      });
    }
  }, [isOpen, employee, reset]);

  const onSubmit = async (values: ProfileEditFormValues) => {
    setSubmitError(null);
    setSubmitSuccess(false);
    try {
      await updateMutation.mutateAsync({
        id: employee.id,
        payload: {
          current_assignment: values.current_assignment,
          education: values.education,
          experience_years: Number(values.experience_years),
          preferred_language: values.preferred_language,
          target_role_id: values.target_role_id || null,
        },
      });
      setSubmitSuccess(true);
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update profile';
      setSubmitError(msg);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.2 }}
            className="w-full max-w-xl bg-[#0F172A] border border-cyan-500/20 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/80 bg-slate-900/50">
              <div>
                <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                  Edit Officer Profile
                  <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    {employee.employee_code}
                  </span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Update service assignments, learning preferences, and cadre aspirations.
                </p>
              </div>
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Notification Messages */}
            {submitSuccess && (
              <div className="mx-6 mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Profile updated and synchronized with PostgreSQL successfully!</span>
              </div>
            )}

            {submitError && (
              <div className="mx-6 mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{submitError}</span>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4 overflow-y-auto">
              {/* Current Assignment */}
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Current Assignment / Posting
                </label>
                <input
                  type="text"
                  {...register('current_assignment')}
                  placeholder="e.g. Survey Data Analysis"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
                />
                {errors.current_assignment && (
                  <p className="text-xs text-rose-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {errors.current_assignment.message}
                  </p>
                )}
              </div>

              {/* Education */}
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Highest Education Qualification
                </label>
                <input
                  type="text"
                  {...register('education')}
                  placeholder="e.g. M.Sc. Statistics"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
                />
                {errors.education && (
                  <p className="text-xs text-rose-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {errors.education.message}
                  </p>
                )}
              </div>

              {/* Grid: Experience & Language */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Experience Years */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                    Experience (Years)
                  </label>
                  <input
                    type="number"
                    min={0}
                    max={50}
                    {...register('experience_years', { valueAsNumber: true })}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
                  />
                  {errors.experience_years && (
                    <p className="text-xs text-rose-400 flex items-center gap-1">
                      <AlertCircle className="w-3.5 h-3.5" />
                      {errors.experience_years.message}
                    </p>
                  )}
                </div>

                {/* Preferred Language */}
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                    Preferred Language
                  </label>
                  <select
                    {...register('preferred_language')}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
                  >
                    {SUPPORTED_LANGUAGES.map((lang) => (
                      <option key={lang} value={lang} className="bg-slate-900 text-slate-100">
                        {lang}
                      </option>
                    ))}
                  </select>
                  {errors.preferred_language && (
                    <p className="text-xs text-rose-400 flex items-center gap-1">
                      <AlertCircle className="w-3.5 h-3.5" />
                      {errors.preferred_language.message}
                    </p>
                  )}
                </div>
              </div>

              {/* Target Cadre Role */}
              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300 uppercase tracking-wider">
                  Target Cadre Role (Aspiration)
                </label>
                <select
                  {...register('target_role_id')}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500"
                >
                  <option value="" className="bg-slate-900 text-slate-400">
                    -- Select Target Cadre Role --
                  </option>
                  {jobRoles.map((role) => (
                    <option key={role.id} value={role.id} className="bg-slate-900 text-slate-100">
                      {role.name} ({role.career_level})
                    </option>
                  ))}
                </select>
                {errors.target_role_id && (
                  <p className="text-xs text-rose-400 flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {errors.target_role_id.message}
                  </p>
                )}
              </div>

              {/* Readonly info notice */}
              <div className="p-3 rounded-xl bg-slate-900/50 border border-slate-800 text-xs text-slate-400 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                Department ({employee.department_name}) and Cadre designation ({employee.designation}) are governed by MoSPI service orders and cannot be arbitrarily modified.
              </div>

              {/* Action Buttons */}
              <div className="pt-3 flex items-center justify-end gap-3 border-t border-slate-800/80">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl text-sm font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-800/60 transition disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-medium shadow-lg shadow-cyan-500/20 transition disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Saving to PostgreSQL...
                    </>
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
