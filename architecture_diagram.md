# System Architecture Visualization

Here is the beautiful, modern architecture diagram for **The AI Scientist** using Mermaid.js!

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'primaryBorderColor': '#e2e8f0', 'lineColor': '#64748b', 'fontFamily': 'Inter, sans-serif'}}}%%
flowchart TD
    classDef input fill:#f8fafc,stroke:#3b82f6,stroke-width:2px,color:#0f172a,rx:8,ry:8;
    classDef module fill:#ffffff,stroke:#6366f1,stroke-width:2px,color:#0f172a,rx:8,ry:8;
    classDef search fill:#fdf4ff,stroke:#d946ef,stroke-width:2px,color:#0f172a,rx:8,ry:8;
    classDef llm fill:#fff7ed,stroke:#f97316,stroke-width:2px,color:#0f172a,rx:8,ry:8;
    classDef generator fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#0f172a,rx:8,ry:8;
    classDef final fill:#ecfeff,stroke:#06b6d4,stroke-width:3px,color:#0f172a,rx:8,ry:8;
    classDef feedback fill:#fff1f2,stroke:#f43f5e,stroke-width:2px,color:#0f172a,stroke-dasharray: 5 5,rx:8,ry:8;
    classDef container fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px,stroke-dasharray: 5 5,rx:12,ry:12;

    A["🧠 <b>User Input</b><br/><small>Scientific Hypothesis</small>"]:::input
    
    subgraph Literature_QC["📚 Literature QC Module"]
        direction LR
        B1["ArXiv API<br/><small>Preprints</small>"]:::search
        B2["Semantic Scholar<br/><small>Graph API</small>"]:::search
    end
    Literature_QC:::container
    
    B3{"🔍 <b>Novelty Signal</b>"}:::module
    
    C["⚡ <b>LLM Orchestrator</b><br/><small>Multi-Provider Fallback<br/>Groq → Gemini → OpenAI</small>"]:::llm
    
    subgraph Experiment_Planners["🧪 AI Generation Modules"]
        direction LR
        D1["📋 <b>Protocol</b><br/><small>Step-by-step</small>"]:::generator
        D2["🧫 <b>Materials</b><br/><small>& Supply Chain</small>"]:::generator
        D3["💰 <b>Budget</b><br/><small>Cost Estimator</small>"]:::generator
        D4["📅 <b>Timeline</b><br/><small>Dependencies</small>"]:::generator
        D5["✅ <b>Validation</b><br/><small>Success Criteria</small>"]:::generator
    end
    Experiment_Planners:::container
    
    E["📄 <b>Complete Experiment Plan</b><br/><small>Ready for Lab Execution</small>"]:::final
    F["👨‍🔬 <b>Scientist Review & Feedback</b><br/><small>Few-Shot Data Storage</small>"]:::feedback

    A ===>|"Evaluates Novelty"| Literature_QC
    Literature_QC --> B3
    
    B3 ===>|"🟢 Not Found"| C
    B3 ===>|"🟡 Similar Work"| C
    B3 ===>|"🔴 Exact Match"| C
    
    C ===> Experiment_Planners
    
    Experiment_Planners ===> E
    
    E -.->|"Sent to Scientist"| F
    F -.->|"Few-Shot Learning Loop"| C
```

> [!TIP]
> This new Mermaid diagram has also been placed directly into your `README.md` to replace the old ASCII representation, providing an impressive and professional look when rendered on GitHub or any markdown viewer.
