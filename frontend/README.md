# 📘 ExamyNex
## AI-Powered Online Examination & Monitoring Platform

**Frontend-Only Complete Version (Academic Project)**

---

## 🎯 Project Overview

ExamyNex is a comprehensive online examination platform designed for academic institutions. It provides a complete frontend solution with role-based dashboards for Admin, Faculty, and Students, featuring AI-powered question generation, real-time monitoring, and comprehensive analytics.

---

## 🛠️ Technology Stack

- **HTML5** - Semantic markup
- **CSS3 + Bootstrap 5** - Responsive styling
- **Vanilla JavaScript** - No frameworks (React/Angular free)
- **Chart.js** - Analytics and data visualization
- **WebSocket Placeholders** - Real-time data simulation

---

## 📁 Project Structure

```
newexamplatform/
├── index.html                          # Landing page
├── templates/
│   ├── auth/
│   │   ├── login.html                  # Login page (Netflix-style)
│   │   └── register.html               # Registration (Student/Faculty)
│   ├── admin/
│   │   ├── dashboard.html              # Admin dashboard
│   │   ├── faculty-approvals.html      # Faculty approval management
│   │   ├── students.html                # Student management
│   │   ├── faculty.html                # Faculty management
│   │   ├── exams.html                  # Exam view (read-only)
│   │   ├── audit-logs.html             # System audit logs
│   │   └── profile.html                 # Admin profile
│   ├── faculty/
│   │   ├── dashboard.html              # Faculty dashboard with charts
│   │   ├── create-exam.html            # Exam creation (AI/Manual)
│   │   ├── students.html                # Student management
│   │   ├── student-profile.html        # Student profile view
│   │   ├── student-performance.html      # Student performance details
│   │   ├── monitoring.html              # Live monitoring dashboard
│   │   ├── analytics.html               # Exam analytics & insights
│   │   └── profile.html                # Faculty profile
│   └── student/
│       ├── dashboard.html              # Student dashboard
│       ├── exams.html                  # Exam list
│       ├── exam-instructions.html      # Exam instructions
│       ├── exam-attempt.html           # Exam interface (with security)
│       ├── submission.html              # Submission status
│       └── results.html                # Exam results
└── static/
    ├── css/
    │   └── main.css                    # Main stylesheet
    └── js/
        ├── utils.js                    # Utility functions
        └── exam-security.js             # Security features
```

---

## 🎨 Design Features

### Color Scheme
- **Primary**: Dark Blue/Indigo (#1e3a8a)
- **Success**: Green (#10b981)
- **Danger**: Red (#ef4444)
- **Warning**: Yellow (#f59e0b)
- **Info**: Blue (#3b82f6)

### Status Badges
- 🟢 **Green** → Success / Passed
- 🔴 **Red** → Failed / Violation
- 🟡 **Yellow** → Warning / Pending
- 🔵 **Blue** → Info / Ongoing

---

## 👥 User Roles

### 1. Admin
- Dashboard with system statistics
- Faculty approval management
- Student and faculty management
- Exam view (read-only)
- Audit logs monitoring
- Profile management

### 2. Faculty
- Dashboard with exam statistics and charts
- Create exams (AI-Generated or Manual)
- Student management and performance tracking
- Live exam monitoring (WebSocket-based)
- Comprehensive analytics with Chart.js
- Profile management

### 3. Student
- Dashboard with exam overview
- View available exams
- Read exam instructions
- Take exams with security features
- View results and performance

---

## 🔒 Security Features

The exam interface includes:

1. **Right-click disabled** - Prevents context menu access
2. **Copy/paste disabled** - Blocks clipboard operations
3. **Tab switch detection** - Monitors window focus
4. **Violation tracking** - Counts security violations
5. **Auto-submit** - Automatically submits after 3 violations
6. **Timer enforcement** - Auto-submits when time expires
7. **Refresh warning** - Prevents accidental page refresh

---

## 📊 Features

### Public Pages
- ✅ Landing page with feature showcase
- ✅ Netflix-style login page
- ✅ Registration with Student/Faculty tabs

### Admin Module
- ✅ Dashboard with statistics
- ✅ Faculty approval system
- ✅ Student management with filters
- ✅ Faculty management
- ✅ Exam view (read-only)
- ✅ Audit logs with filtering

### Faculty Module
- ✅ Dashboard with Chart.js visualizations
- ✅ AI-Generated exam creation
- ✅ Manual exam creation with dynamic questions
- ✅ Student management with branch/semester filters
- ✅ Student profile and performance views
- ✅ Live monitoring dashboard (WebSocket placeholder)
- ✅ Analytics with bar and pie charts
- ✅ PDF download functionality (placeholder)

### Student Module
- ✅ Dashboard with exam overview
- ✅ Exam list with status
- ✅ Exam instructions page
- ✅ Secure exam interface
- ✅ Submission status page
- ✅ Detailed results view

---

## 🚀 Getting Started

### Prerequisites
- A modern web browser (Chrome, Firefox, Edge, Safari)
- A local web server (optional, for testing)

### Installation

1. **Clone or download** the project files
2. **Open** `index.html` in a web browser, OR
3. **Serve** using a local web server:

```bash
# Using Python
python -m http.server 8000

# Using Node.js (http-server)
npx http-server

# Using PHP
php -S localhost:8000
```

4. **Navigate** to `http://localhost:8000` in your browser

---

## 📝 Standardized Dropdowns

### Branches
- CSE (Computer Science Engineering)
- CSM (Computer Science & Mathematics)
- AIML (Artificial Intelligence & Machine Learning)
- CAD (Computer Aided Design)
- IT (Information Technology)
- ECE (Electronics & Communication Engineering)
- EEE (Electrical & Electronics Engineering)
- MECH (Mechanical Engineering)
- CIVIL (Civil Engineering)

### Semesters
- 1, 2, 3, 4, 5, 6, 7, 8

---

## 🔌 API Placeholders

All API endpoints are placeholders and should be connected to a backend:

- `/api/login/` - User authentication
- `/api/register/student/` - Student registration
- `/api/register/faculty/` - Faculty registration
- `/api/admin/approve-faculty/{id}/` - Approve faculty
- `/api/exam/create/` - Create exam
- `/api/exam/{id}/download-pdf/` - Download exam PDF
- WebSocket: `ws://localhost:8000/ws/monitoring/{exam_id}/` - Real-time monitoring

---

## 📱 Responsive Design

The platform is designed to be:
- **Desktop-first** - Optimized for desktop screens
- **Mobile-friendly** - Responsive layout for mobile devices
- **Sidebar navigation** - Collapsible on mobile

---

## ⚠️ Important Notes

1. **Frontend Only**: This is a complete frontend implementation. Backend integration is required for full functionality.

2. **Academic Project**: This platform is developed strictly for academic evaluation purposes. Not intended for commercial deployment.

3. **Placeholder Data**: All data shown is placeholder/demo data. Connect to a real backend for production use.

4. **WebSocket**: Real-time monitoring uses WebSocket placeholders. Implement actual WebSocket server for live updates.

5. **PDF Generation**: PDF download functionality is a placeholder. Implement server-side PDF generation.

---

## 🎓 Academic Disclaimer

**This platform is developed strictly for academic evaluation purposes. Not intended for commercial deployment.**

---

## 📄 License

This project is created for academic purposes only.

---

## 👨‍💻 Development

### File Structure Best Practices
- All HTML files in `templates/` directory
- CSS in `static/css/`
- JavaScript in `static/js/`
- Shared utilities in `utils.js`
- Security features in `exam-security.js`

### Adding New Features
1. Follow the existing code structure
2. Use standardized dropdowns (branches/semesters)
3. Maintain consistent styling with `main.css`
4. Use utility functions from `utils.js`
5. Follow the color scheme and badge conventions

---

## 🐛 Known Limitations

- Backend API integration required
- WebSocket server needed for real-time monitoring
- PDF generation requires server-side implementation
- Database integration needed for persistent data

---

## 📞 Support

For questions or issues related to this academic project, please refer to your course instructor or project guidelines.

---

**Built with ❤️ for Academic Excellence**

