// src/components/Login.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { authenticate } from '../services/authService';

interface LoginForm {
    username: string;
    password: string;
}

const Login: React.FC = () => {
    const { register, handleSubmit, formState: { errors }, reset } = useForm<LoginForm>();
    const [successMessage, setSuccessMessage] = useState<string | null>(null);

    const onSubmit = async (data: LoginForm) => {
        try {
            const authResponse = await authenticate(data.username, data.password);
            console.log('Access Token:', authResponse.access_token);
            // Store the token in local storage or context
            if (authResponse.success) {
              localStorage.setItem('access_token', authResponse.access_token)
              reset();
              const expirationTime = new Date(Date.now() + 30 * 60 * 1000);
              setSuccessMessage(`Login until ${expirationTime.toLocaleTimeString()}`);
            } else console.log("Auth failed", authResponse)
        } catch (err) {
            console.error(err);
        }
    };

    return (
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col items-center">
              <div className="m-3 text-xl w-full max-w-sm">
                <div className="w-full mb-2">
                  <input
                  type="text"
                  className="border border-teal-300 focus:outline-none focus:ring-2 focus:ring-teal-500 text-center"
                  placeholder="Username"
                  {...register('username', { required: true })}
                  />
                  {errors.username && <span>This field is required</span>}
                </div>

                <div className="w-full mb-2">
                  <input
                      type="password"
                      className="border border-teal-300 focus:outline-none focus:ring-2 focus:ring-teal-500 text-center"
                      placeholder="Password"
                      {...register('password', { required: true })}
                  />
                  {errors.password && <span>This field is required</span>}
                </div>

                <button
                  type="submit"
                  className="focus:outline-none focus:ring-2 focus:ring-teal-500 text-center"
                >
                  Login
                </button>
              </div>
              {successMessage && (
                <div className="text-sm text-teal-300">
                    {successMessage}
                </div>
            )}
            </form> 
    );
};

export default Login;
