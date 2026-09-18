import { useState, useRef, useEffect } from 'react';
import api from '@/lib/api';
import type { AIQueryResponse } from '@/types';
import { Bot, Send, Sparkles, Loader2, Mountain, ArrowRight, MessageSquare } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  data?: AIQueryResponse;
  timestamp: Date;
}

const SUGGESTED_PROMPTS = [
  'Which mines require immediate attention?',
  'Why is Rajmahal Mine high risk?',
  'Show recurring violations in the last 6 months',
  'Which contractors have poor safety performance?',
  'What compliance actions are due this week?',
  'Summarize the current governance situation',
];

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const sendQuery = async (query: string) => {
    if (!query.trim()) return;
    const userMsg: ChatMessage = { role: 'user', content: query.trim(), timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/ai/query', { query: query.trim() });
      const data: AIQueryResponse = res.data;
      setMessages(prev => [...prev, {
        role: 'assistant', content: data.answer, data, timestamp: new Date()
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I\'m unable to process your query at the moment. The AI service may be temporarily unavailable. Please try again shortly.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7rem)] animate-fade-in">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="w-6 h-6 text-amber-brand" /> KhanijSetu Intelligence
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Ask questions about mining governance, compliance and operational risk
        </p>
      </div>

      {/* Chat Area */}
      <div className="flex-1 bg-white rounded-xl border border-gray-100 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="w-16 h-16 bg-amber-brand/10 rounded-2xl flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-amber-brand" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-1">KhanijSetu AI Assistant</h3>
              <p className="text-sm text-gray-500 max-w-md mb-6">
                I can help you analyze mining governance data, identify risks, and provide compliance insights.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => sendQuery(prompt)}
                    className="text-left text-xs p-3 bg-gray-50 border border-gray-200 rounded-lg hover:border-amber-brand/40 hover:bg-amber-brand/5 transition-all group"
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare className="w-3.5 h-3.5 text-gray-400 group-hover:text-amber-brand shrink-0 mt-0.5" />
                      <span className="text-gray-600 group-hover:text-gray-800">{prompt}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 bg-amber-brand/10 rounded-lg flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-amber-brand" />
                </div>
              )}
              <div className={`max-w-[75%] ${msg.role === 'user' ? 'bg-charcoal text-white rounded-2xl rounded-tr-md px-4 py-3' : ''}`}>
                {msg.role === 'user' ? (
                  <p className="text-sm">{msg.content}</p>
                ) : (
                  <div className="space-y-3">
                    <div className="chat-message text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {msg.content.split('\n').map((line, j) => (
                        <p key={j} className={line.startsWith('•') || line.startsWith('**') ? 'mb-1' : 'mb-2'}>
                          {line.split(/(\*\*[^*]+\*\*)/).map((part, k) =>
                            part.startsWith('**') && part.endsWith('**') ? <strong key={k}>{part.slice(2, -2)}</strong> : part
                          )}
                        </p>
                      ))}
                    </div>

                    {/* Entity cards */}
                    {msg.data?.entities && msg.data.entities.length > 0 && (
                      <div className="flex gap-2 flex-wrap">
                        {msg.data.entities.map((entity, j) => (
                          <div key={j} className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                            <p className="font-semibold text-gray-700">{entity.name}</p>
                            {'risk_score' in entity ? <p className="text-gray-400">Risk: {String(entity.risk_score)}</p> : null}
                            {'safety_score' in entity ? <p className="text-gray-400">Safety: {String(entity.safety_score)}</p> : null}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Recommendations */}
                    {msg.data?.recommendations && msg.data.recommendations.length > 0 && (
                      <div className="bg-amber-50/50 border border-amber-200 rounded-lg p-3">
                        <p className="text-[10px] font-semibold text-amber-700 uppercase tracking-wider mb-1.5">Recommended Actions</p>
                        {msg.data.recommendations.map((rec, j) => (
                          <div key={j} className="flex items-start gap-1.5 mb-1">
                            <ArrowRight className="w-3 h-3 text-amber-600 shrink-0 mt-0.5" />
                            <p className="text-xs text-amber-800">{rec}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.data?.confidence && (
                      <p className="text-[10px] text-gray-400">Confidence: {(msg.data.confidence * 100).toFixed(0)}%</p>
                    )}
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 bg-charcoal rounded-lg flex items-center justify-center shrink-0">
                  <Mountain className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-amber-brand/10 rounded-lg flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4 text-amber-brand" />
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-3">
          <form onSubmit={(e) => { e.preventDefault(); sendQuery(input); }} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about mining governance, compliance, or risk..."
              className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm outline-none focus:border-amber-brand/50 focus:ring-1 focus:ring-amber-brand/20"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-amber-brand hover:bg-amber-hover text-white p-2.5 rounded-lg transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
