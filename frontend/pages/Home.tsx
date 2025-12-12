import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Card } from '../components/UIComponents';
import { Search, Star, Shield, Zap, CheckCircle, ArrowRight } from 'lucide-react';

const Home = () => {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative pt-20 pb-32 lg:pt-32 lg:pb-40 overflow-visible">
        <div className="container mx-auto px-4 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-white/40 backdrop-blur-md border border-white/50 rounded-full px-4 py-1.5 mb-8 shadow-sm animate-fade-in">
              <span className="flex h-2.5 w-2.5 rounded-full bg-green-400 shadow-[0_0_10px_rgba(74,222,128,0.6)] animate-pulse"></span>
              <span className="text-sm font-bold text-gray-700">Over 30,000 active tutors online</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold mb-8 tracking-tight leading-tight animate-slide-up text-gray-900">
              Master any subject with <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 via-purple-600 to-blue-600 drop-shadow-sm">
                expert personal tutors
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Connect with verified instructors for personalized 1-on-1 lessons. 
              Learn at your own pace, anytime, anywhere.
            </p>
            
            <div className="bg-white/60 backdrop-blur-xl p-3 rounded-3xl shadow-2xl border border-white/50 flex flex-col md:flex-row gap-3 max-w-2xl mx-auto animate-fade-in transform hover:scale-[1.01] transition-transform duration-500">
              <div className="flex-grow flex items-center px-6 bg-white/50 rounded-2xl h-14 border border-white/50 shadow-inner">
                <Search className="text-gray-400 mr-3" />
                <input 
                  type="text" 
                  placeholder="What do you want to learn?" 
                  className="bg-transparent border-none outline-none w-full text-gray-900 placeholder-gray-500 font-medium"
                />
              </div>
              <Link to="/instructors" className="w-full md:w-auto">
                <Button size="lg" className="w-full h-14 text-lg rounded-2xl shadow-primary-500/30">
                  Find a Tutor
                </Button>
              </Link>
            </div>
            
            <div className="mt-12 flex flex-wrap justify-center gap-8 text-gray-600 font-semibold text-sm">
              <span className="flex items-center gap-2 bg-white/30 px-3 py-1 rounded-full border border-white/40"><CheckCircle size={16} className="text-teal-500" /> Verified Tutors</span>
              <span className="flex items-center gap-2 bg-white/30 px-3 py-1 rounded-full border border-white/40"><CheckCircle size={16} className="text-teal-500" /> Pay per lesson</span>
              <span className="flex items-center gap-2 bg-white/30 px-3 py-1 rounded-full border border-white/40"><CheckCircle size={16} className="text-teal-500" /> Affordable prices</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="-mt-20 relative z-20 container mx-auto px-4">
        <Card className="p-10 grid grid-cols-1 md:grid-cols-3 gap-8 divide-y md:divide-y-0 md:divide-x divide-gray-200/50">
          <div className="text-center p-2">
            <div className="text-5xl font-bold text-gray-900 mb-2 tracking-tight">32k+</div>
            <div className="text-gray-500 font-medium">Experienced Tutors</div>
          </div>
          <div className="text-center p-2">
            <div className="text-5xl font-bold text-gray-900 mb-2 tracking-tight">120+</div>
            <div className="text-gray-500 font-medium">Subjects Taught</div>
          </div>
          <div className="text-center p-2">
            <div className="text-5xl font-bold text-gray-900 mb-2 tracking-tight">4.8</div>
            <div className="text-gray-500 font-medium">Average Star Rating</div>
          </div>
        </Card>
      </section>

      {/* Value Props */}
      <section className="py-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Why choose Tutorly?</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">We make learning engaging, effective, and accessible for everyone.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: <Star className="w-8 h-8 text-yellow-500" />, color: "bg-yellow-100", title: "Expert Tutors", desc: "Find teachers verified for their experience and teaching ability." },
              { icon: <Shield className="w-8 h-8 text-green-500" />, color: "bg-green-100", title: "Verified Profiles", desc: "Every tutor passes a rigorous background and qualification check." },
              { icon: <Zap className="w-8 h-8 text-purple-500" />, color: "bg-purple-100", title: "Fast Progress", desc: "Personalized learning plans help you reach your goals faster." }
            ].map((item, i) => (
              <div key={i} className="bg-white/40 backdrop-blur-md p-8 rounded-3xl border border-white/60 hover:bg-white/60 hover:shadow-xl hover:shadow-purple-500/10 transition-all duration-300 group">
                <div className={`${item.color} w-16 h-16 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-sm`}>
                  {item.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{item.title}</h3>
                <p className="text-gray-600 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="bg-gradient-to-r from-violet-600 to-blue-600 rounded-[2.5rem] p-12 md:p-20 text-center text-white shadow-2xl shadow-blue-500/30 relative overflow-hidden">
            {/* Decorative circles inside CTA */}
            <div className="absolute top-0 right-0 -mt-20 -mr-20 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 -mb-20 -ml-20 w-96 h-96 bg-white/10 rounded-full blur-3xl"></div>
            
            <h2 className="text-4xl md:text-6xl font-bold mb-8 relative z-10 tracking-tight">Ready to start learning?</h2>
            <p className="text-xl text-blue-100 mb-12 max-w-2xl mx-auto relative z-10 leading-relaxed">
              Join thousands of students and start your journey today. First lesson is backed by our happiness guarantee.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 relative z-10">
              <Link to="/register">
                <button className="w-full sm:w-auto px-8 py-4 bg-white text-primary-600 font-bold rounded-xl hover:bg-blue-50 transition-colors shadow-lg flex items-center justify-center gap-2">
                  Get Started for Free <ArrowRight size={20} />
                </button>
              </Link>
              <Link to="/instructors">
                <button className="w-full sm:w-auto px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/30 text-white font-bold rounded-xl hover:bg-white/20 transition-colors flex items-center justify-center gap-2">
                  Browse Tutors
                </button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;