import React, { useState } from 'react';

function TaskForm() {
  const [taskName, setTaskName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle add task logic
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <input
        type="text"
        value={taskName}
        onChange={(e) => setTaskName(e.target.value)}
        className="border p-2 mr-2"
        placeholder="Add a new task"
      />
      <button type="submit" className="bg-blue-500 text-white p-2">Add Task</button>
    </form>
  );
}

export default TaskForm;