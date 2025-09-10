import TodoList from '../components/TodoList';
import TodoForm from '../components/TodoForm';

const Home = () => {
  return (
    <main className="flex flex-col items-center p-4">
      <h1 className="text-2xl font-bold mb-4">Todo Management</h1>
      <TodoForm />
      <TodoList />
    </main>
  );
};

export default Home;