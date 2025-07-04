
# 🤖 AgentFusion - Mixture-of-Agents LLM App

Combine the power of multiple AI language models to generate high-quality, well-rounded answers with **AgentFusion**!  

This Streamlit-powered app:
- Sends your question to **multiple LLMs**.
- Displays responses from each individual model.
- Aggregates all answers into a **final synthesized response** using an aggregator model.

---

## 🚀 Key Features:
- Query multiple open-source LLMs via Together AI.
- Compare individual model responses side by side.
- Get a smart, aggregated answer for better decision-making.
- Simple, clean user interface with Streamlit.

---

## 🔧 Setup Instructions:

### 1️⃣ Prerequisites:
- Python **3.8+**  
- Together AI API Key → [https://together.ai](https://together.ai)

---

### 2️⃣ Installation:
```bash
pip install -r requirements.txt
```

---

### 3️⃣ Running the App:
```bash
streamlit run agent_fusion_app.py
```

---

## 📝 How It Works:
1. Enter your **Together AI API key** and question.
2. The app queries these LLMs:
   - Mistralai/Mistral-7B-Instruct-v0.3  
   - Mistralai/Mistral-Small-24B-Instruct-2501  
   - Qwen/Qwen2.5-7B-Instruct-Turbo 
3. Each model returns its individual response.
4. The app combines these using the aggregator model (`Mistralai/Mistral-7B-Instruct-v0.3`) to create a unified answer.

---

## 💡 Notes:
- The app uses **smaller, affordable models** for budget-friendly testing.
- Ideal for experimenting with Mixture-of-Experts (MoE) style approaches.

---

## 📄 Project Location:
Same directory as your previous project (`Podscribe AI - Blog to Podcast Agent`):
```
D:/Projects/agent-verse/agents/AgentFusion
```

---

## 📬 Questions?
If you face issues or want enhancements, feel free to create an issue or PR.

---
