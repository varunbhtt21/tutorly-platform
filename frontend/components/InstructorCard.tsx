import React from 'react';
import { Link } from 'react-router-dom';
import { InstructorProfile } from '../types';
import { Star, Globe } from 'lucide-react';
import { Button, Badge, Card } from './UIComponents';

interface Props {
  instructor: InstructorProfile;
}

const InstructorCard: React.FC<Props> = ({ instructor }) => {
  return (
    <Card className="flex flex-col md:flex-row overflow-hidden group border-white/60 hover:border-white/80 hover:shadow-2xl hover:shadow-primary-500/10 transition-all duration-300">
      {/* Left / Top - Image */}
      <div className="w-full md:w-64 shrink-0 relative overflow-hidden">
        <img 
          src={instructor.photo_url || `https://ui-avatars.com/api/?name=${instructor.user.first_name}+${instructor.user.last_name}&background=random`} 
          alt={instructor.user.first_name}
          className="w-full h-56 md:h-full object-cover group-hover:scale-110 transition-transform duration-700"
        />
        {instructor.is_onboarding_complete && (
          <div className="absolute top-3 left-3">
            <div className="bg-white/90 backdrop-blur text-green-700 text-xs font-bold px-2.5 py-1 rounded-lg shadow-sm flex items-center gap-1 border border-white/50">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Available
            </div>
          </div>
        )}
      </div>

      {/* Right / Content */}
      <div className="p-6 flex flex-col flex-grow">
        <div className="flex justify-between items-start mb-3">
          <div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
              {instructor.user.first_name} {instructor.user.last_name}
            </h3>
            <p className="text-sm text-gray-500 flex items-center gap-1.5 mt-1 font-medium">
              <Globe size={14} /> {instructor.country_of_birth || 'Global'}
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 bg-yellow-100/50 px-2 py-1 rounded-lg border border-yellow-100">
              <Star size={16} className="text-yellow-500 fill-yellow-500" />
              <span className="font-bold text-gray-900">{instructor.rating}</span>
            </div>
            <div className="text-xs text-gray-400 font-medium mt-1">
              {instructor.review_count} reviews
            </div>
          </div>
        </div>

        <h4 className="text-gray-800 font-semibold mb-2 line-clamp-1">
          {instructor.headline}
        </h4>
        
        <p className="text-gray-600 text-sm line-clamp-2 mb-5 flex-grow leading-relaxed">
          {instructor.bio}
        </p>

        <div className="flex flex-wrap gap-2 mb-6">
          {instructor.subjects.slice(0, 3).map((s, i) => (
            <Badge key={i} variant="primary">{s.subject.name}</Badge>
          ))}
          {instructor.languages.slice(0, 2).map((l, i) => (
            <Badge key={`l-${i}`} variant="secondary">{l.language}</Badge>
          ))}
        </div>

        <div className="pt-4 border-t border-gray-100/50 flex items-center justify-between mt-auto">
          <div>
            <span className="text-2xl font-bold text-gray-900">${instructor.hourly_rate}</span>
            <span className="text-sm text-gray-500 font-medium">/hour</span>
          </div>
          <Link to={`/instructors/${instructor.id}`}>
            <Button className="shadow-md shadow-primary-500/20">View Profile</Button>
          </Link>
        </div>
      </div>
    </Card>
  );
};

export default InstructorCard;