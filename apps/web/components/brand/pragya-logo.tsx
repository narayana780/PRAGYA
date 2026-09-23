'use client';

import React from 'react';
import Link from 'next/link';

interface PragyaLogoProps {
  size?: 'sm' | 'md' | 'lg';
  showDescriptor?: boolean;
  href?: string;
  className?: string;
}

export function PragyaLogo({
  size = 'md',
  showDescriptor = false,
  href,
  className = '',
}: PragyaLogoProps) {
  const iconSize = size === 'sm' ? 24 : size === 'lg' ? 40 : 32;
  const textSize = size === 'sm' ? 'text-lg' : size === 'lg' ? 'text-2xl' : 'text-xl';

  const content = (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {/* Abstract geometric leaf + data intelligence visual mark */}
      <div className="relative shrink-0 flex items-center justify-center">
        <svg
          width={iconSize}
          height={iconSize}
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="filter drop-shadow-[0_0_12px_rgba(6,182,212,0.4)]"
          aria-hidden="true"
        >
          <defs>
            <linearGradient id="pragya-primary-grad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#06B6D4" />
              <stop offset="50%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#8B5CF6" />
            </linearGradient>
            <linearGradient id="pragya-accent-grad" x1="12" y1="40" x2="36" y2="8" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="50%" stopColor="#06B6D4" />
              <stop offset="100%" stopColor="#D946EF" />
            </linearGradient>
          </defs>

          {/* Organic statistical leaf arch */}
          <path
            d="M8 24C8 13.5066 16.5066 5 27 5C37.4934 5 40 16 40 24C40 34.4934 31.4934 43 21 43C12 43 8 33 8 24Z"
            stroke="url(#pragya-primary-grad)"
            strokeWidth="2.5"
            strokeLinecap="round"
            className="opacity-90"
          />

          {/* Core intelligence geometric facets */}
          <path
            d="M17 25L24 14L31 25L24 35L17 25Z"
            fill="url(#pragya-accent-grad)"
            fillOpacity="0.25"
            stroke="url(#pragya-accent-grad)"
            strokeWidth="2"
            strokeLinejoin="round"
          />

          {/* Interconnected data nodes */}
          <circle cx="24" cy="14" r="2.5" fill="#06B6D4" />
          <circle cx="31" cy="25" r="2" fill="#8B5CF6" />
          <circle cx="24" cy="35" r="2" fill="#10B981" />
          <circle cx="17" cy="25" r="2" fill="#D946EF" />
          <circle cx="24" cy="25" r="3" fill="#FFFFFF" className="animate-pulse" />
        </svg>
      </div>

      <div className="flex flex-col text-left">
        <span className={`font-black tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-cyan-300 font-sans ${textSize}`}>
          PRAGYA
        </span>
        {showDescriptor && (
          <span className="text-[10px] uppercase font-mono tracking-widest text-cyan-400 font-medium">
            AI Competency Platform
          </span>
        )}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 rounded-lg">
        {content}
      </Link>
    );
  }

  return content;
}
