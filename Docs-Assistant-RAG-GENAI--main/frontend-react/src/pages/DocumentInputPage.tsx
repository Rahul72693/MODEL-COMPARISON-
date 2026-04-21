import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, GitCompareArrows } from 'lucide-react';
import { APIClient } from '../services/api';
import type { UploadResponse } from '../types';

const DocumentInputPage = () => {
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
    const [uploadedFile, setUploadedFile] = useState<string>('');
    const [errorMessage, setErrorMessage] = useState('');

    const onDrop = useCallback(async (acceptedFiles: File[]) => {
        if (acceptedFiles.length === 0) return;

        const file = acceptedFiles[0];
        setUploading(true);
        setUploadStatus('idle');
        setErrorMessage('');

        try {
            const response: UploadResponse = await APIClient.uploadDocument(file);
            setUploadedFile(response.file_name);
            setUploadStatus('success');
        } catch (error: any) {
            setUploadStatus('error');
            setErrorMessage(error.response?.data?.detail || 'Upload failed. Please try again.');
        } finally {
            setUploading(false);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'image/png': ['.png'],
            'image/jpeg': ['.jpg', '.jpeg'],
        },
        multiple: false,
    });

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center space-y-4"
            >
                <h2 className="text-4xl font-bold gradient-text">Upload Your Document</h2>
                <p className="text-gray-400 text-lg">
                    Upload PDF, DOCX, or images to begin comparing model responses
                </p>
            </motion.div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                {...getRootProps()}
                className={`glass-card p-12 text-center cursor-pointer transition-all duration-300
          ${isDragActive ? 'border-primary scale-105 shadow-glow' : 'hover:border-white/20'}
          ${uploading ? 'pointer-events-none opacity-50' : ''}`}
            >
                <input {...getInputProps()} />

                <div className="flex flex-col items-center gap-6">
                    {uploading ? (
                        <>
                            <Loader2 className="w-16 h-16 text-primary animate-spin" />
                            <p className="text-xl text-white font-medium">Processing document...</p>
                        </>
                    ) : uploadStatus === 'success' ? (
                        <>
                            <CheckCircle className="w-16 h-16 text-green-500" />
                            <div>
                                <p className="text-xl text-white font-medium mb-2">Upload Successful!</p>
                                <p className="text-gray-400">{uploadedFile}</p>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setUploadStatus('idle');
                                        setUploadedFile('');
                                    }}
                                    className="mt-4 btn-secondary"
                                >
                                    Upload Another Document
                                </button>
                            </div>
                        </>
                    ) : uploadStatus === 'error' ? (
                        <>
                            <AlertCircle className="w-16 h-16 text-red-500" />
                            <div>
                                <p className="text-xl text-white font-medium mb-2">Upload Failed</p>
                                <p className="text-gray-400">{errorMessage}</p>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setUploadStatus('idle');
                                    }}
                                    className="mt-4 btn-secondary"
                                >
                                    Try Again
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="w-20 h-20 rounded-full bg-gradient-primary flex items-center justify-center">
                                <Upload className="w-10 h-10 text-white" />
                            </div>
                            <div>
                                <p className="text-xl text-white font-medium mb-2">
                                    {isDragActive ? 'Drop your file here' : 'Drop files or click to upload'}
                                </p>
                                <p className="text-gray-400">
                                    Supports PDF, DOCX, PNG, and JPEG files
                                </p>
                            </div>
                        </>
                    )}
                </div>
            </motion.div>

            {/* Info Cards */}
            <div className="grid md:grid-cols-3 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="glass-card p-6"
                >
                    <FileText className="w-8 h-8 text-accent-blue mb-3" />
                    <h3 className="font-semibold text-white mb-2">Supported Formats</h3>
                    <p className="text-sm text-gray-400">
                        PDF, DOCX, PNG, and JPEG with OCR support
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="glass-card p-6"
                >
                    <CheckCircle className="w-8 h-8 text-accent-purple mb-3" />
                    <h3 className="font-semibold text-white mb-2">RAG Pipeline</h3>
                    <p className="text-sm text-gray-400">
                        Automatic extraction, chunking, and vectorization
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card p-6"
                >
                    <GitCompareArrows className="w-8 h-8 text-accent-pink mb-3" />
                    <h3 className="font-semibold text-white mb-2">Dual Models</h3>
                    <p className="text-sm text-gray-400">
                        Compare Gemini and Groq responses side-by-side
                    </p>
                </motion.div>
            </div>
        </div>
    );
};

export default DocumentInputPage;
