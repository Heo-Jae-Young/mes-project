import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns';
import { ko } from 'date-fns/locale';

/**
 * 날짜/시간 포맷팅 유틸리티 (date-fns 기반)
 */

/**
 * 안전한 날짜 파싱
 */
const parseDate = (dateString) => {
  if (!dateString) return null;
  
  try {
    // ISO 문자열인 경우
    if (typeof dateString === 'string' && dateString.includes('T')) {
      return parseISO(dateString);
    }
    
    // Date 객체나 다른 형식
    const date = new Date(dateString);
    return isValid(date) ? date : null;
  } catch {
    return null;
  }
};

/**
 * 날짜를 YYYY-MM-DD 형식으로 포맷
 */
export const formatDate = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return '-';
  
  try {
    return format(date, 'yyyy-MM-dd');
  } catch {
    return '-';
  }
};

/**
 * 날짜와 시간을 YYYY-MM-DD HH:mm 형식으로 포맷
 */
export const formatDateTime = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return '-';
  
  try {
    return format(date, 'yyyy-MM-dd HH:mm');
  } catch {
    return '-';
  }
};

/**
 * 한국어로 상대적 시간 표시 (예: "2시간 전")
 */
export const formatRelativeTime = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return '-';
  
  try {
    return formatDistanceToNow(date, { 
      addSuffix: true,
      locale: ko
    });
  } catch {
    return formatDate(dateString);
  }
};

/**
 * ISO 형식으로 변환 (API 전송용)
 */
export const toISOString = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return null;
  
  try {
    return date.toISOString();
  } catch {
    return null;
  }
};

/**
 * 현재 날짜를 YYYY-MM-DDTHH:mm 형식으로 반환 (datetime-local input용)
 */
export const getCurrentDateTimeLocal = () => {
  try {
    return format(new Date(), "yyyy-MM-dd'T'HH:mm");
  } catch {
    return '';
  }
};

/**
 * 날짜 문자열을 datetime-local input 형식으로 변환
 */
export const toDateTimeLocal = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return '';
  
  try {
    return format(date, "yyyy-MM-dd'T'HH:mm");
  } catch {
    return '';
  }
};

/**
 * 사용자 친화적 날짜 표시 (예: "오늘", "어제", "12월 25일")
 */
export const formatFriendlyDate = (dateString) => {
  const date = parseDate(dateString);
  if (!date) return '-';
  
  try {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const inputDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const diffTime = today.getTime() - inputDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return '오늘';
    if (diffDays === 1) return '어제';
    if (diffDays === -1) return '내일';
    if (diffDays > 1 && diffDays <= 7) return `${diffDays}일 전`;
    if (diffDays < -1 && diffDays >= -7) return `${Math.abs(diffDays)}일 후`;
    
    return format(date, 'M월 d일', { locale: ko });
  } catch {
    return '-';
  }
};