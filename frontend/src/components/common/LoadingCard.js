import React from 'react';
import LoadingSpinner from './LoadingSpinner';

const LoadingCard = ({ loading, children, className = "" }) => {
  if (loading) {
    return (
      <div className={`flex items-center justify-center py-4 ${className}`}>
        <LoadingSpinner size="small" />
        <span className="ml-2 text-sm text-gray-500">로딩 중...</span>
      </div>
    );
  }
  
  return children;
};

export default LoadingCard;