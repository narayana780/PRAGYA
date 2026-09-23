'use client';

import React from 'react';
import {
  Home,
  User,
  Award,
  Target,
  GitMerge,
  BookOpen,
  Sparkles,
  Upload,
  FileCheck,
  TrendingUp,
  History,
  Bell,
  LayoutDashboard,
  Users,
  Building2,
  BarChart3,
  Zap,
  LineChart,
  FileSpreadsheet,
  Layers,
  BrainCircuit,
  FlaskConical,
  Activity,
} from 'lucide-react';

interface NavIconProps {
  name: string;
  className?: string;
}

export function NavIcon({ name, className = 'w-4 h-4' }: NavIconProps) {
  switch (name) {
    case 'Home':
      return <Home className={className} />;
    case 'User':
      return <User className={className} />;
    case 'Award':
      return <Award className={className} />;
    case 'Target':
      return <Target className={className} />;
    case 'GitMerge':
      return <GitMerge className={className} />;
    case 'BookOpen':
      return <BookOpen className={className} />;
    case 'Sparkles':
      return <Sparkles className={className} />;
    case 'Upload':
      return <Upload className={className} />;
    case 'FileCheck':
      return <FileCheck className={className} />;
    case 'TrendingUp':
      return <TrendingUp className={className} />;
    case 'History':
      return <History className={className} />;
    case 'Bell':
      return <Bell className={className} />;
    case 'LayoutDashboard':
      return <LayoutDashboard className={className} />;
    case 'Users':
      return <Users className={className} />;
    case 'Building2':
      return <Building2 className={className} />;
    case 'BarChart3':
      return <BarChart3 className={className} />;
    case 'Zap':
      return <Zap className={className} />;
    case 'LineChart':
      return <LineChart className={className} />;
    case 'FileSpreadsheet':
      return <FileSpreadsheet className={className} />;
    case 'BrainCircuit':
      return <BrainCircuit className={className} />;
    case 'FlaskConical':
      return <FlaskConical className={className} />;
    case 'Activity':
      return <Activity className={className} />;
    default:
      return <Layers className={className} />;
  }
}
