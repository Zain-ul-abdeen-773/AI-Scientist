# Project Architecture Diagram

This diagram reflects the current implementation across Python backend, optional React frontend, external APIs, and local data stores.

```mermaid
flowchart TB
    %% Clients
    user[Researcher]
    gradio_ui[Gradio UI\napp.py]
    react_ui[React Frontend\nfrontend/src/App.jsx]

    user --> gradio_ui
    user --> react_ui
    react_ui -->|@gradio/client API calls| gradio_ui

    %% Backend core
    subgraph backend[Python Backend]
        direction TB
        entry[main.py]
        appstate[AppState]
        llm_client[LLMClient\nProvider fallback + cache + retries]
        novelty[NoveltyChecker\nParallel literature search]
        planner[ExperimentPlanner]
        protocol[ProtocolGenerator]
        materials[MaterialsBudgetGenerator]
        timeline[TimelineBuilder]
        validation[ValidationDesigner]
        store[FeedbackStore]
        learner[FeedbackLearner]
        pdf[PDF Exporter]
        logger[Loguru Logger]

        entry --> gradio_ui
        gradio_ui --> appstate

        appstate --> llm_client
        appstate --> novelty
        appstate --> planner
        appstate --> store
        appstate --> learner

        planner --> protocol
        planner --> materials
        planner --> timeline
        planner --> validation

        learner --> store
        gradio_ui --> pdf
        entry --> logger
    end

    %% External services
    subgraph external[External Services]
        direction TB
        arxiv_api[ArXiv API]
        s2_api[Semantic Scholar API]
        groq_api[Groq API]
        gemini_api[Gemini API]
        openai_api[OpenAI API]
    end

    novelty --> arxiv_api
    novelty --> s2_api

    llm_client -->|priority 1| groq_api
    llm_client -->|priority 2| gemini_api
    llm_client -->|priority 3| openai_api

    %% Storage and artifacts
    subgraph data[Local Storage and Artifacts]
        direction TB
        feedback_json[data/feedback/*.json]
        app_log[data/ai_scientist.log]
        md_out[experiment_plan.md]
        pdf_out[experiment_plan.pdf]
    end

    store <--> feedback_json
    logger --> app_log
    gradio_ui --> md_out
    pdf --> pdf_out

    %% API surface from UI to backend handlers
    react_ui -.->|/check_literature\n/refine_hypothesis\n/generate_plan\n/export_md\n/export_pdf\n/save_feedback\n/get_system_info| gradio_ui
```
