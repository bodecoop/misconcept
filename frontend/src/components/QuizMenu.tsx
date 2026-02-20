import React from 'react';
import QuizUploadForm from './QuizUploadForm';

const QuizMenu: React.FC = () => {
  // Optionally, you could allow class selection here if needed
  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Upload Quiz</h2>
      <QuizUploadForm classId={0} /> {/* Replace 0 with selected classId if you add class selection */}
    </div>
  );
};

export default QuizMenu;
