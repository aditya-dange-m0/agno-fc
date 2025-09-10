import React from 'react';
import ReactDOM from 'react-dom';
import AuthForm from './AuthForm';
import TodoList from './TodoList';

const App = () => {
  const handleAuthSubmit = (credentials) => {
    console.log('User authenticated:', credentials);
  };
  
  const tasks = [
    { id: 1, description: 'Task 1' },
    { id: 2, description: 'Task 2' },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-lg font-bold">User Authentication</h1>
      <AuthForm onSubmit={handleAuthSubmit} />
      <h2 className="text-lg font-bold mt-6">Todo List</h2>
      <TodoList tasks={tasks} />
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById('root'));