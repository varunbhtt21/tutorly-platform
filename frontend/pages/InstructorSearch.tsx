/**
 * Find Tutors Page
 * Modern, Figma-inspired design with micro-animations and polished UX
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { instructorAPI, subjectsAPI } from '../services';
import InstructorCard from '../components/InstructorCard';
import { Input, Select, Button, Card } from '../components/UIComponents';
import {
  Search,
  Filter,
  X,
  SlidersHorizontal,
  Sparkles,
  Users,
  BookOpen,
  Clock,
  ChevronDown,
  Check
} from 'lucide-react';
import { useDebounce } from '../hooks/useDebounce';

// Animated background blob component
const AnimatedBlob: React.FC<{ className?: string; delay?: number }> = ({ className = '', delay = 0 }) => (
  <div
    className={`absolute rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob ${className}`}
    style={{ animationDelay: `${delay}s` }}
  />
);

// Stats counter with animation
const StatCounter: React.FC<{ value: number; label: string; icon: React.ReactNode }> = ({ value, label, icon }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const duration = 1500;
    const steps = 30;
    const increment = value / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  return (
    <div className="flex items-center gap-3 group">
      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-100 to-blue-100 flex items-center justify-center text-primary-600 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <div>
        <div className="text-xl font-bold text-gray-900">{count.toLocaleString()}+</div>
        <div className="text-xs text-gray-500 font-medium">{label}</div>
      </div>
    </div>
  );
};

// Filter chip component with animation
const FilterChip: React.FC<{
  label: string;
  selected?: boolean;
  onClick?: () => void;
}> = ({ label, selected = false, onClick }) => (
  <button
    onClick={onClick}
    className={`
      px-4 py-2 rounded-full text-sm font-medium transition-all duration-300
      transform hover:scale-105 active:scale-95
      ${selected
        ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/30'
        : 'bg-white/70 text-gray-700 hover:bg-white border border-gray-200/50 hover:border-primary-200 hover:text-primary-600'
      }
    `}
  >
    {label}
  </button>
);

// Enhanced skeleton loader
const SkeletonCard: React.FC = () => (
  <div className="bg-white/60 backdrop-blur-xl rounded-2xl border border-white/50 overflow-hidden animate-pulse">
    <div className="flex flex-col md:flex-row">
      <div className="w-full md:w-64 h-56 md:h-auto bg-gradient-to-br from-gray-200 to-gray-100 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent skeleton-shimmer" />
      </div>
      <div className="p-6 flex-grow space-y-4">
        <div className="flex justify-between">
          <div className="space-y-2">
            <div className="h-6 w-40 bg-gray-200 rounded-lg" />
            <div className="h-4 w-24 bg-gray-100 rounded-lg" />
          </div>
          <div className="h-8 w-16 bg-yellow-100 rounded-lg" />
        </div>
        <div className="h-5 w-3/4 bg-gray-200 rounded-lg" />
        <div className="space-y-2">
          <div className="h-4 w-full bg-gray-100 rounded-lg" />
          <div className="h-4 w-2/3 bg-gray-100 rounded-lg" />
        </div>
        <div className="flex gap-2">
          <div className="h-7 w-20 bg-primary-100 rounded-lg" />
          <div className="h-7 w-20 bg-sky-100 rounded-lg" />
          <div className="h-7 w-20 bg-gray-100 rounded-lg" />
        </div>
        <div className="pt-4 border-t border-gray-100 flex justify-between items-center">
          <div className="h-8 w-24 bg-gray-200 rounded-lg" />
          <div className="h-10 w-28 bg-primary-200 rounded-xl" />
        </div>
      </div>
    </div>
  </div>
);

const InstructorSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedDays, setSelectedDays] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });
  const [sortBy, setSortBy] = useState<'rating' | 'price_low' | 'price_high' | 'reviews'>('rating');

  const [activeQuickFilter, setActiveQuickFilter] = useState('All');

  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Fetch subjects from API
  const { data: subjectsData } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => subjectsAPI.getSubjects(),
    staleTime: 10 * 60 * 1000, // Cache subjects for 10 minutes
  });

  // Build subject options for dropdown from API data
  const subjectOptions = useMemo(() => {
    const options = [{ value: '', label: 'All Subjects' }];
    if (subjectsData?.subjects) {
      subjectsData.subjects.forEach((subject) => {
        options.push({ value: subject.slug, label: subject.name });
      });
    }
    return options;
  }, [subjectsData]);

  // Build quick filter chips from first 6 subjects
  const quickFilters = useMemo(() => {
    const filters = ['All'];
    if (subjectsData?.subjects) {
      // Take first 6 subjects for quick filters
      subjectsData.subjects.slice(0, 6).forEach((subject) => {
        filters.push(subject.name);
      });
    }
    return filters;
  }, [subjectsData]);

  const { data, isLoading: loading, isFetching } = useQuery({
    queryKey: ['instructors', debouncedSearchTerm, selectedSubject, priceRange],
    queryFn: () => instructorAPI.searchInstructors({}),
    staleTime: 2 * 60 * 1000,
  });

  const instructors = data?.instructors || [];

  const toggleDay = (day: string) => {
    setSelectedDays(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20 relative overflow-hidden">
      {/* CSS for animations */}
      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -30px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(30px, 10px) scale(1.05); }
        }
        .animate-blob { animation: blob 8s ease-in-out infinite; }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .skeleton-shimmer { animation: shimmer 1.5s infinite; }

        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up { animation: fadeInUp 0.5s ease-out forwards; }

        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-slide-in-right { animation: slideInRight 0.3s ease-out forwards; }

        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        .animate-scale-in { animation: scaleIn 0.2s ease-out forwards; }
      `}</style>

      {/* Animated background blobs */}
      <AnimatedBlob className="w-96 h-96 bg-blue-300 -top-48 -left-48" delay={0} />
      <AnimatedBlob className="w-80 h-80 bg-purple-300 top-1/4 -right-40" delay={2} />
      <AnimatedBlob className="w-72 h-72 bg-pink-300 bottom-1/4 left-1/4" delay={4} />

      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Hero Section */}
        <div className="text-center mb-10 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-100 to-blue-100 rounded-full mb-4">
            <Sparkles size={16} className="text-primary-600" />
            <span className="text-sm font-semibold text-primary-700">Find Your Perfect Match</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
            Learn from the <span className="bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">Best Tutors</span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
            Connect with expert tutors who are passionate about helping you succeed.
            Personalized learning, flexible scheduling.
          </p>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mb-8">
            <StatCounter value={2500} label="Expert Tutors" icon={<Users size={18} />} />
            <StatCounter value={150} label="Subjects" icon={<BookOpen size={18} />} />
            <StatCounter value={50000} label="Lessons Completed" icon={<Clock size={18} />} />
          </div>
        </div>

        {/* Search Bar - Enhanced */}
        <div className="max-w-3xl mx-auto mb-8 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary-500 via-blue-500 to-purple-500 rounded-2xl blur-lg opacity-20 group-hover:opacity-40 transition-opacity duration-500" />
            <div className="relative flex items-center bg-white/90 backdrop-blur-xl rounded-2xl border border-white/50 shadow-xl shadow-gray-200/50 overflow-hidden">
              <div className="pl-5">
                <Search className={`text-gray-400 transition-colors duration-300 ${searchTerm ? 'text-primary-500' : ''}`} size={22} />
              </div>
              <input
                type="text"
                placeholder="Search by name, subject, or skill..."
                className="flex-grow px-4 py-4 bg-transparent focus:outline-none text-gray-900 placeholder-gray-400 font-medium"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="p-2 mr-2 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X size={18} className="text-gray-400" />
                </button>
              )}
              <button
                onClick={() => setFiltersOpen(!filtersOpen)}
                className={`
                  flex items-center gap-2 px-5 py-4 border-l border-gray-200/50
                  hover:bg-gray-50 transition-all duration-300 font-medium
                  ${filtersOpen ? 'bg-primary-50 text-primary-600' : 'text-gray-600'}
                `}
              >
                <SlidersHorizontal size={18} />
                <span className="hidden sm:inline">Filters</span>
                {(selectedDays.length > 0 || selectedSubject || priceRange.min || priceRange.max) && (
                  <span className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Quick Filter Chips */}
        <div className="flex flex-wrap justify-center gap-2 mb-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          {quickFilters.map((filter) => (
            <FilterChip
              key={filter}
              label={filter}
              selected={activeQuickFilter === filter}
              onClick={() => setActiveQuickFilter(filter)}
            />
          ))}
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar - Enhanced */}
          <div className={`
            lg:w-80 shrink-0 transition-all duration-500 ease-out
            ${filtersOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 lg:max-h-none opacity-0 lg:opacity-100 overflow-hidden lg:overflow-visible'}
          `}>
            <Card className="sticky top-24 p-6 space-y-6 animate-slide-in-right">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Filter size={18} className="text-primary-600" />
                  Filters
                </h2>
                <button
                  onClick={() => setFiltersOpen(false)}
                  className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Subject Filter */}
              <div className="space-y-3">
                <label className="font-semibold text-gray-800 block text-sm">Subject</label>
                <div className="relative">
                  <Select
                    options={subjectOptions}
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                  />
                </div>
              </div>

              {/* Price Range */}
              <div className="space-y-3">
                <label className="font-semibold text-gray-800 block text-sm">Hourly Rate</label>
                <div className="flex items-center gap-3">
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                    <Input
                      type="number"
                      placeholder="Min"
                      className="pl-7"
                      value={priceRange.min}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, min: e.target.value }))}
                    />
                  </div>
                  <span className="text-gray-300 font-medium">—</span>
                  <div className="relative flex-1">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
                    <Input
                      type="number"
                      placeholder="Max"
                      className="pl-7"
                      value={priceRange.max}
                      onChange={(e) => setPriceRange(prev => ({ ...prev, max: e.target.value }))}
                    />
                  </div>
                </div>
              </div>

              {/* Availability */}
              <div className="space-y-3">
                <label className="font-semibold text-gray-800 block text-sm">Availability</label>
                <div className="grid grid-cols-7 gap-1">
                  {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, i) => {
                    const fullDay = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i];
                    const isSelected = selectedDays.includes(fullDay);
                    return (
                      <button
                        key={i}
                        onClick={() => toggleDay(fullDay)}
                        className={`
                          w-full aspect-square rounded-lg text-xs font-bold
                          transition-all duration-200 transform hover:scale-110
                          ${isSelected
                            ? 'bg-primary-600 text-white shadow-md shadow-primary-500/30'
                            : 'bg-gray-100 text-gray-600 hover:bg-primary-100 hover:text-primary-600'
                          }
                        `}
                      >
                        {day}
                      </button>
                    );
                  })}
                </div>
                <p className="text-xs text-gray-500">
                  {selectedDays.length > 0
                    ? `Selected: ${selectedDays.join(', ')}`
                    : 'Click to filter by availability'
                  }
                </p>
              </div>

              {/* Sort By */}
              <div className="space-y-3">
                <label className="font-semibold text-gray-800 block text-sm">Sort By</label>
                <div className="space-y-2">
                  {[
                    { value: 'rating', label: 'Highest Rated' },
                    { value: 'reviews', label: 'Most Reviews' },
                    { value: 'price_low', label: 'Price: Low to High' },
                    { value: 'price_high', label: 'Price: High to Low' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setSortBy(option.value as typeof sortBy)}
                      className={`
                        w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm
                        transition-all duration-200
                        ${sortBy === option.value
                          ? 'bg-primary-50 text-primary-700 font-medium'
                          : 'text-gray-600 hover:bg-gray-50'
                        }
                      `}
                    >
                      {option.label}
                      {sortBy === option.value && (
                        <Check size={16} className="text-primary-600" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Clear Filters */}
              {(selectedSubject || selectedDays.length > 0 || priceRange.min || priceRange.max) && (
                <Button
                  variant="ghost"
                  className="w-full"
                  onClick={() => {
                    setSelectedSubject('');
                    setSelectedDays([]);
                    setPriceRange({ min: '', max: '' });
                  }}
                >
                  Clear All Filters
                </Button>
              )}
            </Card>
          </div>

          {/* Main Content */}
          <div className="flex-grow">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {loading ? 'Finding tutors...' : `${instructors.length} tutors found`}
                </h2>
                {activeQuickFilter !== 'All' && (
                  <p className="text-sm text-gray-500">Filtered by: {activeQuickFilter}</p>
                )}
              </div>
              {isFetching && !loading && (
                <div className="flex items-center gap-2 text-sm text-primary-600">
                  <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                  Updating...
                </div>
              )}
            </div>

            {/* Results */}
            {loading ? (
              <div className="space-y-6">
                {[1, 2, 3].map((i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            ) : instructors.length > 0 ? (
              <div className="space-y-6">
                {instructors.map((instructor, index) => (
                  <div
                    key={instructor.id}
                    className="animate-fade-in-up"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <InstructorCard instructor={instructor} />
                  </div>
                ))}
              </div>
            ) : (
              <Card className="text-center py-16 animate-scale-in">
                <div className="mx-auto w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-50 rounded-2xl flex items-center justify-center text-gray-400 mb-6 rotate-3">
                  <Search size={36} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">No tutors found</h3>
                <p className="text-gray-500 mb-6 max-w-sm mx-auto">
                  We couldn't find any tutors matching your criteria. Try adjusting your filters or search term.
                </p>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedSubject('');
                    setSelectedDays([]);
                    setPriceRange({ min: '', max: '' });
                    setActiveQuickFilter('All');
                  }}
                >
                  Clear All Filters
                </Button>
              </Card>
            )}

            {/* Load More */}
            {instructors.length > 0 && instructors.length >= 10 && (
              <div className="text-center mt-10">
                <Button variant="outline" size="lg" className="px-8">
                  Load More Tutors
                  <ChevronDown size={18} className="ml-2" />
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstructorSearch;
