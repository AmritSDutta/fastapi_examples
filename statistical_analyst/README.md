
# 📊 Statistical Analysis Agent — Powered by Gemini + Gradio  
Welcome to your **data-first AI analytics cockpit** 🚀 — upload datasets, interrogate them, and extract insights with **surgical statistical precision** (minus the surgical bills).

---

## **1. How to Use**
1. ▶️ **Start the app**  
   ```bash
   python ui.py
   ```
2. 📁 **Upload one or more XLSX/CSV/TXT files**.  
   A fresh FileSearch store is provisioned—because your data deserves a clean room.
3. 💬 Once upload completes, the chat automatically activates.  
   Start asking: “What is the variance of…”, “Any anomalies across sheets?”, etc.
4. 🧠 The agent performs **provably accurate statistical analysis** (no creative math).
5. 🧹 Hit **Close Chat** to:  
   - Clean up FileSearch stores  
   - Export a `Conversation.md`  
   - Reset the session  

---

## **2. Expectations & Behavior**
- **Exact calculations** — the agent never approximates unless explicitly requested.  
- **Short, analytical responses** — no fluff, no essays.  
- **Automatically identifies trends, patterns, anomalies.**  
- **Asks clarifying questions** when context is insufficient.  
- Uses **tables**, **correlations**, and **summaries** when beneficial.  
- Multi-file and multi-sheet XLSX analysis supported.  

---

## **3. Supported Use Cases**
- Descriptive statistics  
- Outlier detection  
- Covariance/Correlation analysis  
- Distribution inspection  
- Data sanity checks  
- Cross-file and cross-sheet comparisons  
- Basic inferential prep work  

(😄 For full Nobel-Prize-winning econometrics, please bring snacks.😄)

---

## **4. Constraints**
- Zero hallucinated values.  
- Only uses data present in FileSearch.  
- Never picks the wrong statistical method.  
- Uploading new files resets session.  

---

## **5. Architecture Overview**

```
                    ┌────────────────────────────────┐
                    │            User UI             │
                    │     (Gradio Frontend)          │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │        analyst ui Layer        │
                    │ - Button handlers              │
                    │ - Gradio states                │
                    │ - Converts primitives → UI     │
                    │ - No business logic (ever!)    │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │         agent.py Layer         │
                    │ - FileSearch store mgmt        │
                    │ - safe_call retry logic        │
                    │ - Upload orchestration         │
                    │ - Chat session creation        │
                    │ - Cleanup + transcript build   │
                    └───────────────┬────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────┐
                    │       Gemini 2.5 models        │
                    │        + FileSearch API        │
                    │   Statistical reasoning engine │
                    └────────────────────────────────┘
```

---

## **6. References**
- Gemini FileSearch Docs → https://ai.google.dev  
- Gradio Components → https://www.gradio.app/docs  
- Statistical Data Quality (ISO 8000) → https://www.iso.org/standard/69466.html  

A reminder: your intern (the AI) works 24×7 and never complains 😄




--------------------------------------------------------------------------
# ▶️ Running the Statistical Analysis UI — Concise Guide

**Quick start**
```bash
python ui.py
# or with Docker:
docker build -t stat-agent:latest .
docker run --rm -p 7860:7860 -e GOOGLE_API_KEY="$GOOGLE_API_KEY" stat-agent:latest
```

**Single-section summary (Sections 3–6: Upload / Chat / Close / Troubleshoot)**  
Upload one or more `.xlsx/.csv/.txt` files → backend creates an isolated FileSearch store and indexes them. Once indexing finishes the chat activates; ask crisp analytics prompts (e.g., “descriptive stats for Sheet1”, “find outliers across files”). Use **Send** to get short, validated numerical outputs, tables, correlations and anomaly flags. Click **Close Chat** to trigger safe cleanup, export `Conversation.md`, and reset UI (uploading new files always starts a fresh session). Troubleshooting: ensure files aren’t locked, check API quotas/creds, and disable popup-blockers for auto-downloads. (No drama—just logs and JSON.)

**Operational notes & Docker tips**  
- Pass credentials via env vars (e.g., `GOOGLE_API_KEY` or ADC JSON mount).  
- Expose port `7860` and bind to `0.0.0.0` for external access.  
- For production, run with a process supervisor, mount persistent logs, and limit container privileges.  

**Witty elevator pitch (30% sass, 70% utility)**  
Think of this as your overqualified stats intern who never sleeps, never steals your lunch, and always cites sources — but sometimes needs a gentle nudge if data context is missing. 🧠✨

**References**  
- Gradio docs: https://www.gradio.app/docs  
- Gemini / FileSearch overview: https://ai.google.dev  




### 📌 Docker MIME Handling (Important)

When running inside `python:slim` Docker images, Python’s built-in MIME database is incomplete.  
As a result, `mimetypes.guess_type()` returns `None` for `.xlsx`, `.xls`, and `.csv`, causing Google FileSearch uploads to fail.

To ensure consistent behavior across Windows, macOS, and Docker, explicitly register the missing MIME types at module import:

```python
mimetypes.add_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx")
mimetypes.add_type("application/vnd.ms-excel", ".xls")
mimetypes.add_type("text/csv", ".csv")
```

### 📌 User UI Guide — Multi-file Statistical Analysis Agent

1. **Drop files**: Drag or click the large left panel to upload XLSX/CSV/TXT. (Marker 1)
2. **Upload & Start Chat**: Press the button to ingest files and open the chat session. (Marker 2)
3. **Check the Status**: Monitor the status box for processing updates and readiness. (Marker 3)
4. **Enter Queries**: Type questions about the uploaded data in the textbox. Use natural language. (Marker 4)
5. **Send**: Press the Send button to submit your query and get responses. (Marker 5)
6. **Close Chat**: When done, press Close Chat to end the session and clear state. (Marker 6)

![UI Guide](./Statistical_analyst_annotated_v2.png)