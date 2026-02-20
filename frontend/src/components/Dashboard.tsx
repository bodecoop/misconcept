// Helper to extract top 3 concepts from either structured or plain text analysis
function extractTopConceptsStructured(analysis: any) {
  // If structured, use as before
  if (analysis && Array.isArray(analysis.top_concepts)) {
    return analysis.top_concepts;
  }
  // If plain text, parse flexibly
  if (analysis && typeof analysis.text === 'string') {
    const text = analysis.text;
    // Split into blocks for each concept (numbered, with or without markdown)
    const blocks = text
      .split(/\n(?=\d+\.|\*\*\d+\.|\d+\.\s*\*\*)/g)
      .map((b: string) => b.trim())
      .filter((b: string) => b.length > 0 && /(Concept|Concept Name)/i.test(b));

    // Canonical field labels and their regex patterns
    const fieldPatterns = [
      { key: 'concept', patterns: [/Concept Name:?/i, /Concept:?/i] },
      { key: 'mastery', patterns: [/Estimated Mastery Score:?/i, /Mastery:?/i] },
      { key: 'covered', patterns: [/Where It Was Covered:?/i, /Covered:?/i] },
      { key: 'reason', patterns: [/Why Students Struggled:?/i, /Reason:?/i, /Why:?/i] },
      { key: 'improvement', patterns: [/How to Revisit \/ Improve It:?/i, /How to Improve:?/i, /Improvement:?/i] },
    ];

    // Helper to clean up field values
    const clean = (str: string) => str.replace(/^\*\*\s*/, '').replace(/\s*\*\*$/, '').replace(/^:+/, '').trim();

    // For each block, extract all fields flexibly
    return blocks.map((block: string) => {
      const result: any = { concept: '', mastery: null, covered: '', reason: '', improvement: '' };
      // For each field, try all patterns
      fieldPatterns.forEach(({ key, patterns }, idx) => {
        for (let pat of patterns) {
          // Find the field label
          const match = pat.exec(block);
          if (match) {
            // Find where this label ends
            const start = match.index + match[0].length;
            // Find the next field label (or end of block)
            let end = block.length;
            for (let j = idx + 1; j < fieldPatterns.length; j++) {
              for (let nextPat of fieldPatterns[j].patterns) {
                const nextMatch = nextPat.exec(block.slice(start));
                if (nextMatch) {
                  end = start + nextMatch.index;
                  break;
                }
              }
              if (end !== block.length) break;
            }
            let value = block.slice(start, end).replace(/\n/g, ' ').trim();
            if (key === 'mastery') {
              // Extract just the number
              const num = value.match(/\d+/);
              result[key] = num ? parseInt(num[0], 10) : null;
            } else {
              // For concept, also strip trailing '**' or similar markdown
              if (key === 'concept') {
                result[key] = clean(value).replace(/\*+\s*$/, '').trim();
              } else {
                result[key] = clean(value);
              }
            }
            break;
          }
        }
      });
      return result;
    })
    // Filter out header or invalid concepts
    .filter((item: any) => {
      if (!item.concept) return false;
      // Remove if concept is too short or looks like a header
      const c = item.concept.trim();
      if (c.length < 5) return false;
      if (/based on the quiz|materials:?$/i.test(c)) return false;
      return true;
    })
    // Only keep the last 3 valid concepts (top 3)
    .slice(-3);
  }
  return [];
}

import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import Sidebar from './Sidebar';
import ClassList from './ClassList';
import CreateClassForm from './CreateClassForm';
import CreateLectureForm from './CreateLectureForm';
import QuizUploadForm from './QuizUploadForm';
import LectureList from './LectureList';
import QuizList from './QuizList';

interface Class {
  id: number;
  class_name: string;
  description?: string;
}

const Dashboard: React.FC = () => {
  const [classes, setClasses] = useState<Class[]>([]);
  const [selectedClass, setSelectedClass] = useState<Class | null>(null);
  const [showCreateClass, setShowCreateClass] = useState(false);
  const [showLectureModal, setShowLectureModal] = useState(false);
  const [showQuizModal, setShowQuizModal] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [analysisDate, setAnalysisDate] = useState<string | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');
  const [lectureRefreshKey, setLectureRefreshKey] = useState(0);
  const [quizRefreshKey, setQuizRefreshKey] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);

  // Fetch classes and auto-select first or new
  useEffect(() => {
    const fetchClasses = async () => {
      const res = await fetch('http://localhost:8000/classes/');
      const data = await res.json();
      setClasses(data);
      if (!selectedClass && data.length > 0) setSelectedClass(data[0]);
    };
    fetchClasses();
  }, []);

  // Handler for class creation success
  const handleClassCreated = async (newClass?: { id: number; class_name: string; description?: string }) => {
    setShowCreateClass(false);
    const res = await fetch('http://localhost:8000/classes/');
    const data = await res.json();
    setClasses(data);
    // Prefer selecting the new class if provided
    if (newClass) {
      setSelectedClass(newClass);
    } else {
      setSelectedClass(data[data.length - 1]);
    }
    setLectureRefreshKey(k => k + 1);
    setQuizRefreshKey(k => k + 1);
    setFeedback('Class created successfully!');
    setTimeout(() => setFeedback(null), 2500);
  };

  // Handler for lecture upload success
  const handleLectureUploaded = () => {
    setLectureRefreshKey(k => k + 1);
    setShowLectureModal(false);
    setFeedback('Lecture uploaded successfully!');
    setTimeout(() => setFeedback(null), 2500);
  };

  // Handler for quiz upload success
  const handleQuizUploaded = () => {
    setQuizRefreshKey(k => k + 1);
    setShowQuizModal(false);
    setFeedback('Quiz uploaded successfully!');
    setTimeout(() => setFeedback(null), 2500);
  };

  // Fetch analysis when class changes
  useEffect(() => {
    if (!selectedClass) return;
    setAnalysis(null);
    setAnalysisError('');
    setAnalysisLoading(true);
    fetch(`http://localhost:8000/quizzes/class_analytics/${selectedClass.id}`)
      .then(res => {
        if (!res.ok) throw new Error('No analysis found');
        return res.json();
      })
      .then(data => {
        setAnalysis(data.analysis);
        setAnalysisDate(data.created_at);
      })
      .catch(() => setAnalysis(null))
      .finally(() => setAnalysisLoading(false));
  }, [selectedClass]);

  // Handler to run analysis
  const handleRunAnalysis = async () => {
    if (!selectedClass) return;
    setAnalysisLoading(true);
    setAnalysisError('');
    try {
      const res = await fetch(`http://localhost:8000/quizzes/class_analytics/${selectedClass.id}`, { method: 'POST' });
      if (!res.ok) throw new Error('Failed to run analysis');
      const data = await res.json();
      setAnalysis(data.analysis);
      setAnalysisDate(new Date().toISOString());
    } catch (err: any) {
      setAnalysisError(err.message || 'Error running analysis');
    } finally {
      setAnalysisLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-white">
      {/* Sidebar */}
      <Sidebar>
        <div className="flex flex-col h-full">
          <ClassList
            onClassCreated={handleClassCreated}
            selectedClassId={selectedClass?.id}
            onSelectClass={cls => setSelectedClass(cls)}
          />
        </div>
      </Sidebar>

      {/* Main Content */}
      <main className="flex-1 p-8 bg-faded-grey">
        {selectedClass ? (
          <>
            {/* Feedback message at top, fixed position, not shifting buttons */}
            {feedback && (
              <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-blue-light border border-blue-300 text-dark px-6 py-2 rounded shadow-lg text-center min-w-[220px]">
                {feedback}
              </div>
            )}
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-3xl font-bold text-dark">{selectedClass.class_name}</h1>
              <div className="space-x-2">
                <button className="bg-blue-light text-dark px-4 py-2 rounded hover:bg-blue-200" onClick={() => setShowLectureModal(true)}>Upload Lecture</button>
                <button className="bg-orange-light text-dark px-4 py-2 rounded hover:bg-orange-200" onClick={() => setShowQuizModal(true)}>Upload Quiz</button>
                <button className="bg-dark text-primary px-4 py-2 rounded" onClick={handleRunAnalysis} disabled={analysisLoading}>
                  {analysisLoading
                    ? 'Analyzing...'
                    : analysis
                      ? 'Update Analysis'
                      : 'Run Analysis'}
                </button>
              </div>
            </div>
            {/* Class Analysis Section */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-2 text-dark">Class Analysis</h2>
              {analysisLoading && <div className="text-dark">Loading analysis...</div>}
              {analysisError && <div className="text-orange-light">{analysisError}</div>}
              {analysis && (
                <>
                  {/* Top 3 Concepts Cards */}
                  {typeof analysis === 'object' && (() => {
                    // Expecting analysis.top_concepts: Array<{ concept, mastery, covered, reason, improvement }>
                    const topConcepts = extractTopConceptsStructured(analysis);
                    if (!topConcepts || topConcepts.length === 0) {
                      return null; // Or display a message if you prefer
                    }
                    return (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        {topConcepts.map((item: any, idx: number) => (
                          <div key={idx} className="bg-primary rounded shadow p-4 border border-orange-light text-dark">
                            <div className="font-bold text-lg mb-2">Concept: {item.concept}</div>
                            <div className="text-yellow-700 font-mono text-xl mb-1">Mastery: {item.mastery}/100</div>
                            <div className="text-gray-700 text-sm mb-1"><span className="font-semibold">Covered:</span> {item.covered}</div>
                            <div className="text-gray-700 text-sm mb-1"><span className="font-semibold">Why Struggled:</span> {item.reason}</div>
                            <div className="text-gray-700 text-sm"><span className="font-semibold">How to Improve:</span> {item.improvement}</div>
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                  {/* Removed markdown/JSON analysis display under the cards */}
                </>
              )}
              {!analysis && !analysisLoading && <div className="text-gray-500">No analysis available for this class yet.</div>}
            </div>
            {/* Lists */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <LectureList classId={selectedClass.id} refreshKey={selectedClass.id} />
              </div>
              <div>
                <QuizList classId={selectedClass.id} refreshKey={selectedClass.id} />
              </div>
            </div>
          </>
        ) : (
          <div className="text-gray-500">Select a class to view dashboard.</div>
        )}

        {/* Lecture Upload Modal */}
        {showLectureModal && selectedClass && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="fixed inset-0 bg-dark opacity-30" onClick={() => setShowLectureModal(false)} />
            <div className="relative bg-primary rounded-lg shadow-xl p-8 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4 text-dark">Upload Lecture</h2>
              <CreateLectureForm classId={selectedClass.id} onSuccess={handleLectureUploaded} />
              <button className="absolute top-2 right-2 text-gray-500" onClick={() => setShowLectureModal(false)}>✕</button>
            </div>
          </div>
        )}

        {/* Quiz Upload Modal */}
        {showQuizModal && selectedClass && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div className="fixed inset-0 bg-dark opacity-30" onClick={() => setShowQuizModal(false)} />
            <div className="relative bg-primary rounded-lg shadow-xl p-8 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4 text-dark">Upload Quiz</h2>
              <QuizUploadForm classId={selectedClass.id} onQuizUploaded={handleQuizUploaded} />
              <button className="absolute top-2 right-2 text-gray-500" onClick={() => setShowQuizModal(false)}>✕</button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
