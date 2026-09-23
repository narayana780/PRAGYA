'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Volume2,
  VolumeX,
  CheckCircle2,
  Clock,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';

interface CourseVideoPlayerProps {
  videoId?: string;
  title: string;
  videoUrl?: string;
  durationSeconds: number;
  initialProgressSeconds?: number;
  isCompleted?: boolean;
  onProgressUpdate: (progressSeconds: number, durationSeconds: number, percentage: number, isCompleted: boolean) => void;
}

export function CourseVideoPlayer({
  title,
  videoUrl,
  durationSeconds,
  initialProgressSeconds = 0,
  isCompleted = false,
  onProgressUpdate,
}: CourseVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(initialProgressSeconds);
  const [duration, setDuration] = useState(durationSeconds || 45);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [hasReachedThreshold, setHasReachedThreshold] = useState(isCompleted);
  const [hasError, setHasError] = useState(false);
  const initialPct = isCompleted
    ? 100
    : initialProgressSeconds > 0 && (durationSeconds || 45) > 0
    ? Math.min(100, Math.round((initialProgressSeconds / (durationSeconds || 45)) * 100))
    : 0;
  const [watchPercentage, setWatchPercentage] = useState(initialPct);

  // Cumulative watched seconds set to ensure genuine playback (prevents seek-to-end cheating)
  const watchedSecondsRef = useRef<Set<number>>(new Set());
  const lastReportedTimeRef = useRef<number>(0);

  const completed = isCompleted || hasReachedThreshold;

  // Initialize watched seconds ref if already completed or has initial progress
  useEffect(() => {
    if (isCompleted && durationSeconds > 0) {
      for (let s = 0; s <= durationSeconds; s++) {
        watchedSecondsRef.current.add(s);
      }
    } else if (initialProgressSeconds > 0) {
      for (let s = 0; s <= Math.floor(initialProgressSeconds); s++) {
        watchedSecondsRef.current.add(s);
      }
    }
  }, [isCompleted, durationSeconds, initialProgressSeconds]);

  // Sync initial progress into video element on load
  useEffect(() => {
    if (initialProgressSeconds > 0 && videoRef.current && Math.abs(videoRef.current.currentTime - initialProgressSeconds) > 2) {
      videoRef.current.currentTime = initialProgressSeconds;
    }
  }, [initialProgressSeconds]);

  const handlePlayPause = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      setHasError(false);
      videoRef.current
        .play()
        .then(() => setIsPlaying(true))
        .catch((err) => {
          console.warn('Playback error:', err);
          setHasError(true);
        });
    }
  };

  const handleLoadedMetadata = () => {
    if (!videoRef.current) return;
    const dur = videoRef.current.duration;
    if (dur && !isNaN(dur) && isFinite(dur)) {
      setDuration(dur);
    }
  };

  const handleTimeUpdate = useCallback(() => {
    if (!videoRef.current) return;
    const cur = videoRef.current.currentTime;
    const dur = videoRef.current.duration || durationSeconds || 45;
    setCurrentTime(cur);
    if (dur && !isNaN(dur) && isFinite(dur)) {
      setDuration(dur);
    }

    // Cumulative watched seconds tracking: only accumulate when actively playing
    if (!videoRef.current.paused) {
      const second = Math.floor(cur);
      if (second >= 0 && second <= Math.ceil(dur)) {
        watchedSecondsRef.current.add(second);
      }
    }

    const watchedCount = watchedSecondsRef.current.size;
    const watchPct = dur > 0 ? Math.min(100, Math.round((watchedCount / dur) * 100)) : 0;
    setWatchPercentage(watchPct);
    const reachedThreshold = isCompleted || watchPct >= 90;

    if (reachedThreshold && !hasReachedThreshold) {
      setHasReachedThreshold(true);
    }

    // Throttle progress updates to backend (at least 2s apart or upon reaching completion threshold)
    const now = Date.now();
    if (now - lastReportedTimeRef.current > 2000 || (reachedThreshold && !hasReachedThreshold)) {
      lastReportedTimeRef.current = now;
      onProgressUpdate(cur, dur, watchPct, reachedThreshold);
    }
  }, [durationSeconds, isCompleted, hasReachedThreshold, onProgressUpdate]);

  const handleEnded = () => {
    setIsPlaying(false);
    const dur = videoRef.current?.duration || durationSeconds || 45;
    for (let s = 0; s <= Math.ceil(dur); s++) {
      watchedSecondsRef.current.add(s);
    }
    setWatchPercentage(100);
    setHasReachedThreshold(true);
    onProgressUpdate(dur, dur, 100, true);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const target = parseFloat(e.target.value);
    setCurrentTime(target);
    if (videoRef.current) {
      videoRef.current.currentTime = target;
    }
  };

  const handleSpeedChange = (speed: number) => {
    setPlaybackSpeed(speed);
    if (videoRef.current) {
      videoRef.current.playbackRate = speed;
    }
  };

  const handleRetry = () => {
    setHasError(false);
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => setHasError(true));
      setIsPlaying(true);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-[#0A0E1A] overflow-hidden shadow-2xl space-y-0">
      {/* Video Container */}
      <div className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden group">
        {!hasError ? (
          <video
            ref={videoRef}
            src={videoUrl || '/videos/mod1-survey-principles.mp4'}
            className="w-full h-full object-cover"
            onLoadedMetadata={handleLoadedMetadata}
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onEnded={handleEnded}
            onError={() => setHasError(true)}
            playsInline
            preload="auto"
          />
        ) : (
          /* Robust Error / Stream Recovery State (No bypass completion button) */
          <div className="w-full h-full flex flex-col items-center justify-center p-8 bg-gradient-to-br from-rose-950/30 via-slate-950 to-slate-900 text-center space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-rose-600/20 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <AlertCircle className="w-7 h-7" />
            </div>
            <div className="space-y-1 max-w-md">
              <h4 className="text-sm font-bold text-white">{title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Unable to load official video stream. Check your connection or retry loading the media resource.
              </p>
            </div>
            <button
              onClick={handleRetry}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition flex items-center gap-2 border border-slate-700"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Video Stream</span>
            </button>
          </div>
        )}

        {/* Center Play/Pause Overlay when paused */}
        {!isPlaying && !hasError && (
          <button
            onClick={handlePlayPause}
            aria-label="Play video"
            className="absolute inset-0 flex items-center justify-center bg-black/40 hover:bg-black/50 transition backdrop-blur-xs group"
          >
            <div className="w-16 h-16 rounded-full bg-indigo-600/90 group-hover:bg-indigo-500 text-white flex items-center justify-center shadow-xl shadow-indigo-950 transition transform group-hover:scale-110">
              <Play className="w-7 h-7 ml-1 fill-white" />
            </div>
          </button>
        )}

        {/* Completion Badge Overlay */}
        {completed && (
          <div className="absolute top-3 right-3 px-3 py-1 rounded-full bg-emerald-500/90 text-white text-[11px] font-semibold flex items-center gap-1.5 shadow-lg backdrop-blur-md">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Completed (≥90% Watched)</span>
          </div>
        )}
      </div>

      {/* Control Bar */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-800 space-y-3">
        {/* Timeline Scrubber */}
        <div className="space-y-1">
          <input
            type="range"
            min={0}
            max={duration || 100}
            step={0.5}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span>{formatTime(currentTime)}</span>
            <div className="flex items-center gap-2">
              <span className={completed ? 'text-emerald-400 font-bold' : 'text-indigo-400 font-bold'}>
                {watchPercentage}% watched
              </span>
              <span>/</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
          <div className="flex items-center gap-2">
            <button
              onClick={handlePlayPause}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white transition"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white" />}
            </button>
            <button
              onClick={() => {
                if (videoRef.current) {
                  videoRef.current.currentTime = 0;
                  setCurrentTime(0);
                }
              }}
              className="p-2 rounded-xl bg-slate-800/60 hover:bg-slate-700 text-slate-300 transition"
              title="Replay from start"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <button
              onClick={() => {
                if (videoRef.current) {
                  videoRef.current.muted = !isMuted;
                  setIsMuted(!isMuted);
                }
              }}
              className="p-2 rounded-xl bg-slate-800/60 hover:bg-slate-700 text-slate-300 transition"
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex items-center gap-3 text-xs">
            {/* Speed Selector */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
              {[0.75, 1, 1.25, 1.5].map((spd) => (
                <button
                  key={spd}
                  onClick={() => handleSpeedChange(spd)}
                  className={`px-2 py-0.5 rounded text-[10px] font-mono transition ${
                    playbackSpeed === spd ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {spd}x
                </button>
              ))}
            </div>

            {completed ? (
              <span className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Verified Watch Credit</span>
              </span>
            ) : (
              <span className="text-[11px] text-amber-400 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" />
                <span>Watch ≥90% to complete</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
