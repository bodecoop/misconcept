import React, { useEffect, useState } from 'react';

interface Lecture {
  id: number;
  lecture_title: string;
  class_id: number;
  created_at?: string;
}

interface LectureListProps {
  classId: number;
  refreshKey?: number;
}

const LectureList: React.FC<LectureListProps> = ({ classId, refreshKey }) => {
  const [lectures, setLectures] = useState<Lecture[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLectures = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`http://localhost:8000/lectures/by_class/${classId}`);
        if (!res.ok) throw new Error('Failed to fetch lectures');
        const data = await res.json();
        setLectures(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching lectures');
      } finally {
        setLoading(false);
      }
    };
    fetchLectures();
  }, [classId, refreshKey]);

  return (
    <div className="ml-4 mt-2 bg-primary rounded shadow p-4">
      <h3 className="font-semibold mb-2 text-dark">Lectures</h3>
      {loading && <div className="text-dark">Loading...</div>}
      {error && <div className="text-orange-light">{error}</div>}
      <ul className="space-y-2">
        {lectures.map(lecture => (
          <li key={lecture.id} className="bg-blue-light rounded px-3 py-2 text-dark">
            {lecture.lecture_title}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LectureList;
