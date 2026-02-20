import QuizList from './QuizList';
import React, { useEffect, useState } from 'react';
import CreateClassForm from './CreateClassForm';
import LectureList from './LectureList';
// import CreateLectureForm from './CreateLectureForm';
// import QuizUploadForm from './QuizUploadForm';

interface Class {
  id: number;
  class_name: string;
  description?: string;
  created_at?: string;
}

interface ClassListProps {
  onClassCreated?: (newClass: { id: number; class_name: string; description?: string }) => void;
  selectedClassId?: number;
  onSelectClass?: (cls: Class) => void;
}

const ClassList: React.FC<ClassListProps> = ({ onClassCreated, selectedClassId, onSelectClass }) => {
  const [classes, setClasses] = useState<Class[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchClasses = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch('http://localhost:8000/classes/');
        if (!res.ok) throw new Error('Failed to fetch classes');
        const data = await res.json();
        setClasses(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching classes');
      } finally {
        setLoading(false);
      }
    };
    fetchClasses();
  }, [onClassCreated]); // re-fetch when onClassCreated changes

  // Helper to trigger refresh when a class is created
  const handleClassCreatedInternal = (newClass: { id: number; class_name: string; description?: string }) => {
    if (onClassCreated) onClassCreated(newClass);
    // Re-fetch classes after creation
    (async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch('http://localhost:8000/classes/');
        if (!res.ok) throw new Error('Failed to fetch classes');
        const data = await res.json();
        setClasses(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching classes');
      } finally {
        setLoading(false);
      }
    })();
  };

  return (
    <div className="mb-8 bg-primary rounded shadow p-4">
      <h2 className="text-xl font-semibold mb-4 text-dark">Current Classes</h2>
      {loading && <div className="text-dark">Loading...</div>}
      {error && <div className="text-orange-light">{error}</div>}
      <ul className="space-y-2 mb-6">
        {classes.map(cls => (
          <li key={cls.id}>
            <button
              className={`w-full text-left px-3 py-2 rounded ${selectedClassId === cls.id ? 'bg-blue-light font-bold text-dark' : 'hover:bg-faded-blue text-dark'}`}
              onClick={() => onSelectClass && onSelectClass(cls)}
            >
              {cls.class_name}
              {cls.description && <span className="block text-xs text-faded-grey">{cls.description}</span>}
            </button>
          </li>
        ))}
      </ul>
      <div className="pt-2 border-t border-faded-grey">
        <CreateClassForm onSuccess={handleClassCreatedInternal} />
      </div>
    </div>
  );
};

export default ClassList;
