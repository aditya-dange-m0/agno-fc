import React from 'react';
import TaskItem from './TaskItem';
import { useTasks } from '../hooks/useTasks';

function TaskList() {
  const { tasks } = useTasks();

  return (
    <ul className="list-none">
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </ul>
  );
}

export default TaskList;