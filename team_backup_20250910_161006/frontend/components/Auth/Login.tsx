import { useForm } from 'react-hook-form';

export default function Login() {
  const { register, handleSubmit } = useForm();
  const onSubmit = async (data: any) => {
    // Handle login via API
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-4">
      <h2 className="text-xl mb-4">Login</h2>
      <input {...register('email')} type="email" placeholder="Email" className="border p-2" required />
      <input {...register('password')} type="password" placeholder="Password" className="border p-2 mt-2" required />
      <button type="submit" className="bg-blue-500 text-white p-2 mt-4">Login</button>
    </form>
  );
}