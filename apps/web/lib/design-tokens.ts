/**
 * PRAGYA Centralized Design Tokens (TypeScript)
 * Shared across components, charts, and visualizations
 */

export const PRAGYA_COLORS = {
  // Base
  midnightNavy: '#070A13',
  backgroundSecondary: '#0A0F1D',
  surface: '#0B1021',
  surfaceElevated: '#11182E',
  surfaceHover: '#16203B',
  
  // Accents
  cyan: '#06B6D4',
  teal: '#14B8A6',
  violet: '#8B5CF6',
  magenta: '#D946EF',
  emerald: '#10B981',
  coral: '#F97316',
  amber: '#F59E0B',
  
  // Semantic
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#0284C7',
  
  // Text
  textPrimary: '#F8FAFC',
  textSecondary: '#CBD5E1',
  textMuted: '#64748B',
  textDisabled: '#475569',
  
  // Borders
  border: 'rgba(255, 255, 255, 0.08)',
  borderActive: 'rgba(6, 182, 212, 0.4)',
} as const;

export const PRAGYA_GRADIENTS = {
  primary: 'linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%)',
  ai: 'linear-gradient(135deg, #8B5CF6 0%, #D946EF 100%)',
  tealCyan: 'linear-gradient(135deg, #14B8A6 0%, #06B6D4 100%)',
  purpleCoral: 'linear-gradient(135deg, #8B5CF6 0%, #F97316 100%)',
  emeraldCyan: 'linear-gradient(135deg, #10B981 0%, #06B6D4 100%)',
} as const;
