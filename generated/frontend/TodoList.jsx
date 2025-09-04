import React from 'react';
import PropTypes from 'prop-types';

const TodoList = ({ tasks }) => {
  return (
    <ul className="list-disc pl-5">
      {tasks.map((task) => (
        <li key={task.id} className="text-gray-800">{task.description}</li>
      ))}
    </ul>
  );
};

TodoList.propTypes = {
  tasks: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
  })).isRequired,
};

export default TodoList;