# Real Estate Analysis Chatbot

## 🏠 Project Overview
A full-stack web application that provides real estate analysis for different localities. Users can query area data and get text summaries, interactive charts, and detailed data tables.

## 🚀 Features
- **Chat-style Interface** - Natural language queries
- **Real Estate Analysis** - Price and demand trends
- **Interactive Charts** - Visual data representation  
- **Comparison Tool** - Compare multiple areas
- **Data Tables** - Detailed filtered data

## 🛠️ Tech Stack
- **Backend**: Django + Django REST Framework + Pandas
- **Frontend**: React + TypeScript + Bootstrap
- **Charts**: Recharts
- **Data Processing**: Excel file parsing

## 📁 Project Structure
\`\`\`
realestate_project/
├── backend/                 # Django backend
│   ├── chatbot/            # Django app
│   │   ├── views.py        # API endpoints
│   │   ├── utils.py        # Data analysis logic
│   │   └── urls.py         # URL routing
│   ├── realestate_backend/ # Django project
│   │   ├── settings.py     # Project settings
│   │   └── urls.py         # Main URLs
│   ├── requirements.txt    # Python dependencies
│   └── manage.py           # Django management
├── frontend/               # React frontend  
│   ├── src/
│   │   ├── App.tsx         # Main React component
│   │   └── ...other files
│   ├── package.json        # Node dependencies
│   └── package-lock.json
└── README.md
\`\`\`

## 🏃‍♂️ Quick Start

### Backend Setup
\`\`\`bash
cd backend
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py runserver
\`\`\`
Backend runs on: http://127.0.0.1:8000

### Frontend Setup  
\`\`\`bash
cd frontend
npm install
npm start
\`\`\`
Frontend runs on: http://localhost:3001

## 📊 Sample Queries
- \\\"Analyze Wakad\\\"
- \\\"Compare Wakad and Aundh\\\" 
- \\\"Show price growth for Akurdi\\\"

## 🎯 Assignment Requirements
✅ Backend with Django & Python  
✅ Frontend with React & Bootstrap  
✅ Excel data processing  
✅ Text summaries, charts, and tables  
✅ Chat-style interface  
✅ Comparison functionality  

## 👨‍💻 Developer
Hinda Vishewale
" > README.md
