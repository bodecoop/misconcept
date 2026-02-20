import React, { useState } from 'react';

interface CreateClassFormProps {
  onSuccess?: (newClass: { id: number; class_name: string; description?: string }) => void;
}

const CreateClassForm: React.FC<CreateClassFormProps> = ({ onSuccess }) => {
  const [className, setClassName] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    try {
      const response = await fetch('http://localhost:8000/classes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class_name: className,
          description: description,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create class');
      }
      setMessage('Class created successfully!');
      setClassName('');
      setDescription('');
      // Fetch the new class list and call onSuccess with the new class
      const classesRes = await fetch('http://localhost:8000/classes/');
      if (classesRes.ok) {
        const classes = await classesRes.json();
        const newClass = classes[classes.length - 1];
        if (onSuccess) onSuccess(newClass);
      }
    } catch (err: any) {
      setMessage(err.message || 'Error creating class');
    }
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
