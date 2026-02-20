import React from 'react';
import CreateClassForm from './CreateClassForm';
import CreateLectureForm from './CreateLectureForm';

const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create Class</h2>
          <CreateClassForm />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create & Upload Lecture</h2>
          <CreateLectureForm />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
