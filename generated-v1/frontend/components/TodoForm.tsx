import { useState } from 'react';
import axios from 'axios';

const TodoForm = ({ existingTodo, onUpdate }) => {
  const [title, setTitle] = useState(existingTodo ? existingTodo.title : '');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if(existingTodo) {
        await axios.put(`/api/todos/${existingTodo.id}`, { title });
        onUpdate();
    } else {
        await axios.post('/api/todos', { title });
        setTitle('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Enter task title"
        className="border p-2 mr-2"
        required
      />
      <button type="submit" className="bg-blue-500 text-white p-2">Submit</button>
    </form>
  );
};

export default TodoForm;