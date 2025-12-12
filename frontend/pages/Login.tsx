import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card } from '../components/UIComponents';
import { BookOpen } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);

  // Get the redirect path from location state or default to dashboard
  const from = (location.state as any)?.from?.pathname || '/dashboard';

  // Load remembered email on mount
  useEffect(() => {
    const rememberedEmail = localStorage.getItem('remembered_email');
    if (rememberedEmail) {
      setEmail(rememberedEmail);
      setRememberMe(true);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password, rememberMe);

      // Save or clear remembered email
      if (rememberMe) {
        localStorage.setItem('remembered_email', email);
      } else {
        localStorage.removeItem('remembered_email');
      }

      navigate(from, { replace: true });
    } catch (err) {
      // Error handling is done in AuthContext with toast
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Helper for demo login
  const demoLogin = (role: 'student' | 'instructor') => {
    setEmail(role === 'instructor' ? 'demo_instructor@tutorly.com' : 'demo_student@tutorly.com');
    setPassword('password123');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <div className="bg-gradient-to-br from-primary-600 to-blue-600 text-white p-3 rounded-2xl shadow-lg shadow-primary-500/30">
              <BookOpen size={32} strokeWidth={2.5} />
            </div>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Welcome back</h2>
          <p className="mt-2 text-sm text-gray-600 font-medium">
            Or{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-500 hover:underline">
              create a new account
            </Link>
          </p>
        </div>

        <Card className="p-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <Input 
              label="Email Address" 
              type="email" 
              required 
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
            <div className="relative">
              <Input 
                label="Password" 
                type="password" 
                required 
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <div className="absolute right-0 top-0">
                 <Link to="/forgot-password" className="text-xs font-bold text-primary-600 hover:text-primary-500">
                  Forgot password?
                </Link>
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded cursor-pointer"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 cursor-pointer select-none">
                Keep me signed in
              </label>
            </div>

            <Button type="submit" className="w-full py-3 text-base shadow-primary-500/25 shadow-lg" isLoading={loading}>
              Sign in
            </Button>
          </form>

          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white/80 backdrop-blur rounded-full text-gray-500 font-medium">Quick Demo Access</span>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-4">
              <Button variant="glass" size="sm" onClick={() => demoLogin('student')}>
                Student Demo
              </Button>
              <Button variant="glass" size="sm" onClick={() => demoLogin('instructor')}>
                Instructor Demo
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;