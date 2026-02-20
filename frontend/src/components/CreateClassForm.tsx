import React, { useState } from 'react';

const CreateClassForm: React.FC = () => {
  const [className, setClassName] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Replace with actual API call
    setMessage('Class created successfully!');
    setClassName('');
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Class Name</label>
        <input
          type="text"
          className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-400"
          value={className}
          onChange={e => setClassName(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Description</label>
        <textarea
          className="w-full border rounded px-3 py-2 focus:outline-none focus:ring focus:border-blue-400"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
      </div>
      <button
        type="submit"
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
      >
        Create Class
      </button>
      {message && <div className="text-green-600 mt-2">{message}</div>}
    </form>
  );
};

export default CreateClassForm;
