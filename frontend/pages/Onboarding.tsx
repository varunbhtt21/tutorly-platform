/**
 * Instructor Onboarding Wizard - Airbnb Style
 *
 * Full viewport single questions, smooth transitions, and celebration on completion.
 */

import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import confetti from 'canvas-confetti';
import { instructorAPI, uploadAPI, formatAPIError } from '../services';
import { useAuth } from '../context/AuthContext';
import {
  ChevronRight,
  ChevronLeft,
  DollarSign,
  Camera,
  Video,
  X,
  Loader2,
  Plus,
  Trash2,
  GraduationCap,
  Briefcase,
  Globe,
  Languages,
  User,
  FileText,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';
import type {
  LanguageInput,
  EducationInput,
  ExperienceInput,
  SubjectInput,
} from '../types/api';

// ============================================================================
// Step Configuration - Simplified for better UX
// ============================================================================

const steps = [
  { id: 1, label: 'About', icon: User },
  { id: 2, label: 'Profile', icon: FileText },
  { id: 3, label: 'Photo', icon: Camera },
  { id: 4, label: 'Video', icon: Video },
  { id: 5, label: 'Pricing', icon: DollarSign },
  { id: 6, label: 'Subjects', icon: GraduationCap },
  { id: 7, label: 'Background', icon: Briefcase },
];

// ============================================================================
// Form Data Interface
// ============================================================================

interface OnboardingFormData {
  first_name: string;
  last_name: string;
  country: string;
  languages: LanguageInput[];
  phone_number: string;
  headline: string;
  bio: string;
  years_of_experience: number;
  teaching_style: string;
  photo_url: string;
  video_url: string;
  hourly_rate: number;
  trial_lesson_price: number;
  subjects: SubjectInput[];
  education: EducationInput[];
  experience: ExperienceInput[];
  certifications: string[];
}

// ============================================================================
// Confetti Celebration
// ============================================================================

const triggerConfetti = () => {
  const duration = 3000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

  const randomInRange = (min: number, max: number) =>
    Math.random() * (max - min) + min;

  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now();
    if (timeLeft <= 0) {
      return clearInterval(interval);
    }
    const particleCount = 50 * (timeLeft / duration);
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
    });
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
    });
  }, 250);
};

// ============================================================================
// Main Component
// ============================================================================

const Onboarding = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [showCompletion, setShowCompletion] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

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
    hourly_rate: 25,
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
  // API Mutations
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
      goToStep(2);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
    },
  });

  const step2Mutation = useMutation({
    mutationFn: (photoUrl: string) =>
      instructorAPI.onboardingStep2({ photo_url: photoUrl }),
    onSuccess: () => {
      toast.success('Profile photo saved');
      goToStep(4);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
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
      goToStep(3);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
    },
  });

  const step4Mutation = useMutation({
    mutationFn: (videoUrl: string) =>
      instructorAPI.onboardingStep4({ video_url: videoUrl }),
    onSuccess: () => {
      toast.success('Introduction video saved');
      goToStep(5);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
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
      goToStep(7);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
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
      // Invalidate dashboard cache so it refetches with is_onboarding_complete: true
      queryClient.invalidateQueries({ queryKey: ['instructorDashboard'] });
      setShowCompletion(true);
      triggerConfetti();
      setTimeout(() => {
        navigate('/dashboard');
      }, 4000);
    },
    onError: (error) => {
      toast.error(formatAPIError(error).message);
    },
  });

  // ==========================================================================
  // Navigation
  // ==========================================================================

  const goToStep = (step: number) => {
    setCurrentStep(step);
  };

  const handleNext = async () => {
    try {
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
        if (!photoFile) {
          toast.error('Please upload a profile photo');
          return;
        }
        setIsUploading(true);
        try {
          const uploadResponse = await uploadAPI.uploadPhoto(photoFile, true, true);
          await step2Mutation.mutateAsync(uploadResponse.public_url || uploadResponse.file_path);
        } finally {
          setIsUploading(false);
        }
      } else if (currentStep === 4) {
        if (!videoFile) {
          toast.error('Please upload an introduction video');
          return;
        }
        setIsUploading(true);
        try {
          const uploadResponse = await uploadAPI.uploadVideo(videoFile, false);
          await step4Mutation.mutateAsync(uploadResponse.public_url || uploadResponse.file_path);
        } finally {
          setIsUploading(false);
        }
      } else if (currentStep === 5) {
        if (formData.hourly_rate < 5) {
          toast.error('Please set a valid hourly rate');
          return;
        }
        await step6Mutation.mutateAsync();
      } else if (currentStep === 6) {
        goToStep(7);
      } else if (currentStep === 7) {
        await step7Mutation.mutateAsync();
      }
    } catch (error) {
      console.error('Step submission error:', error);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      goToStep(currentStep - 1);
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
  // Completion Screen
  // ==========================================================================

  if (showCompletion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-8 animate-bounce">
            <CheckCircle2 className="w-12 h-12 text-green-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            You're all set!
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Your profile is under review.
          </p>
          <p className="text-gray-500">
            Redirecting to your dashboard...
          </p>
          <div className="mt-8 flex justify-center">
            <Sparkles className="w-6 h-6 text-yellow-500 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================================
  // Step Content Renderer
  // ==========================================================================

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Globe className="w-8 h-8 text-primary-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Where are you from?
              </h1>
              <p className="text-lg text-gray-500">
                Help students know more about your background.
              </p>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) =>
                      setFormData({ ...formData, first_name: e.target.value })
                    }
                    className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) =>
                      setFormData({ ...formData, last_name: e.target.value })
                    }
                    className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors"
                    placeholder="Doe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Country of Birth <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.country}
                  onChange={(e) =>
                    setFormData({ ...formData, country: e.target.value })
                  }
                  className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors appearance-none bg-white"
                >
                  <option value="">Select your country</option>
                  <option value="United States">United States</option>
                  <option value="United Kingdom">United Kingdom</option>
                  <option value="Canada">Canada</option>
                  <option value="Australia">Australia</option>
                  <option value="Germany">Germany</option>
                  <option value="France">France</option>
                  <option value="Spain">Spain</option>
                  <option value="Italy">Italy</option>
                  <option value="India">India</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Languages className="w-4 h-4 inline mr-1" />
                  Languages You Speak
                </label>
                <div className="flex flex-wrap gap-2 p-4 bg-gray-50 rounded-xl border-2 border-gray-200">
                  {formData.languages.map((lang, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-4 py-2 bg-white rounded-full text-sm font-medium text-gray-700 border border-gray-200 shadow-sm"
                    >
                      {lang.language}
                      <span className="ml-2 text-gray-400">({lang.proficiency})</span>
                    </span>
                  ))}
                </div>
                <p className="text-sm text-gray-400 mt-2">
                  You can add more languages from your dashboard later.
                </p>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Tell students about yourself
              </h1>
              <p className="text-lg text-gray-500">
                This is what students will see on your profile.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Headline <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.headline}
                  onChange={(e) =>
                    setFormData({ ...formData, headline: e.target.value.slice(0, 200) })
                  }
                  className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors"
                  placeholder="e.g. Certified Math Tutor with 5 years experience"
                />
                <p className="text-sm text-gray-400 mt-1 text-right">
                  {formData.headline.length}/200
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bio <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.bio}
                  onChange={(e) =>
                    setFormData({ ...formData, bio: e.target.value })
                  }
                  className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors resize-none"
                  rows={5}
                  placeholder="Introduce yourself to students. What's your teaching style? What can students expect?"
                  maxLength={2000}
                />
                <p className="text-sm text-gray-400 mt-1 text-right">
                  {formData.bio.length}/2000 (min 50)
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Teaching Style <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.teaching_style}
                  onChange={(e) =>
                    setFormData({ ...formData, teaching_style: e.target.value })
                  }
                  className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors resize-none"
                  rows={3}
                  placeholder="Describe your teaching approach - how do you engage students?"
                  maxLength={1000}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Years of Experience
                </label>
                <input
                  type="number"
                  value={formData.years_of_experience}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      years_of_experience: parseInt(e.target.value) || 0,
                    })
                  }
                  className="w-full px-4 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0 transition-colors"
                  min={0}
                  max={100}
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Camera className="w-8 h-8 text-purple-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Add your profile photo
              </h1>
              <p className="text-lg text-gray-500">
                A friendly photo helps students connect with you.
              </p>
            </div>

            <div className="flex flex-col items-center">
              {photoPreview ? (
                <div className="relative group">
                  <img
                    src={photoPreview}
                    alt="Profile preview"
                    className="w-48 h-48 rounded-full object-cover border-4 border-white shadow-2xl"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setPhotoFile(null);
                      setPhotoPreview(null);
                    }}
                    className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer group">
                  <div className="w-48 h-48 rounded-full border-4 border-dashed border-gray-300 bg-gray-50 flex flex-col items-center justify-center hover:border-primary-400 hover:bg-primary-50 transition-all group-hover:scale-105">
                    <Camera className="w-12 h-12 text-gray-400 mb-3 group-hover:text-primary-500 transition-colors" />
                    <span className="text-sm font-medium text-gray-500 group-hover:text-primary-600">
                      Upload photo
                    </span>
                    <span className="text-xs text-gray-400 mt-1">
                      JPG, PNG up to 10MB
                    </span>
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

              {isUploading && (
                <div className="flex items-center gap-2 mt-6 text-primary-600">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Uploading photo...</span>
                </div>
              )}

              <div className="mt-8 p-6 bg-blue-50 rounded-2xl max-w-md">
                <h4 className="font-semibold text-blue-900 mb-3">Photo tips:</h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Use a recent, high-quality photo
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Make sure your face is clearly visible
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Smile and look approachable
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Video className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Record an intro video
              </h1>
              <p className="text-lg text-gray-500">
                Help students get to know you before booking.
              </p>
            </div>

            <div className="flex flex-col items-center">
              {videoPreview ? (
                <div className="relative w-full max-w-md">
                  <video
                    src={videoPreview}
                    controls
                    className="w-full rounded-2xl shadow-2xl"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setVideoFile(null);
                      setVideoPreview(null);
                    }}
                    className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg"
                  >
                    <X size={16} />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer w-full max-w-md group">
                  <div className="aspect-video rounded-2xl border-4 border-dashed border-gray-300 bg-gray-50 flex flex-col items-center justify-center hover:border-primary-400 hover:bg-primary-50 transition-all group-hover:scale-[1.02]">
                    <Video className="w-16 h-16 text-gray-400 mb-4 group-hover:text-primary-500 transition-colors" />
                    <span className="text-lg font-medium text-gray-500 group-hover:text-primary-600">
                      Upload video
                    </span>
                    <span className="text-sm text-gray-400 mt-1">
                      MP4, WebM up to 100MB
                    </span>
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

              {isUploading && (
                <div className="flex items-center gap-2 mt-6 text-primary-600">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Uploading video...</span>
                </div>
              )}

              <div className="mt-8 p-6 bg-blue-50 rounded-2xl max-w-md">
                <h4 className="font-semibold text-blue-900 mb-3">Video tips:</h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Keep it between 1-3 minutes
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Introduce yourself naturally
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                    Good lighting and clear audio
                  </li>
                </ul>
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <DollarSign className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Set your pricing
              </h1>
              <p className="text-lg text-gray-500">
                Choose competitive rates for your lessons.
              </p>
            </div>

            <div className="space-y-8">
              <div className="p-8 bg-white rounded-2xl border-2 border-gray-100 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">Hourly Rate</h3>
                    <p className="text-sm text-gray-500">
                      Your standard 60-minute lesson
                    </p>
                  </div>
                  <div className="text-4xl font-bold text-primary-600">
                    ${formData.hourly_rate}
                  </div>
                </div>
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
                  className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer accent-primary-600"
                />
                <div className="flex justify-between text-sm text-gray-400 mt-2">
                  <span>$5</span>
                  <span>$100</span>
                </div>
              </div>

              <div className="p-8 bg-white rounded-2xl border-2 border-gray-100 shadow-sm">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">Trial Lesson</h3>
                    <p className="text-sm text-gray-500">
                      Discounted first lesson to attract students
                    </p>
                  </div>
                  <div className="text-4xl font-bold text-blue-600">
                    ${formData.trial_lesson_price}
                  </div>
                </div>
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
                  className="w-full h-3 bg-gray-200 rounded-full appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-sm text-gray-400 mt-2">
                  <span>$1</span>
                  <span>$50</span>
                </div>
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="max-w-xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <GraduationCap className="w-8 h-8 text-yellow-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                What do you teach?
              </h1>
              <p className="text-lg text-gray-500">
                Select the subjects you can teach.
              </p>
            </div>

            <div className="text-center p-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
              <GraduationCap className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-700 mb-2">
                Coming Soon
              </h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Subject selection will be available soon. You can add subjects
                from your dashboard after completing setup.
              </p>
              <p className="text-primary-600 font-medium mt-4">
                Click Next to continue
              </p>
            </div>
          </div>
        );

      case 7:
        return (
          <div className="max-w-2xl mx-auto">
            <div className="mb-12 text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Briefcase className="w-8 h-8 text-indigo-600" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Share your background
              </h1>
              <p className="text-lg text-gray-500">
                Add your education and work experience.
              </p>
            </div>

            <div className="space-y-8">
              {/* Education Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <GraduationCap className="w-5 h-5 text-primary-600" />
                    Education
                  </h3>
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
                    className="flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
                  >
                    <Plus size={16} /> Add
                  </button>
                </div>

                {formData.education.length === 0 ? (
                  <div className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 text-center">
                    <p className="text-gray-500">No education added yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {formData.education.map((edu, idx) => (
                      <div
                        key={idx}
                        className="p-6 bg-white rounded-xl border-2 border-gray-100 shadow-sm"
                      >
                        <div className="flex justify-end mb-3">
                          <button
                            type="button"
                            onClick={() => {
                              const updated = formData.education.filter(
                                (_, i) => i !== idx
                              );
                              setFormData({ ...formData, education: updated });
                            }}
                            className="text-red-500 hover:text-red-600 p-1"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                        <div className="grid gap-4">
                          <input
                            type="text"
                            placeholder="Institution name"
                            value={edu.institution}
                            onChange={(e) => {
                              const updated = [...formData.education];
                              updated[idx] = {
                                ...updated[idx],
                                institution: e.target.value,
                              };
                              setFormData({ ...formData, education: updated });
                            }}
                            className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                          />
                          <div className="grid grid-cols-2 gap-4">
                            <input
                              type="text"
                              placeholder="Degree"
                              value={edu.degree}
                              onChange={(e) => {
                                const updated = [...formData.education];
                                updated[idx] = {
                                  ...updated[idx],
                                  degree: e.target.value,
                                };
                                setFormData({ ...formData, education: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                            <input
                              type="text"
                              placeholder="Field of study"
                              value={edu.field_of_study}
                              onChange={(e) => {
                                const updated = [...formData.education];
                                updated[idx] = {
                                  ...updated[idx],
                                  field_of_study: e.target.value,
                                };
                                setFormData({ ...formData, education: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <input
                              type="number"
                              placeholder="Start year"
                              value={edu.start_year}
                              onChange={(e) => {
                                const updated = [...formData.education];
                                updated[idx] = {
                                  ...updated[idx],
                                  start_year: parseInt(e.target.value) || 0,
                                };
                                setFormData({ ...formData, education: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                            <input
                              type="number"
                              placeholder="End year"
                              value={edu.end_year || ''}
                              onChange={(e) => {
                                const updated = [...formData.education];
                                updated[idx] = {
                                  ...updated[idx],
                                  end_year: e.target.value
                                    ? parseInt(e.target.value)
                                    : undefined,
                                };
                                setFormData({ ...formData, education: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Experience Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-blue-600" />
                    Work Experience
                  </h3>
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
                    className="flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700"
                  >
                    <Plus size={16} /> Add
                  </button>
                </div>

                {formData.experience.length === 0 ? (
                  <div className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 text-center">
                    <p className="text-gray-500">No experience added yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {formData.experience.map((exp, idx) => (
                      <div
                        key={idx}
                        className="p-6 bg-white rounded-xl border-2 border-gray-100 shadow-sm"
                      >
                        <div className="flex justify-end mb-3">
                          <button
                            type="button"
                            onClick={() => {
                              const updated = formData.experience.filter(
                                (_, i) => i !== idx
                              );
                              setFormData({ ...formData, experience: updated });
                            }}
                            className="text-red-500 hover:text-red-600 p-1"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                        <div className="grid gap-4">
                          <div className="grid grid-cols-2 gap-4">
                            <input
                              type="text"
                              placeholder="Company"
                              value={exp.company}
                              onChange={(e) => {
                                const updated = [...formData.experience];
                                updated[idx] = {
                                  ...updated[idx],
                                  company: e.target.value,
                                };
                                setFormData({ ...formData, experience: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                            <input
                              type="text"
                              placeholder="Position"
                              value={exp.position}
                              onChange={(e) => {
                                const updated = [...formData.experience];
                                updated[idx] = {
                                  ...updated[idx],
                                  position: e.target.value,
                                };
                                setFormData({ ...formData, experience: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                          </div>
                          <div className="grid grid-cols-2 gap-4">
                            <input
                              type="number"
                              placeholder="Start year"
                              value={exp.start_year}
                              onChange={(e) => {
                                const updated = [...formData.experience];
                                updated[idx] = {
                                  ...updated[idx],
                                  start_year: parseInt(e.target.value) || 0,
                                };
                                setFormData({ ...formData, experience: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
                            />
                            <input
                              type="number"
                              placeholder="End year (empty if current)"
                              value={exp.end_year || ''}
                              onChange={(e) => {
                                const updated = [...formData.experience];
                                updated[idx] = {
                                  ...updated[idx],
                                  end_year: e.target.value
                                    ? parseInt(e.target.value)
                                    : undefined,
                                };
                                setFormData({ ...formData, experience: updated });
                              }}
                              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-primary-500 focus:ring-0"
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
                                  end_year: e.target.checked
                                    ? undefined
                                    : updated[idx].end_year,
                                };
                                setFormData({ ...formData, experience: updated });
                              }}
                              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                            />
                            <span className="text-sm text-gray-700">
                              I currently work here
                            </span>
                          </label>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Final Message */}
              <div className="text-center p-8 bg-gradient-to-br from-primary-50 to-blue-50 rounded-2xl">
                <Sparkles className="w-8 h-8 text-yellow-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Almost there!
                </h3>
                <p className="text-gray-600">
                  {formData.education.length === 0 &&
                  formData.experience.length === 0
                    ? "You can skip this for now and add details later."
                    : `Great! You've added ${formData.education.length} education and ${formData.experience.length} experience entries.`}
                </p>
                <p className="text-primary-600 font-medium mt-2">
                  Click Finish to submit your profile for review.
                </p>
              </div>
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 flex flex-col">
      {/* Sticky Progress Bar */}
      <div className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-500">
              Step {currentStep} of {steps.length}
            </span>
            <span className="text-sm font-medium text-primary-600">
              {steps[currentStep - 1].label}
            </span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-blue-500 rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${(currentStep / steps.length) * 100}%`,
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div ref={containerRef} className="w-full max-w-4xl relative min-h-[500px]">
          <div className="animate-fade-in">{renderStepContent()}</div>
        </div>
      </div>

      {/* Sticky Footer Navigation */}
      <div className="sticky bottom-0 bg-white/80 backdrop-blur-lg border-t border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <button
            onClick={handleBack}
            disabled={currentStep === 1 || isLoading}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
              currentStep === 1 || isLoading
                ? 'text-gray-300 cursor-not-allowed'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            <ChevronLeft size={20} />
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={isLoading}
            className="flex items-center gap-2 px-8 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Saving...
              </>
            ) : currentStep === steps.length ? (
              <>
                Finish
                <CheckCircle2 size={20} />
              </>
            ) : (
              <>
                Next
                <ChevronRight size={20} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
