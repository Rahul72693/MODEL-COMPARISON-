import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileText, GitCompareArrows, BarChart3 } from 'lucide-react';

const tabs = [
    { path: '/document', label: 'Document Input', icon: FileText },
    { path: '/comparison', label: 'Model Comparison', icon: GitCompareArrows },
    { path: '/metrics', label: 'Metrics & Analytics', icon: BarChart3 },
];

const TabNavigation = () => {
    return (
        <nav className="glass-card p-2 inline-flex gap-2 rounded-xl">
            {tabs.map((tab) => (
                <NavLink
                    key={tab.path}
                    to={tab.path}
                    className={({ isActive }) =>
                        `relative px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center gap-2
            ${isActive
                            ? 'text-white'
                            : 'text-gray-400 hover:text-white hover:bg-white/5'
                        }`
                    }
                >
                    {({ isActive }) => (
                        <>
                            {isActive && (
                                <motion.div
                                    layoutId="activeTab"
                                    className="absolute inset-0 bg-gradient-primary rounded-lg"
                                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                                />
                            )}
                            <tab.icon className="w-5 h-5 relative z-10" />
                            <span className="relative z-10">{tab.label}</span>
                        </>
                    )}
                </NavLink>
            ))}
        </nav>
    );
};

export default TabNavigation;
