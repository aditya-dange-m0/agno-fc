import { useState, useEffect } from 'react';
import axios from 'axios';

const useTodos = () => {
  const [todos, setTodos] = useState([]);

  const fetchTodos = async () => {
    const response = await axios.get('/api/todos');
    setTodos(response.data);
  };

  const addTodo = async (todo) => {
    await axios.post('/api/todos', todo);
    fetchTodos();
  };

  const editTodo = async (id, updatedTodo) => {
    await axios.put(`/api/todos/${id}`, updatedTodo);
    fetchTodos();
  };

  const deleteTodo = async (id) => {
    await axios.delete(`/api/todos/${id}`);
    fetchTodos();
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  return { todos, addTodo, editTodo, deleteTodo };
};

export default useTodos;