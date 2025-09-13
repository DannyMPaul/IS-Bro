import { formatDistanceToNow, format, isToday, isYesterday } from 'date-fns';

export function formatChatTimestamp(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  
  if (isToday(date)) {
    return format(date, 'h:mm a');
  } else if (isYesterday(date)) {
    return 'Yesterday ' + format(date, 'h:mm a');
  } else {
    return format(date, 'MMM d, h:mm a');
  }
}

export function formatRelativeTime(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  return formatDistanceToNow(date, { addSuffix: true });
}

export function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}
