import React from 'react';

interface SidebarProps {
  children?: React.ReactNode;
}

const Sidebar: React.FC<SidebarProps> = ({ children }) => {
  return (
    <aside className="bg-white rounded-lg shadow p-6 mb-8 md:mb-0 md:mr-8 w-full md:w-64">
      {children}
    </aside>
  );
};

export default Sidebar;
