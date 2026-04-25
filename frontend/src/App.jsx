import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, BookOpen, FlaskConical, Users, Info, 
  ChevronRight, ChevronDown, CheckCircle2, Circle, 
  ExternalLink, FileText, Download, Activity, Play,
  Microscope, Sparkles, AlertCircle
} from 'lucide-react';

// --- Animation Variants & Physics ---
const springTransition = { type: "spring", stiffness: 350, damping: 30 };
const fadeUpProps = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
};

// --- Mock Data ---
const MOCK_REFERENCES = [
  {
    id: 1,
    title: "Enhancing post-thaw viability of HeLa cells using trehalose",
    authors: "Smith, J. et al.",
    year: 2024,
    abstract: "This study investigates the use of trehalose as a non-toxic alternative to DMSO in cryopreservation, demonstrating a 12% improvement in post-thaw recovery...",
    url: "#"
  },
  {
    id: 2,
    title: "Cryoprotectant mechanisms of disaccharides in mammalian cells",
    authors: "Chen, X. & Davis, R.",
    year: 2023,
    abstract: "We review the membrane stabilization effects of intracellular and extracellular trehalose during the freezing process of various immortalized cell lines.",
    url: "#"
  }
];

const MOCK_MATERIALS = [
  { item: "HeLa Cell Line", cat: "CCL-2", supplier: "ATCC", qty: "1 vial", cost: "$450.00" },
  { item: "D-(+)-Trehalose dihydrate", cat: "T9531", supplier: "Sigma-Aldrich", qty: "100 g", cost: "$68.50" },
  { item: "DMSO (Control)", cat: "D2650", supplier: "Sigma-Aldrich", qty: "5x5 mL", cost: "$42.00" },
  { item: "DMEM High Glucose", cat: "11965092", supplier: "Thermo Fisher", qty: "500 mL", cost: "$24.00" },
  { item: "Fetal Bovine Serum", cat: "10082147", supplier: "Thermo Fisher", qty: "50 mL", cost: "$115.00" },
];

export default function AIScientistApp() {
  const [activeTab, setActiveTab] = useState('input');
  
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
              {activeTab === 'review' && "Review"}
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
              {activeTab === 'input' && <ViewInput key="input" onNext={() => setActiveTab('plan')} />}
              {activeTab === 'plan' && <ViewPlan key="plan" />}
              {activeTab !== 'input' && activeTab !== 'plan' && (
                <motion.div key="placeholder" {...fadeUpProps} className="flex flex-col items-center justify-center h-64 text-zinc-400">
                  <p>View under construction.</p>
                </motion.div>
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
function ViewInput({ onNext }) {
  const [hypothesis, setHypothesis] = useState("");
  const [isChecking, setIsChecking] = useState(false);
  const [hasResults, setHasResults] = useState(false);

  const handleCheck = () => {
    if (!hypothesis.trim()) return;
    setIsChecking(true);
    setHasResults(false);
    // Mock network request
    setTimeout(() => {
      setIsChecking(false);
      setHasResults(true);
    }, 2000);
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
          <div className="text-xs text-zinc-400 flex items-center gap-1">
            <Sparkles size={14} className="text-amber-500" /> 
            AI optimization available after checking
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

      {/* Empty State: Suggestions */}
      <AnimatePresence>
        {!hasResults && !isChecking && (
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
            {/* Shimmer gradient */}
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
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-100 text-amber-800 border border-amber-200 font-medium text-xs">
                  <AlertCircle size={14} /> Similar Work Exists
                </div>
              </div>
              <div className="p-4 rounded-lg bg-zinc-50 border border-zinc-100 text-sm text-zinc-700 leading-relaxed">
                While trehalose is a known cryoprotectant, its specific use as a complete replacement for DMSO in HeLa cell lines to achieve a &gt;15% viability increase represents a highly specific protocol modification. Existing literature explores partial substitutions or different cell lines.
              </div>
            </div>

            {/* References */}
            <div>
              <h3 className="text-sm font-semibold text-zinc-900 mb-3 flex items-center gap-2">
                <BookOpen size={16} className="text-zinc-400"/> Relevant Literature
              </h3>
              <div className="space-y-3">
                {MOCK_REFERENCES.map((ref) => (
                  <div key={ref.id} className="p-5 rounded-xl border border-zinc-200/60 bg-white shadow-sm hover:border-zinc-300 transition-colors">
                    <div className="flex justify-between items-start gap-4">
                      <div>
                        <a href={ref.url} className="text-sm font-semibold text-indigo-600 hover:underline flex items-center gap-1">
                          {ref.title} <ExternalLink size={12} />
                        </a>
                        <div className="text-xs text-zinc-500 mt-1 flex items-center gap-2">
                          <span>{ref.authors}</span>
                          <span className="w-1 h-1 rounded-full bg-zinc-300"></span>
                          <span className="font-mono">{ref.year}</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-zinc-600 mt-3 leading-relaxed">{ref.abstract}</p>
                  </div>
                ))}
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
function ViewPlan() {
  const [isGenerating, setIsGenerating] = useState(true);
  const [generationStep, setGenerationStep] = useState(0);

  // Mock Generation Sequence
  useEffect(() => {
    if (!isGenerating) return;
    const steps = [
      { delay: 1000, step: 1 }, // Drafting protocol
      { delay: 2500, step: 2 }, // Sourcing materials
      { delay: 4000, step: 3 }, // Calculating budget
      { delay: 5500, step: 4 }, // Finalizing
    ];
    
    let timeouts = steps.map(({ delay, step }) => 
      setTimeout(() => setGenerationStep(step), delay)
    );
    
    const finish = setTimeout(() => setIsGenerating(false), 6000);
    
    return () => {
      timeouts.forEach(clearTimeout);
      clearTimeout(finish);
    };
  }, [isGenerating]);

  if (isGenerating) {
    return (
      <motion.div {...fadeUpProps} className="max-w-md mx-auto mt-20 p-8 rounded-2xl bg-white border border-zinc-200/60 shadow-sm text-center">
        <div className="relative w-16 h-16 mx-auto mb-6">
          <motion.div 
            className="absolute inset-0 rounded-full border-4 border-indigo-100"
          />
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
    );
  }

  return (
    <motion.div {...fadeUpProps} className="space-y-6">
      
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-zinc-900 tracking-tight">Experiment Plan</h2>
          <p className="text-sm text-zinc-500 mt-1 font-mono text-xs bg-zinc-100 px-2 py-1 rounded inline-block mt-2">
            ID: EXP-74B-2026
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-zinc-200/60 text-zinc-700 text-sm font-medium rounded-lg hover:bg-zinc-50 transition-colors shadow-sm">
            <Download size={16} /> Export Markdown
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            <FileText size={16} /> Export PDF
          </button>
        </div>
      </div>

      <div className="w-full h-px bg-zinc-200/60" />

      {/* Accordion Sections */}
      <div className="space-y-4">
        <AccordionSection title="1. Protocol" icon={<FlaskConical size={18} />} defaultOpen>
          <div className="prose prose-sm prose-zinc max-w-none">
            <p><strong>Objective:</strong> Compare post-thaw viability of HeLa cells frozen in standard DMSO media vs. trehalose-based media.</p>
            <ol className="mt-4 space-y-2">
              <li><strong>Cell Preparation:</strong> Harvest HeLa cells at 80% confluency using 0.25% Trypsin-EDTA. Centrifuge at <span className="font-mono text-indigo-600 bg-indigo-50 px-1 rounded">125 x g</span> for 5 mins.</li>
              <li><strong>Media Preparation:</strong> Prepare experimental freeze media consisting of complete DMEM supplemented with <span className="font-mono text-indigo-600 bg-indigo-50 px-1 rounded">200 mM</span> Trehalose. (Control: DMEM + 10% DMSO).</li>
              <li><strong>Resuspension:</strong> Resuspend cell pellets in respective freezing media to a final concentration of <span className="font-mono">1 x 10^6 cells/mL</span>.</li>
              <li><strong>Cooling:</strong> Aliquot 1 mL per cryovial. Place in a Mr. Frosty freezing container at -80°C overnight (-1°C/min cooling rate).</li>
            </ol>
          </div>
        </AccordionSection>

        <AccordionSection title="2. Materials & Budget" icon={<BookOpen size={18} />}>
          <div className="border border-zinc-200/60 rounded-lg overflow-hidden bg-white">
            <table className="w-full text-sm text-left">
              <thead className="bg-zinc-50 border-b border-zinc-200/60 text-xs uppercase text-zinc-500">
                <tr>
                  <th className="px-4 py-3 font-semibold">Material</th>
                  <th className="px-4 py-3 font-semibold">Cat #</th>
                  <th className="px-4 py-3 font-semibold">Supplier</th>
                  <th className="px-4 py-3 font-semibold">Qty</th>
                  <th className="px-4 py-3 font-semibold text-right">Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200/60">
                {MOCK_MATERIALS.map((mat, i) => (
                  <tr key={i} className="hover:bg-zinc-50/50 transition-colors">
                    <td className="px-4 py-3 font-medium text-zinc-900">{mat.item}</td>
                    <td className="px-4 py-3 font-mono text-xs text-zinc-500">{mat.cat}</td>
                    <td className="px-4 py-3 text-zinc-600">{mat.supplier}</td>
                    <td className="px-4 py-3 font-mono text-xs text-zinc-600">{mat.qty}</td>
                    <td className="px-4 py-3 font-mono text-xs text-zinc-900 text-right">{mat.cost}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-zinc-50 font-semibold border-t-2 border-zinc-200 text-zinc-900">
                <tr>
                  <td colSpan={4} className="px-4 py-3 text-right">Estimated Total:</td>
                  <td className="px-4 py-3 text-right font-mono">$704.50</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </AccordionSection>

        <AccordionSection title="3. Validation Approach" icon={<CheckCircle2 size={18} />}>
          <div className="space-y-4 text-sm text-zinc-700">
            <div>
              <h4 className="font-semibold text-zinc-900 mb-1">Primary Endpoint</h4>
              <p>Post-thaw cell viability (%) measured via Trypan Blue exclusion assay at 0h and 24h post-thawing.</p>
            </div>
            <div>
              <h4 className="font-semibold text-zinc-900 mb-1">Statistical Analysis</h4>
              <p>Unpaired Student's t-test comparing mean viability between DMSO and Trehalose groups. Significance defined as <span className="font-mono bg-zinc-100 px-1 rounded">p &lt; 0.05</span>. Required sample size calculated at <span className="font-mono bg-zinc-100 px-1 rounded">n=6</span> independent cryopreservations per group to achieve 80% power.</p>
            </div>
          </div>
        </AccordionSection>
      </div>
      
    </motion.div>
  );
}

// --- Helpers ---

function GenStepItem({ active, text }) {
  return (
    <div className={`flex items-center gap-3 text-sm transition-colors duration-500 ${active ? 'text-zinc-900' : 'text-zinc-400'}`}>
      {active ? <CheckCircle2 size={16} className="text-emerald-500" /> : <Circle size={16} className="text-zinc-300" />}
      {text}
    </div>
  );
}

function AccordionSection({ title, icon, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border border-zinc-200/60 rounded-xl bg-white shadow-[0_2px_8px_rgba(0,0,0,0.02)] overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-5 py-4 flex items-center justify-between bg-white hover:bg-zinc-50 transition-colors outline-none"
      >
        <div className="flex items-center gap-3 text-zinc-900 font-semibold">
          <span className="text-indigo-600">{icon}</span>
          {title}
        </div>
        <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={springTransition}>
          <ChevronDown size={18} className="text-zinc-400" />
        </motion.div>
      </button>
      
      <AnimatePresence initial={false}>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={springTransition}
          >
            <div className="px-5 pb-5 pt-2 border-t border-zinc-100">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
