import React from 'react';

function TaskItem({ task }) {
  return (
    <li className="border p-2 mb-2 flex justify-between items-center">
      <span>{task.name}</span>
      <span>
        <button className="text-blue-500">Edit</button>
        <button className="text-red-500 ml-2">Delete</button>
      </span>
    </li>
  );
}

export default TaskItem;