export interface NavItemConfig {
  label: string;
  href: string;
  iconName: string;
  badge?: string | number;
}

export interface NavSectionConfig {
  title?: string;
  items: NavItemConfig[];
}

export const employeeNavigation: NavSectionConfig[] = [
  {
    title: 'Core Workspace',
    items: [
      { label: 'Home', href: '/employee', iconName: 'Home' },
      { label: 'My Profile', href: '/employee/profile', iconName: 'User' },
    ],
  },
  {
    title: 'Competency & Gaps',
    items: [
      { label: 'Competency', href: '/employee/competency', iconName: 'Award' },
      { label: 'Skill Gaps', href: '/employee/gaps', iconName: 'Target' },
    ],
  },
  {
    title: 'Personalized Learning',
    items: [
      { label: 'Learning Path', href: '/employee/learning', iconName: 'GitMerge' },
      { label: 'Courses', href: '/employee/courses', iconName: 'BookOpen' },
      { label: 'AI Assistant', href: '/employee/assistant', iconName: 'Sparkles', badge: 'AI' },
      { label: 'AI Quizzes', href: '/employee/quizzes', iconName: 'BrainCircuit', badge: 'AI' },
      { label: 'Upload Material', href: '/employee/materials', iconName: 'Upload' },
    ],
  },
  {
    title: 'Evaluation & Records',
    items: [
      { label: 'Virtual Labs', href: '/employee/labs', iconName: 'FlaskConical', badge: 'LAB' },
      { label: 'Adaptive Assessment', href: '/employee/adaptive-assessment', iconName: 'Activity', badge: 'CAT' },
      { label: 'Assessments', href: '/employee/assessments', iconName: 'FileCheck' },
      { label: 'Progress', href: '/employee/progress', iconName: 'TrendingUp' },
      { label: 'History', href: '/employee/history', iconName: 'History' },
      { label: 'Notifications', href: '/employee/notifications', iconName: 'Bell' },
    ],
  },
];

export const adminNavigation: NavSectionConfig[] = [
  {
    title: 'Overview',
    items: [
      { label: 'Dashboard', href: '/admin', iconName: 'LayoutDashboard' },
      { label: 'Workforce Analytics', href: '/admin/workforce', iconName: 'Users' },
    ],
  },
  {
    title: 'Competency & Operations',
    items: [
      { label: 'Competencies', href: '/admin/competencies', iconName: 'Award' },
      { label: 'Department Analysis', href: '/admin/departments', iconName: 'Building2' },
      { label: 'Training Effectiveness', href: '/admin/training', iconName: 'BarChart3' },
    ],
  },
  {
    title: 'Strategic Intelligence',
    items: [
      { label: 'Emerging Skills', href: '/admin/emerging-skills', iconName: 'Zap' },
      { label: 'Workforce Planning', href: '/admin/planning', iconName: 'LineChart', badge: 'PLAN' },
      { label: 'Reports', href: '/admin/reports', iconName: 'FileSpreadsheet' },
    ],
  },
];

export function getNavigationForRole(role: 'EMPLOYEE' | 'ADMIN'): NavSectionConfig[] {
  return role === 'ADMIN' ? adminNavigation : employeeNavigation;
}
