import React, { useState } from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './UIComponents';
import { Menu, X, BookOpen, LogOut, Calendar } from 'lucide-react';

const Layout: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-gray-900 relative">
      {/* Liquid Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40rem] h-[40rem] bg-violet-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob"></div>
        <div className="absolute top-[-10%] right-[-10%] w-[40rem] h-[40rem] bg-sky-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-20%] left-[20%] w-[40rem] h-[40rem] bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <header className="sticky top-4 z-50 mx-4 rounded-2xl bg-white/60 backdrop-blur-xl border border-white/40 shadow-sm mt-2">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 group">
              <div className="bg-gradient-to-br from-primary-600 to-blue-600 text-white p-2 rounded-xl shadow-lg shadow-primary-500/30 group-hover:rotate-3 transition-transform">
                <BookOpen size={20} strokeWidth={3} />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-700 to-blue-600">
                Tutorly
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden md:flex items-center gap-8">
              <Link to="/instructors" className="text-sm font-semibold text-gray-600 hover:text-primary-600 transition-colors">
                Find Tutors
              </Link>
              <Link to="/subjects" className="text-sm font-semibold text-gray-600 hover:text-primary-600 transition-colors">
                Subjects
              </Link>
              
              {isAuthenticated ? (
                <div className="flex items-center gap-4 pl-4 border-l border-gray-200/50">
                  <Link to="/dashboard" className="text-sm font-semibold text-gray-800 hover:text-primary-600">
                    Dashboard
                  </Link>
                  {user?.role === 'instructor' && (
                    <Link to="/calendar" className="text-sm font-semibold text-gray-600 hover:text-primary-600 flex items-center gap-1.5">
                      <Calendar size={16} />
                      Calendar
                    </Link>
                  )}
                  <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-full bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center text-primary-700 font-bold border border-white shadow-sm">
                      {user?.first_name[0]}
                    </div>
                    <button onClick={handleLogout} className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50">
                      <LogOut size={18} />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <Link to="/login" className="text-sm font-bold text-gray-600 hover:text-primary-600 transition-colors">
                    Log in
                  </Link>
                  <Link to="/register">
                    <Button size="sm" className="rounded-full px-6">Get Started</Button>
                  </Link>
                </div>
              )}
            </nav>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full mt-2 p-4 rounded-2xl bg-white/80 backdrop-blur-xl border border-white/40 shadow-xl animate-slide-up">
            <div className="flex flex-col space-y-2">
              <Link to="/instructors" onClick={() => setMobileMenuOpen(false)} className="px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-white/50 hover:text-primary-600">
                Find Tutors
              </Link>
              <Link to="/subjects" onClick={() => setMobileMenuOpen(false)} className="px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-white/50 hover:text-primary-600">
                Subjects
              </Link>
              {isAuthenticated ? (
                <>
                  <div className="h-px bg-gray-200/50 my-1"></div>
                  <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)} className="px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-white/50 hover:text-primary-600">
                    Dashboard
                  </Link>
                  {user?.role === 'instructor' && (
                    <Link to="/calendar" onClick={() => setMobileMenuOpen(false)} className="px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-white/50 hover:text-primary-600 flex items-center gap-2">
                      <Calendar size={16} />
                      Calendar
                    </Link>
                  )}
                  <button
                    onClick={() => { handleLogout(); setMobileMenuOpen(false); }}
                    className="w-full text-left px-4 py-3 text-sm font-semibold text-red-600 rounded-xl hover:bg-red-50"
                  >
                    Log Out
                  </button>
                </>
              ) : (
                <div className="grid grid-cols-2 gap-3 mt-2 pt-2 border-t border-gray-200/50">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                    <Button variant="glass" className="w-full justify-center">Log in</Button>
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                    <Button className="w-full justify-center">Sign up</Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-grow relative z-0">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white/30 backdrop-blur-lg border-t border-white/40 pt-12 pb-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div className="col-span-2 md:col-span-1">
               <Link to="/" className="flex items-center gap-2 mb-4 group">
                <div className="bg-gradient-to-br from-primary-600 to-blue-600 text-white p-1.5 rounded-lg shadow-md">
                  <BookOpen size={16} strokeWidth={3} />
                </div>
                <span className="text-lg font-bold text-gray-900">Tutorly</span>
              </Link>
              <p className="text-sm text-gray-600 leading-relaxed">
                Empowering learners worldwide to master new skills with the help of expert tutors.
              </p>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Learn</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="#" className="hover:text-primary-600 transition-colors">English Tutors</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Spanish Tutors</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Math Tutors</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">About</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Who we are</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">How it works</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Help Center</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Terms of Service</Link></li>
                <li><Link to="#" className="hover:text-primary-600 transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200/50 text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Tutorly Inc. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;