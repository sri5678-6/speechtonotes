# Live Voice-to-Notes Web App

**Overview:**  
- Web app to record voice, get live transcription, generate summarized notes using Gemini AI, and download as `.txt`.  
- Frontend: HTML, CSS, JavaScript, TailwindCSS  
- Backend: Python, FastAPI  

**Key Features:**  
1. Live voice recording  
2. Real-time transcription  
3. AI-generated summarized notes  
4. Download summarized notes as `.txt`  
5. Simple and intuitive user interface  

**Setup & Run Backend:**  
1. Open terminal and go to backend folder: `cd backend`  
2. Install dependencies:  
3. Set up API key (private):  
- Create file `api.env` in backend folder  
- Add: `GEMINI_API_KEY=your_api_key_here`  
- Do **not** upload this file to GitHub; add to `.gitignore`  
4. Run backend: `uvicorn main:app --reload`  
- Backend runs at `http://localhost:8000`  

**Setup & Run Frontend:**  
1. Open `frontend` folder  
2. Open `index.html` in any browser (Chrome, Firefox, Edge, etc.)  
3. Buttons functionality:  
- **Start Recording:** record audio and show live text  
- **Stop & Generate Notes:** generate summarized notes  
- **Download Notes:** save summarized notes as `.txt`  
4. Ensure frontend connects to backend: `http://localhost:8000/process-audio/`  

**Access:**  
- Backend: `http://localhost:8000`  
- Frontend: open `index.html` in browser  

**Notes & Important:**  
- Max audio length: 60 seconds  
- Microphone permissions required  
- Summarization uses Gemini AI → valid API key needed  
- Keep API key private; do **not** commit `api.env` to GitHub
