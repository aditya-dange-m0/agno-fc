import { useForm } from 'react-hook-form';

export default function Register() {
  const { register, handleSubmit } = useForm();
  const onSubmit = async (data: any) => {
    // Handle registration via API
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto p-4">
      <h2 className="text-xl mb-4">Register</h2>
      <input {...register('email')} type="email" placeholder="Email" className="border p-2" required />
      <input {...register('password')} type="password" placeholder="Password" className="border p-2 mt-2" required />
      <input {...register('full_name')} type="text" placeholder="Full Name" className="border p-2 mt-2" />
      <button type="submit" className="bg-blue-500 text-white p-2 mt-4">Register</button>
    </form>
  );
}