import React, { useState } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Zap, 
  Target, 
  Briefcase, 
  LayoutDashboard,
  Users,
  BarChart,
  Settings,
  Search,
  Bell,
  LogOut,
  TrendingUp,
  CheckCircle2,
  MoreVertical,
  Activity,
  X,
  User,
  Mail,
  Lock,
  ArrowRight,
  UserPlus,
  Puzzle,
  ChevronDown,
  Sparkles,
  MapPin,
  Clock,
  Award,
  BookOpen,
  AlertTriangle,
  ChevronRight
} from 'lucide-react';

// --- CORPORATE DASHBOARD COMPONENT ---
const CorporateDashboard = ({ onLogout }) => {
  const activeJobs = [
    {
      title: "Senior React Engineer",
      type: "Full-time",
      location: "San Francisco, CA (Hybrid)",
      posted: "Posted 2 days ago",
      candidates: 45,
      parseRate: 89,
      status: "Actively Sourcing",
      skills: ["React", "TypeScript", "GraphQL", "Next.js"]
    },
    {
      title: "ML Ops Lead",
      type: "Full-time",
      location: "Remote",
      posted: "Posted 5 days ago",
      candidates: 12,
      parseRate: 94,
      status: "Interviewing",
      skills: ["Python", "Kubernetes", "AWS SageMaker"]
    },
    {
      title: "Product Designer",
      type: "Contract",
      location: "New York, NY",
      posted: "Posted 1 week ago",
      candidates: 87,
      parseRate: 91,
      status: "Reviewing",
      skills: ["Figma", "Design Systems", "Prototyping"]
    }
  ];

  const topCandidates = [
    { name: "Sarah Jenkins", role: "Sr. React Engineer", match: 95, status: "Interviewing", initial: "SJ", color: "bg-purple-500/20 text-purple-400 border-purple-500/30" },
    { name: "Michael Chen", role: "ML Ops Lead", match: 92, status: "Screening", initial: "MC", color: "bg-blue-500/20 text-blue-400 border-blue-500/30" },
    { name: "Emily Davis", role: "Product Designer", match: 88, status: "New Match", initial: "ED", color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
    { name: "David Kim", role: "Sr. React Engineer", match: 85, status: "New Match", initial: "DK", color: "bg-orange-500/20 text-orange-400 border-orange-500/30" }
  ];

  return (
    <div className="min-h-screen flex bg-[#0a0c10] text-slate-300 font-sans selection:bg-indigo-500/30">
      
      {/* Sidebar */}
      <aside className="w-[280px] bg-[#0f1117] border-r border-white/5 flex flex-col hidden lg:flex">
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-sm tracking-widest text-white uppercase">Resume Intel</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
          <div className="space-y-1">
            <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Corporate Menu</p>
            <button className="w-full flex items-center gap-3 px-3 py-2 bg-indigo-500/10 text-indigo-400 rounded-lg text-sm font-medium border border-indigo-500/20 transition-colors">
              <LayoutDashboard className="w-4 h-4" /> Overview
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
              <Briefcase className="w-4 h-4" /> Job Requisitions
              <span className="ml-auto bg-white/5 text-slate-300 py-0.5 px-2 rounded text-xs">12</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
              <Users className="w-4 h-4" /> Talent Pool
            </button>
          </div>
        </div>

        <div className="p-4 border-t border-white/5">
          <button onClick={onLogout} className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg text-sm font-medium transition-colors">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        <header className="h-16 flex items-center justify-between px-6 lg:px-8 border-b border-white/5 bg-[#0f1117]/80 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Corporate Dashboard</span>
            <span className="text-slate-600">/</span>
            <span className="text-white font-medium">Overview</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 cursor-pointer group">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-white leading-tight">Jane Doe</p>
                <p className="text-xs text-slate-500">Tech Recruiter</p>
              </div>
              <img src="https://ui-avatars.com/api/?name=Jane+Doe&background=6366f1&color=fff" alt="User" className="w-8 h-8 rounded-full ring-2 ring-white/10 group-hover:ring-indigo-500/50 transition-all" />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
            {/* Left Column */}
            <div className="lg:col-span-8 space-y-6 lg:space-y-8">
              <section>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-indigo-400" /> Active Job Roles
                  </h2>
                </div>
                <div className="bg-[#0f1117] border border-white/5 rounded-2xl overflow-hidden shadow-xl shadow-black/20">
                  {activeJobs.map((job, idx) => (
                    <div key={idx} className="p-5 border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-1.5">
                          <h3 className="text-white font-semibold text-base">{job.title}</h3>
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 text-slate-300 border border-white/10 uppercase tracking-wider font-medium">{job.type}</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-400 mb-3">
                          <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {job.location}</span>
                          <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {job.posted}</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {job.skills.map((skill, sIdx) => (
                            <span key={sIdx} className="text-[11px] font-medium px-2 py-1 bg-[#0a0c10] text-slate-300 rounded border border-white/5">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-4 sm:gap-2 sm:min-w-[140px]">
                        <div className="flex flex-col items-start sm:items-end">
                          <div className="text-sm font-medium text-white mb-0.5">{job.candidates} Candidates</div>
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs text-emerald-400 font-medium">{job.parseRate}% Parse Rate</span>
                            <TrendingUp className="w-3 h-3 text-emerald-400" />
                          </div>
                        </div>
                        <span className="text-[10px] uppercase tracking-wider font-bold text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded border border-indigo-500/20">
                          {job.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* Right Column */}
            <div className="lg:col-span-4 space-y-6 lg:space-y-8">
              <section>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Target className="w-5 h-5 text-orange-400" /> Top Ranked
                  </h2>
                </div>
                <div className="bg-[#0f1117] border border-white/5 rounded-2xl overflow-hidden shadow-xl shadow-black/20">
                  {topCandidates.map((cand, idx) => (
                    <div key={idx} className="p-4 border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm border ${cand.color}`}>
                        {cand.initial}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white font-medium text-sm truncate">{cand.name}</h4>
                        <p className="text-xs text-slate-400 truncate">{cand.role}</p>
                      </div>
                      <div className="text-right">
                        <div className="inline-flex items-center gap-1 text-emerald-400 mb-0.5">
                          <span className="text-sm font-bold">{cand.match}%</span>
                        </div>
                        <p className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">{cand.status}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};


// --- SEEKER DASHBOARD COMPONENT ---
const SeekerDashboard = ({ onLogout }) => {
  const skills = [
    { name: "Product Strategy", level: "Expert", conf: 92, years: 7, width: "92%" },
    { name: "UI/UX Design", level: "Advanced", conf: 85, years: 5, width: "85%" },
    { name: "Design Systems", level: "Intermediate", conf: 71, years: 3, width: "71%" },
    { name: "Frontend Basics (HTML/CSS)", level: "Intermediate", conf: 62, years: 2, width: "62%" }
  ];

  const keywords = [
    "Figma", "Prototyping", "Stakeholder Mgmt", "A/B Testing", 
    "User Stories", "Agile", "Wireframing", "User Research", "Jira"
  ];

  return (
    <div className="min-h-screen flex bg-[#0a0c10] text-slate-300 font-sans selection:bg-violet-500/30">
      
      {/* Sidebar */}
      <aside className="w-[280px] bg-[#0f1117] border-r border-white/5 flex flex-col hidden lg:flex">
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <div className="flex items-center gap-2 cursor-pointer">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center shadow-lg shadow-violet-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-sm tracking-widest text-white uppercase">SkillForge</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto py-6 px-4 space-y-8">
          <div className="space-y-1">
            <p className="px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">My Profile</p>
            <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
              <FileText className="w-4 h-4" /> Resume Analysis
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 bg-violet-500/10 text-violet-400 rounded-lg text-sm font-medium border border-violet-500/20 transition-colors">
              <BarChart className="w-4 h-4" /> Skill Breakdown
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
              <Target className="w-4 h-4" /> Gap Analysis
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
              <BookOpen className="w-4 h-4" /> Career Path
            </button>
          </div>
        </div>

        <div className="p-4 border-t border-white/5">
          <button onClick={onLogout} className="w-full flex items-center gap-3 px-3 py-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg text-sm font-medium transition-colors">
            <LogOut className="w-4 h-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        <header className="h-16 flex items-center justify-between px-6 lg:px-8 border-b border-white/5 bg-[#0f1117]/80 backdrop-blur-md sticky top-0 z-40">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 font-medium">Seeker Mode</span>
            <span className="text-slate-600">/</span>
            <span className="text-white font-medium">Skill Breakdown</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 cursor-pointer group">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold text-white leading-tight">Alex Hunter</p>
                <p className="text-xs text-slate-500">Product Manager</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-white font-bold text-xs ring-2 ring-white/10 group-hover:ring-violet-500/50 transition-all">
                AH
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-5xl mx-auto space-y-8">
            
            {/* Header / Score Section */}
            <div className="bg-[#0f1117] border border-white/5 rounded-2xl p-6 lg:p-8 shadow-xl shadow-black/20 flex flex-col lg:flex-row items-center justify-between gap-8 relative overflow-hidden">
              <div className="absolute right-0 top-0 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
              
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-violet-500/10 text-violet-400 rounded-full text-xs font-bold border border-violet-500/20 mb-4 uppercase tracking-wider">
                  <Award className="w-3.5 h-3.5" /> Resume Parsed Successfully
                </div>
                <h1 className="text-3xl font-extrabold text-white mb-2">Resume Intelligence Report</h1>
                <p className="text-slate-400 max-w-lg">
                  We've analyzed your uploaded resume against senior product roles. Here is a detailed breakdown of your extracted skills and identified experience levels.
                </p>
              </div>

              <div className="flex items-center gap-6 bg-[#0a0c10] border border-white/5 rounded-2xl p-6 min-w-[240px]">
                <div className="relative w-20 h-20 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path strokeDasharray="100, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
                    <path strokeDasharray="85, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#a78bfa" strokeWidth="3" strokeLinecap="round" />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-xl font-black text-white">85<span className="text-xs text-violet-400">%</span></span>
                  </div>
                </div>
                <div>
                  <h3 className="text-white font-bold mb-1">Profile Strength</h3>
                  <p className="text-xs text-slate-400">Highly competitive for PM roles</p>
                </div>
              </div>
            </div>

            {/* Main Skills Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-violet-400" /> Extracted Core Skills
                </h2>
                
                <div className="space-y-4">
                  {skills.map((skill, i) => (
                    <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/[0.07] transition-colors">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-white font-semibold text-base">{skill.name}</span>
                        <span className="text-violet-400 font-bold text-sm bg-violet-400/10 px-3 py-1 rounded-md border border-violet-400/20">{skill.level}</span>
                      </div>
                      <div className="h-2.5 bg-[#0a0c10] rounded-full overflow-hidden shadow-inner border border-white/5">
                        <div className="h-full bg-gradient-to-r from-violet-600 to-violet-400 rounded-full relative" style={{ width: skill.width }}>
                          <div className="absolute right-0 top-0 bottom-0 w-4 bg-white/20 blur-[2px]"></div>
                        </div>
                      </div>
                      <div className="mt-3 text-xs text-violet-400/70 flex justify-between font-medium">
                        <span className="flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Confidence: {skill.conf}%</span>
                        <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {skill.years} Years Experience</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sidebar Info */}
              <div className="space-y-6">
                <div className="bg-[#0f1117] border border-white/5 rounded-2xl p-6 shadow-xl shadow-black/20">
                  <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-orange-400" /> Missing Critical Skills
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                      <span className="text-sm font-medium text-orange-200">Data Analytics (SQL)</span>
                      <button className="text-orange-400 hover:text-orange-300"><ChevronRight className="w-4 h-4" /></button>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                      <span className="text-sm font-medium text-orange-200">Go-to-Market Strategy</span>
                      <button className="text-orange-400 hover:text-orange-300"><ChevronRight className="w-4 h-4" /></button>
                    </div>
                  </div>
                </div>

                <div className="bg-[#0f1117] border border-white/5 rounded-2xl p-6 shadow-xl shadow-black/20">
                  <h3 className="text-white font-bold mb-4">Keyword Analysis</h3>
                  <p className="text-xs text-slate-400 mb-4">Terms successfully matched across your work history and project descriptions.</p>
                  <div className="flex flex-wrap gap-2">
                    {keywords.map(kw => (
                      <span key={kw} className="px-3 py-1.5 bg-[#0a0c10] border border-white/10 rounded-lg text-xs font-medium text-slate-300 hover:border-violet-400/40 hover:text-violet-300 transition-colors cursor-default shadow-sm">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </main>
    </div>
  );
};


// --- MAIN APP COMPONENT (Landing Page & Auth Flow) ---
export default function App() {
  const [theme, setTheme] = useState('nebula'); 
  const [activeTab, setActiveTab] = useState('jd');
  const [message, setMessage] = useState(null);
  
  // App View & Auth State
  const [currentView, setCurrentView] = useState('landing'); // 'landing', 'recruiter', 'seeker'

  // Modal State
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('signin'); 
  const [authRole, setAuthRole] = useState('seeker'); 

  // Routing View Logic
  if (currentView === 'recruiter') {
    return <CorporateDashboard onLogout={() => setCurrentView('landing')} />;
  }
  if (currentView === 'seeker') {
    return <SeekerDashboard onLogout={() => setCurrentView('landing')} />;
  }

  const showMessage = (msg, type) => {
    setMessage({ text: msg, type });
    setTimeout(() => setMessage(null), 4000);
  };

  const openAuth = (mode) => {
    setAuthMode(mode);
    setIsAuthModalOpen(true);
  };

  const handleAuthSubmit = (e) => {
    e.preventDefault();
    if (authRole === 'recruiter') {
      setCurrentView('recruiter');
    } else {
      setCurrentView('seeker');
    }
    setIsAuthModalOpen(false);
  };

  const featuresData = [
    {
      title: "Advanced Resume Parsing",
      headline: "Understand resumes beyond keywords",
      content: "Extract structured data from resumes with high accuracy, even from complex layouts and formats.",
    },
    {
      title: "Hybrid Skill Extraction",
      headline: "Keyword + AI combined",
      content: "Identify skills using both direct keyword matching and semantic understanding for deeper insights.",
    },
    {
      title: "Experience-Aware Scoring",
      headline: "Not all skills are equal",
      content: "Evaluate skill strength based on where and how it appears — not just if it exists.",
    },
    {
      title: "Intelligent JD Parsing",
      headline: "Understand what recruiters want",
      content: "Break down job descriptions to extract required, preferred, and critical skills.",
    }
  ];

  return (
    <div className={`min-h-screen flex flex-col relative overflow-x-hidden font-sans selection:bg-purple-500/30 ${theme === 'nebula' ? 'bg-slate-900 text-white nebula-gradient-bg' : 'bg-slate-50 text-slate-900'}`}>
      
      <style dangerouslySetInnerHTML={{__html: `
        .nebula-gradient-bg {
          background-image: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
                            radial-gradient(circle at 85% 30%, rgba(168, 85, 247, 0.12) 0%, transparent 50%),
                            radial-gradient(circle at 50% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 50%);
        }
        .glass-morphism {
          background: rgba(30, 41, 59, 0.7);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
        }
        .modal-glass {
          background: rgba(15, 23, 42, 0.85);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
        }
      `}} />

      {/* Navigation */}
      <nav className={`fixed w-full z-40 transition-all duration-300 ${theme === 'nebula' ? 'bg-slate-900/80 border-b border-white/10 backdrop-blur-md' : 'bg-white/80 border-b border-slate-200 backdrop-blur-md shadow-sm'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2 cursor-pointer">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-xl tracking-tight">SkillForge</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className={`text-sm font-medium transition-colors ${theme === 'nebula' ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`}>Features</a>
              <a href="#demo" className={`text-sm font-medium transition-colors ${theme === 'nebula' ? 'text-slate-300 hover:text-white' : 'text-slate-600 hover:text-slate-900'}`}>Interactive Demo</a>
            </div>
            
            <div className="flex items-center gap-4">
              <button 
                onClick={() => setTheme(theme === 'nebula' ? 'light' : 'nebula')}
                className={`p-2 rounded-full transition-colors ${theme === 'nebula' ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                title="Toggle Theme"
              >
                {theme === 'nebula' ? <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg> : <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>}
              </button>
              
              <button 
                onClick={() => openAuth('signin')}
                className={`hidden sm:flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all ${theme === 'nebula' ? 'text-slate-300 hover:text-white hover:bg-slate-800' : 'text-slate-700 hover:bg-slate-100'}`}
              >
                Sign In
              </button>

              <button 
                onClick={() => openAuth('signup')}
                className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white px-5 py-2 rounded-lg text-sm font-bold transition-all shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Hero Section */}
      <main className="flex-1 relative z-10 pt-32 pb-20 w-full">
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {message && (
             <div className={`fixed top-24 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-full flex items-center gap-2 shadow-2xl animate-bounce ${message.type === 'success' ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'bg-indigo-500/10 border border-indigo-500/20 text-indigo-400'}`}>
               {message.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
               <span className="text-sm font-semibold">{message.text}</span>
             </div>
          )}

          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left Content */}
            <div className="max-w-2xl">
              <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium mb-6 ${theme === 'nebula' ? 'bg-indigo-500/10 text-indigo-300 border border-indigo-500/20' : 'bg-indigo-50 text-indigo-700 border border-indigo-100'}`}>
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                Next-Gen Career Intelligence
              </div>
              <h1 className={`text-5xl lg:text-7xl font-extrabold tracking-tight mb-6 leading-tight ${theme === 'nebula' ? 'text-white' : 'text-slate-900'}`}>
                Unlock Your <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
                  Career Potential
                </span>
              </h1>
              <p className={`text-lg mb-8 leading-relaxed ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>
                Stop guessing. Upload your resume or a job description to instantly uncover missing skills, match percentages, and a personalized graph-based learning roadmap.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => openAuth('signup')}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all shadow-xl shadow-indigo-500/20 hover:shadow-indigo-500/40 hover:-translate-y-0.5"
                >
                  <UploadCloud className="w-5 h-5" /> Get Started Free
                </button>
                <button className={`px-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition-all border ${theme === 'nebula' ? 'bg-white/5 border-white/10 hover:bg-white/10 text-white' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-700 shadow-sm'}`}>
                  View Live Demo
                </button>
              </div>
            </div>

            {/* Right Interactive Demo Panel */}
            <div id="demo" className={`rounded-2xl border p-1 shadow-2xl relative ${theme === 'nebula' ? 'bg-slate-800/50 border-white/10 shadow-indigo-500/10 backdrop-blur-sm' : 'bg-white border-slate-200 shadow-slate-200/50'}`}>
              
              <div className="absolute -top-4 -right-4 bg-gradient-to-r from-pink-500 to-orange-400 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg transform rotate-3">
                Try it now
              </div>

              <div className="flex p-2 gap-2 mb-2">
                <button 
                  onClick={() => setActiveTab('jd')}
                  className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 ${activeTab === 'jd' ? 'bg-indigo-600 text-white shadow-md' : (theme === 'nebula' ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-50')}`}
                >
                  <Target className="w-4 h-4" /> Match Job
                </button>
                <button 
                  onClick={() => setActiveTab('resume')}
                  className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-2 ${activeTab === 'resume' ? 'bg-indigo-600 text-white shadow-md' : (theme === 'nebula' ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-500 hover:bg-slate-50')}`}
                >
                  <FileText className="w-4 h-4" /> Parse Resume
                </button>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  showMessage("This is a UI demo. Sign up for full access!", "info");
                }}
                className={`p-6 rounded-xl ${theme === 'nebula' ? 'bg-slate-900/80 border border-white/5' : 'bg-slate-50 border border-slate-100'}`}
              >
                {activeTab === 'jd' ? (
                  <>
                    <label className={`block text-sm font-bold mb-2 ${theme === 'nebula' ? 'text-slate-300' : 'text-slate-700'}`}>Paste Job Description</label>
                    <textarea 
                      className={`w-full h-32 rounded-xl p-4 text-sm resize-none focus:ring-2 focus:ring-indigo-500 outline-none transition-all ${theme === 'nebula' ? 'bg-slate-950 border-slate-800 text-slate-300 placeholder-slate-600' : 'bg-white border-slate-200 text-slate-700 placeholder-slate-400 border shadow-inner'}`}
                      placeholder="e.g. Looking for a Senior React Developer with experience in Node.js, AWS, and modern CI/CD pipelines..."
                    ></textarea>
                  </>
                ) : (
                  <div className={`h-32 rounded-xl border-2 border-dashed flex flex-col items-center justify-center transition-colors cursor-pointer ${theme === 'nebula' ? 'border-slate-700 hover:border-indigo-500 bg-slate-950/50' : 'border-slate-300 hover:border-indigo-400 bg-white'}`}>
                    <UploadCloud className={`w-8 h-8 mb-2 ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-400'}`} />
                    <p className={`text-sm font-medium ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>Click to upload PDF</p>
                    <p className={`text-xs mt-1 ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-400'}`}>Max file size 5MB</p>
                  </div>
                )}

                <div className="mt-6 grid grid-cols-2 gap-4">
                  <button type="submit" className="flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white py-3 px-4 rounded-xl font-bold transition-all shadow-lg hover:shadow-indigo-500/30">
                    <Zap className="w-4 h-4" /> Analyze
                  </button>
                  <button type="button" className={`flex items-center justify-center gap-2 py-3 px-4 rounded-xl border transition-all ${theme === 'nebula' ? 'glass-morphism border-white/10 hover:bg-white/10 text-white' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-700'}`}>
                    <span className="text-sm font-medium">Sample JD</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </main>

      {/* Features Section */}
      <section id="features" className={`relative z-10 w-full border-t py-24 ${theme === 'nebula' ? 'glass-morphism border-white/10' : 'bg-white/60 backdrop-blur-md border-slate-200'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className={`text-4xl md:text-5xl font-extrabold mb-6 ${theme === 'nebula' ? 'text-white' : 'text-slate-900'}`}>
              Built for <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Real Intelligence</span>
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuresData.map((feature, idx) => (
              <div key={idx} className={`p-6 rounded-2xl border-t-4 transition-all duration-300 hover:-translate-y-1 ${theme === 'nebula' ? 'bg-slate-800/40 border-t-cyan-500 border-x border-b border-white/5 hover:bg-slate-800/60 shadow-lg' : 'bg-white border-t-cyan-500 border-x border-b border-slate-100 shadow-md'}`}>
                <div className={`text-[11px] font-bold uppercase tracking-widest mb-2 ${theme === 'nebula' ? 'text-cyan-400' : 'text-cyan-600'}`}>
                  {feature.headline}
                </div>
                <h3 className={`text-xl font-bold mb-3 ${theme === 'nebula' ? 'text-white' : 'text-slate-900'}`}>
                  {feature.title}
                </h3>
                <p className={`text-sm mb-5 leading-relaxed ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>
                  {feature.content}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`relative z-10 py-10 border-t ${theme === 'nebula' ? 'border-white/5 bg-slate-950/20' : 'border-slate-200 bg-slate-100'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <Zap className={`w-5 h-5 ${theme === 'nebula' ? 'text-indigo-400' : 'text-indigo-600'}`} />
            <span className={`font-bold ${theme === 'nebula' ? 'text-white' : 'text-slate-900'}`}>SkillForge</span>
          </div>
          <p className={`text-sm ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-500'}`}>
            © 2026 Resume Intelligence AI. All rights reserved.
          </p>
        </div>
      </footer>

      {/* AUTHENTICATION MODAL */}
      {isAuthModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-md" onClick={() => setIsAuthModalOpen(false)}></div>
          
          <div className={`relative w-full max-w-md rounded-2xl shadow-2xl overflow-hidden border ${theme === 'nebula' ? 'modal-glass border-slate-700/50' : 'bg-white border-slate-200'}`}>
            
            <div className={`flex items-center justify-between p-5 border-b ${theme === 'nebula' ? 'border-slate-700/50' : 'border-slate-100'}`}>
              <h2 className={`text-xl font-extrabold ${theme === 'nebula' ? 'text-white' : 'text-slate-900'}`}>
                {authMode === 'signin' ? 'Welcome Back' : 'Create an Account'}
              </h2>
              <button 
                onClick={() => setIsAuthModalOpen(false)}
                className={`p-1.5 rounded-lg transition-colors ${theme === 'nebula' ? 'text-slate-400 hover:bg-slate-800 hover:text-white' : 'text-slate-500 hover:bg-slate-100'}`}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6">
              
              <div className={`flex p-1 rounded-xl mb-6 ${theme === 'nebula' ? 'bg-slate-900/50 border border-slate-700/50' : 'bg-slate-100 border border-slate-200'}`}>
                <button
                  onClick={() => setAuthRole('seeker')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    authRole === 'seeker' 
                      ? (theme === 'nebula' ? 'bg-violet-600 text-white shadow-md shadow-violet-500/20' : 'bg-white text-violet-600 shadow-sm border border-slate-200')
                      : (theme === 'nebula' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')
                  }`}
                >
                  <User className="w-4 h-4" /> Seeker Mode
                </button>
                <button
                  onClick={() => setAuthRole('recruiter')}
                  className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    authRole === 'recruiter' 
                      ? (theme === 'nebula' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20' : 'bg-white text-indigo-600 shadow-sm border border-slate-200')
                      : (theme === 'nebula' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')
                  }`}
                >
                  <Briefcase className="w-4 h-4" /> Corporate Mode
                </button>
              </div>

              <form onSubmit={handleAuthSubmit} className="space-y-4">
                {authMode === 'signup' && (
                  <div>
                    <label className={`block text-xs font-bold mb-1.5 ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>Full Name</label>
                    <div className="relative">
                      <User className={`w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-400'}`} />
                      <input 
                        required
                        type="text" 
                        placeholder={authRole === 'seeker' ? "John Doe" : "Company Name"}
                        className={`w-full rounded-xl py-2.5 pl-10 pr-4 text-sm outline-none transition-all focus:ring-2 ${authRole === 'seeker' ? 'focus:ring-violet-500' : 'focus:ring-indigo-500'} ${theme === 'nebula' ? 'bg-slate-900 border border-slate-700 text-white placeholder-slate-600' : 'bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400'}`}
                      />
                    </div>
                  </div>
                )}
                
                <div>
                  <label className={`block text-xs font-bold mb-1.5 ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>Email</label>
                  <div className="relative">
                    <Mail className={`w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-400'}`} />
                    <input 
                      required
                      type="email" 
                      placeholder="hello@example.com"
                      className={`w-full rounded-xl py-2.5 pl-10 pr-4 text-sm outline-none transition-all focus:ring-2 ${authRole === 'seeker' ? 'focus:ring-violet-500' : 'focus:ring-indigo-500'} ${theme === 'nebula' ? 'bg-slate-900 border border-slate-700 text-white placeholder-slate-600' : 'bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400'}`}
                    />
                  </div>
                </div>

                <div>
                  <label className={`block text-xs font-bold mb-1.5 ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-600'}`}>Password</label>
                  <div className="relative">
                    <Lock className={`w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 ${theme === 'nebula' ? 'text-slate-500' : 'text-slate-400'}`} />
                    <input 
                      required
                      type="password" 
                      placeholder="••••••••"
                      className={`w-full rounded-xl py-2.5 pl-10 pr-4 text-sm outline-none transition-all focus:ring-2 ${authRole === 'seeker' ? 'focus:ring-violet-500' : 'focus:ring-indigo-500'} ${theme === 'nebula' ? 'bg-slate-900 border border-slate-700 text-white placeholder-slate-600' : 'bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400'}`}
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  className={`w-full flex items-center justify-center gap-2 py-3 mt-2 rounded-xl text-sm font-bold text-white transition-all shadow-lg ${authRole === 'seeker' ? 'bg-violet-600 hover:bg-violet-500 shadow-violet-500/25' : 'bg-indigo-600 hover:bg-indigo-500 shadow-indigo-500/25'}`}
                >
                  {authMode === 'signin' ? 'Sign In' : 'Create Account'} <ArrowRight className="w-4 h-4" />
                </button>
              </form>

              <div className="mt-6 text-center">
                <p className={`text-sm ${theme === 'nebula' ? 'text-slate-400' : 'text-slate-500'}`}>
                  {authMode === 'signin' ? "Don't have an account?" : "Already have an account?"}{' '}
                  <button 
                    onClick={() => setAuthMode(authMode === 'signin' ? 'signup' : 'signin')}
                    className={`font-bold hover:underline ${theme === 'nebula' ? 'text-indigo-400' : 'text-indigo-600'}`}
                  >
                    {authMode === 'signin' ? 'Sign up' : 'Sign in'}
                  </button>
                </p>
              </div>

            </div>
          </div>
        </div>
      )}

    </div>
  );
}