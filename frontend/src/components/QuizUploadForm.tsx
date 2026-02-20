import React, { useState } from 'react';

interface QuizUploadFormProps {
  classId: number;
  onQuizUploaded?: () => void;
}

const QuizUploadForm: React.FC<QuizUploadFormProps> = ({ classId, onQuizUploaded }) => {
  const [quizTitle, setQuizTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [resultsFile, setResultsFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  // No parsing needed, just upload files

  // No file parsing, just set files

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);
    try {
      const formData = new FormData();

      formData.append('class_id', String(classId));
      formData.append('quiz_title', quizTitle);
      if (file) formData.append('file', file);
      if (resultsFile) formData.append('results_file', resultsFile);

      const response = await fetch('http://localhost:8000/quizzes/', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to upload quiz');
      }
      setMessage('Quiz uploaded successfully!');
      setQuizTitle('');
      setFile(null);
      if (onQuizUploaded) onQuizUploaded();
    } catch (err: any) {
      setMessage(err.message || 'Error uploading quiz');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 mt-4">
      <div>
        <label className="block text-sm font-medium mb-1">Quiz Title</label>
        <input
          type="text"
          className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-400"
          value={quizTitle}
          onChange={e => setQuizTitle(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Quiz File (.pdf)</label>
        <input
          type="file"
          accept="application/pdf"
          className="w-full"
          onChange={e => setFile(e.target.files?.[0] || null)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Quiz Results File (.pdf or .txt)</label>
        <input
          type="file"
          accept="application/pdf,text/plain"
          className="w-full"
          onChange={e => setResultsFile(e.target.files?.[0] || null)}
        />
      </div>
      <button
        type="submit"
        className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition"
        disabled={loading}
      >
        {loading ? 'Uploading...' : 'Upload Quiz'}
      </button>
      {message && <div className="text-green-600 mt-2">{message}</div>}
    </form>
  );
};

export default QuizUploadForm;
function setQuizContentFile(arg0: null) {
    throw new Error('Function not implemented.');
}

