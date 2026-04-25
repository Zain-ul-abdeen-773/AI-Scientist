import os

filepath = r"d:\Study\Deep Neural Networks\MIT Project\app.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add get_system_info
if "def get_system_info" not in content:
    get_system_info_func = '''
def get_system_info(state: AppState):
    llm_status = state.llm.status()
    status_lines = []
    for provider, available in llm_status.items():
        icon = "✅" if available else "❌"
        status_lines.append(f"- {icon} **{provider.title()}**")

    feedback_stats = state.feedback_store.get_stats()
    
    return f"""### 🏗️ Architecture

```
User Input (Hypothesis)
       │
       ▼
┌─────────────────┐
│  Literature QC  │ ── ArXiv + Semantic Scholar (parallel)
│  (Novelty Check)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Experiment Planner        │
│  ┌──────────┐ ┌───────────┐│
│  │ Protocol │ │ Materials ││
│  └──────────┘ └───────────┘│
│  ┌──────────┐ ┌───────────┐│
│  │ Timeline │ │Validation ││
│  └──────────┘ └───────────┘│
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────┐
│ Scientist Review│ ── Feedback Store → Few-Shot Learning
│ (Learning Loop) │
└─────────────────┘
```

### 🔌 LLM Providers
{chr(10).join(status_lines)}

Active provider: **{state.llm.provider_name}**

### ⚡ Optimizations
- **Parallel search** — ArXiv + S2 via ThreadPoolExecutor
- **Response caching** — Repeated prompts return instantly
- **Retry + backoff** — Handles rate limits gracefully (3 retries)
- **S2 rate limiting** — Prevents 429 throttling
- **BM25 Retrieval** — Advanced semantic routing for few-shot feedback

### 📊 Feedback Stats
- Total feedback items: **{feedback_stats['total_count']}**
- Diagnostics: **{feedback_stats['types'].get('diagnostics', 0)}**
- Cell Biology: **{feedback_stats['types'].get('cell_biology', 0)}**
- Average Rating: **{feedback_stats['avg_rating']:.1f}/5**"""
'''
    content = content.replace('def create_app', get_system_info_func + '\n\ndef create_app')

# Replace Tab 4 content
tab4_target = '''            with gr.Tab("ℹ️ System Info", id="info_tab"):
                # LLM status
                llm_status = state.llm.status()
                status_lines = []
                for provider, available in llm_status.items():
                    icon = "✅" if available else "❌"
                    status_lines.append(f"- {icon} **{provider.title()}**")

                feedback_stats = state.feedback_store.get_stats()

                gr.Markdown(
                    f"""
### 🏗️ Architecture

```
User Input (Hypothesis)
       │
       ▼
┌─────────────────┐
│  Literature QC  │ ── ArXiv + Semantic Scholar (parallel)
│  (Novelty Check)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Experiment Planner        │
│  ┌──────────┐ ┌───────────┐│
│  │ Protocol │ │ Materials ││
│  └──────────┘ └───────────┘│
│  ┌──────────┐ ┌───────────┐│
│  │ Timeline │ │Validation ││
│  └──────────┘ └───────────┘│
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────┐
│ Scientist Review│ ── Feedback Store → Few-Shot Learning
│ (Learning Loop) │
└─────────────────┘
```

### 🔌 LLM Providers
{chr(10).join(status_lines)}

Active provider: **{state.llm.provider_name}**

### ⚡ Optimizations
- **Parallel search** — ArXiv + S2 via ThreadPoolExecutor
- **Response caching** — Repeated prompts return instantly
- **Retry + backoff** — Handles rate limits gracefully (3 retries)
- **S2 rate limiting** — Prevents 429 throttling

### 📊 Feedback Stats
- Total feedback items: **{feedback_stats['total_count']}**
- Average rating: **{feedback_stats['avg_rating']:.1f}/5**
- Experiment types: {json.dumps(feedback_stats.get('types', {}), indent=2) if feedback_stats.get('types') else 'None yet'}

### 🔗 Data Sources
- **ArXiv** — REST API (no key needed)
- **Semantic Scholar** — Graph API (no key needed)
- **protocols.io** — Referenced in generated protocols
- **Bio-protocol** — Referenced in generated protocols

### 🏆 Hack-Nation × World Bank Youth Summit
Global AI Hackathon 2026 — FULCRUM × Hack-Nation Challenge
                    """
                )

    return app'''

tab4_replacement = '''            with gr.Tab("ℹ️ System Info", id="info_tab"):
                info_markdown = gr.Markdown()
                
                # Hidden button to fetch system info for API clients
                get_info_btn = gr.Button("Get Info", visible=False)
                get_info_btn.click(
                    fn=get_system_info,
                    inputs=[gr.State(state)],
                    outputs=[info_markdown],
                    api_name="get_system_info",
                )
                
                # Also load it on page load for Gradio UI
                app.load(
                    fn=get_system_info,
                    inputs=[gr.State(state)],
                    outputs=[info_markdown],
                )

    return app'''

content = content.replace(tab4_target, tab4_replacement)

# Apply api_name to buttons
if 'api_name="check_literature"' not in content:
    content = content.replace('outputs=[novelty_badge, assessment_text, references_text],', 'outputs=[novelty_badge, assessment_text, references_text],\n                    api_name="check_literature",')
    content = content.replace('outputs=[refined_output, refine_accordion],', 'outputs=[refined_output, refine_accordion],\n                    api_name="refine_hypothesis",')
    content = content.replace('outputs=[plan_output],', 'outputs=[plan_output],\n                    api_name="generate_plan",')
    content = content.replace('outputs=[download_file],', 'outputs=[download_file],\n                    api_name="export_md",', 1)
    
    # second instance is export_pdf
    parts = content.split('outputs=[download_file],')
    if len(parts) > 2:
        content = parts[0] + 'outputs=[download_file],' + parts[1] + 'outputs=[download_file],\n                    api_name="export_pdf",' + parts[2]
        
    content = content.replace('outputs=[feedback_status],', 'outputs=[feedback_status],\n                    api_name="save_feedback",')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated app.py successfully!")
