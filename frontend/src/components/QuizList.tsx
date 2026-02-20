import React, { useEffect, useState } from 'react';

interface Quiz {
  id: number;
  class_id: number;
  quiz_title?: string;
  quiz_content?: string;
  quiz_results?: string;
  created_at?: string;
}

interface QuizListProps {
  classId: number;
  refreshKey?: number;
}

const QuizList: React.FC<QuizListProps> = ({ classId, refreshKey }) => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchQuizzes = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`http://localhost:8000/quizzes/by_class/${classId}`);
        if (!res.ok) throw new Error('Failed to fetch quizzes');
        const data = await res.json();
        setQuizzes(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching quizzes');
      } finally {
        setLoading(false);
      }
    };
    fetchQuizzes();
  }, [classId, refreshKey]);

  return (
    <div className="ml-4 mt-2 bg-primary rounded shadow p-4">
      <h3 className="font-semibold mb-2 text-dark">Quizzes</h3>
      {loading && <div className="text-dark">Loading...</div>}
      {error && <div className="text-orange-light">{error}</div>}
      <ul className="space-y-2">
        {quizzes.map(quiz => (
          <li key={quiz.id} className="bg-orange-light rounded px-3 py-2 text-dark">
            {quiz.quiz_title || 'Untitled Quiz'}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default QuizList;
