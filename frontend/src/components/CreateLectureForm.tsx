import React, { useState } from 'react';

const CreateLectureForm: React.FC = () => {
  const [lectureTitle, setLectureTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage('Please select a file.');
      return;
    }
    // TODO: Replace with actual API call
    setMessage('Lecture uploaded successfully!');
    setLectureTitle('');
    setFile(null);
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
        <label className="block text-sm font-medium mb-1">Lecture File</label>
        <input
          type="file"
          className="w-full"
          onChange={e => setFile(e.target.files ? e.target.files[0] : null)}
          required
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
