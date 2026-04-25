import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Client } from '@gradio/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Search, BookOpen, FlaskConical, Users, Info, 
  ChevronRight, ChevronDown, CheckCircle2, Circle, 
  ExternalLink, FileText, Download, Activity, Play,
  Microscope, Sparkles, AlertCircle, Save,
  Star, Database, GitMerge, Cpu, ArrowRight
} from 'lucide-react';

// --- Animation Variants & Physics ---
const springTransition = { type: "spring", stiffness: 350, damping: 30 };
const fadeUpProps = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
};

// Global Gradio Client Instance
let gradioClient = null;
const initClient = async () => {
  if (!gradioClient) {
    try {
      gradioClient = await Client.connect("http://localhost:7860");
      console.log("Connected to Gradio backend");
    } catch (e) {
      console.error("Failed to connect to Gradio", e);
    }
  }
  return gradioClient;
};

// Custom Markdown Components for Links
const MarkdownComponents = {
  a: ({ node, ...props }) => (
    <a {...props} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 hover:underline inline-flex items-center gap-0.5">
      {props.children} <ExternalLink size={10} className="inline opacity-70" />
    </a>
  ),
  table: ({ node, ...props }) => (
    <div className="overflow-x-auto my-4 rounded-lg border border-zinc-200">
      <table className="min-w-full divide-y divide-zinc-200 text-sm" {...props} />
    </div>
  ),
  th: ({ node, ...props }) => <th className="bg-zinc-50 px-4 py-3 text-left font-medium text-zinc-900" {...props} />,
  td: ({ node, ...props }) => <td className="px-4 py-3 text-zinc-600 border-t border-zinc-100" {...props} />
};

export default function AIScientistApp() {
  const [activeTab, setActiveTab] = useState('input');
  
  // Shared State
  const [hypothesis, setHypothesis] = useState("");
  const [planResult, setPlanResult] = useState("");
  
  useEffect(() => {
    initClient();
  }, []);
  
  return (
    <div className="flex h-screen w-full bg-zinc-50 text-zinc-900 font-sans overflow-hidden">
      
      {/* --- Sidebar --- */}
      <motion.aside 
        className="w-64 flex-shrink-0 bg-white border-r border-zinc-200/60 flex flex-col z-20 shadow-[1px_0_10px_rgba(0,0,0,0.02)]"
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={springTransition}
      >
        <div className="p-6 border-b border-zinc-200/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-sm shadow-indigo-600/20">
            <Microscope size={18} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="font-semibold text-sm tracking-tight text-zinc-900">The AI Scientist</h1>
            <p className="text-[10px] text-zinc-500 font-medium uppercase tracking-wider">Enterprise Edition</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <NavItem id="input" label="📝 Input & Literature QC" active={activeTab === 'input'} onClick={() => setActiveTab('input')} />
          <NavItem id="plan" label="🧪 Experiment Plan" active={activeTab === 'plan'} onClick={() => setActiveTab('plan')} />
          <NavItem id="review" label="👨‍🔬 Scientist Review" active={activeTab === 'review'} onClick={() => setActiveTab('review')} />
          <NavItem id="info" label="ℹ️ System Info" active={activeTab === 'info'} onClick={() => setActiveTab('info')} />
        </nav>

        <div className="p-4 border-t border-zinc-200/60 bg-zinc-50/50">
          <div className="flex items-center gap-2 px-3 py-2 rounded-md bg-white border border-zinc-200/60 shadow-sm">
            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
            <span className="text-xs font-medium text-zinc-600">System Ready</span>
          </div>
        </div>
      </motion.aside>

      {/* --- Main Content --- */}
      <main className="flex-1 flex flex-col h-full relative overflow-hidden">
        
        {/* Sticky Header */}
        <header className="h-14 border-b border-zinc-200/60 bg-white/80 backdrop-blur-md sticky top-0 z-10 flex items-center justify-between px-6">
          <div className="flex items-center text-sm font-medium text-zinc-500 gap-2">
            <span>Workspace</span>
            <ChevronRight size={14} className="text-zinc-300" />
            <span className="text-zinc-900">
              {activeTab === 'input' && "Literature QC"}
              {activeTab === 'plan' && "Experiment Plan"}
              {activeTab === 'review' && "Scientist Review"}
              {activeTab === 'info' && "System Info"}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono font-medium text-indigo-600 bg-indigo-50 px-2.5 py-1.5 rounded-full border border-indigo-100">
            <Activity size={12} />
            LLM: Connected - Gemini 2.0
          </div>
        </header>

        {/* Scrollable Canvas */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-4xl mx-auto w-full pb-20">
            <AnimatePresence mode="wait">
              {activeTab === 'input' && (
                <ViewInput 
                  key="input" 
                  hypothesis={hypothesis} 
                  setHypothesis={setHypothesis} 
                  onNext={() => setActiveTab('plan')} 
                />
              )}
              {activeTab === 'plan' && (
                <ViewPlan 
                  key="plan" 
                  hypothesis={hypothesis}
                  planResult={planResult}
                  setPlanResult={setPlanResult}
                />
              )}
              {activeTab === 'review' && (
                <ViewReview 
                  key="review" 
                  hypothesis={hypothesis}
                />
              )}
              {activeTab === 'info' && (
                <ViewInfo 
                  key="info" 
                />
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>
    </div>
  );
}

// --- Navigation Item Component ---
function NavItem({ id, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`relative w-full flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
        active ? "text-indigo-700 bg-indigo-50/80" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
      }`}
    >
      {active && (
        <motion.div
          layoutId="activeNavTab"
          className="absolute left-0 top-1 bottom-1 w-1 bg-indigo-600 rounded-r-md"
          transition={springTransition}
        />
      )}
      <span className="truncate ml-1">{label}</span>
    </button>
  );
}

// ==========================================
// VIEW 1: INPUT & LITERATURE QC
// ==========================================
function ViewInput({ hypothesis, setHypothesis, onNext }) {
  const [isChecking, setIsChecking] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [hasResults, setHasResults] = useState(false);
  const [qcData, setQcData] = useState({ badge: "", assessment: "", references: "" });
  const [refinedHypothesis, setRefinedHypothesis] = useState("");

  const handleCheck = async () => {
    if (!hypothesis.trim()) return;
    setIsChecking(true);
    setHasResults(false);
    
    try {
      const client = await initClient();
      const result = await client.predict("/check_literature", [hypothesis]);
      
      setQcData({
        badge: result.data[0],
        assessment: result.data[1],
        references: result.data[2]
      });
      setHasResults(true);
    } catch (error) {
      console.error(error);
      alert("Failed to check literature. Is the backend running?");
    } finally {
      setIsChecking(false);
    }
  };

  const handleRefine = async () => {
    if (!hypothesis.trim()) return;
    setIsRefining(true);
    try {
      const client = await initClient();
      const result = await client.predict("/refine_hypothesis", [hypothesis]);
      setRefinedHypothesis(result.data[0]);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRefining(false);
    }
  };

  const samplePrompts = [
    "Replacing sucrose with trehalose will increase post-thaw viability of HeLa cells by >15%.",
    "Supplementing with Lactobacillus rhamnosus GG reduces intestinal permeability by 30%.",
    "Introducing Sporomusa ovata at -400mV vs SHE fixes CO2 into acetate at 150 mmol/L/day."
  ];

  return (
    <motion.div {...fadeUpProps} className="space-y-8">
      
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-zinc-900 tracking-tight">Formulate Hypothesis</h2>
        <p className="text-sm text-zinc-500 mt-1">Write your hypothesis as a specific, testable statement with measurable outcomes.</p>
      </div>

      {/* Input Area */}
      <div className="bg-white rounded-xl border border-zinc-200/60 shadow-sm overflow-hidden transition-all duration-300 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/20">
        <textarea 
          className="w-full min-h-[140px] p-5 bg-transparent resize-none outline-none text-zinc-800 placeholder-zinc-400"
          placeholder="e.g., Replacing sucrose with trehalose as a cryoprotectant in the freezing medium will increase post-thaw viability of HeLa cells by at least 15 percentage points compared to the standard DMSO protocol."
          value={hypothesis}
          onChange={(e) => setHypothesis(e.target.value)}
        />
        <div className="bg-zinc-50 border-t border-zinc-100 px-4 py-3 flex items-center justify-between">
          <div className="text-xs text-zinc-400 flex items-center gap-2">
            <button 
              onClick={handleRefine}
              disabled={!hypothesis.trim() || isRefining}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-md border font-medium transition-colors
                ${(!hypothesis.trim() || isRefining) ? 'bg-zinc-100 text-zinc-400 border-zinc-200' : 'bg-white text-zinc-700 border-zinc-200 hover:bg-zinc-50 hover:border-zinc-300'}`}
            >
              <Sparkles size={14} className={isRefining ? 'animate-pulse text-indigo-500' : 'text-amber-500'} /> 
              {isRefining ? "Refining..." : "Refine Hypothesis"}
            </button>
          </div>
          <button 
            onClick={handleCheck}
            disabled={!hypothesis.trim() || isChecking}
            className={`flex items-center gap-2 px-5 py-2 text-sm font-medium text-white rounded-lg transition-all shadow-sm
              ${(!hypothesis.trim() || isChecking) ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-md active:scale-[0.98]'}`}
          >
            {isChecking ? (
              <span className="flex items-center gap-2">
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                  <Search size={16} />
                </motion.div>
                Analyzing...
              </span>
            ) : (
              <>
                <Search size={16} /> Check Literature
              </>
            )}
          </button>
        </div>
      </div>

      {/* Refined Hypothesis Result */}
      <AnimatePresence>
        {refinedHypothesis && (
          <motion.div {...fadeUpProps} className="p-5 rounded-xl border border-indigo-200 bg-indigo-50/50 shadow-sm">
            <h3 className="text-sm font-semibold text-indigo-900 mb-2 flex items-center gap-2">
              <Sparkles size={16} className="text-indigo-600" /> AI Refinement
            </h3>
            <div className="prose prose-sm prose-indigo max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{refinedHypothesis}</ReactMarkdown>
            </div>
            <button 
              onClick={() => { setHypothesis(refinedHypothesis.split("### Refined Hypothesis")[1]?.split("###")[0]?.trim() || refinedHypothesis); setRefinedHypothesis(""); }}
              className="mt-4 px-4 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded shadow-sm hover:bg-indigo-700 transition-colors"
            >
              Use Refined Hypothesis
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State: Suggestions */}
      <AnimatePresence>
        {!hasResults && !isChecking && !refinedHypothesis && (
          <motion.div {...fadeUpProps} className="space-y-3">
            <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Example Hypotheses</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {samplePrompts.map((prompt, i) => (
                <button 
                  key={i} 
                  onClick={() => setHypothesis(prompt)}
                  className="text-left p-4 rounded-xl border border-zinc-200/60 bg-white hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors shadow-[0_2px_8px_rgba(0,0,0,0.02)] group"
                >
                  <p className="text-sm text-zinc-600 group-hover:text-zinc-900 leading-relaxed">{prompt}</p>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Checking State: Shimmer Loader */}
      <AnimatePresence>
        {isChecking && (
          <motion.div {...fadeUpProps} className="p-6 rounded-xl border border-zinc-200/60 bg-white shadow-sm overflow-hidden relative">
            <motion.div 
              className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-zinc-100/50 to-transparent z-10"
              animate={{ translateX: ["-100%", "200%"] }}
              transition={{ repeat: Infinity, duration: 1.5, ease: "easeInOut" }}
            />
            <div className="flex items-center gap-3 mb-6">
              <div className="w-5 h-5 rounded-full bg-zinc-200" />
              <div className="h-4 bg-zinc-200 rounded w-1/3" />
            </div>
            <div className="space-y-3">
              <div className="h-3 bg-zinc-100 rounded w-full" />
              <div className="h-3 bg-zinc-100 rounded w-5/6" />
              <div className="h-3 bg-zinc-100 rounded w-4/6" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results State */}
      <AnimatePresence>
        {hasResults && (
          <motion.div {...fadeUpProps} className="space-y-6">
            
            {/* Novelty Badge & Assessment */}
            <div className="p-6 rounded-xl border border-zinc-200/60 bg-white shadow-sm">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-zinc-900 mb-1">Novelty Assessment</h3>
                  <p className="text-sm text-zinc-500">Cross-referenced against ArXiv and Semantic Scholar.</p>
                </div>
                <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full border font-medium text-xs
                  ${qcData.badge.includes('🟢') ? 'bg-emerald-100 text-emerald-800 border-emerald-200' : 
                    qcData.badge.includes('🔴') ? 'bg-rose-100 text-rose-800 border-rose-200' : 
                    'bg-amber-100 text-amber-800 border-amber-200'}`}>
                  <AlertCircle size={14} /> 
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{qcData.badge.replace(/🟢|🔴|🟡|⚪/g, '').trim()}</ReactMarkdown>
                </div>
              </div>
              <div className="p-4 rounded-lg bg-zinc-50 border border-zinc-100 text-sm text-zinc-700 leading-relaxed">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{qcData.assessment}</ReactMarkdown>
              </div>
            </div>

            {/* References */}
            <div>
              <h3 className="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
                <BookOpen size={16} className="text-zinc-400"/> Relevant Literature
              </h3>
              <div className="p-5 rounded-xl border border-zinc-200/60 bg-white shadow-sm hover:border-zinc-300 transition-colors prose prose-sm prose-indigo max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{qcData.references}</ReactMarkdown>
              </div>
            </div>

            {/* Next Step Action */}
            <div className="pt-4 flex justify-end">
              <button 
                onClick={onNext}
                className="flex items-center gap-2 px-6 py-2.5 bg-zinc-900 text-white text-sm font-medium rounded-lg hover:bg-zinc-800 transition-colors shadow-sm"
              >
                Proceed to Experiment Plan <ChevronRight size={16} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </motion.div>
  );
}

// ==========================================
// VIEW 2: EXPERIMENT PLAN
// ==========================================
function ViewPlan({ hypothesis, planResult, setPlanResult }) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setPlanResult("");
    
    // UI Mock sequence for visual feedback while API runs
    const steps = [
      { delay: 1000, step: 1 }, 
      { delay: 2500, step: 2 }, 
      { delay: 4000, step: 3 }, 
      { delay: 5500, step: 4 }, 
    ];
    let timeouts = steps.map(({ delay, step }) => setTimeout(() => setGenerationStep(step), delay));
    
    try {
      const client = await initClient();
      const result = await client.predict("/generate_plan", [hypothesis, "single_shot"]);
      setPlanResult(result.data[0]);
    } catch (e) {
      console.error(e);
      setPlanResult("❌ Error generating plan. Check backend.");
    } finally {
      timeouts.forEach(clearTimeout);
      setIsGenerating(false);
    }
  };

  const handleExport = async (type) => {
    const endpoint = type === 'md' ? "/export_md" : "/export_pdf";
    try {
      const client = await initClient();
      const result = await client.predict(endpoint);
      
      // result.data[0] is typically an object { url: string } when it's a File from Gradio
      let fileUrl = "";
      if (typeof result.data[0] === "object" && result.data[0].url) {
         fileUrl = result.data[0].url;
      } else if (typeof result.data[0] === "string") {
         fileUrl = result.data[0];
      }

      if (fileUrl) {
         const a = document.createElement('a');
         a.href = fileUrl;
         a.download = type === 'md' ? 'experiment_plan.md' : 'experiment_plan.pdf';
         document.body.appendChild(a);
         a.click();
         document.body.removeChild(a);
      }
    } catch (e) {
      console.error(`Failed to export ${type}`, e);
      alert(`Export failed: ${e.message}`);
    }
  };

  return (
    <motion.div {...fadeUpProps} className="space-y-6">
      
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-zinc-900 tracking-tight">Experiment Plan</h2>
          {planResult && (
            <p className="text-sm text-zinc-500 mt-1 font-mono text-xs bg-zinc-100 px-2 py-1 rounded inline-block mt-2">
              ID: EXP-74B-2026
            </p>
          )}
        </div>
        <div className="flex gap-3">
          {planResult && (
             <>
               <button onClick={() => handleExport('md')} className="flex items-center gap-2 px-4 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-sm font-medium rounded-lg transition-colors">
                 <FileText size={16} /> Export MD
               </button>
               <button onClick={() => handleExport('pdf')} className="flex items-center gap-2 px-4 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-700 text-sm font-medium rounded-lg transition-colors">
                 <Download size={16} /> Export PDF
               </button>
             </>
          )}
          <button 
            onClick={handleGenerate}
            disabled={isGenerating || !hypothesis}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors shadow-sm
              ${isGenerating ? 'bg-zinc-200 text-zinc-500' : 'bg-indigo-600 text-white hover:bg-indigo-700'}`}
          >
            <FlaskConical size={16} /> 
            {isGenerating ? "Generating..." : planResult ? "Regenerate Plan" : "Generate Plan"}
          </button>
        </div>
      </div>

      <div className="w-full h-px bg-zinc-200/60" />

      {/* Empty State */}
      {!isGenerating && !planResult && (
        <div className="text-center py-20 text-zinc-500">
          <p>Click "Generate Plan" to synthesize the protocol for your hypothesis.</p>
        </div>
      )}

      {/* Loading State */}
      {isGenerating && (
        <motion.div {...fadeUpProps} className="max-w-md mx-auto mt-20 p-8 rounded-2xl bg-white border border-zinc-200/60 shadow-sm text-center">
          <div className="relative w-16 h-16 mx-auto mb-6">
            <motion.div className="absolute inset-0 rounded-full border-4 border-indigo-100" />
            <motion.div 
              className="absolute inset-0 rounded-full border-4 border-indigo-600 border-t-transparent"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
            <div className="absolute inset-0 flex items-center justify-center">
              <FlaskConical size={20} className="text-indigo-600" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-zinc-900">Synthesizing Plan</h3>
          
          <div className="mt-6 space-y-3 text-left">
            <GenStepItem active={generationStep >= 0} text="Initializing LLM parameters" />
            <GenStepItem active={generationStep >= 1} text="Drafting step-by-step protocol" />
            <GenStepItem active={generationStep >= 2} text="Sourcing materials & estimating budget" />
            <GenStepItem active={generationStep >= 3} text="Designing statistical validation" />
          </div>
        </motion.div>
      )}

      {/* Results State */}
      {!isGenerating && planResult && (
        <motion.div {...fadeUpProps} className="bg-white border border-zinc-200/60 shadow-sm rounded-xl p-8 prose prose-sm prose-zinc max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{planResult}</ReactMarkdown>
        </motion.div>
      )}
      
    </motion.div>
  );
}

function GenStepItem({ active, text }) {
  return (
    <div className={`flex items-center gap-3 text-sm transition-colors duration-500 ${active ? 'text-zinc-900' : 'text-zinc-400'}`}>
      {active ? <CheckCircle2 size={16} className="text-emerald-500" /> : <Circle size={16} className="text-zinc-300" />}
      {text}
    </div>
  );
}

// ==========================================
// VIEW 3: SCIENTIST REVIEW
// ==========================================
function ViewReview({ hypothesis }) {
  const [form, setForm] = useState({
    hypothesis: hypothesis,
    experiment_type: "other",
    overall_rating: 3,
    protocol_rating: 3, protocol_correction: "",
    materials_rating: 3, materials_correction: "",
    timeline_rating: 3, timeline_correction: "",
    validation_rating: 3, validation_correction: "",
    notes: ""
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackResult, setFeedbackResult] = useState("");

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const client = await initClient();
      const res = await client.predict("/save_feedback", [
        form.hypothesis,
        form.experiment_type,
        form.overall_rating,
        form.protocol_rating,
        form.protocol_correction,
        form.materials_rating,
        form.materials_correction,
        form.timeline_rating,
        form.timeline_correction,
        form.validation_rating,
        form.validation_correction,
        form.notes
      ]);
      setFeedbackResult(res.data[0]);
    } catch (e) {
      console.error(e);
      setFeedbackResult("❌ Failed to save feedback.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRatingChange = (field, val) => setForm(f => ({ ...f, [field]: val }));
  const handleTextChange = (field, val) => setForm(f => ({ ...f, [field]: val }));

  return (
    <motion.div {...fadeUpProps} className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-zinc-900 tracking-tight">Scientist Review</h2>
        <p className="text-sm text-zinc-500 mt-1">Your feedback improves future plans for similar experiments via our BM25 Semantic learning engine.</p>
      </div>

      <div className="bg-white rounded-xl border border-zinc-200/60 shadow-sm p-6 space-y-6">
        <div>
           <label className="block text-sm font-medium text-zinc-700 mb-1">Hypothesis Being Reviewed</label>
           <textarea 
             className="w-full border border-zinc-200 rounded-md p-3 text-sm text-zinc-800"
             value={form.hypothesis}
             onChange={e => handleTextChange('hypothesis', e.target.value)}
             rows={2}
           />
        </div>

        <div className="flex gap-6">
           <div className="flex-1">
             <label className="block text-sm font-medium text-zinc-700 mb-1">Experiment Type</label>
             <select 
                className="w-full border border-zinc-200 rounded-md p-2.5 text-sm bg-white text-zinc-800"
                value={form.experiment_type}
                onChange={e => handleTextChange('experiment_type', e.target.value)}
             >
               <option value="diagnostics">Diagnostics</option>
               <option value="gut_health">Gut Health</option>
               <option value="cell_biology">Cell Biology</option>
               <option value="climate">Climate</option>
               <option value="other">Other</option>
             </select>
           </div>
           <div className="flex-1">
             <label className="block text-sm font-medium text-zinc-700 mb-1">Overall Plan Quality (1-5)</label>
             <div className="flex items-center gap-2 h-[42px]">
               {[1,2,3,4,5].map(i => (
                 <button key={i} onClick={() => handleRatingChange('overall_rating', i)} className="text-amber-400 hover:scale-110 transition-transform">
                   <Star fill={form.overall_rating >= i ? "currentColor" : "none"} strokeWidth={1.5} />
                 </button>
               ))}
             </div>
           </div>
        </div>
        
        <div className="pt-4 border-t border-zinc-100">
           <h3 className="font-medium text-zinc-900 mb-4">Section-by-Section Corrections</h3>
           
           {['protocol', 'materials', 'timeline', 'validation'].map((sec) => (
             <div key={sec} className="mb-4 bg-zinc-50 p-4 rounded-lg border border-zinc-100">
               <div className="flex items-center justify-between mb-2">
                 <span className="text-sm font-medium capitalize">{sec}</span>
                 <div className="flex items-center gap-1">
                   {[1,2,3,4,5].map(i => (
                     <button key={i} onClick={() => handleRatingChange(`${sec}_rating`, i)} className="text-indigo-400 hover:text-indigo-600 w-6 h-6 flex items-center justify-center rounded hover:bg-indigo-50">
                       <Star size={14} fill={form[`${sec}_rating`] >= i ? "currentColor" : "none"} />
                     </button>
                   ))}
                 </div>
               </div>
               <textarea 
                 placeholder={`Any corrections for ${sec}? (leave blank if none)`}
                 className="w-full border border-zinc-200 rounded bg-white p-2.5 text-sm placeholder:text-zinc-400"
                 rows={2}
                 value={form[`${sec}_correction`]}
                 onChange={e => handleTextChange(`${sec}_correction`, e.target.value)}
               />
             </div>
           ))}
        </div>

        <div>
           <label className="block text-sm font-medium text-zinc-700 mb-1">Additional Notes</label>
           <textarea 
             className="w-full border border-zinc-200 rounded-md p-3 text-sm text-zinc-800"
             value={form.notes}
             onChange={e => handleTextChange('notes', e.target.value)}
             rows={2}
           />
        </div>

        <div className="pt-2">
           <button 
             onClick={handleSubmit}
             disabled={isSubmitting || !form.hypothesis}
             className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
           >
             <Save size={16} /> {isSubmitting ? "Saving..." : "Submit Feedback"}
           </button>
        </div>

        {feedbackResult && (
          <motion.div {...fadeUpProps} className="p-4 mt-4 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-sm">
             <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{feedbackResult}</ReactMarkdown>
          </motion.div>
        )}

      </div>
    </motion.div>
  );
}

// ==========================================
// VIEW 4: SYSTEM INFO
// ==========================================
function ViewInfo() {
  const [infoMd, setInfoMd] = useState("Loading system info...");

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const client = await initClient();
        const res = await client.predict("/get_system_info");
        setInfoMd(res.data[0]);
      } catch (e) {
         setInfoMd("❌ Failed to connect to Python backend.");
      }
    };
    fetchInfo();
  }, []);

  return (
    <motion.div {...fadeUpProps} className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-zinc-900 tracking-tight">System Info</h2>
        <p className="text-sm text-zinc-500 mt-1">Live architecture and backend parameters.</p>
      </div>

      <div className="bg-white border border-zinc-200/60 shadow-sm rounded-xl p-8 prose prose-sm prose-zinc max-w-none prose-pre:bg-zinc-900 prose-pre:text-zinc-100">
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>{infoMd}</ReactMarkdown>
      </div>
    </motion.div>
  );
}
