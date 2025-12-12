import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Card } from '../components/UIComponents';
import { BookOpen } from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [role, setRole] = useState<'student' | 'instructor'>('student');
  const [formData, setFormData] = useState({ first_name: '', last_name: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register({ ...formData, role });
      navigate('/dashboard');
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
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
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Create your account</h2>
          <p className="mt-2 text-sm text-gray-600 font-medium">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-500 hover:underline">
              Log in
            </Link>
          </p>
        </div>

        {/* Role Selection */}
        <div className="grid grid-cols-2 gap-2 p-1.5 bg-white/40 backdrop-blur-sm border border-white/50 rounded-2xl shadow-sm">
          <button
            onClick={() => setRole('student')}
            className={`py-3 text-sm font-bold rounded-xl transition-all duration-200 ${
              role === 'student' 
              ? 'bg-white text-primary-700 shadow-md scale-[1.02] ring-1 ring-black/5' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
            }`}
          >
            I want to Learn
          </button>
          <button
            onClick={() => setRole('instructor')}
            className={`py-3 text-sm font-bold rounded-xl transition-all duration-200 ${
              role === 'instructor' 
              ? 'bg-white text-primary-700 shadow-md scale-[1.02] ring-1 ring-black/5' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
            }`}
          >
            I want to Teach
          </button>
        </div>

        <Card className="p-8 md:p-10">
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="grid grid-cols-2 gap-4">
              <Input 
                label="First Name" 
                required 
                value={formData.first_name}
                onChange={e => setFormData({...formData, first_name: e.target.value})}
                placeholder="Jane"
              />
              <Input 
                label="Last Name" 
                required 
                value={formData.last_name}
                onChange={e => setFormData({...formData, last_name: e.target.value})}
                placeholder="Doe"
              />
            </div>
            <Input 
              label="Email Address" 
              type="email" 
              required 
              value={formData.email}
              onChange={e => setFormData({...formData, email: e.target.value})}
              placeholder="jane@example.com"
            />
            <Input 
              label="Password" 
              type="password" 
              required 
              minLength={6}
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
              placeholder="Create a strong password"
            />
            
            <Button type="submit" className="w-full py-3.5 text-lg mt-2 shadow-lg shadow-primary-500/25" isLoading={loading}>
              Sign up as {role === 'student' ? 'Student' : 'Instructor'}
            </Button>

            <p className="text-xs text-gray-500 text-center mt-4">
              By signing up, you agree to our Terms of Service and Privacy Policy.
            </p>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Register;