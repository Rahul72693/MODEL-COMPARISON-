import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
} from 'recharts';
import { Loader2, TrendingUp, DollarSign, Zap } from 'lucide-react';
import { APIClient } from '../services/api';
import type { MetricsSummary } from '../types';

interface Props {
    sessionId: string;
}

const COLORS = ['#667eea', '#764ba2', '#4F46E5', '#7C3AED'];

const MetricsPage = ({ sessionId }: Props) => {
    const [loading, setLoading] = useState(true);
    const [metrics, setMetrics] = useState<MetricsSummary | null>(null);

    useEffect(() => {
        loadMetrics();
    }, [sessionId]);

    const loadMetrics = async () => {
        try {
            const data = await APIClient.getMetricsSummary(sessionId);
            setMetrics(data);
        } catch (error) {
            console.error('Failed to load metrics:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
            </div>
        );
    }

    if (!metrics || metrics.total_queries === 0) {
        return (
            <div className="glass-card p-12 text-center">
                <TrendingUp className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">No Data Yet</h3>
                <p className="text-gray-400">
                    Run some comparisons to see analytics and metrics
                </p>
            </div>
        );
    }

    const performanceData = [
        {
            name: 'Gemini',
            'Avg Response Time (s)': metrics.gemini.avg_response_time.toFixed(2),
        },
        {
            name: 'Groq',
            'Avg Response Time (s)': metrics.groq.avg_response_time.toFixed(2),
        },
    ];

    const costData = [
        { name: 'Gemini', value: metrics.gemini.total_cost },
        { name: 'Groq', value: metrics.groq.total_cost },
    ];

    const tokenData = [
        { name: 'Gemini', tokens: metrics.gemini.total_tokens },
        { name: 'Groq', tokens: metrics.groq.total_tokens },
    ];

    return (
        <div className="space-y-8">
            {/* Overview Cards */}
            <div className="grid md:grid-cols-4 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="glass-card p-6"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-accent-blue" />
                        <span className="text-sm text-gray-400">Total Queries</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{metrics.total_queries}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="glass-card p-6"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-5 h-5 text-accent-purple" />
                        <span className="text-sm text-gray-400">Gemini Queries</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{metrics.gemini.query_count}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-6"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-5 h-5 text-accent-pink" />
                        <span className="text-sm text-gray-400">Groq Queries</span>
                    </div>
                    <p className="text-3xl font-bold text-white">{metrics.groq.query_count}</p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card p-6"
                >
                    <div className="flex items-center gap-2 mb-2">
                        <DollarSign className="w-5 h-5 text-green-500" />
                        <span className="text-sm text-gray-400">Total Cost</span>
                    </div>
                    <p className="text-3xl font-bold text-white">
                        ${(metrics.gemini.total_cost + metrics.groq.total_cost).toFixed(4)}
                    </p>
                </motion.div>
            </div>

            {/* Charts */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Response Time Comparison */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card p-6"
                >
                    <h3 className="text-lg font-bold text-white mb-4">
                        Average Response Time
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={performanceData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="#9CA3AF" />
                            <YAxis stroke="#9CA3AF" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1E293B',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                }}
                            />
                            <Bar
                                dataKey="Avg Response Time (s)"
                                fill="url(#colorGradient)"
                                radius={[8, 8, 0, 0]}
                            />
                            <defs>
                                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#667eea" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#764ba2" stopOpacity={0.8} />
                                </linearGradient>
                            </defs>
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Token Usage */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="glass-card p-6"
                >
                    <h3 className="text-lg font-bold text-white mb-4">Token Usage</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={tokenData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="name" stroke="#9CA3AF" />
                            <YAxis stroke="#9CA3AF" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1E293B',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                }}
                            />
                            <Bar dataKey="tokens" fill="#4F46E5" radius={[8, 8, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Cost Distribution */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="glass-card p-6"
                >
                    <h3 className="text-lg font-bold text-white mb-4">Cost Distribution</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={costData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, value }) =>
                                    `${name}: $${value.toFixed(5)}`
                                }
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {costData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1E293B',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px',
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </motion.div>

                {/* Stats Grid */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.7 }}
                    className="glass-card p-6 space-y-4"
                >
                    <h3 className="text-lg font-bold text-white mb-4">Detailed Stats</h3>

                    <div className="space-y-3">
                        <div className="flex justify-between items-center pb-2 border-b border-white/10">
                            <span className="text-gray-400">Gemini Avg Time</span>
                            <span className="text-white font-semibold">
                                {metrics.gemini.avg_response_time.toFixed(3)}s
                            </span>
                        </div>

                        <div className="flex justify-between items-center pb-2 border-b border-white/10">
                            <span className="text-gray-400">Groq Avg Time</span>
                            <span className="text-white font-semibold">
                                {metrics.groq.avg_response_time.toFixed(3)}s
                            </span>
                        </div>

                        <div className="flex justify-between items-center pb-2 border-b border-white/10">
                            <span className="text-gray-400">Gemini Total Cost</span>
                            <span className="text-white font-semibold">
                                ${metrics.gemini.total_cost.toFixed(5)}
                            </span>
                        </div>

                        <div className="flex justify-between items-center pb-2 border-b border-white/10">
                            <span className="text-gray-400">Groq Total Cost</span>
                            <span className="text-white font-semibold">
                                ${metrics.groq.total_cost.toFixed(5)}
                            </span>
                        </div>

                        <div className="flex justify-between items-center">
                            <span className="text-gray-400">Speed Winner</span>
                            <span className={`font-semibold ${metrics.gemini.avg_response_time < metrics.groq.avg_response_time
                                    ? 'text-blue-400'
                                    : 'text-purple-400'
                                }`}>
                                {metrics.gemini.avg_response_time < metrics.groq.avg_response_time
                                    ? 'Gemini'
                                    : 'Groq'}
                            </span>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default MetricsPage;
