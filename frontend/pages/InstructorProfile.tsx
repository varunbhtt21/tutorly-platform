import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'sonner';
import { instructorAPI, messagingAPI } from '../services';
import { Button, Badge, Card } from '../components/UIComponents';
import { PlayCircle, MessageSquare, Check, Loader2 } from 'lucide-react';
import { getMediaUrl } from '../lib/axios';
import { BookingModal } from '../components/booking';
import { ScheduleSection } from '../components/instructor';
import { useAuth } from '../context/AuthContext';

const InstructorProfile = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // Handle slot selection from schedule - opens booking modal
  const handleSlotSelect = () => {
    setShowBookingModal(true);
  };

  // Fetch instructor profile with React Query
  const { data: instructor, isLoading: loading, isError } = useQuery({
    queryKey: ['instructor', id],
    queryFn: () => {
      if (!id) throw new Error('Instructor ID is required');
      return instructorAPI.getProfileById(parseInt(id));
    },
    enabled: !!id, // Only run query if id exists
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Handle Send Message button click
  const handleSendMessage = async () => {
    // Check if user is authenticated
    if (!isAuthenticated || !user) {
      toast.error('Please log in to send a message');
      navigate('/login', { state: { from: `/instructor/${id}` } });
      return;
    }

    // Check if user is trying to message themselves
    if (instructor?.user_id === user.id) {
      toast.error("You can't message yourself");
      return;
    }

    setIsSendingMessage(true);
    try {
      // Start or get existing conversation with the instructor
      const conversation = await messagingAPI.startConversation({
        recipient_id: instructor!.user_id,
      });

      // Navigate to the messages page with the conversation selected
      navigate(`/messages?conversation=${conversation.id}`);
    } catch (error: any) {
      console.error('Failed to start conversation:', error);
      toast.error(error.response?.data?.detail || 'Failed to start conversation. Please try again.');
    } finally {
      setIsSendingMessage(false);
    }
  };

  if (loading) return <div className="h-screen flex items-center justify-center"><div className="animate-spin h-10 w-10 border-4 border-primary-600 rounded-full border-t-transparent"></div></div>;
  if (isError || !instructor) return <div className="text-center py-20">Instructor not found</div>;

  return (
    <div className="min-h-screen pb-12">
      {/* Header Background with Liquid Glass effect override */}
      <div className="h-60 relative overflow-hidden">
         <div className="absolute inset-0 bg-gradient-to-r from-primary-900/80 to-blue-900/80 backdrop-blur-sm"></div>
         <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
      </div>

      <div className="container mx-auto px-4 -mt-32 relative z-10">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Column - Main Content */}
          <div className="lg:w-2/3 space-y-6">
            {/* Profile Header Card */}
            <Card className="p-8">
              <div className="flex flex-col sm:flex-row gap-8 items-start">
                <div className="relative shrink-0">
                  <img
                    src={getMediaUrl(instructor.profile_photo_url) || 'https://via.placeholder.com/144'}
                    className="w-36 h-36 rounded-2xl object-cover border-4 border-white shadow-xl"
                    alt="Profile"
                  />
                  <div className="absolute -bottom-3 -right-3 bg-white p-1.5 rounded-xl shadow-lg border border-gray-100">
                    <img src={`https://flagcdn.com/w40/${instructor.country_of_birth?.slice(0,2).toLowerCase() || 'us'}.png`} className="w-8 h-5 object-cover rounded-md" alt="Flag" />
                  </div>
                </div>
                <div className="flex-grow w-full">
                  <div className="flex justify-between items-start">
                    <div>
                      <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        {instructor.first_name
                          ? `${instructor.first_name}${instructor.last_name ? ` ${instructor.last_name.charAt(0)}.` : ''}`
                          : `Instructor #${instructor.id}`}
                      </h1>
                      <p className="text-lg text-primary-600 font-medium mb-3">{instructor.headline || 'Professional Tutor'}</p>
                    </div>
                    {/* TODO: Rating/Review system not yet implemented in backend */}
                    {/* <div className="flex flex-col items-end bg-white/50 p-2 rounded-xl border border-white/60 backdrop-blur-sm">
                       <div className="flex items-center gap-1">
                        <Star className="text-yellow-400 fill-yellow-400" size={20} />
                        <span className="text-xl font-bold text-gray-900">5.0</span>
                      </div>
                      <span className="text-xs text-gray-500 font-semibold">0 reviews</span>
                    </div> */}
                  </div>

                  <div className="flex flex-wrap gap-2 mt-2">
                    {/* TODO: Subjects not yet implemented in backend - will be added in future */}
                    {instructor.languages.map(l => (
                      <Badge key={l.language} variant="neutral">{l.language} ({l.proficiency})</Badge>
                    ))}
                  </div>
                </div>
              </div>
            </Card>

            {/* About */}
            <Card className="p-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">About Me</h2>
              <p className="text-gray-600 leading-relaxed whitespace-pre-line text-lg">{instructor.bio}</p>
            </Card>

            {/* Schedule Section */}
            <Card className="p-8">
              <ScheduleSection
                instructorId={instructor.id}
                onSlotSelect={handleSlotSelect}
                showFullScheduleLink={true}
              />
            </Card>
          </div>

          {/* Right Column - Video & Booking Card */}
          <div className="lg:w-1/3">
            <div className="sticky top-28 space-y-6">
              {/* Introduction Video */}
              <Card className="p-6 overflow-hidden">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Introduction Video</h2>
                {instructor.intro_video_url ? (
                  <video
                    src={getMediaUrl(instructor.intro_video_url)}
                    controls
                    className="w-full aspect-video rounded-xl bg-gray-900 shadow-inner"
                    poster={getMediaUrl(instructor.profile_photo_url)}
                  />
                ) : (
                  <div className="aspect-video bg-gray-900 rounded-xl flex flex-col items-center justify-center text-white relative overflow-hidden group cursor-pointer shadow-inner">
                    <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors"></div>
                    <div className="w-16 h-16 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center relative z-10 group-hover:scale-110 transition-transform duration-300 border border-white/30">
                        <PlayCircle size={32} className="text-white fill-white/20" />
                    </div>
                    <p className="relative z-10 mt-3 font-medium text-white/90 text-sm">Video coming soon</p>
                  </div>
                )}
              </Card>

              {/* Trial Lesson Price & Booking Card */}
              <Card className="p-8 border-t-8 border-t-primary-500 shadow-2xl shadow-primary-900/5">
                <div className="text-center mb-8">
                  <p className="text-gray-500 font-medium mb-2 text-sm uppercase tracking-wider">Trial Lesson Price</p>
                  <div className="text-5xl font-extrabold text-gray-900">
                    ₹{instructor.trial_lesson_price?.toString() || instructor.hourly_rate?.toString() || '0'}
                  </div>
                </div>

                <div className="space-y-4 mb-8">
                  <Button
                    onClick={() => setShowBookingModal(true)}
                    className="w-full py-4 text-lg shadow-xl shadow-primary-500/30"
                  >
                    Book Trial Lesson
                  </Button>
                  <Button
                    variant="glass"
                    className="w-full gap-2"
                    onClick={handleSendMessage}
                    disabled={isSendingMessage}
                  >
                    {isSendingMessage ? (
                      <Loader2 size={18} className="animate-spin" />
                    ) : (
                      <MessageSquare size={18} />
                    )}
                    {isSendingMessage ? 'Starting conversation...' : 'Send Message'}
                  </Button>
                </div>

                <div className="space-y-4 text-sm text-gray-600 bg-gray-50/50 p-4 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="bg-green-100 p-1.5 rounded-full text-green-600"><Check size={14} strokeWidth={3} /></div>
                    <span className="font-medium">Free cancellation up to 24h</span>
                  </div>
                  <div className="flex items-center gap-3">
                     <div className="bg-blue-100 p-1.5 rounded-full text-blue-600"><Check size={14} strokeWidth={3} /></div>
                    <span className="font-medium">100% Satisfaction Guarantee</span>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      <BookingModal
        isOpen={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        instructorId={instructor.id}
        instructorName={instructor.first_name || `Instructor #${instructor.id}`}
        instructorPhoto={instructor.profile_photo_url}
        trialPrice={parseFloat(instructor.trial_lesson_price?.toString() || instructor.hourly_rate?.toString() || '0')}
        hourlyRate={parseFloat(instructor.hourly_rate?.toString() || '0')}
      />
    </div>
  );
};

export default InstructorProfile;