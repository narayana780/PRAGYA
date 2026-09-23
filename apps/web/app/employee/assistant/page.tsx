'use client';

import React, { useState, useEffect, useRef, Suspense, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { AppShell } from '@/components/layout/app-shell';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AIOrb } from '@/components/ui/ai-orb';
import { ToastContainer, type ToastItem } from '@/components/ui/toast';
import {
  useAssistantConversations,
  useAssistantMessages,
  useCreateConversation,
  useDeleteConversation,
  useSendMessage,
} from '@/hooks/use-assistant';
import { useCurrentEmployee } from '@/hooks/use-employee';
import { useEmployeeSkillGaps } from '@/hooks/use-skill-gaps';
import type {
  AssistantResponse,
  AssistantContextType,
} from '@pragya/types';
import {
  Send,
  Plus,
  Trash2,
  Sparkles,
  Shield,
  ShieldCheck,
  AlertTriangle,
  BookOpen,
  Target,
  Award,
  MessageSquare,
  Globe,
  ChevronRight,
  Loader2,
} from 'lucide-react';

const emptySubscribe = () => () => {};

function useMounted(): boolean {
  return React.useSyncExternalStore(
    emptySubscribe,
    () => true,
    () => false
  );
}

const SUGGESTED_PROMPTS = [
  'Explain this simply',
  'Give me an example',
  'Give me a hint',
  'Test my understanding',
  'What should I revise?',
  'Summarize this topic',
];

function AssistantContent() {
  const searchParams = useSearchParams();
  const contextCompetencyId = searchParams.get('competency_id') || undefined;
  const contextSkillGapId = searchParams.get('skill_gap_id') || undefined;
  const contextDocumentId = searchParams.get('document_id') || undefined;
  const contextCourseId = searchParams.get('course_id') || undefined;

  // React official hydration-safe mounted flag
  const isMounted = useMounted();

  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [inputQuery, setInputQuery] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'hi' | 'te'>('en');
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Refs for scrolling and focus
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const isUserScrolledUpRef = useRef(false);
  const lastPendingTextRef = useRef<string>('');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const contextInitializedRef = useRef(false);

  // Queries
  const { data: currentEmployee, isLoading: isLoadingEmployee } = useCurrentEmployee();
  const { data: skillGaps, isLoading: isLoadingSkillGaps } = useEmployeeSkillGaps(currentEmployee?.id);
  const {
    data: conversations = [],
    isLoading: isLoadingConversations,
  } = useAssistantConversations();

  // Determine active conversation ID safely
  const selectedConversationId =
    (activeConversationId && conversations.some((c) => c.id === activeConversationId))
      ? activeConversationId
      : (conversations.length > 0 ? conversations[0].id : null);

  const {
    data: messages = [],
    isLoading: isLoadingMessages,
  } = useAssistantMessages(selectedConversationId || undefined);

  // Mutations
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();
  const sendMessage = useSendMessage(selectedConversationId || '');

  // Prioritized skill gap
  const prioritizedGap = skillGaps && skillGaps.length > 0 ? skillGaps[0] : null;

  // Smart scroll management: only auto-scroll if user hasn't scrolled up to read history
  const scrollToBottom = useCallback((force = false) => {
    if (!chatScrollRef.current) return;
    if (force || !isUserScrolledUpRef.current) {
      chatScrollRef.current.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, []);

  const handleChatScroll = () => {
    if (!chatScrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = chatScrollRef.current;
    // If distance from bottom is greater than 80px, user has scrolled up
    isUserScrolledUpRef.current = scrollHeight - scrollTop - clientHeight > 80;
  };

  // Scroll to bottom when messages update or sending starts
  useEffect(() => {
    scrollToBottom(false);
  }, [messages, sendMessage.isPending, scrollToBottom]);

  // Contextual entry from query params on mount
  useEffect(() => {
    if (contextInitializedRef.current) return;
    if (contextCompetencyId || contextSkillGapId || contextDocumentId) {
      contextInitializedRef.current = true;
      let contextType: AssistantContextType = 'GENERAL_LEARNING';
      let title = 'Learning Session';
      if (contextCompetencyId) {
        contextType = 'COMPETENCY';
        title = 'Competency Focus';
      } else if (contextSkillGapId) {
        contextType = 'SKILL_GAP';
        title = 'Skill Gap Guidance';
      } else if (contextDocumentId) {
        contextType = 'MATERIAL';
        title = 'Material Assistant';
      }

      createConversation.mutate(
        {
          title,
          context_type: contextType,
          competency_id: contextCompetencyId,
          skill_gap_id: contextSkillGapId,
          document_id: contextDocumentId,
          course_id: contextCourseId,
        },
        {
          onSuccess: (newConv) => {
            setActiveConversationId(newConv.id);
            isUserScrolledUpRef.current = false;
            setTimeout(() => inputRef.current?.focus(), 100);
          },
        }
      );
    }
  }, [contextCompetencyId, contextSkillGapId, contextDocumentId, contextCourseId, createConversation]);

  // Handle creating a new conversation
  const handleCreateNewChat = () => {
    if (createConversation.isPending) return;

    createConversation.mutate(
      {
        title: 'New Learning Session',
        context_type: 'GENERAL_LEARNING',
      },
      {
        onSuccess: (newConv) => {
          setActiveConversationId(newConv.id);
          isUserScrolledUpRef.current = false;
          setInputQuery('');
          setTimeout(() => inputRef.current?.focus(), 100);
          setToasts((prev) => [
            ...prev,
            { id: Date.now().toString(), title: 'Session Created', message: 'New conversation started.', type: 'info' },
          ]);
        },
        onError: () => {
          setToasts((prev) => [
            ...prev,
            { id: Date.now().toString(), title: 'Error', message: 'Failed to create conversation.', type: 'danger' },
          ]);
        },
      }
    );
  };

  // Handle deleting a conversation
  const handleDeleteConversation = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (deletingId || deleteConversation.isPending) return;

    setDeletingId(id);
    deleteConversation.mutate(id, {
      onSuccess: () => {
        setDeletingId(null);
        if (selectedConversationId === id) {
          const remaining = conversations.filter((c) => c.id !== id);
          setActiveConversationId(remaining.length > 0 ? remaining[0].id : null);
        }
        setToasts((prev) => [
          ...prev,
          { id: Date.now().toString(), title: 'Session Deleted', message: 'Conversation was removed.', type: 'success' },
        ]);
      },
      onError: () => {
        setDeletingId(null);
        setToasts((prev) => [
          ...prev,
          { id: Date.now().toString(), title: 'Error', message: 'Could not delete conversation. Please try again.', type: 'danger' },
        ]);
      },
    });
  };

  // Send message handler with error-resilience and debounce
  const handleSendMessage = (queryText?: string) => {
    const query = (queryText || inputQuery).trim();
    if (!query || isSubmitting || sendMessage.isPending) return;

    setIsSubmitting(true);
    lastPendingTextRef.current = query;
    isUserScrolledUpRef.current = false;

    // If no conversation currently exists, create one first, then dispatch
    if (!selectedConversationId) {
      createConversation.mutate(
        {
          title: query.slice(0, 40),
          context_type: 'GENERAL_LEARNING',
        },
        {
          onSuccess: (newConv) => {
            setActiveConversationId(newConv.id);
            setInputQuery('');
            dispatchMessage(newConv.id, query);
          },
          onError: () => {
            setIsSubmitting(false);
            setToasts((prev) => [
              ...prev,
              { id: Date.now().toString(), title: 'Error', message: 'Failed to initialize session.', type: 'danger' },
            ]);
          },
        }
      );
      return;
    }

    setInputQuery('');
    dispatchMessage(selectedConversationId, query);
  };

  const dispatchMessage = (convId: string, query: string) => {
    sendMessage.mutate(
      {
        content: query,
        language: selectedLanguage,
        competency_id: contextCompetencyId,
        skill_gap_id: contextSkillGapId,
      },
      {
        onSuccess: (resp: AssistantResponse) => {
          setIsSubmitting(false);
          lastPendingTextRef.current = '';
          scrollToBottom(true);

          if (resp.grounding_status === 'INSUFFICIENT_EVIDENCE') {
            setToasts((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                title: 'Insufficient Evidence',
                message: 'No matching learning material found. Safe grounded fallback returned.',
                type: 'warning',
              },
            ]);
          }
          setTimeout(() => inputRef.current?.focus(), 100);
        },
        onError: (err) => {
          setIsSubmitting(false);
          // Restore input query so user doesn't lose text
          setInputQuery(lastPendingTextRef.current);
          setToasts((prev) => [
            ...prev,
            {
              id: Date.now().toString(),
              title: 'Assistant Error',
              message: err.message || 'PRAGYA AI is temporarily unavailable.',
              type: 'danger',
            },
          ]);
          setTimeout(() => inputRef.current?.focus(), 100);
        },
      }
    );
  };

  const activeConvTitle = conversations.find((c) => c.id === selectedConversationId)?.title || 'Learning Session';

  return (
    <div className="flex flex-col h-[calc(100vh-5rem)] max-w-full overflow-hidden">
      <ToastContainer toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />

      {/* Top Header Bar */}
      <div className="pb-3 border-b border-white/10 flex items-center justify-between shrink-0">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              PRAGYA AI
            </h1>
            <Badge variant="primary" size="sm" className="bg-indigo-500/10 text-indigo-300 border-indigo-500/20">
              Competency-Aware
            </Badge>
            <Badge variant="outline" size="sm" className="font-mono text-[10px] text-slate-400 border-white/10">
              Grounded Assistant
            </Badge>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Source-grounded statistical capacity building assistant with verified MoSPI citations.
          </p>
        </div>

        {/* Language selector */}
        <div className="flex items-center gap-2">
          <Globe className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value as 'en' | 'hi' | 'te')}
            className="bg-[#0B0F19] border border-white/10 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-indigo-500/50"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="te">తెలుగు (Telugu)</option>
          </select>
        </div>
      </div>

      {/* 3-Panel Main Layout with Strong Visual Separation */}
      <div className="grid grid-cols-12 gap-4 flex-1 min-h-0 mt-3 overflow-hidden">
        {/* ========================================================================= */}
        {/* LEFT PANEL: Conversation Sessions (3 cols) */}
        {/* ========================================================================= */}
        <div className="col-span-12 lg:col-span-3 flex flex-col h-full bg-[#0A0E1A]/95 border border-white/10 rounded-2xl p-3.5 shadow-xl overflow-hidden backdrop-blur-md">
          {/* Header & New Conversation Button */}
          <div className="flex items-center justify-between mb-3 pb-2.5 border-b border-white/5 shrink-0">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-indigo-400" />
              <span className="text-xs font-semibold text-white tracking-wide uppercase">Sessions</span>
              <span className="px-1.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-slate-400">
                {conversations.length}
              </span>
            </div>
            <Button
              size="sm"
              onClick={handleCreateNewChat}
              disabled={createConversation.isPending}
              className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-2.5 py-1.5 h-7 rounded-lg flex items-center gap-1.5 font-medium transition-all shadow-sm"
            >
              {createConversation.isPending ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Plus className="w-3.5 h-3.5" />
              )}
              <span>New</span>
            </Button>
          </div>

          {/* Conversations Scrollable List */}
          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 scrollbar-thin scrollbar-thumb-slate-700/60">
            {isLoadingConversations && conversations.length === 0 ? (
              <div className="space-y-2 p-1">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-10 bg-white/5 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : conversations.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-center p-4">
                <MessageSquare className="w-8 h-8 text-slate-600 mb-2" />
                <p className="text-xs text-slate-400 font-medium">No sessions yet</p>
                <p className="text-[11px] text-slate-500 mt-1">Click &quot;New&quot; to begin learning.</p>
              </div>
            ) : (
              conversations.map((conv) => {
                const isActive = conv.id === selectedConversationId;
                const isThisDeleting = deletingId === conv.id;
                return (
                  <div
                    key={conv.id}
                    onClick={() => {
                      if (deletingId) return;
                      setActiveConversationId(conv.id);
                      isUserScrolledUpRef.current = false;
                      setTimeout(() => inputRef.current?.focus(), 100);
                    }}
                    className={`group relative flex items-center justify-between p-2.5 rounded-xl cursor-pointer transition-all text-xs border ${
                      isActive
                        ? 'bg-indigo-600/20 border-indigo-500/40 text-white font-medium shadow-md'
                        : 'bg-white/[0.02] border-white/5 text-slate-400 hover:bg-white/5 hover:border-white/10 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 overflow-hidden flex-1 mr-2">
                      <div className={`w-2 h-2 rounded-full shrink-0 ${isActive ? 'bg-indigo-400 shadow-[0_0_8px_#818CF8]' : 'bg-slate-600'}`} />
                      <span className="truncate">{conv.title || 'Learning Session'}</span>
                    </div>

                    <button
                      type="button"
                      onClick={(e) => handleDeleteConversation(conv.id, e)}
                      disabled={!!deletingId}
                      className={`p-1 rounded hover:bg-red-500/20 hover:text-red-400 text-slate-500 transition-all shrink-0 ${
                        isThisDeleting ? 'opacity-100 cursor-not-allowed' : 'opacity-0 group-hover:opacity-100'
                      }`}
                      title="Delete session"
                      aria-label="Delete session"
                    >
                      {isThisDeleting ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                      ) : (
                        <Trash2 className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* CENTER PANEL: Chat & Grounded Stream (6 cols) */}
        {/* ========================================================================= */}
        <div className="col-span-12 lg:col-span-6 flex flex-col h-full bg-[#0A0E1A]/95 border border-indigo-500/20 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-md">
          {/* Chat Panel Header */}
          <div className="px-4 py-3 border-b border-white/10 bg-[#070A13]/80 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
              <div className="truncate">
                <span className="text-xs font-semibold text-white truncate block">
                  {activeConvTitle}
                </span>
                <span className="text-[10px] font-mono text-cyan-400/80 block">
                  pgvector (cosine) • Grounded RAG
                </span>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-medium text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Active
              </span>
            </div>
          </div>

          {/* Messages Scroll Area */}
          <div
            ref={chatScrollRef}
            onScroll={handleChatScroll}
            className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-700/60"
          >
            {isLoadingMessages && messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full space-y-3">
                <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
                <span className="text-xs text-slate-400">Loading conversation history...</span>
              </div>
            ) : messages.length === 0 && !sendMessage.isPending ? (
              /* Empty state with suggested prompts */
              <div className="flex flex-col items-center justify-center h-full py-8 text-center space-y-4">
                <AIOrb size="md" />
                <div>
                  <h3 className="text-sm font-semibold text-white tracking-tight">
                    {conversations.length === 0 ? 'Start a new conversation' : 'How can PRAGYA help you learn today?'}
                  </h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 leading-relaxed">
                    {conversations.length === 0
                      ? 'Ask a question below or pick a suggested topic to begin learning with grounded citations.'
                      : 'Answers are strictly grounded in official MoSPI manuals and guidelines with verifiable page citations.'}
                  </p>
                </div>

                {/* Suggested Prompts Grid */}
                <div className="grid grid-cols-2 gap-2 w-full max-w-md pt-3">
                  {SUGGESTED_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handleSendMessage(prompt)}
                      disabled={sendMessage.isPending || isSubmitting}
                      className="p-2.5 text-left rounded-xl bg-white/[0.03] hover:bg-indigo-600/15 border border-white/5 hover:border-indigo-500/30 text-[11px] text-slate-300 hover:text-white transition-all flex items-center justify-between group shadow-sm disabled:opacity-50"
                    >
                      <span>{prompt}</span>
                      <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 transition-colors" />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              /* Render conversation message list */
              <div key={selectedConversationId} className="space-y-4">
                {messages.map((msg) => {
                  const isUser = msg.role === 'USER';
                  const meta = msg.metadata || {};
                  const citations = msg.sources || [];
                  const groundingStatus = meta.grounding_status as string;

                  return (
                    <div
                      key={msg.id}
                      className={`flex flex-col space-y-1.5 ${isUser ? 'items-end' : 'items-start'}`}
                    >
                      <div className="flex items-center gap-1.5 text-[10px] text-slate-500 px-1">
                        {isUser ? (
                          <span>You</span>
                        ) : (
                          <span className="flex items-center gap-1 text-indigo-400 font-medium">
                            <Sparkles className="w-3 h-3" /> PRAGYA AI
                          </span>
                        )}
                      </div>

                      <div
                        className={`rounded-2xl p-4 text-xs leading-relaxed shadow-md ${
                          isUser
                            ? 'bg-indigo-600/30 border border-indigo-500/30 text-slate-100 max-w-[85%] rounded-tr-sm'
                            : 'bg-white/[0.04] border border-white/10 text-slate-200 max-w-[92%] rounded-tl-sm space-y-3'
                        }`}
                      >
                        {/* Grounding Badge for Assistant */}
                        {!isUser && groundingStatus && (
                          <div className="mb-2">
                            {groundingStatus === 'GROUNDED' || groundingStatus === 'PARTIALLY_GROUNDED' ? (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[10px] font-medium text-emerald-400">
                                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                                Grounded in uploaded learning material
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-[10px] font-medium text-amber-400">
                                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                                Insufficient source evidence
                              </span>
                            )}
                          </div>
                        )}

                        {/* Main Message Content */}
                        <div className="whitespace-pre-wrap leading-relaxed text-slate-100 font-normal">
                          {msg.content}
                        </div>

                        {/* Structured Verified Citations */}
                        {!isUser && citations && citations.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                            <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                              <BookOpen className="w-3 h-3 text-cyan-400" />
                              Verified Sources ({citations.length})
                            </div>
                            <div className="space-y-1.5">
                              {citations.map((cit, idx) => (
                                <div
                                  key={cit.chunk_id || idx}
                                  className="flex items-center justify-between p-2 rounded-lg bg-black/40 border border-white/5 text-[11px]"
                                >
                                  <div className="flex items-center gap-2 truncate mr-2">
                                    <span className="text-cyan-400 font-mono font-semibold shrink-0">
                                      [{idx + 1}]
                                    </span>
                                    <span className="text-slate-300 font-medium truncate">
                                      {cit.citation_label || 'Official Manual'}
                                    </span>
                                  </div>
                                  {cit.similarity_score !== undefined && (
                                    <span className="text-[10px] font-mono text-cyan-300/80 bg-cyan-950/40 px-1.5 py-0.5 rounded border border-cyan-500/20 shrink-0">
                                      {Math.round(cit.similarity_score * 100)}% match
                                    </span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Pending assistant generation indicator */}
            {sendMessage.isPending && (
              <div className="flex flex-col items-start space-y-2 animate-pulse">
                <span className="text-[10px] text-indigo-400 font-medium flex items-center gap-1.5">
                  <Loader2 className="w-3 h-3 animate-spin text-indigo-400" /> PRAGYA AI is formulating answer...
                </span>
                <div className="bg-white/[0.04] border border-white/10 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-300 max-w-[85%] flex items-center gap-3 shadow-md">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                  <span>Searching pgvector evidence and verifying citations...</span>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input Shell */}
          <div className="p-3.5 border-t border-white/10 bg-[#070A13]/90 shrink-0">
            <div className="relative flex items-center">
              <textarea
                ref={inputRef}
                rows={1}
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={sendMessage.isPending || isSubmitting}
                placeholder="Ask about sampling, index numbers, formulas, or concepts..."
                className="w-full bg-[#0B0F19] border border-white/10 rounded-xl pl-4 pr-12 py-3 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500/50 resize-none disabled:opacity-60 leading-normal"
              />
              <Button
                size="sm"
                onClick={() => handleSendMessage()}
                disabled={sendMessage.isPending || isSubmitting || !inputQuery.trim()}
                className="absolute right-1.5 bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded-lg transition-all disabled:opacity-40"
              >
                {sendMessage.isPending || isSubmitting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Send className="w-3.5 h-3.5" />
                )}
              </Button>
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1.5 px-1">
              <span>Enter to send • Shift+Enter for newline</span>
              <span>pgvector cosine similarity</span>
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* RIGHT PANEL: Learning Context (3 cols) */}
        {/* ========================================================================= */}
        <div className="col-span-12 lg:col-span-3 flex flex-col h-full bg-[#0A0E1A]/95 border border-white/10 rounded-2xl p-4 shadow-xl overflow-y-auto space-y-4 backdrop-blur-md">
          {/* Header */}
          <div className="flex items-center gap-2 pb-2.5 border-b border-white/10">
            <Target className="w-4 h-4 text-indigo-400" />
            <div>
              <h3 className="text-xs font-semibold text-white uppercase tracking-wider">
                Learning Context
              </h3>
              <p className="text-[10px] text-slate-500">Personalized Pedagogical Alignment</p>
            </div>
          </div>

          {/* Hydration-safe Card 1: Officer Cadre & Designation */}
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-1.5">
            <div className="text-[10px] text-slate-400 font-medium uppercase flex items-center justify-between">
              <span>Officer Profile</span>
              <span className="text-[9px] text-indigo-400 font-mono">CADRE</span>
            </div>

            {!isMounted || isLoadingEmployee ? (
              <div className="space-y-2 py-1 animate-pulse">
                <div className="h-4 w-32 bg-white/10 rounded" />
                <div className="h-3 w-48 bg-white/5 rounded" />
              </div>
            ) : (
              <div>
                <div className="text-xs font-semibold text-slate-200">
                  {currentEmployee?.designation || 'Statistical Officer'}
                </div>
                <div className="text-[10px] text-slate-400 truncate mt-0.5">
                  {currentEmployee?.department_name || 'Ministry of Statistics & Programme Implementation'}
                </div>
              </div>
            )}
          </div>

          {/* Hydration-safe Card 2: Competency & Skill Gap Details */}
          <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-500/20 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-indigo-300 font-medium uppercase tracking-wide">
                Target Competency
              </span>
              {!isMounted || isLoadingSkillGaps ? (
                <div className="h-4 w-16 bg-white/10 rounded animate-pulse" />
              ) : prioritizedGap ? (
                <Badge
                  variant={
                    prioritizedGap.priority_level === 'CRITICAL' || prioritizedGap.priority_level === 'HIGH'
                      ? 'warning'
                      : 'outline'
                  }
                  size="sm"
                  className="text-[9px]"
                >
                  {prioritizedGap.priority_level} PRIORITY
                </Badge>
              ) : null}
            </div>

            {!isMounted || isLoadingSkillGaps ? (
              <div className="space-y-2 animate-pulse">
                <div className="h-4 w-40 bg-white/10 rounded" />
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <div className="h-10 bg-white/5 rounded" />
                  <div className="h-10 bg-white/5 rounded" />
                </div>
              </div>
            ) : (
              <>
                <div className="text-xs font-bold text-white leading-tight">
                  {prioritizedGap?.competency_name || 'Survey Sampling & Estimation'}
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1 text-[11px]">
                  <div className="bg-black/40 p-2 rounded-lg border border-white/5">
                    <div className="text-[9px] text-slate-500 uppercase">CURRENT</div>
                    <div className="font-semibold text-slate-200 mt-0.5">
                      Level {prioritizedGap?.current_level_number ?? 2}
                    </div>
                  </div>
                  <div className="bg-black/40 p-2 rounded-lg border border-white/5">
                    <div className="text-[9px] text-slate-500 uppercase">REQUIRED</div>
                    <div className="font-semibold text-cyan-400 mt-0.5">
                      Level {prioritizedGap?.required_level_number ?? 4}
                    </div>
                  </div>
                </div>

                {prioritizedGap?.gap_score !== undefined && (
                  <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-white/5 text-slate-300">
                    <span>Skill Gap Score:</span>
                    <span className="font-mono text-amber-400 font-semibold">
                      {prioritizedGap.gap_score} pts
                    </span>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Hydration-safe Card 3: Adaptive Explanation Level */}
          <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-1.5">
            <div className="text-[10px] text-slate-400 uppercase font-medium flex items-center gap-1.5">
              <Award className="w-3.5 h-3.5 text-cyan-400" />
              Explanation Adaptation
            </div>
            {!isMounted || isLoadingSkillGaps ? (
              <div className="h-4 w-28 bg-white/10 rounded animate-pulse" />
            ) : (
              <div className="text-xs font-semibold text-cyan-300">
                {prioritizedGap?.current_level_number && prioritizedGap.current_level_number >= 4
                  ? 'ADVANCED MODE'
                  : prioritizedGap?.current_level_number === 3
                  ? 'WORKING LEVEL'
                  : 'FOUNDATION LEVEL'}
              </div>
            )}
            <p className="text-[10px] text-slate-400 leading-relaxed">
              Explanations are tuned to your assessed level with definitions, analogies, and verified manual examples.
            </p>
          </div>

          {/* Card 4: Grounding & Security Safeguards */}
          <div className="p-3 rounded-xl bg-emerald-950/10 border border-emerald-500/20 space-y-1 text-[10px] text-slate-400">
            <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <Shield className="w-3.5 h-3.5 text-emerald-400" /> Grounding Protection Active
            </div>
            <div className="leading-normal">
              Uploaded materials are treated as untrusted reference data only. Model-invented citations are strictly stripped.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EmployeeAssistantPage() {
  return (
    <AppShell role="EMPLOYEE" pageTitle="AI Assistant">
      <Suspense fallback={<div className="p-6 text-xs text-slate-400">Loading AI Assistant...</div>}>
        <AssistantContent />
      </Suspense>
    </AppShell>
  );
}
