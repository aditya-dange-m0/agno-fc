import { useEffect, useState } from 'react';
import axios from 'axios';
import TodoForm from './TodoForm';

const TodoList = () => {
  const [todos, setTodos] = useState([]);
  const [selectedTodo, setSelectedTodo] = useState(null);

  const fetchTodos = async () => {
    const response = await axios.get('/api/todos');
    setTodos(response.data);
  };

  const handleDelete = async (id) => {
    await axios.delete(`/api/todos/${id}`);
    fetchTodos();
  };

  const handleUpdate = () => {
    setSelectedTodo(null);
    fetchTodos();
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div>
      <h2 className="text-xl font-semibold mb-2">Todo List</h2>
      {todos.map(todo => (
        <div key={todo.id} className="flex items-center justify-between border-b py-2">
          <span>{todo.title}</span>
          <div>
            <button onClick={() => setSelectedTodo(todo)} className="text-blue-500 mr-2">Edit</button>
            <button onClick={() => handleDelete(todo.id)} className="text-red-500">Delete</button>
          </div>
        </div>
      ))}
      {selectedTodo && <TodoForm existingTodo={selectedTodo} onUpdate={handleUpdate} />}
    </div>
  );
};

export default TodoList;