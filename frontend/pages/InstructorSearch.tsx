import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { instructorAPI } from '../services';
import InstructorCard from '../components/InstructorCard';
import { Input, Select, Button, Card } from '../components/UIComponents';
import { Search, Filter, X } from 'lucide-react';
import { useDebounce } from '../hooks/useDebounce';

const InstructorSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filtersOpen, setFiltersOpen] = useState(false);

  // Debounce search term to avoid too many API calls
  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  // Fetch instructors with React Query
  const { data, isLoading: loading } = useQuery({
    queryKey: ['instructors', debouncedSearchTerm],
    queryFn: () => instructorAPI.searchInstructors({
      // Note: The backend API doesn't support text search yet
      // Only filtering by subject_id, price range, languages, and experience
      // We'll need to implement text search on the backend later
    }),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const instructors = data?.instructors || [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar - Mobile Collapsible */}
        <div className={`lg:w-1/4 shrink-0 ${filtersOpen ? 'block' : 'hidden lg:block'}`}>
          <Card className="sticky top-24 p-6 space-y-6">
            <div className="flex justify-between items-center lg:hidden mb-4">
              <h2 className="text-xl font-bold">Filters</h2>
              <button onClick={() => setFiltersOpen(false)}><X /></button>
            </div>
            
            <div>
              <label className="font-bold text-gray-900 block mb-3 ml-1">Subject</label>
              <Select options={[
                { value: '', label: 'All Subjects' },
                { value: 'english', label: 'English' },
                { value: 'math', label: 'Mathematics' },
                { value: 'spanish', label: 'Spanish' },
              ]} />
            </div>

            <div>
              <label className="font-bold text-gray-900 block mb-3 ml-1">Price per hour</label>
              <div className="flex items-center gap-2">
                <Input type="number" placeholder="Min" className="w-1/2" />
                <span className="text-gray-400 font-medium">-</span>
                <Input type="number" placeholder="Max" className="w-1/2" />
              </div>
            </div>

            <div>
              <label className="font-bold text-gray-900 block mb-3 ml-1">Availability</label>
              <div className="space-y-2 p-1">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(d => (
                  <label key={d} className="flex items-center gap-3 text-sm text-gray-600 cursor-pointer hover:text-primary-600 transition-colors">
                    <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                    <span className="font-medium">{d}</span>
                  </label>
                ))}
              </div>
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <div className="flex-grow">
          <div className="mb-8">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-6 tracking-tight">Find the perfect tutor</h1>
            <div className="flex gap-3">
              <div className="relative flex-grow">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search by name, subject, or keyword..."
                  className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-white/50 bg-white/60 backdrop-blur-xl focus:ring-2 focus:ring-primary-200 focus:border-primary-500 focus:bg-white/80 outline-none transition-all shadow-sm placeholder-gray-500 font-medium text-gray-900"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button 
                variant="glass" 
                className="lg:hidden px-4 rounded-2xl"
                onClick={() => setFiltersOpen(true)}
              >
                <Filter size={20} />
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="space-y-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="bg-white/40 rounded-3xl h-64 animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              {instructors.length > 0 ? (
                instructors.map(instructor => (
                  <InstructorCard key={instructor.id} instructor={instructor} />
                ))
              ) : (
                <Card className="text-center py-16">
                  <div className="mx-auto h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 mb-4">
                    <Search size={32} />
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">No tutors found</h3>
                  <p className="text-gray-500">Try adjusting your search or filters.</p>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InstructorSearch;