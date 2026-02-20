import React, { useState, useEffect } from 'react';

interface CreateLectureFormProps {
  classId?: number;
  onSuccess?: () => void;
}

const CreateLectureForm: React.FC<CreateLectureFormProps> = ({ classId, onSuccess }) => {
  const [lectureTitle, setLectureTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [transcriptFile, setTranscriptFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [loadingClasses, setLoadingClasses] = useState(false);
  const [errorClasses, setErrorClasses] = useState('');
  const [classes, setClasses] = useState<any[]>([]);

  useEffect(() => {
    if (classId) return;
    const fetchClasses = async () => {
      setLoadingClasses(true);
      setErrorClasses('');
      try {
        const res = await fetch('http://localhost:8000/classes/');
        if (!res.ok) throw new Error('Failed to fetch classes');
        const data = await res.json();
        setClasses(data);
      } catch (err: any) {
        setErrorClasses(err.message || 'Error fetching classes');
      } finally {
        setLoadingClasses(false);
      }
    };
    fetchClasses();
  }, [classId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    if (!file) {
      setMessage('Please select a file.');
      return;
    }
    const finalClassId = classId ? String(classId) : '';
    if (!finalClassId) {
      setMessage('Class ID missing.');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('lecture_title', lectureTitle);
      formData.append('pdf_file', file);
      if (transcriptFile) formData.append('transcript_file', transcriptFile);
      formData.append('class_id', finalClassId);
      formData.append('lecture_date', new Date().toISOString().slice(0, 10));
      formData.append('labels', '');

      const response = await fetch('http://localhost:8000/lectures/upload', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to upload lecture');
      }
      setMessage('Lecture uploaded successfully!');
      setLectureTitle('');
      setFile(null);
      setTranscriptFile(null);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setMessage(err.message || 'Error uploading lecture');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Lecture Title</label>
        <input
          type="text"
          className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-400"
          value={lectureTitle}
          onChange={e => setLectureTitle(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Lecture PDF File</label>
        <input
          type="file"
          accept="application/pdf"
          className="w-full"
          onChange={e => setFile(e.target.files ? e.target.files[0] : null)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Transcript File (.txt)</label>
        <input
          type="file"
          accept="text/plain"
          className="w-full"
          onChange={e => setTranscriptFile(e.target.files ? e.target.files[0] : null)}
        />
      </div>
      <button
        type="submit"
        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
      >
        Upload Lecture
      </button>
      {message && <div className="text-green-600 mt-2">{message}</div>}
    </form>
  );
};

export default CreateLectureForm;
function setLoadingClasses(arg0: boolean) {
  throw new Error('Function not implemented.');
}

