import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import time
from enum import Enum
import json
import io
import numpy as np

# Enhanced Enum classes with emojis
class PerformanceStatus(Enum):
    EXCELLENT = "⭐ Excellent"
    GOOD = "👍 Good" 
    AVERAGE = "📊 Average"
    NEEDS_IMPROVEMENT = "🚨 Needs Improvement"

class Grade(Enum):
    A = "🎯 A"
    B = "📚 B"
    C = "📝 C" 
    D = "⚠️ D"
    F = "❌ F"

class AttendanceStatus(Enum):
    EXCELLENT = "✅ Excellent"
    GOOD = "👍 Good"
    AVERAGE = "📊 Average" 
    POOR = "😟 Poor"

class Student:
    def __init__(self, student_id, name, age, grade, email, performance, phone="", course="", department="", enrollment_date="", attendance=95.0):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.performance = performance
        self.phone = phone
        self.course = course
        self.department = department
        self.enrollment_date = enrollment_date
        self.attendance = attendance
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activities = []
    
    def calculate_status(self):
        if self.performance >= 90:
            return PerformanceStatus.EXCELLENT.value
        elif self.performance >= 75:
            return PerformanceStatus.GOOD.value
        elif self.performance >= 60:
            return PerformanceStatus.AVERAGE.value
        else:
            return PerformanceStatus.NEEDS_IMPROVEMENT.value
    
    def calculate_attendance_status(self):
        if self.attendance >= 95:
            return AttendanceStatus.EXCELLENT.value
        elif self.attendance >= 85:
            return AttendanceStatus.GOOD.value
        elif self.attendance >= 75:
            return AttendanceStatus.AVERAGE.value
        else:
            return AttendanceStatus.POOR.value
    
    def add_activity(self, activity_type, description, date=None):
        activity = {
            'type': activity_type,
            'description': description,
            'date': date or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'id': len(self.activities) + 1
        }
        self.activities.append(activity)
        return activity
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'email': self.email,
            'performance': self.performance,
            'phone': self.phone,
            'course': self.course,
            'department': self.department,
            'enrollment_date': self.enrollment_date,
            'attendance': self.attendance,
            'last_updated': self.last_updated,
            'activities': self.activities
        }

class StudentValidator:
    @staticmethod
    def validate_student_data(data):
        errors = []
        if not data.get('name') or len(data['name'].strip()) < 2:
            errors.append("Name must be at least 2 characters long")
        if not data.get('age') or data['age'] < 15 or data['age'] > 70:
            errors.append("Age must be between 15 and 70")
        if not data.get('email') or '@' not in data['email']:
            errors.append("Valid email address is required")
        if not data.get('performance') or data['performance'] < 0 or data['performance'] > 100:
            errors.append("Performance must be between 0 and 100")
        if not data.get('course') or len(data['course'].strip()) < 2:
            errors.append("Course must be at least 2 characters long")
        if data.get('attendance') and (data['attendance'] < 0 or data['attendance'] > 100):
            errors.append("Attendance must be between 0 and 100")
        return errors

class AdvancedStudentManager:
    def __init__(self):
        self.students = []
        self.analytics_data = {}
        self.cache_stats = None
        self.cache_time = None
        self.load_sample_data()
    
    def load_sample_data(self):
        # Enhanced sample data with realistic information
        sample_students = [
            Student("ST001", "John Smith", 20, Grade.A.value, "john.smith@university.edu", 92.0, "+1234567890", 
                   "Computer Science", "Engineering", "2023-09-01", 96.5),
            Student("ST002", "Emma Johnson", 22, Grade.B.value, "emma.johnson@university.edu", 78.5, "+1234567891", 
                   "Data Science", "Computer Science", "2023-09-01", 88.2),
            Student("ST003", "Michael Brown", 21, Grade.A.value, "michael.brown@university.edu", 88.0, "+1234567892", 
                   "Artificial Intelligence", "Computer Science", "2023-09-01", 94.7),
            Student("ST004", "Sarah Davis", 19, Grade.C.value, "sarah.davis@university.edu", 65.5, "+1234567893", 
                   "Biology", "Life Sciences", "2023-09-01", 92.1),
            Student("ST005", "David Wilson", 23, Grade.B.value, "david.wilson@university.edu", 72.0, "+1234567894", 
                   "Mechanical Engineering", "Engineering", "2023-09-01", 85.4),
            Student("ST006", "Lisa Anderson", 20, Grade.A.value, "lisa.anderson@university.edu", 95.0, "+1234567895", 
                   "Business Administration", "Business", "2023-09-01", 98.2),
            Student("ST007", "Robert Garcia", 22, Grade.C.value, "robert.garcia@university.edu", 62.0, "+1234567896", 
                   "Chemistry", "Science", "2023-09-01", 76.8),
            Student("ST008", "Maria Martinez", 21, Grade.B.value, "maria.martinez@university.edu", 79.0, "+1234567897", 
                   "Psychology", "Social Sciences", "2023-09-01", 89.3),
            Student("ST009", "James Taylor", 24, Grade.A.value, "james.taylor@university.edu", 91.5, "+1234567898",
                   "Electrical Engineering", "Engineering", "2023-09-01", 93.7),
            Student("ST010", "Sophia Clark", 19, Grade.B.value, "sophia.clark@university.edu", 81.0, "+1234567899",
                   "Mathematics", "Science", "2023-09-01", 87.9),
        ]
        
        # Add sample activities
        sample_students[0].add_activity("Assignment", "Completed Advanced Algorithms assignment")
        sample_students[1].add_activity("Project", "Submitted Data Visualization project")
        sample_students[2].add_activity("Exam", "Scored 95% in AI Midterm")
        
        self.students = sample_students
    
    def get_next_student_id(self):
        if not self.students:
            return "ST001"
        max_id = max(int(s.student_id[2:]) for s in self.students)
        return f"ST{max_id + 1:03d}"
    
    def add_student(self, student):
        try:
            self.students.append(student)
            self.clear_cache()
            return True, "Student added successfully"
        except Exception as e:
            return False, f"Error adding student: {str(e)}"
    
    def get_all_students(self):
        return self.students
    
    def get_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def update_student(self, student_id, **kwargs):
        student = self.get_student(student_id)
        if not student:
            return False, "Student not found"
        
        try:
            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            student.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.clear_cache()
            return True, "Student updated successfully"
        except Exception as e:
            return False, f"Error updating student: {str(e)}"
    
    def delete_student(self, student_id):
        student = self.get_student(student_id)
        if not student:
            return False, "Student not found"
        
        try:
            self.students = [s for s in self.students if s.student_id != student_id]
            self.clear_cache()
            return True, "Student deleted successfully"
        except Exception as e:
            return False, f"Error deleting student: {str(e)}"
    
    def clear_cache(self):
        self.cache_stats = None
        self.cache_time = None
    
    def search_students(self, query):
        if not query:
            return self.students
        
        query = query.lower()
        results = []
        for student in self.students:
            if (query in student.name.lower() or 
                query in student.email.lower() or 
                query in student.course.lower() or 
                query in student.department.lower() or 
                query in student.phone.lower() or
                query in student.student_id.lower()):
                results.append(student)
        return results
    
    def get_statistics(self):
        # Cache statistics for 30 seconds
        current_time = time.time()
        if self.cache_stats and self.cache_time and (current_time - self.cache_time) < 30:
            return self.cache_stats
        
        if not self.students:
            stats = {}
        else:
            total_students = len(self.students)
            average_performance = sum(s.performance for s in self.students) / total_students
            average_age = sum(s.age for s in self.students) / total_students
            average_attendance = sum(s.attendance for s in self.students) / total_students
            
            status_distribution = {status.value: 0 for status in PerformanceStatus}
            grade_distribution = {grade.value: 0 for grade in Grade}
            attendance_distribution = {status.value: 0 for status in AttendanceStatus}
            course_distribution = {}
            department_distribution = {}
            
            for student in self.students:
                status = student.calculate_status()
                attendance_status = student.calculate_attendance_status()
                
                status_distribution[status] = status_distribution.get(status, 0) + 1
                grade_distribution[student.grade] = grade_distribution.get(student.grade, 0) + 1
                attendance_distribution[attendance_status] = attendance_distribution.get(attendance_status, 0) + 1
                course_distribution[student.course] = course_distribution.get(student.course, 0) + 1
                department_distribution[student.department] = department_distribution.get(student.department, 0) + 1
            
            # Performance trends
            performances = [s.performance for s in self.students]
            performance_trend = "Stable"
            if len(performances) >= 2:
                if performances[-1] > performances[0]:
                    performance_trend = "Improving"
                elif performances[-1] < performances[0]:
                    performance_trend = "Declining"
            
            stats = {
                'total_students': total_students,
                'average_performance': round(average_performance, 1),
                'average_age': round(average_age, 1),
                'average_attendance': round(average_attendance, 1),
                'status_distribution': status_distribution,
                'grade_distribution': grade_distribution,
                'attendance_distribution': attendance_distribution,
                'course_distribution': course_distribution,
                'department_distribution': department_distribution,
                'performance_trend': performance_trend,
                'top_performer': max(self.students, key=lambda x: x.performance).name if self.students else "N/A",
                'most_attended': max(self.students, key=lambda x: x.attendance).name if self.students else "N/A"
            }
        
        self.cache_stats = stats
        self.cache_time = current_time
        return stats
    
    def get_performance_analysis(self):
        if not self.students:
            return {}
        
        performances = [s.performance for s in self.students]
        attendances = [s.attendance for s in self.students]
        
        return {
            'max_performance': max(performances),
            'min_performance': min(performances),
            'median_performance': np.median(performances),
            'pass_rate': (sum(1 for s in self.students if s.performance >= 60) / len(self.students)) * 100,
            'excellence_rate': (sum(1 for s in self.students if s.performance >= 90) / len(self.students)) * 100,
            'avg_attendance': sum(attendances) / len(attendances),
            'correlation': np.corrcoef(performances, attendances)[0,1] if len(performances) > 1 else 0
        }
    
    def bulk_delete_students(self, student_ids):
        try:
            initial_count = len(self.students)
            self.students = [s for s in self.students if s.student_id not in student_ids]
            deleted_count = initial_count - len(self.students)
            self.clear_cache()
            return True, f"Successfully deleted {deleted_count} students"
        except Exception as e:
            return False, f"Error during bulk deletion: {str(e)}"
    
    def export_to_csv(self):
        try:
            data = []
            for student in self.students:
                data.append({
                    'student_id': student.student_id,
                    'name': student.name,
                    'age': student.age,
                    'grade': student.grade,
                    'email': student.email,
                    'performance': student.performance,
                    'phone': student.phone,
                    'course': student.course,
                    'department': student.department,
                    'enrollment_date': student.enrollment_date,
                    'attendance': student.attendance,
                    'last_updated': student.last_updated
                })
            
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            return True, "Data exported successfully", csv
        except Exception as e:
            return False, f"Export failed: {str(e)}", None
    
    def import_from_csv(self, file_content):
        try:
            df = pd.read_csv(io.StringIO(file_content))
            imported_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    student_data = {
                        'name': str(row.get('name', '')),
                        'age': int(row.get('age', 18)),
                        'grade': str(row.get('grade', Grade.B.value)),
                        'email': str(row.get('email', '')),
                        'performance': float(row.get('performance', 75)),
                        'phone': str(row.get('phone', '')),
                        'course': str(row.get('course', '')),
                        'department': str(row.get('department', 'General')),
                        'attendance': float(row.get('attendance', 95.0))
                    }
                    
                    validation_errors = StudentValidator.validate_student_data(student_data)
                    if validation_errors:
                        errors.append(f"Row {_ + 1}: {', '.join(validation_errors)}")
                        continue
                    
                    student_id = self.get_next_student_id()
                    new_student = Student(
                        student_id=student_id,
                        name=student_data['name'],
                        age=student_data['age'],
                        grade=student_data['grade'],
                        email=student_data['email'],
                        performance=student_data['performance'],
                        phone=student_data['phone'],
                        course=student_data['course'],
                        department=student_data['department'],
                        enrollment_date=datetime.now().strftime("%Y-%m-%d"),
                        attendance=student_data['attendance']
                    )
                    
                    self.students.append(new_student)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {_ + 1}: Error processing - {str(e)}")
            
            self.clear_cache()
            return True, f"Successfully imported {imported_count} students", errors
            
        except Exception as e:
            return False, f"Import failed: {str(e)}", []

class ModernStudentManagementUI:
    def __init__(self):
        self.manager = AdvancedStudentManager()
        self.setup_page()
    
    def setup_page(self):
        st.set_page_config(
            page_title="Student Record Management System",
            layout="wide",
            initial_sidebar_state="expanded",
            page_icon="🎓"
        )
        
        # Initialize session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "main_dashboard"
        
        # Black Theme CSS
        st.markdown("""
        <style>
        /* Main background - Black Theme */
        .main {
            background: #121212;
            color: #E0E0E0;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(to right, #1A1A1A, #2D2D2D);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        .header-title {
            font-size: 24px;
            font-weight: bold;
        }
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .welcome-message {
            font-size: 16px;
        }
        
        .current-date {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .logout-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .logout-btn:hover {
            background: rgba(255,255,255,0.2);
        }
        
        /* Sidebar styling */
        .sidebar-container {
            background: #1A1A1A;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        .sidebar-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .sidebar-menu {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .sidebar-menu li {
            margin-bottom: 10px;
        }
        
        .sidebar-menu a {
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            padding: 10px 15px;
            border-radius: 4px;
            transition: all 0.3s;
        }
        
        .sidebar-menu a:hover, .sidebar-menu a.active {
            background: rgba(255,255,255,0.1);
        }
        
        .sidebar-menu a i {
            margin-right: 10px;
        }
        
        .sidebar-time {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 16px;
            text-align: center;
        }
        
        /* Main content area */
        .content-container {
            padding: 20px;
        }
        
        /* Dashboard buttons */
        .dashboard-buttons {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 50px;
        }
        
        .dashboard-btn {
            background: #1A1A1A;
            color: white;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 200px;
            height: 200px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .dashboard-btn:hover {
            background: #2D2D2D;
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        
        .dashboard-btn i {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .dashboard-btn span {
            font-size: 18px;
            font-weight: bold;
        }
        
        /* Override Streamlit styles */
        .stApp {
            background-color: #121212;
        }
        
        .css-1d391kg, .css-1lcbmhc {
            background: #121212;
        }
        
        .stButton > button {
            background-color: #1A1A1A;
            color: white;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 8px 15px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: #2D2D2D;
        }
        
        /* Form styling */
        .stForm {
            background: #1A1A1A;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            background: #2D2D2D;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 8px;
            color: white;
        }
        
        /* Table styling */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        .dataframe th {
            background: #1A1A1A;
            color: white;
        }
        
        .dataframe td {
            background: #2D2D2D;
            color: white;
        }
        
        /* Card styling */
        .card {
            background: #1A1A1A;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: white;
        }
        
        /* Status badges */
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
        }
        
        .status-excellent {
            background: rgba(76, 175, 80, 0.2);
            color: #81C784;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        
        .status-good {
            background: rgba(33, 150, 243, 0.2);
            color: #64B5F6;
            border: 1px solid rgba(33, 150, 243, 0.3);
        }
        
        .status-average {
            background: rgba(255, 152, 0, 0.2);
            color: #FFB74D;
            border: 1px solid rgba(255, 152, 0, 0.3);
        }
        
        .status-needs-improvement {
            background: rgba(244, 67, 54, 0.2);
            color: #E57373;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }
        
        /* Hide default Streamlit elements */
        .stDeployButton {
            display: none;
        }
        
        /* Icon styling */
        .icon {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        /* Streamlit text elements */
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader {
            color: #E0E0E0 !important;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            background: #1A1A1A;
            border: 1px solid #333;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #2D2D2D;
            color: white;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: #1A1A1A;
            color: white;
        }
        
        /* Selectbox styling */
        .stSelectbox div[data-baseweb="select"] {
            background: #2D2D2D;
            color: white;
        }
        
        /* Slider styling */
        .stSlider {
            color: white;
        }
        
        /* Chart background */
        .js-plotly-plot .plotly .main-svg {
            background: #1A1A1A !important;
        }
        
        /* Metric cards */
        .metric {
            background: #1A1A1A;
            border: 1px solid #333;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: #1A1A1A;
            color: white;
        }
        
        .streamlit-expanderContent {
            background: #2D2D2D;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def show_header(self):
        # Get current date and time
        now = datetime.now()
        current_date = now.strftime("%A, %B %d, %Y")
        current_time = now.strftime("%I:%M:%S %p")
        
        # Header with title, welcome message, date, and logout
        st.markdown(f"""
        <div class="header-container">
            <div class="header-title">Student Record Management System</div>
            <div class="header-info">
                <div class="welcome-message">Welcome: admin</div>
                <div class="current-date">{current_date}</div>
                
                
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    
        
    
    def show_sidebar(self):
        # Get current time
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        
        # Sidebar with navigation menu
        st.markdown(f"""
        <div class="sidebar-container">
            <div class="sidebar-title">Navigation</div>
            <ul class="sidebar-menu">
                <li><a href="?page=dashboard" class="{'active' if st.session_state.current_page == 'main_dashboard' else ''}">📊 Dashboard</a></li>
                <li><a href="?page=students" class="{'active' if st.session_state.current_page == 'student_directory' else ''}">👥 Manage Students</a></li>
                <li><a href="?page=add_student" class="{'active' if st.session_state.current_page == 'student_registration' else ''}">➕ Add Student</a></li>
                <li><a href="?page=analytics" class="{'active' if st.session_state.current_page == 'advanced_analytics' else ''}">📈 About Data</a></li>
                <li><a href="?page=management" class="{'active' if st.session_state.current_page == 'student_management' else ''}">⚙️ Update Student</a></li>
            </ul>
                
            
            
        </div>
        """, unsafe_allow_html=True)
        
        # Check for page parameter in URL
        query_params = st.experimental_get_query_params()
        if 'page' in query_params:
            page = query_params['page'][0]
            if page == 'dashboard':
                st.session_state.current_page = 'main_dashboard'
            elif page == 'students':
                st.session_state.current_page = 'student_directory'
            elif page == 'add_student':
                st.session_state.current_page = 'student_registration'
            elif page == 'analytics':
                st.session_state.current_page = 'advanced_analytics'
            elif page == 'management':
                st.session_state.current_page = 'student_management'
            elif page == 'data':
                st.session_state.current_page = 'data_operations'
    
    def show_main_dashboard(self):
        # Add custom CSS for dashboard buttons
        st.markdown("""
        <style>
        .dashboard-btn-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 50px 0;
        }
        
        .stButton > button {
            background: #1A1A1A;
            color: white;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 200px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            line-height: 1.5;
        }
        
        .stButton > button:hover {
            background: #2D2D2D;
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        }
        
        .stButton > button:focus {
            outline: none;
            box-shadow: 0 0 0 2px rgba(255,255,255,0.1), 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .stButton > button span {
            margin-top: 10px;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create two columns for buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Students button
            if st.button("👥\n\nStudents", 
                       key="dashboard_students_btn",
                       use_container_width=True):
                st.session_state.current_page = "student_directory"
                st.rerun()
        
        with col2:
            # Add Student button
            if st.button("➕\n\nAdd Student", 
                       key="dashboard_add_student_btn",
                       use_container_width=True):
                st.session_state.current_page = "student_registration"
                st.rerun()
        
        # Add spacing
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Add some statistics below the buttons
        stats = self.manager.get_statistics()
        
        if stats:
            st.markdown("---")
            st.markdown('<div class="card-title">📊 Quick Statistics</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div style="font-size: 24px; font-weight: bold; color: white;">{stats['total_students']}</div>
                    <div>Total Students</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <div style="font-size: 24px; font-weight: bold; color: white;">{stats['average_performance']}%</div>
                    <div>Average Performance</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="card">
                    <div style="font-size: 24px; font-weight: bold; color: white;">{stats['average_attendance']}%</div>
                    <div>Average Attendance</div>
                </div>
                """, unsafe_allow_html=True)
    
    def show_student_registration(self):
        st.markdown('<div class="card-title">➕ Add New Student</div>', unsafe_allow_html=True)
        
        with st.form("student_registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *", placeholder="Enter student's full name")
                age = st.number_input("Age *", min_value=15, max_value=70, value=18)
                email = st.text_input("Email Address *", placeholder="student@institution.edu")
                phone = st.text_input("Phone Number", placeholder="+1 (555) 123-4567")
            
            with col2:
                course = st.text_input("Course/Program *", placeholder="Computer Science")
                department = st.selectbox("Department *", [
                    "Computer Science", "Engineering", "Mathematics", "Physics", 
                    "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                    "Life Sciences", "Data Science", "Artificial Intelligence"
                ])
                grade_options = [grade.value for grade in Grade]
                grade = st.selectbox("Current Grade *", grade_options)
                performance = st.slider("Academic Performance (%) *", 0, 100, 75)
                attendance = st.slider("Attendance Rate (%)", 0, 100, 95)
                enrollment_date = st.date_input("Enrollment Date", value=datetime.now())
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("🚀 Register Student", use_container_width=True)
            
            if submitted:
                student_data = {
                    'name': name,
                    'age': age,
                    'grade': grade,
                    'email': email,
                    'performance': performance,
                    'phone': phone,
                    'course': course,
                    'department': department,
                    'attendance': attendance
                }
                
                errors = StudentValidator.validate_student_data(student_data)
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    student_id = self.manager.get_next_student_id()
                    new_student = Student(
                        student_id=student_id,
                        name=name.strip(),
                        age=int(age),
                        grade=grade,
                        email=email.strip(),
                        performance=float(performance),
                        phone=phone.strip(),
                        course=course.strip(),
                        department=department,
                        enrollment_date=enrollment_date.strftime("%Y-%m-%d"),
                        attendance=float(attendance)
                    )
                    
                    success, message = self.manager.add_student(new_student)
                    if success:
                        st.success(f"Student registered successfully! Student ID: {student_id}")
                        st.balloons()
                        time.sleep(2)
                        st.session_state.current_page = "student_directory"
                        st.rerun()
                    else:
                        st.error(message)
    
    def show_student_directory(self):
        st.markdown('<div class="card-title">👥 Student Directory</div>', unsafe_allow_html=True)
        
        # Search and filters
        search_query = st.text_input("🔍 Search Students", placeholder="Search by name, email, course, department...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All"] + [status.value for status in PerformanceStatus])
        with col2:
            grade_filter = st.selectbox("Grade", ["All"] + [grade.value for grade in Grade])
        with col3:
            department_filter = st.selectbox("Department", ["All"] + sorted(list(set(s.department for s in self.manager.students))))
        
        # Get filtered students
        students = self.manager.get_all_students()
        
        if search_query:
            students = self.manager.search_students(search_query)
        
        if status_filter != "All":
            students = [s for s in students if s.calculate_status() == status_filter]
        
        if grade_filter != "All":
            students = [s for s in students if s.grade == grade_filter]
        
        if department_filter != "All":
            students = [s for s in students if s.department == department_filter]
        
        if not students:
            st.info("No student records found matching the current criteria.")
            return
        
        # Display students in a table
        data = []
        for student in students:
            status = student.calculate_status()
            attendance_status = student.calculate_attendance_status()
            
            data.append({
                'Student ID': student.student_id,
                'Name': student.name,
                'Age': student.age,
                'Grade': student.grade,
                'Email': student.email,
                'Performance': f"{student.performance}%",
                'Attendance': f"{student.attendance}%",
                'Status': status,
                'Course': student.course,
                'Department': student.department,
                'Phone': student.phone,
                'Enrollment Date': student.enrollment_date
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        # Add action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add New Student"):
                st.session_state.current_page = "student_registration"
                st.rerun()
        
        with col2:
            if st.button("📊 View Analytics"):
                st.session_state.current_page = "advanced_analytics"
                st.rerun()
    
    def show_advanced_analytics(self):
        st.markdown('<div class="card-title">📈 Advanced Analytics</div>', unsafe_allow_html=True)
        
        stats = self.manager.get_statistics()
        performance_analysis = self.manager.get_performance_analysis()
        
        if not stats:
            st.info("No student data available. Start by adding students to see analytics.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 24px; font-weight: bold; color: white;">{stats['total_students']}</div>
                <div>Total Students</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 24px; font-weight: bold; color: white;">{stats['average_performance']}%</div>
                <div>Average Performance</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 24px; font-weight: bold; color: white;">{performance_analysis.get('pass_rate', 0):.1f}%</div>
                <div>Pass Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 24px; font-weight: bold; color: white;">{stats['average_attendance']}%</div>
                <div>Average Attendance</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            if any(stats['status_distribution'].values()):
                status_data = stats['status_distribution']
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#F44336']
                
                fig_status = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    title="Student Performance Distribution",
                    color_discrete_sequence=colors
                )
                fig_status.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hoverinfo='label+percent+value'
                )
                fig_status.update_layout(
                    paper_bgcolor='#1A1A1A',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            if any(stats['grade_distribution'].values()):
                grade_data = stats['grade_distribution']
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#FF5722', '#F44336']
                
                fig_grade = px.bar(
                    x=list(grade_data.keys()),
                    y=list(grade_data.values()),
                    title="Grade Distribution",
                    color=list(grade_data.keys()),
                    color_discrete_sequence=colors
                )
                fig_grade.update_layout(
                    xaxis_title="Grade",
                    yaxis_title="Number of Students",
                    paper_bgcolor='#1A1A1A',
                    font=dict(color='white')
                )
                st.plotly_chart(fig_grade, use_container_width=True)
    
    def show_student_management(self):
        st.markdown('<div class="card-title">⚙️ Update Student</div>', unsafe_allow_html=True)
        
        # Get all students
        students = self.manager.get_all_students()
        
        if not students:
            st.info("No student records found.")
            return
        
        # Select a student to manage
        student_options = {f"{s.student_id} - {s.name}": s.student_id for s in students}
        selected_student_id = st.selectbox("Select a student to manage", list(student_options.keys()))
        student_id = student_options[selected_student_id]
        student = self.manager.get_student(student_id)
        
        if student:
            # Display student information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Student Information</div>
                    <p><strong>Student ID:</strong> {student.student_id}</p>
                    <p><strong>Name:</strong> {student.name}</p>
                    <p><strong>Age:</strong> {student.age}</p>
                    <p><strong>Email:</strong> {student.email}</p>
                    <p><strong>Phone:</strong> {student.phone}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Academic Information</div>
                    <p><strong>Course:</strong> {student.course}</p>
                    <p><strong>Department:</strong> {student.department}</p>
                    <p><strong>Grade:</strong> {student.grade}</p>
                    <p><strong>Performance:</strong> {student.performance}%</p>
                    <p><strong>Attendance:</strong> {student.attendance}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Update student form
            with st.form("update_student_form"):
                st.markdown('<div class="card-title">Update Student Information</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    update_name = st.text_input("Full Name", value=student.name)
                    update_age = st.number_input("Age", min_value=15, max_value=70, value=student.age)
                    update_email = st.text_input("Email Address", value=student.email)
                    update_phone = st.text_input("Phone Number", value=student.phone)
                
                with col2:
                    update_course = st.text_input("Course/Program", value=student.course)
                    update_department = st.selectbox("Department", [
                        "Computer Science", "Engineering", "Mathematics", "Physics", 
                        "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                        "Life Sciences", "Data Science", "Artificial Intelligence"
                    ], index=[
                        "Computer Science", "Engineering", "Mathematics", "Physics", 
                        "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                        "Life Sciences", "Data Science", "Artificial Intelligence"
                    ].index(student.department) if student.department in [
                        "Computer Science", "Engineering", "Mathematics", "Physics", 
                        "Chemistry", "Biology", "Business", "Arts", "Social Sciences",
                        "Life Sciences", "Data Science", "Artificial Intelligence"
                    ] else 0)
                    grade_options = [grade.value for grade in Grade]
                    update_grade = st.selectbox("Current Grade", grade_options, index=grade_options.index(student.grade) if student.grade in grade_options else 0)
                    update_performance = st.slider("Academic Performance (%)", 0, 100, int(student.performance))
                    update_attendance = st.slider("Attendance Rate (%)", 0, 100, int(student.attendance))
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    update_submitted = st.form_submit_button("🔄 Update Student", use_container_width=True)
                
                if update_submitted:
                    success, message = self.manager.update_student(
                        student_id,
                        name=update_name.strip(),
                        age=int(update_age),
                        grade=update_grade,
                        email=update_email.strip(),
                        performance=float(update_performance),
                        phone=update_phone.strip(),
                        course=update_course.strip(),
                        department=update_department,
                        attendance=float(update_attendance)
                    )
                    
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            # Delete student button
            if st.button("🗑️ Delete Student", type="secondary"):
                if st.session_state.get('confirm_delete', False):
                    success, message = self.manager.delete_student(student_id)
                    if success:
                        st.success(message)
                        st.session_state.current_page = "student_directory"
                        st.rerun()
                    else:
                        st.error(message)
                    st.session_state.confirm_delete = False
                else:
                    st.session_state.confirm_delete = True
                    st.warning("Are you sure you want to delete this student? Click the button again to confirm.")
    
    def show_data_operations(self):
        st.markdown('<div class="card-title">💾 Data Operations</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Export Data", "Import Data"])
        
        with tab1:
            st.markdown('<div class="card-title">📤 Export Student Data</div>', unsafe_allow_html=True)
            
            if st.button("Export to CSV"):
                success, message, csv_data = self.manager.export_to_csv()
                if success:
                    st.success(message)
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"student_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(message)
        
        with tab2:
            st.markdown('<div class="card-title">📥 Import Student Data</div>', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            
            if uploaded_file is not None:
                # To convert to a string based IO:
                stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                file_content = stringio.read()
                
                if st.button("Import Data"):
                    success, message, errors = self.manager.import_from_csv(file_content)
                    if success:
                        st.success(message)
                        if errors:
                            st.warning("Some rows had errors:")
                            for error in errors:
                                st.error(error)
                        st.rerun()
                    else:
                        st.error(message)
                        if errors:
                            for error in errors:
                                st.error(error)
    
    def run(self):
        # Show header
        self.show_header()
        
        # Show sidebar
        self.show_sidebar()
        
        # Show main content based on current page
        if st.session_state.current_page == "main_dashboard":
            self.show_main_dashboard()
        elif st.session_state.current_page == "student_registration":
            self.show_student_registration()
        elif st.session_state.current_page == "student_directory":
            self.show_student_directory()
        elif st.session_state.current_page == "advanced_analytics":
            self.show_advanced_analytics()
        elif st.session_state.current_page == "student_management":
            self.show_student_management()
        elif st.session_state.current_page == "data_operations":
            self.show_data_operations()

# Run the app
if __name__ == "__main__":
    app = ModernStudentManagementUI()
    app.run()