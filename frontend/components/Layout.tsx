/**
 * Layout Component
 * Modern navigation with micro-animations, glassmorphism, and Figma-style design
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useUnreadCount } from '../context/UnreadCountContext';
import { Button } from './UIComponents';
import {
  Menu,
  X,
  BookOpen,
  LogOut,
  Calendar,
  Search,
  Users,
  LayoutDashboard,
  ChevronDown,
  Bell,
  Settings,
  User,
  Sparkles,
  Home,
  MessageSquare,
  Shield,
} from 'lucide-react';
import { WalletDropdown } from './wallet';

// NavLink component with active state and hover animation
interface NavLinkProps {
  to: string;
  children: React.ReactNode;
  icon?: React.ReactNode;
  isActive?: boolean;
  onClick?: () => void;
}

const NavLink: React.FC<NavLinkProps> = ({ to, children, icon, isActive, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <Link
      to={to}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        relative flex items-center gap-2 px-4 py-2 rounded-xl
        text-sm font-semibold transition-all duration-300
        ${isActive
          ? 'text-primary-700 bg-primary-50/80'
          : 'text-gray-600 hover:text-primary-600 hover:bg-white/50'
        }
      `}
    >
      {icon && (
        <span
          className={`
            transition-all duration-300
            ${isHovered ? 'scale-110' : 'scale-100'}
            ${isActive ? 'text-primary-600' : ''}
          `}
        >
          {icon}
        </span>
      )}
      <span>{children}</span>

      {/* Active indicator */}
      <span
        className={`
          absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 rounded-full
          bg-gradient-to-r from-primary-500 to-blue-500
          transition-all duration-300
          ${isActive ? 'w-8 opacity-100' : 'w-0 opacity-0'}
        `}
      />

      {/* Hover glow effect */}
      {isHovered && !isActive && (
        <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-100/20 to-blue-100/20 animate-pulse" />
      )}
    </Link>
  );
};

// User dropdown menu
interface UserMenuProps {
  user: { first_name: string; last_name?: string; email?: string; role?: string } | null;
  onLogout: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ user, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  if (!user) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`
          flex items-center gap-2 p-1.5 pr-3 rounded-xl
          transition-all duration-300
          ${isOpen ? 'bg-white shadow-lg' : 'hover:bg-white/50'}
        `}
      >
        {/* Avatar */}
        <div
          className={`
            relative h-9 w-9 rounded-xl overflow-hidden
            bg-gradient-to-br from-primary-500 to-blue-500
            flex items-center justify-center
            transition-all duration-300
            ${isHovered ? 'scale-105 shadow-lg shadow-primary-500/30' : ''}
          `}
        >
          <span className="text-white font-bold text-sm">
            {user.first_name[0]}{user.last_name?.[0] || ''}
          </span>
          {/* Online indicator */}
          <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 border-2 border-white rounded-full" />
        </div>

        <ChevronDown
          size={16}
          className={`
            text-gray-400 transition-transform duration-300
            ${isOpen ? 'rotate-180' : ''}
          `}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div
            className="absolute right-0 top-full mt-2 w-64 z-50
              bg-white/95 backdrop-blur-xl rounded-2xl
              border border-white/50 shadow-2xl shadow-gray-200/50
              overflow-hidden animate-slideDown"
          >
            {/* User info header */}
            <div className="p-4 bg-gradient-to-r from-primary-50/50 to-blue-50/50 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary-500 to-blue-500 flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-lg">
                    {user.first_name[0]}{user.last_name?.[0] || ''}
                  </span>
                </div>
                <div>
                  <p className="font-semibold text-gray-900">
                    {user.first_name} {user.last_name || ''}
                  </p>
                  <p className="text-xs text-gray-500">{user.email || user.role}</p>
                </div>
              </div>
            </div>

            {/* Menu items */}
            <div className="p-2">
              <Link
                to={user.role === 'admin' ? '/admin' : '/dashboard'}
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-primary-600 transition-colors"
              >
                <LayoutDashboard size={18} />
                {user.role === 'admin' ? 'Admin Dashboard' : 'Dashboard'}
              </Link>
              <Link
                to="/settings"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-primary-600 transition-colors"
              >
                <Settings size={18} />
                Settings
              </Link>
              <Link
                to="/profile"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-primary-600 transition-colors"
              >
                <User size={18} />
                Profile
              </Link>
            </div>

            {/* Logout */}
            <div className="p-2 border-t border-gray-100">
              <button
                onClick={() => {
                  onLogout();
                  setIsOpen(false);
                }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut size={18} />
                Log out
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// Notification bell with badge - connected to real unread count
const NotificationBell: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);
  const { unreadCount } = useUnreadCount();

  return (
    <Link
      to="/messages"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        relative p-2.5 rounded-xl transition-all duration-300
        ${isHovered ? 'bg-white shadow-md' : 'hover:bg-white/50'}
      `}
    >
      <Bell
        size={20}
        className={`
          text-gray-500 transition-all duration-300
          ${isHovered ? 'text-primary-600 scale-110' : ''}
        `}
      />
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 bg-red-500 rounded-full border-2 border-white flex items-center justify-center">
          <span className="text-[10px] font-bold text-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        </span>
      )}
    </Link>
  );
};

const Layout: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Track scroll for navbar styling
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActivePath = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
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
      <header
        className={`
          sticky top-0 z-50 transition-all duration-500
          ${scrolled
            ? 'py-2 mx-2 mt-2 rounded-2xl bg-white/80 backdrop-blur-xl border border-white/50 shadow-lg shadow-gray-200/50'
            : 'py-3 mx-4 mt-3 rounded-2xl bg-white/60 backdrop-blur-xl border border-white/40 shadow-sm'
          }
        `}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2.5 group">
              <div
                className={`
                  relative bg-gradient-to-br from-primary-600 to-blue-600
                  text-white p-2.5 rounded-xl
                  shadow-lg shadow-primary-500/30
                  transition-all duration-500 group-hover:shadow-xl group-hover:shadow-primary-500/40
                  group-hover:scale-105 group-hover:rotate-3
                `}
              >
                <BookOpen size={22} strokeWidth={2.5} />
                {/* Sparkle effect on hover */}
                <Sparkles
                  size={12}
                  className="absolute -top-1 -right-1 text-yellow-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary-700 via-primary-600 to-blue-600">
                  Tutorly
                </span>
                <span className="text-[10px] font-medium text-gray-400 -mt-1 hidden sm:block">
                  Learn from the best
                </span>
              </div>
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1">
              <NavLink
                to="/instructors"
                icon={<Search size={16} />}
                isActive={isActivePath('/instructors')}
              >
                Find Tutors
              </NavLink>
              <NavLink
                to="/subjects"
                icon={<Users size={16} />}
                isActive={isActivePath('/subjects')}
              >
                Subjects
              </NavLink>

              {isAuthenticated && (
                <>
                  <div className="w-px h-6 bg-gray-200/50 mx-2" />
                  {user?.role === 'instructor' && (
                    <NavLink
                      to="/instructor/home"
                      icon={<Home size={16} />}
                      isActive={isActivePath('/instructor/home')}
                    >
                      Home
                    </NavLink>
                  )}
                  {user?.role !== 'admin' && (
                    <NavLink
                      to="/dashboard"
                      icon={<LayoutDashboard size={16} />}
                      isActive={isActivePath('/dashboard')}
                    >
                      Dashboard
                    </NavLink>
                  )}
                  {user?.role === 'instructor' && (
                    <NavLink
                      to="/calendar"
                      icon={<Calendar size={16} />}
                      isActive={isActivePath('/calendar')}
                    >
                      Calendar
                    </NavLink>
                  )}
                  <NavLink
                    to="/messages"
                    icon={<MessageSquare size={16} />}
                    isActive={isActivePath('/messages')}
                  >
                    Messages
                  </NavLink>
                  {user?.role === 'admin' && (
                    <NavLink
                      to="/admin"
                      icon={<Shield size={16} />}
                      isActive={isActivePath('/admin')}
                    >
                      Admin
                    </NavLink>
                  )}
                </>
              )}
            </nav>

            {/* Right side actions */}
            <div className="hidden lg:flex items-center gap-2">
              {isAuthenticated ? (
                <>
                  <WalletDropdown />
                  <NotificationBell />
                  <UserMenu user={user} onLogout={handleLogout} />
                </>
              ) : (
                <div className="flex items-center gap-3">
                  <Link
                    to="/login"
                    className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-primary-600 transition-colors rounded-xl hover:bg-white/50"
                  >
                    Log in
                  </Link>
                  <Link to="/register">
                    <Button
                      size="sm"
                      className="rounded-xl px-5 shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
                    >
                      Get Started
                    </Button>
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile Menu Button */}
            <button
              className={`
                lg:hidden p-2.5 rounded-xl transition-all duration-300
                ${mobileMenuOpen
                  ? 'bg-primary-100 text-primary-600'
                  : 'text-gray-600 hover:bg-white/50'
                }
              `}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              <div className="relative w-6 h-6">
                <Menu
                  size={24}
                  className={`
                    absolute inset-0 transition-all duration-300
                    ${mobileMenuOpen ? 'opacity-0 rotate-90 scale-50' : 'opacity-100 rotate-0 scale-100'}
                  `}
                />
                <X
                  size={24}
                  className={`
                    absolute inset-0 transition-all duration-300
                    ${mobileMenuOpen ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-50'}
                  `}
                />
              </div>
            </button>
          </div>
        </div>

        {/* Mobile Nav */}
        <div
          className={`
            lg:hidden absolute top-full left-0 right-0 mx-2 mt-2
            transition-all duration-300 ease-out
            ${mobileMenuOpen
              ? 'opacity-100 translate-y-0 pointer-events-auto'
              : 'opacity-0 -translate-y-4 pointer-events-none'
            }
          `}
        >
          <div className="p-4 rounded-2xl bg-white/95 backdrop-blur-xl border border-white/50 shadow-2xl shadow-gray-200/50">
            <div className="flex flex-col space-y-1">
              <Link
                to="/instructors"
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                  transition-colors duration-200
                  ${isActivePath('/instructors')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                  }
                `}
              >
                <Search size={18} />
                Find Tutors
              </Link>
              <Link
                to="/subjects"
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                  transition-colors duration-200
                  ${isActivePath('/subjects')
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                  }
                `}
              >
                <Users size={18} />
                Subjects
              </Link>

              {isAuthenticated ? (
                <>
                  <div className="h-px bg-gray-200/50 my-2" />

                  {/* User info in mobile */}
                  <div className="flex items-center gap-3 px-4 py-3 mb-2">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-500 to-blue-500 flex items-center justify-center shadow-lg">
                      <span className="text-white font-bold">
                        {user?.first_name[0]}{user?.last_name?.[0] || ''}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 text-sm">
                        {user?.first_name} {user?.last_name || ''}
                      </p>
                      <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                    </div>
                  </div>

                  {user?.role === 'instructor' && (
                    <Link
                      to="/instructor/home"
                      onClick={() => setMobileMenuOpen(false)}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                        transition-colors duration-200
                        ${isActivePath('/instructor/home')
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                        }
                      `}
                    >
                      <Home size={18} />
                      Home
                    </Link>
                  )}

                  {user?.role !== 'admin' && (
                    <Link
                      to="/dashboard"
                      onClick={() => setMobileMenuOpen(false)}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                        transition-colors duration-200
                        ${isActivePath('/dashboard')
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                        }
                      `}
                    >
                      <LayoutDashboard size={18} />
                      Dashboard
                    </Link>
                  )}

                  {user?.role === 'instructor' && (
                    <Link
                      to="/calendar"
                      onClick={() => setMobileMenuOpen(false)}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                        transition-colors duration-200
                        ${isActivePath('/calendar')
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                        }
                      `}
                    >
                      <Calendar size={18} />
                      Calendar
                    </Link>
                  )}

                  <Link
                    to="/messages"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`
                      flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                      transition-colors duration-200
                      ${isActivePath('/messages')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                      }
                    `}
                  >
                    <MessageSquare size={18} />
                    Messages
                  </Link>

                  {user?.role === 'admin' && (
                    <Link
                      to="/admin"
                      onClick={() => setMobileMenuOpen(false)}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold
                        transition-colors duration-200
                        ${isActivePath('/admin')
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-700 hover:bg-gray-50 hover:text-primary-600'
                        }
                      `}
                    >
                      <Shield size={18} />
                      Admin Dashboard
                    </Link>
                  )}

                  <div className="h-px bg-gray-200/50 my-2" />

                  <button
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold text-red-600 hover:bg-red-50 transition-colors w-full text-left"
                  >
                    <LogOut size={18} />
                    Log Out
                  </button>
                </>
              ) : (
                <>
                  <div className="h-px bg-gray-200/50 my-2" />
                  <div className="grid grid-cols-2 gap-3 pt-2">
                    <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                      <Button variant="outline" className="w-full justify-center rounded-xl">
                        Log in
                      </Button>
                    </Link>
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                      <Button className="w-full justify-center rounded-xl">
                        Sign up
                      </Button>
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
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
                <div className="bg-gradient-to-br from-primary-600 to-blue-600 text-white p-2 rounded-xl shadow-md group-hover:shadow-lg group-hover:scale-105 transition-all duration-300">
                  <BookOpen size={18} strokeWidth={2.5} />
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
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Python Tutors
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    JavaScript Tutors
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Machine Learning Tutors
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">About</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Who we are
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    How it works
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Careers
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Help Center
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link to="#" className="hover:text-primary-600 transition-colors">
                    Privacy Policy
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-200/50 text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} Tutorly Inc. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Global animations */}
      <style>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.2s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default Layout;
