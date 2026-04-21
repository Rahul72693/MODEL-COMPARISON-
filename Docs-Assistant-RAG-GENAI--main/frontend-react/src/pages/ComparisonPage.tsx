import { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, Zap, DollarSign, Clock, Award } from 'lucide-react';
import { APIClient } from '../services/api';
import type { ComparisonResponse } from '../types';

interface Props {
    sessionId: string;
}

const ComparisonPage = ({ sessionId }: Props) => {
    const [query, setQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<ComparisonResponse | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        setLoading(true);
        try {
            const response = await APIClient.compareModels(sessionId, query);
            setResult(response);
        } catch (error) {
            console.error('Comparison failed:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            {/* Query Input */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card p-6"
            >
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Enter your question
                        </label>
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="What are the risk factors for NAFLD?"
                            className="input-field w-full h-24 resize-none custom-scrollbar"
                            disabled={loading}
                        />
                    </div>
                    <button
                        type="submit"
                        disabled={!query.trim() || loading}
                        className="btn-primary w-full flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                Comparing Models...
                            </>
                        ) : (
                            <>
                                <Send className="w-5 h-5" />
                                Compare Models
                            </>
                        )}
                    </button>
                </form>
            </motion.div>

            {/* Results */}
            {result && (
                <>
                    {/* Comparison Overview */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="grid md:grid-cols-4 gap-4"
                    >
                        <div className="glass-card p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Award className="w-5 h-5 text-accent-blue" />
                                <span className="text-sm text-gray-400">Agreement</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                                {(result.comparison.agreement_score * 100).toFixed(0)}%
                            </p>
                        </div>

                        <div className="glass-card p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Clock className="w-5 h-5 text-accent-purple" />
                                <span className="text-sm text-gray-400">Speed Winner</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                                {result.comparison.gemini_faster ? 'Gemini' : 'Groq'}
                            </p>
                            <p className="text-xs text-gray-400">
                                {result.comparison.speed_ratio.toFixed(2)}x
                            </p>
                        </div>

                        <div className="glass-card p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <DollarSign className="w-5 h-5 text-accent-pink" />
                                <span className="text-sm text-gray-400">Cost Ratio</span>
                            </div>
                            <p className="text-2xl font-bold text-white">
                                {result.comparison.cost_ratio.toFixed(2)}x
                            </p>
                        </div>

                        <div className="glass-card p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Zap className="w-5 h-5 text-green-500" />
                                <span className="text-sm text-gray-400">Quality</span>
                            </div>
                            <p className="text-xl font-bold text-white">
                                G: {(result.comparison.gemini_quality_avg * 100).toFixed(0)}%
                            </p>
                            <p className="text-xl font-bold text-white">
                                R: {(result.comparison.groq_quality_avg * 100).toFixed(0)}%
                            </p>
                        </div>
                    </motion.div>

                    {/* Side-by-Side Comparison */}
                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Gemini Response */}
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass-card p-6 space-y-4"
                        >
                            <div className="flex items-center justify-between">
                                <h3 className="text-xl font-bold text-white">Gemini 1.5 Flash</h3>
                                <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium">
                                    Google
                                </span>
                            </div>

                            <div className="prose prose-invert max-w-none">
                                <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                                    {result.gemini.answer}
                                </p>
                            </div>

                            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/10">
                                <div>
                                    <p className="text-xs text-gray-400">Time</p>
                                    <p className="text-sm font-semibold text-white">
                                        {result.gemini.response_time.toFixed(2)}s
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400">Tokens</p>
                                    <p className="text-sm font-semibold text-white">
                                        {result.gemini.tokens}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400">Cost</p>
                                    <p className="text-sm font-semibold text-white">
                                        ${result.gemini.cost.toFixed(6)}
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-xs font-medium text-gray-400">Quality Metrics</p>
                                <div className="space-y-1">
                                    <QualityBar
                                        label="Semantic Similarity"
                                        value={result.gemini.quality.semantic_similarity}
                                    />
                                    <QualityBar
                                        label="Context Relevance"
                                        value={result.gemini.quality.context_relevance}
                                    />
                                    <QualityBar
                                        label="Citation Quality"
                                        value={result.gemini.quality.citation_quality}
                                    />
                                    <QualityBar
                                        label="Completeness"
                                        value={result.gemini.quality.completeness_score}
                                    />
                                </div>
                            </div>
                        </motion.div>

                        {/* Groq Response */}
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="glass-card p-6 space-y-4"
                        >
                            <div className="flex items-center justify-between">
                                <h3 className="text-xl font-bold text-white">Llama 3 70B</h3>
                                <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 text-sm font-medium">
                                    Groq
                                </span>
                            </div>

                            <div className="prose prose-invert max-w-none">
                                <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                                    {result.groq.answer}
                                </p>
                            </div>

                            <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/10">
                                <div>
                                    <p className="text-xs text-gray-400">Time</p>
                                    <p className="text-sm font-semibold text-white">
                                        {result.groq.response_time.toFixed(2)}s
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400">Tokens</p>
                                    <p className="text-sm font-semibold text-white">
                                        {result.groq.tokens}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400">Cost</p>
                                    <p className="text-sm font-semibold text-white">
                                        ${result.groq.cost.toFixed(6)}
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <p className="text-xs font-medium text-gray-400">Quality Metrics</p>
                                <div className="space-y-1">
                                    <QualityBar
                                        label="Semantic Similarity"
                                        value={result.groq.quality.semantic_similarity}
                                    />
                                    <QualityBar
                                        label="Context Relevance"
                                        value={result.groq.quality.context_relevance}
                                    />
                                    <QualityBar
                                        label="Citation Quality"
                                        value={result.groq.quality.citation_quality}
                                    />
                                    <QualityBar
                                        label="Completeness"
                                        value={result.groq.quality.completeness_score}
                                    />
                                </div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Sources */}
                    {result.sources.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="glass-card p-6"
                        >
                            <h3 className="text-lg font-bold text-white mb-4">
                                Retrieved Context ({result.sources.length} chunks)
                            </h3>
                            <div className="space-y-3">
                                {result.sources.map((source, idx) => (
                                    <div
                                        key={idx}
                                        className="p-3 rounded-lg bg-white/5 border border-white/10"
                                    >
                                        <div className="flex items-start gap-3">
                                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 text-primary text-sm font-bold flex items-center justify-center">
                                                {idx + 1}
                                            </span>
                                            <div className="flex-1">
                                                <p className="text-sm text-gray-300 mb-2">{source.text}</p>
                                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                                    <span>Score: {source.score.toFixed(3)}</span>
                                                    {source.meta.file_name && (
                                                        <span>File: {source.meta.file_name}</span>
                                                    )}
                                                    {source.meta.page_number && (
                                                        <span>Page: {source.meta.page_number}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </>
            )}
        </div>
    );
};

// Quality Progress Bar Component
const QualityBar = ({ label, value }: { label: string; value: number }) => {
    const percentage = Math.round(value * 100);
    const color =
        percentage >= 75
            ? 'bg-green-500'
            : percentage >= 50
                ? 'bg-yellow-500'
                : 'bg-red-500';

    return (
        <div>
            <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">{label}</span>
                <span className="text-white font-medium">{percentage}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className={`h-full ${color} rounded-full`}
                />
            </div>
        </div>
    );
};

export default ComparisonPage;
