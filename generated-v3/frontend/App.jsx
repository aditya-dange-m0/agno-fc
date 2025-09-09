import React from 'react';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';

function App() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Task Manager</h1>
      <TaskForm />
      <TaskList />
    </div>
  );
}

export default App;