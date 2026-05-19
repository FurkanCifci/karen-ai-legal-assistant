# ✦ KarenAI — Multi-Agent Legal RAG Assistant

> This project is my direct response to the provided Case Challenge.
> My goal was to take the conceptual architectural planning and rapidly transform it into a fully functioning, production-ready system.
> Following an intensive, non-stop **5-hour engineering sprint**, this implementation is the result.
> 
> To maximize delivery velocity and mimic modern engineering workflows, I actively leveraged AI coding companions (like Cursor Agents).
>  Rather than shying away from AI, I embraced it as a force-multiplier to rapidly iterate on custom CSS components,
>  debug vector store collisions, and stitch together a complex multi-agent pipeline in record time.
> I believe true engineering today is about leveraging the best tools to ship robust products, fast.

---

## 🚀 Live Demo
👉 [Click here to experience KarenAI Live](https://karen-ai-legal-assistant-foda8mgwgmclvrpqtrh4h8.streamlit.app)

## 🏗️ Architecture & Core Components
- **RAG Context Store:** Orchestrates a local vector database (**ChromaDB**) to retrieve grounded airline rules and passenger rights documents.
- **Execution Engine:** Compiles legal complaint drafts by blending user disruption context with retrieved legal foundations.
- **The Judge:** An adversarial LLM agent that scores drafts for "pushover risk," detects voucher traps, and suggests strategic next tactics.

## 🛠️ Tech Stack
- **Frontend:** Streamlit (Custom Premium Glassmorphism UI)
- **Database:** ChromaDB (Vector Indexing)
- **AI Infrastructure:** Pollinations AI / LangChain Architecture
- **Language:** Python 3.11

---
Proudly crafted and deployed by **Furkan Cifci** — *Prospect Engineer*
