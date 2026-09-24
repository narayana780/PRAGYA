export interface CourseLaunchItem {
  id?: string;
  provider?: string;
  url?: string | null;
  type?: string;
}

/**
 * Resolves the appropriate course launch destination.
 * - PRAGYA internal labs route to /employee/labs.
 * - External mock URLs (mock.igotkarmayogi.gov.in, mock.nssta.gov.in) route to the integrated in-platform
 *   course player at /employee/courses/[id]/launch when no external mock host is configured.
 * - Configured external hosts (via NEXT_PUBLIC_MOCK_IGOT_BASE_URL) are rewritten properly.
 */
export function getCourseLaunchUrl(item?: CourseLaunchItem | null): string {
  if (!item) return '/employee/courses';

  // PRAGYA Lab items link to internal virtual labs
  if (
    item.provider === 'PRAGYA' ||
    item.type === 'LAB' ||
    (item.url && item.url.includes('pragya.gov.in/labs'))
  ) {
    return '/employee/labs';
  }

  // If configured with an external mock server URL, rewrite the mock domain
  const mockIgotBase = process.env.NEXT_PUBLIC_MOCK_IGOT_BASE_URL;
  if (mockIgotBase && item.url) {
    if (item.url.includes('mock.igotkarmayogi.gov.in')) {
      return item.url.replace(/https?:\/\/mock\.igotkarmayogi\.gov\.in/, mockIgotBase.replace(/\/$/, ''));
    }
    if (item.url.includes('mock.nssta.gov.in')) {
      return item.url.replace(/https?:\/\/mock\.nssta\.gov\.in/, mockIgotBase.replace(/\/$/, ''));
    }
  }

  // If pointing to unreachable mock prototype domains or internal path, use integrated player
  if (
    !item.url ||
    item.url.includes('mock.igotkarmayogi.gov.in') ||
    item.url.includes('mock.nssta.gov.in') ||
    item.url.startsWith('/')
  ) {
    return item.id ? `/employee/courses/${item.id}/launch` : '/employee/courses';
  }

  return item.url;
}

export function isExternalLaunchUrl(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}
