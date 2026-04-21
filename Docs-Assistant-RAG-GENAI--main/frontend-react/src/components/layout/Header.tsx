import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const Header = () => {
    return (
        <motion.header
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="glass-card border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl"
        >
            <div className="container mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-primary flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold gradient-text">
                                Model Comparison System
                            </h1>
                            <p className="text-sm text-gray-400">
                                Gemini vs Groq • RAG-based Evaluation
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            <span className="text-sm text-gray-300">Backend Connected</span>
                        </div>
                    </div>
                </div>
            </div>
        </motion.header>
    );
};

export default Header;
