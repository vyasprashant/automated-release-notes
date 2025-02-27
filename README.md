# 📌 Automated Release Notes Generator

## 🚀 Overview
This project provides an **AI-powered automated release notes generator** that fetches Jira issues and summarizes them into well-structured release notes. You can choose between two AI-powered summarization methods:

1️⃣ **Transformers-based Summarization** (`release_notes_ai_transformers.py`) – Uses a transformer model (BART) for summarization.
2️⃣ **Agent-based Summarization** (`release_notes_ai_agent.py`) – Uses an AI agent (Ollama) for dynamic summarization.

Both options take Jira issues, categorize them, and generate release notes automatically. The solution is containerized using **Docker**, allowing it to run consistently across environments.

---

## 📂 Project Structure
```
├── release_notes_ai_transformers.py  # Script using Transformers (BART) for summarization
├── release_notes_ai_agent.py         # Script using Ollama AI Agent for summarization
├── config.json                       # Configuration file with Jira details
├── requirements.txt                   # Dependencies for Python environment
├── Dockerfile                         # Docker setup for running the script
├── docker-compose-transformers.yml    # Docker Compose for Transformers-based summarization
├── docker-compose-ollama.yml          # Docker Compose for Ollama AI Agent-based summarization
├── output/                            # Folder where release notes are saved
```

---

## 🛠️ Setup and Usage

### 1️⃣ **Configuration (config.json)**
Before running the script, update `config.json` with your Jira credentials and project details:
```json
{
  "JIRA_URL": "https://your-jira-instance.atlassian.net",
  "JIRA_USERNAME": "your-email@example.com",
  "JIRA_PASSWORD": "your-api-token",
  "VERSION": "Release-1.0.0"
}
```

---

## 🐳 Running with Docker
The solution is **containerized**, so you can run it using Docker:

### **1️⃣ Running with Transformers (BART)**
#### **🔹 Build and Run the Container**
```bash
docker-compose -f docker-compose-transformers.yml up --build
```
✅ This runs `release_notes_ai_transformers.py` inside a container.

---

### **2️⃣ Running with AI Agent (Ollama)**
#### **🔹 Start Ollama (If Running Locally)**
```bash
docker-compose -f docker-compose-ollama.yml up --build
```
✅ This runs `release_notes_ai_agent.py` inside a container along with an Ollama AI container.

---

## 📌 Summary
| Method | AI Used | Best For |
|--------|--------|----------|
| **Transformers (BART)** | Facebook BART | Summarization using a pre-trained transformer |
| **AI Agent (Ollama)** | Llama3 (or other models) | Dynamic, prompt-driven summarization |

Both approaches are effective—**Transformers** work best for structured summarization, while **Agents** provide a more dynamic and natural summary. 🚀

---

## 🔗 Next Steps
- 🎯 **Test both methods** and choose the one that best fits your needs.
- 🔧 **Customize the summarization prompts** in `release_notes_ai_agent.py` for better results.
- 📈 **Integrate this into CI/CD pipelines** to generate release notes automatically.

Happy automating! 🎉

