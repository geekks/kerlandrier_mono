import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { authenticate, getAccessToken, logout } from '../services/authService';

interface LoginForm {
  username: string;
  password: string;
}

const Login: React.FC = () => {
  const { register, handleSubmit, formState: { errors }, reset } = useForm<LoginForm>();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const onSubmit = async (data: LoginForm) => {
    try {
      const authResponse = await authenticate(data.username, data.password);
      console.log('Access Token:', authResponse.access_token);
      if (authResponse.success) {
        localStorage.setItem('kl_token', authResponse.access_token);
        reset();
        const expirationTime = new Date(Date.now() + 30 * 60 * 1000);
        setSuccessMessage(`Connexion jusqu'à ${expirationTime.toLocaleTimeString()}`);
        setIsAuthenticated(true);
      } else {
        console.log("Auth failed", authResponse);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    logout();
    setIsAuthenticated(false);
    setSuccessMessage(null);
  };

  return (
    <div className="flex flex-col items-center mt-4 sm:mt-12">
      {!isAuthenticated ? (
        <form onSubmit={handleSubmit(onSubmit)} className="flex items-center">
          <div className="flex items-center">
            <div className="mr-2">
              <input
                type="text"
                className="p-2 font-size-16 border border-main-color rounded w-full max-w-xs text-center"
                placeholder="Nom d'utilisateur"
                autoComplete="username"
                {...register('username', { required: true })}
              />
              {errors.username && <span className="text-red-500 text-xs">Ce champ est requis</span>}
            </div>

            <div className="mr-2">
              <input
                type="password"
                className="p-2 font-size-16 border border-main-color rounded w-full max-w-xs text-center"
                placeholder="Mot de passe"
                autoComplete="current-password"
                {...register('password', { required: true })}
              />
              {errors.password && <span className="text-red-500 text-xs">Ce champ est requis</span>}
            </div>

            <button
              type="submit"
              className="p-2.5 font-size-16 bg-main-color text-lite-bkg border-none rounded cursor-pointer"
            >
              Connexion
            </button>
          </div>
          {successMessage && (
            <div className="text-sm text-teal-300">
              {successMessage}
            </div>
          )}
        </form>
      ) : (
        <button
          onClick={handleLogout}
          className="p-1.5 sm:p-2.5 font-size-16 bg-main-color text-lite-bkg border-none rounded cursor-pointer"
        >
          Se déconnecter
        </button>
      )}
    </div>
  );
};

export default Login;
