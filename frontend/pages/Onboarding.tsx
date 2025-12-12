/**
 * Instructor Onboarding Wizard
 *
 * 7-step onboarding process integrated with real backend API
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { instructorAPI, uploadAPI, formatAPIError } from '../services';
import { useAuth } from '../context/AuthContext';
import { Button, Input, Select, Card } from '../components/UIComponents';
import { Check, ChevronRight, ChevronLeft, DollarSign, Image, Video, X, Loader2, Plus, Trash2, GraduationCap, Briefcase } from 'lucide-react';
import type {
  LanguageInput,
  EducationInput,
  ExperienceInput,
  SubjectInput,
} from '../types/api';

// ============================================================================
// Step Configuration
// ============================================================================

const steps = [
  { id: 1, label: 'About', description: 'Tell us about yourself' },
  { id: 2, label: 'Profile', description: 'Describe your teaching' },
  { id: 3, label: 'Photo', description: 'Upload your photo' },
  { id: 4, label: 'Video', description: 'Record introduction' },
  { id: 5, label: 'Pricing', description: 'Set your rates' },
  { id: 6, label: 'Subjects', description: 'What you teach' },
  { id: 7, label: 'Background', description: 'Education & experience' },
];

// ============================================================================
// Form Data Interface
// ============================================================================

interface OnboardingFormData {
  // Step 1: About
  first_name: string;
  last_name: string;
  country: string;
  languages: LanguageInput[];
  phone_number: string;

  // Step 2: Profile
  headline: string;
  bio: string;
  years_of_experience: number;
  teaching_style: string;

  // Step 3 & 4: Media (not implemented yet)
  photo_url: string;
  video_url: string;

  // Step 5: Pricing
  hourly_rate: number;
  trial_lesson_price: number;

  // Step 6: Subjects
  subjects: SubjectInput[];

  // Step 7: Background
  education: EducationInput[];
  experience: ExperienceInput[];
  certifications: string[];
}

// ============================================================================
// Main Component
// ============================================================================

const Onboarding = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);

  // Form state
  const [formData, setFormData] = useState<OnboardingFormData>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    country: '',
    languages: [{ language: 'English', proficiency: 'native' }],
    phone_number: '',
    headline: '',
    bio: '',
    years_of_experience: 0,
    teaching_style: '',
    photo_url: '',
    video_url: '',
    hourly_rate: 20,
    trial_lesson_price: 5,
    subjects: [],
    education: [],
    experience: [],
    certifications: [],
  });

  // File upload state
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // ==========================================================================
  // API Mutations for each step
  // ==========================================================================

  const step1Mutation = useMutation({
    mutationFn: () =>
      instructorAPI.onboardingStep1({
        first_name: formData.first_name,
        last_name: formData.last_name,
        country: formData.country,
        languages: formData.languages,
        phone_number: formData.phone_number || undefined,
      }),
    onSuccess: () => {
      toast.success('About information saved');
      setCurrentStep(2);
      window.scrollTo(0, 0);
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  const step2Mutation = useMutation({
    mutationFn: (photoUrl: string) =>
      instructorAPI.onboardingStep2({
        photo_url: photoUrl,
      }),
    onSuccess: () => {
      toast.success('Profile photo saved');
      setCurrentStep(4);
      window.scrollTo(0, 0);
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  const step3Mutation = useMutation({
    mutationFn: () =>
      instructorAPI.onboardingStep3({
        bio: formData.bio,
        headline: formData.headline,
        years_of_experience: formData.years_of_experience,
        teaching_style: formData.teaching_style || undefined,
      }),
    onSuccess: () => {
      toast.success('Profile description saved');
      setCurrentStep(3); // Go to Photo upload step
      window.scrollTo(0, 0);
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  const step4Mutation = useMutation({
    mutationFn: (videoUrl: string) =>
      instructorAPI.onboardingStep4({
        video_url: videoUrl,
      }),
    onSuccess: () => {
      toast.success('Introduction video saved');
      setCurrentStep(5);
      window.scrollTo(0, 0);
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  const step6Mutation = useMutation({
    mutationFn: () =>
      instructorAPI.onboardingStep6({
        hourly_rate: formData.hourly_rate,
        trial_lesson_price: formData.trial_lesson_price,
      }),
    onSuccess: () => {
      toast.success('Pricing saved');
      setCurrentStep(7);
      window.scrollTo(0, 0);
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  const step7Mutation = useMutation({
    mutationFn: () =>
      instructorAPI.onboardingStep7({
        education: formData.education,
        experience: formData.experience,
        certifications: formData.certifications,
      }),
    onSuccess: () => {
      toast.success('Onboarding complete! Your profile is under review.');
      navigate('/dashboard');
    },
    onError: (error) => {
      const formatted = formatAPIError(error);
      toast.error(formatted.message);
    },
  });

  // ==========================================================================
  // Navigation Handlers
  // ==========================================================================

  const handleNext = async () => {
    try {
      // Validate current step before proceeding
      if (currentStep === 1) {
        if (!formData.country || formData.languages.length === 0) {
          toast.error('Please fill in all required fields');
          return;
        }
        await step1Mutation.mutateAsync();
      } else if (currentStep === 2) {
        if (!formData.headline || formData.headline.length < 10) {
          toast.error('Please provide a headline (min 10 characters)');
          return;
        }
        if (formData.headline.length > 200) {
          toast.error('Headline must be 200 characters or less');
          return;
        }
        if (formData.bio.length < 50) {
          toast.error('Bio must be at least 50 characters');
          return;
        }
        if (!formData.teaching_style?.trim()) {
          toast.error('Please provide your teaching style');
          return;
        }
        await step3Mutation.mutateAsync();
      } else if (currentStep === 3) {
        // Photo upload step
        if (!photoFile) {
          toast.error('Please upload a profile photo');
          return;
        }
        setIsUploading(true);
        try {
          // Upload photo first
          const uploadResponse = await uploadAPI.uploadPhoto(photoFile, true, true);
          // Then save the URL to the instructor profile
          await step2Mutation.mutateAsync(uploadResponse.public_url || uploadResponse.file_path);
        } catch (error) {
          const formatted = formatAPIError(error);
          toast.error(formatted.message || 'Failed to upload photo');
        } finally {
          setIsUploading(false);
        }
        return; // mutation handles step change on success
      } else if (currentStep === 4) {
        // Video upload step
        if (!videoFile) {
          toast.error('Please upload an introduction video');
          return;
        }
        setIsUploading(true);
        try {
          // Upload video first
          const uploadResponse = await uploadAPI.uploadVideo(videoFile, false);
          // Then save the URL to the instructor profile
          await step4Mutation.mutateAsync(uploadResponse.public_url || uploadResponse.file_path);
        } catch (error) {
          const formatted = formatAPIError(error);
          toast.error(formatted.message || 'Failed to upload video');
        } finally {
          setIsUploading(false);
        }
        return; // mutation handles step change on success
      } else if (currentStep === 5) {
        if (formData.hourly_rate < 5 || formData.trial_lesson_price < 1) {
          toast.error('Please set valid pricing');
          return;
        }
        await step6Mutation.mutateAsync();
      } else if (currentStep === 6) {
        // Skip subjects step for now (would need subject list)
        toast.info('Subject selection will be added in next step');
        setCurrentStep(7);
        window.scrollTo(0, 0);
      } else if (currentStep === 7) {
        await step7Mutation.mutateAsync();
      }
    } catch (error) {
      // Error already handled by mutation onError
      console.error('Step submission error:', error);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo(0, 0);
    }
  };

  const isLoading =
    step1Mutation.isPending ||
    step2Mutation.isPending ||
    step3Mutation.isPending ||
    step4Mutation.isPending ||
    step6Mutation.isPending ||
    step7Mutation.isPending ||
    isUploading;

  // ==========================================================================
  // Step Rendering
  // ==========================================================================

  const renderStep = () => {
    switch (currentStep) {
      case 1: // About
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">About You</h2>
              <p className="text-gray-500 mt-1">
                Tell us where you're from and what languages you speak.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <Input
                label="First Name"
                required
                value={formData.first_name}
                onChange={(e) =>
                  setFormData({ ...formData, first_name: e.target.value })
                }
                placeholder="John"
              />
              <Input
                label="Last Name"
                required
                value={formData.last_name}
                onChange={(e) =>
                  setFormData({ ...formData, last_name: e.target.value })
                }
                placeholder="Doe"
              />
            </div>

            <Select
              label="Country of Birth"
              options={[
                { value: '', label: 'Select Country' },
                { value: 'United States', label: 'United States' },
                { value: 'United Kingdom', label: 'United Kingdom' },
                { value: 'Canada', label: 'Canada' },
                { value: 'Australia', label: 'Australia' },
                { value: 'Germany', label: 'Germany' },
                { value: 'France', label: 'France' },
                { value: 'Spain', label: 'Spain' },
                { value: 'Italy', label: 'Italy' },
                { value: 'Other', label: 'Other' },
              ]}
              value={formData.country}
              onChange={(e) =>
                setFormData({ ...formData, country: e.target.value })
              }
            />

            <Input
              label="Phone Number (Optional)"
              type="tel"
              value={formData.phone_number}
              onChange={(e) =>
                setFormData({ ...formData, phone_number: e.target.value })
              }
              placeholder="+1 (555) 123-4567"
            />

            <div className="p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-white/60">
              <h4 className="font-bold text-sm mb-3 text-gray-700">
                Languages Spoken *
              </h4>
              <div className="flex flex-wrap gap-2">
                {formData.languages.map((lang, idx) => (
                  <span
                    key={idx}
                    className="bg-white/80 px-3 py-1.5 rounded-lg border border-gray-200 text-sm font-medium shadow-sm"
                  >
                    {lang.language} ({lang.proficiency})
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Language management will be enhanced in next update
              </p>
            </div>
          </div>
        );

      case 2: // Profile Description
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Profile Description
              </h2>
              <p className="text-gray-500 mt-1">
                This is what students will see on your profile.
              </p>
            </div>

            <div>
              <Input
                label="Headline"
                required
                placeholder="e.g. Certified Math Tutor with 5 years experience"
                value={formData.headline}
                onChange={(e) =>
                  setFormData({ ...formData, headline: e.target.value.slice(0, 200) })
                }
              />
              <p className="text-xs text-gray-500 mt-1 ml-1">
                {formData.headline.length}/200 (min 10 characters)
              </p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">
                Bio *
              </label>
              <textarea
                required
                className="block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all h-48 shadow-sm"
                placeholder="Introduce yourself to students. What's your teaching style? What can students expect from your lessons?"
                value={formData.bio}
                onChange={(e) =>
                  setFormData({ ...formData, bio: e.target.value })
                }
                minLength={50}
                maxLength={2000}
              />
              <p className="text-xs text-gray-500 mt-1 text-right">
                {formData.bio.length}/2000 (min 50 characters)
              </p>
            </div>

            <Input
              label="Years of Teaching Experience"
              type="number"
              min={0}
              max={100}
              value={formData.years_of_experience}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  years_of_experience: parseInt(e.target.value) || 0,
                })
              }
            />

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">
                Teaching Style <span className="text-red-500">*</span>
              </label>
              <textarea
                className="block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-3 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all h-32 shadow-sm"
                placeholder="Describe your teaching approach - how do you engage students? What methods do you use?"
                value={formData.teaching_style}
                onChange={(e) =>
                  setFormData({ ...formData, teaching_style: e.target.value })
                }
                maxLength={1000}
                required
              />
              <p className="text-xs text-gray-500 mt-1 ml-1">Help students understand how you teach</p>
            </div>
          </div>
        );

      case 3: // Photo
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Profile Photo</h2>
              <p className="text-gray-500 mt-1">
                Upload a professional profile photo that shows your face clearly
              </p>
            </div>

            {/* Photo Upload Area */}
            <div className="flex flex-col items-center">
              {photoPreview ? (
                <div className="relative">
                  <img
                    src={photoPreview}
                    alt="Profile preview"
                    className="w-48 h-48 rounded-full object-cover border-4 border-white shadow-lg"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setPhotoFile(null);
                      setPhotoPreview(null);
                      setFormData({ ...formData, photo_url: '' });
                    }}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1.5 hover:bg-red-600 transition-colors shadow-md"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer">
                  <div className="w-48 h-48 rounded-full border-2 border-dashed border-gray-300 bg-white/50 backdrop-blur-sm flex flex-col items-center justify-center hover:border-primary-400 hover:bg-primary-50/50 transition-all">
                    <div className="bg-primary-100 p-3 rounded-full mb-3">
                      <Image size={28} className="text-primary-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-600">Click to upload</span>
                    <span className="text-xs text-gray-400 mt-1">JPG, PNG up to 10MB</span>
                  </div>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        if (file.size > 10 * 1024 * 1024) {
                          toast.error('Photo must be less than 10MB');
                          return;
                        }
                        setPhotoFile(file);
                        const reader = new FileReader();
                        reader.onloadend = () => {
                          setPhotoPreview(reader.result as string);
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                </label>
              )}
            </div>

            {isUploading && (
              <div className="flex items-center justify-center gap-2 text-primary-600">
                <Loader2 size={20} className="animate-spin" />
                <span>Uploading photo...</span>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Photo Tips:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use a recent, high-quality photo</li>
                <li>• Make sure your face is clearly visible</li>
                <li>• Choose a neutral background</li>
                <li>• Smile and look professional</li>
              </ul>
            </div>
          </div>
        );

      case 4: // Video
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Introduction Video</h2>
              <p className="text-gray-500 mt-1">
                Record a short video introducing yourself to potential students
              </p>
            </div>

            {/* Video Upload Area */}
            <div className="flex flex-col items-center">
              {videoPreview ? (
                <div className="relative w-full max-w-md">
                  <video
                    src={videoPreview}
                    controls
                    className="w-full rounded-2xl shadow-lg"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setVideoFile(null);
                      setVideoPreview(null);
                      setFormData({ ...formData, video_url: '' });
                    }}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1.5 hover:bg-red-600 transition-colors shadow-md"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer w-full max-w-md">
                  <div className="aspect-video rounded-2xl border-2 border-dashed border-gray-300 bg-white/50 backdrop-blur-sm flex flex-col items-center justify-center hover:border-primary-400 hover:bg-primary-50/50 transition-all">
                    <div className="bg-primary-100 p-4 rounded-full mb-3">
                      <Video size={32} className="text-primary-600" />
                    </div>
                    <span className="text-sm font-medium text-gray-600">Click to upload video</span>
                    <span className="text-xs text-gray-400 mt-1">MP4, WebM up to 100MB</span>
                  </div>
                  <input
                    type="file"
                    accept="video/mp4,video/webm,video/quicktime"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        if (file.size > 100 * 1024 * 1024) {
                          toast.error('Video must be less than 100MB');
                          return;
                        }
                        setVideoFile(file);
                        const reader = new FileReader();
                        reader.onloadend = () => {
                          setVideoPreview(reader.result as string);
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                </label>
              )}
            </div>

            {isUploading && (
              <div className="flex items-center justify-center gap-2 text-primary-600">
                <Loader2 size={20} className="animate-spin" />
                <span>Uploading video...</span>
              </div>
            )}

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Video Tips:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Keep it between 1-3 minutes</li>
                <li>• Introduce yourself and your teaching style</li>
                <li>• Speak clearly and maintain eye contact</li>
                <li>• Use good lighting and minimal background noise</li>
              </ul>
            </div>
          </div>
        );

      case 5: // Pricing
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Set Your Rates
              </h2>
              <p className="text-gray-500 mt-1">
                Choose competitive pricing for your lessons
              </p>
            </div>

            <div className="bg-white/50 backdrop-blur-sm p-6 rounded-2xl border border-white/60 shadow-sm">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 bg-green-100 text-green-600 rounded-xl shadow-sm">
                  <DollarSign />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Hourly Rate</h3>
                  <p className="text-sm text-gray-500">
                    Your standard rate for a 60-minute lesson.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="5"
                  max="100"
                  step="1"
                  value={formData.hourly_rate}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      hourly_rate: parseInt(e.target.value),
                    })
                  }
                  className="flex-grow h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                />
                <div className="w-24 text-center font-bold text-2xl text-primary-700 border border-primary-100 rounded-xl py-2 bg-white shadow-sm">
                  ${formData.hourly_rate}
                </div>
              </div>
            </div>

            <div className="bg-white/50 backdrop-blur-sm p-6 rounded-2xl border border-white/60 shadow-sm">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-xl shadow-sm">
                  <DollarSign />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Trial Lesson</h3>
                  <p className="text-sm text-gray-500">
                    Discounted rate for the first lesson (optional).
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min="1"
                  max="50"
                  step="1"
                  value={formData.trial_lesson_price}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      trial_lesson_price: parseInt(e.target.value),
                    })
                  }
                  className="flex-grow h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="w-24 text-center font-bold text-2xl text-blue-700 border border-blue-100 rounded-xl py-2 bg-white shadow-sm">
                  ${formData.trial_lesson_price}
                </div>
              </div>
            </div>
          </div>
        );

      case 6: // Subjects
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Subjects You Teach
              </h2>
              <p className="text-gray-500 mt-1">
                Select the subjects you can teach
              </p>
            </div>

            <div className="p-8 bg-white/30 backdrop-blur-sm rounded-2xl border border-white/50 text-center">
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Subject Selection Coming Soon
              </h3>
              <p className="text-gray-500 max-w-md mx-auto mb-4">
                The subject selection interface will be available in the next
                update. You can add subjects later from your dashboard.
              </p>
              <p className="text-sm text-primary-600 font-medium">
                Click "Next" to continue
              </p>
            </div>
          </div>
        );

      case 7: // Education & Experience
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Education & Experience
              </h2>
              <p className="text-gray-500 mt-1">
                Share your educational background and work experience
              </p>
            </div>

            {/* Education Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GraduationCap className="text-primary-600" size={20} />
                  <h3 className="font-bold text-gray-900">Education</h3>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      education: [
                        ...formData.education,
                        {
                          institution: '',
                          degree: '',
                          field_of_study: '',
                          start_year: new Date().getFullYear() - 4,
                          end_year: new Date().getFullYear(),
                          description: '',
                        },
                      ],
                    });
                  }}
                  className="flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  <Plus size={16} /> Add Education
                </button>
              </div>

              {formData.education.length === 0 ? (
                <div className="p-4 bg-gray-50/50 rounded-xl border border-dashed border-gray-300 text-center">
                  <p className="text-gray-500 text-sm">No education added yet. Click "Add Education" to get started.</p>
                </div>
              ) : (
                formData.education.map((edu, idx) => (
                  <div key={idx} className="p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-white/60 space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-medium text-gray-500">Education #{idx + 1}</span>
                      <button
                        type="button"
                        onClick={() => {
                          const updated = formData.education.filter((_, i) => i !== idx);
                          setFormData({ ...formData, education: updated });
                        }}
                        className="text-red-500 hover:text-red-600 p-1"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    <div className="grid md:grid-cols-2 gap-3">
                      <Input
                        label="Institution"
                        required
                        placeholder="University name"
                        value={edu.institution}
                        onChange={(e) => {
                          const updated = [...formData.education];
                          updated[idx] = { ...updated[idx], institution: e.target.value };
                          setFormData({ ...formData, education: updated });
                        }}
                      />
                      <Input
                        label="Degree"
                        required
                        placeholder="e.g. Bachelor's, Master's"
                        value={edu.degree}
                        onChange={(e) => {
                          const updated = [...formData.education];
                          updated[idx] = { ...updated[idx], degree: e.target.value };
                          setFormData({ ...formData, education: updated });
                        }}
                      />
                    </div>
                    <Input
                      label="Field of Study"
                      required
                      placeholder="e.g. Mathematics, Computer Science"
                      value={edu.field_of_study}
                      onChange={(e) => {
                        const updated = [...formData.education];
                        updated[idx] = { ...updated[idx], field_of_study: e.target.value };
                        setFormData({ ...formData, education: updated });
                      }}
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        label="Start Year"
                        type="number"
                        min={1950}
                        max={new Date().getFullYear()}
                        value={edu.start_year}
                        onChange={(e) => {
                          const updated = [...formData.education];
                          updated[idx] = { ...updated[idx], start_year: parseInt(e.target.value) || 0 };
                          setFormData({ ...formData, education: updated });
                        }}
                      />
                      <Input
                        label="End Year"
                        type="number"
                        min={1950}
                        max={new Date().getFullYear() + 10}
                        value={edu.end_year || ''}
                        onChange={(e) => {
                          const updated = [...formData.education];
                          updated[idx] = { ...updated[idx], end_year: e.target.value ? parseInt(e.target.value) : undefined };
                          setFormData({ ...formData, education: updated });
                        }}
                        placeholder="Leave empty if ongoing"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">
                        Description (Optional)
                      </label>
                      <textarea
                        className="block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-2 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all h-20 text-sm shadow-sm"
                        placeholder="Relevant coursework, achievements, etc."
                        value={edu.description || ''}
                        onChange={(e) => {
                          const updated = [...formData.education];
                          updated[idx] = { ...updated[idx], description: e.target.value };
                          setFormData({ ...formData, education: updated });
                        }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Experience Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Briefcase className="text-blue-600" size={20} />
                  <h3 className="font-bold text-gray-900">Work Experience</h3>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFormData({
                      ...formData,
                      experience: [
                        ...formData.experience,
                        {
                          company: '',
                          position: '',
                          start_year: new Date().getFullYear() - 2,
                          end_year: undefined,
                          description: '',
                          is_current: false,
                        },
                      ],
                    });
                  }}
                  className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  <Plus size={16} /> Add Experience
                </button>
              </div>

              {formData.experience.length === 0 ? (
                <div className="p-4 bg-gray-50/50 rounded-xl border border-dashed border-gray-300 text-center">
                  <p className="text-gray-500 text-sm">No experience added yet. Click "Add Experience" to get started.</p>
                </div>
              ) : (
                formData.experience.map((exp, idx) => (
                  <div key={idx} className="p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-white/60 space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-medium text-gray-500">Experience #{idx + 1}</span>
                      <button
                        type="button"
                        onClick={() => {
                          const updated = formData.experience.filter((_, i) => i !== idx);
                          setFormData({ ...formData, experience: updated });
                        }}
                        className="text-red-500 hover:text-red-600 p-1"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                    <div className="grid md:grid-cols-2 gap-3">
                      <Input
                        label="Company/Organization"
                        required
                        placeholder="Company name"
                        value={exp.company}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = { ...updated[idx], company: e.target.value };
                          setFormData({ ...formData, experience: updated });
                        }}
                      />
                      <Input
                        label="Position/Role"
                        required
                        placeholder="e.g. Math Teacher, Tutor"
                        value={exp.position}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = { ...updated[idx], position: e.target.value };
                          setFormData({ ...formData, experience: updated });
                        }}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        label="Start Year"
                        type="number"
                        min={1950}
                        max={new Date().getFullYear()}
                        value={exp.start_year}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = { ...updated[idx], start_year: parseInt(e.target.value) || 0 };
                          setFormData({ ...formData, experience: updated });
                        }}
                      />
                      <Input
                        label="End Year"
                        type="number"
                        min={1950}
                        max={new Date().getFullYear() + 10}
                        value={exp.end_year || ''}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = { ...updated[idx], end_year: e.target.value ? parseInt(e.target.value) : undefined };
                          setFormData({ ...formData, experience: updated });
                        }}
                        placeholder="Leave empty if current"
                        disabled={exp.is_current}
                      />
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={exp.is_current}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = {
                            ...updated[idx],
                            is_current: e.target.checked,
                            end_year: e.target.checked ? undefined : updated[idx].end_year
                          };
                          setFormData({ ...formData, experience: updated });
                        }}
                        className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">I currently work here</span>
                    </label>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-1.5 ml-1">
                        Description (Optional)
                      </label>
                      <textarea
                        className="block w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-4 py-2 focus:border-primary-500 focus:ring-2 focus:ring-primary-200/50 focus:bg-white/80 transition-all h-20 text-sm shadow-sm"
                        placeholder="Key responsibilities, achievements, etc."
                        value={exp.description || ''}
                        onChange={(e) => {
                          const updated = [...formData.experience];
                          updated[idx] = { ...updated[idx], description: e.target.value };
                          setFormData({ ...formData, experience: updated });
                        }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Summary */}
            <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-blue-50 rounded-2xl border border-primary-100">
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Almost Done!
              </h3>
              <p className="text-gray-600 text-sm">
                {formData.education.length === 0 && formData.experience.length === 0
                  ? "You can add education and experience now, or skip and add them later from your dashboard."
                  : `You've added ${formData.education.length} education ${formData.education.length === 1 ? 'entry' : 'entries'} and ${formData.experience.length} experience ${formData.experience.length === 1 ? 'entry' : 'entries'}.`
                }
              </p>
              <p className="text-primary-600 font-medium text-sm mt-2">
                Click "Finish" to submit your profile for review.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // ==========================================================================
  // Render
  // ==========================================================================

  return (
    <div className="min-h-screen py-12">
      <div className="container max-w-3xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-12">
          <div className="flex justify-between mb-4 relative">
            {/* Background line */}
            <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200/50 -z-10 -translate-y-1/2 rounded-full" />
            {/* Progress line */}
            <div
              className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-primary-600 to-blue-500 -z-10 -translate-y-1/2 rounded-full transition-all duration-500"
              style={{
                width: `${((currentStep - 1) / (steps.length - 1)) * 100}%`,
              }}
            />

            {steps.map((step) => {
              const isActive = step.id === currentStep;
              const isCompleted = step.id < currentStep;
              return (
                <div key={step.id} className="flex flex-col items-center gap-2 px-2">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all duration-300 border-2 ${
                      isActive
                        ? 'bg-primary-600 border-primary-600 text-white scale-110 shadow-lg shadow-primary-500/30'
                        : isCompleted
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'bg-white border-gray-300 text-gray-400'
                    }`}
                  >
                    {isCompleted ? <Check size={20} /> : step.id}
                  </div>
                  <span
                    className={`text-xs font-bold hidden sm:block ${
                      isActive ? 'text-primary-700' : 'text-gray-400'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Form Card */}
        <Card className="p-8 md:p-12 min-h-[550px] flex flex-col shadow-2xl shadow-blue-900/5">
          <div className="flex-grow">{renderStep()}</div>

          <div className="flex justify-between pt-8 border-t border-gray-100/50 mt-8">
            <Button
              variant="ghost"
              onClick={handleBack}
              disabled={currentStep === 1 || isLoading}
              className="gap-2 rounded-xl"
            >
              <ChevronLeft size={20} /> Back
            </Button>
            <Button
              onClick={handleNext}
              isLoading={isLoading}
              className="gap-2 px-8 rounded-xl"
            >
              {currentStep === steps.length ? 'Finish' : 'Next'}{' '}
              <ChevronRight size={20} />
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Onboarding;
