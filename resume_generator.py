"""
Resume Generator module for creating professional PDF resumes
"""
import os
import random
import io
from datetime import datetime
from typing import Dict, Any, List, Tuple
import streamlit as st
from fpdf import FPDF


# Constants for resume styling
COLORS = [
    (0, 123, 255),  # Blue
    (40, 167, 69),  # Green
    (108, 117, 125),  # Gray
    (0, 31, 63),    # Navy
    (102, 16, 242), # Purple
    (23, 162, 184), # Teal
    (220, 53, 69),  # Red
    (255, 193, 7),  # Yellow
]

FONTS = ["Helvetica", "Times", "Courier"]
LAYOUTS = ["classic", "modern", "minimal", "creative"]


def safe_text(text: str) -> str:
    """
    Ensures text is safe for FPDF by encoding to latin-1.
    
    Args:
        text (str): Text to make safe
        
    Returns:
        str: Safe text for PDF
    """
    return text.encode('latin-1', 'replace').decode('latin-1')


def generate_resume_pdf(data: Dict[str, Any]) -> bytes:
    """
    Generates a PDF resume with a randomly selected layout.
    
    Args:
        data (Dict[str, Any]): Resume data including personal info, skills, education, etc.
        
    Returns:
        bytes: PDF file as bytes
    """
    # Sanitize all text data
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = safe_text(value)
        elif isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                data[key] = [safe_text(item) for item in value]
            elif all(isinstance(item, dict) for item in value):
                for item in value:
                    for k, v in item.items():
                        if isinstance(v, str):
                            item[k] = safe_text(v)
                        elif isinstance(v, list) and all(isinstance(x, str) for x in v):
                            item[k] = [safe_text(x) for x in v]
    
    # Randomly select layout and styling
    layout = random.choice(LAYOUTS)
    accent_color = random.choice(COLORS)
    font = random.choice(FONTS)
    
    # Create PDF with selected layout
    if layout == "classic":
        pdf_bytes = create_classic_layout(data, accent_color, font)
    elif layout == "modern":
        pdf_bytes = create_modern_layout(data, accent_color, font)
    elif layout == "minimal":
        pdf_bytes = create_minimal_layout(data, accent_color, font)
    else:  # creative
        pdf_bytes = create_creative_layout(data, accent_color, font)
    
    # Ensure we return bytes, not a bytearray
    if isinstance(pdf_bytes, bytearray):
        return bytes(pdf_bytes)
    # If it's already bytes, return as is
    elif isinstance(pdf_bytes, bytes):
        return pdf_bytes
    # If it's a string (from pdf.output()), encode it
    elif isinstance(pdf_bytes, str):
        return pdf_bytes.encode('latin-1')
    # For any other type, convert to string and then to bytes
    else:
        return str(pdf_bytes).encode('latin-1')


def create_classic_layout(data: Dict[str, Any], accent_color: Tuple[int, int, int], font: str) -> bytes:
    """Creates a classic layout resume"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(left=15, top=15, right=15)
    
    # Header with name and contact info
    pdf.set_font(font, 'B', 18)
    pdf.cell(0, 10, data["name"].upper(), 0, 1, 'C')
    
    # Contact info
    pdf.set_font(font, '', 10)
    contact_info = f"{data['email']} | {data['phone']}"
    if "website" in data and data["website"]:
        contact_info += f" | {data['website']}"
    pdf.cell(0, 5, contact_info, 0, 1, 'C')
    
    if "address" in data and data["address"]:
        pdf.cell(0, 5, data["address"], 0, 1, 'C')
    
    pdf.ln(5)
    
    # Horizontal line
    pdf.set_draw_color(accent_color[0], accent_color[1], accent_color[2])
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    # Summary/Objective
    if "summary" in data and data["summary"]:
        pdf.set_font(font, 'B', 12)
        pdf.cell(0, 10, "PROFESSIONAL SUMMARY", 0, 1)
        pdf.set_font(font, '', 10)
        pdf.multi_cell(0, 5, data["summary"])
        pdf.ln(5)
    
    # Skills
    if "skills" in data and data["skills"]:
        pdf.set_font(font, 'B', 12)
        pdf.cell(0, 10, "SKILLS", 0, 1)
        pdf.set_font(font, '', 10)
        
        # Format skills as a comma-separated list
        skills_text = ", ".join(data["skills"])
        pdf.multi_cell(0, 5, skills_text)
        pdf.ln(5)
    
    # Experience
    if "experience" in data and data["experience"]:
        pdf.set_font(font, 'B', 12)
        pdf.cell(0, 10, "PROFESSIONAL EXPERIENCE", 0, 1)
        
        for job in data["experience"]:
            pdf.set_font(font, 'B', 11)
            pdf.cell(0, 6, job["title"], 0, 1)
            
            pdf.set_font(font, 'I', 10)
            company_date = f"{job['company']} | {job['start_date']} - {job['end_date']}"
            pdf.cell(0, 6, company_date, 0, 1)
            
            pdf.set_font(font, '', 10)
            for bullet in job["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(3)
    
    # Education
    if "education" in data and data["education"]:
        pdf.set_font(font, 'B', 12)
        pdf.cell(0, 10, "EDUCATION", 0, 1)
        
        for edu in data["education"]:
            pdf.set_font(font, 'B', 11)
            pdf.cell(0, 6, edu["degree"], 0, 1)
            
            pdf.set_font(font, 'I', 10)
            school_date = f"{edu['school']} | {edu['graduation_year']}"
            pdf.cell(0, 6, school_date, 0, 1)
            
            if "gpa" in edu and edu["gpa"]:
                pdf.set_font(font, '', 10)
                pdf.cell(0, 5, f"GPA: {edu['gpa']}", 0, 1)
            
            pdf.ln(3)
    
    # Projects
    if "projects" in data and data["projects"]:
        pdf.set_font(font, 'B', 12)
        pdf.cell(0, 10, "PROJECTS", 0, 1)
        
        for project in data["projects"]:
            pdf.set_font(font, 'B', 11)
            pdf.cell(0, 6, project["name"], 0, 1)
            
            pdf.set_font(font, '', 10)
            for bullet in project["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(3)
    
    # Footer with date
    pdf.set_y(-20)
    pdf.set_font(font, 'I', 8)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')}", 0, 0, 'C')
    
    # Return PDF as bytes
    try:
        output = pdf.output(dest='S')
        if isinstance(output, str):
            return output.encode('latin-1')
        return output
    except Exception as e:
        # Fallback method
        return bytes(pdf.output())


def create_modern_layout(data: Dict[str, Any], accent_color: Tuple[int, int, int], font: str) -> bytes:
    """Creates a modern layout resume with sidebar"""
    pdf = FPDF()
    pdf.add_page()
    
    # Set colors
    r, g, b = accent_color
    
    # Create sidebar
    pdf.set_fill_color(r, g, b)
    pdf.rect(0, 0, 60, 297, 'F')
    
    # Main content area
    pdf.set_margins(left=70, top=15, right=15)
    
    # Header with name
    pdf.set_font(font, 'B', 24)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 15, data["name"], 0, 1)
    
    # Professional title if available
    if "title" in data and data["title"]:
        pdf.set_font(font, 'I', 14)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 10, data["title"], 0, 1)
    
    pdf.ln(5)
    
    # Summary/Objective
    if "summary" in data and data["summary"]:
        pdf.set_font(font, '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, data["summary"])
        pdf.ln(10)
    
    # Experience
    if "experience" in data and data["experience"]:
        pdf.set_font(font, 'B', 14)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "EXPERIENCE", 0, 1)
        pdf.line(70, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(5)
        
        for job in data["experience"]:
            pdf.set_font(font, 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, job["title"], 0, 1)
            
            pdf.set_font(font, 'I', 10)
            pdf.set_text_color(80, 80, 80)
            company_date = f"{job['company']} | {job['start_date']} - {job['end_date']}"
            pdf.cell(0, 6, company_date, 0, 1)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(0, 0, 0)
            for bullet in job["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(5)
    
    # Education
    if "education" in data and data["education"]:
        pdf.set_font(font, 'B', 14)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "EDUCATION", 0, 1)
        pdf.line(70, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(5)
        
        for edu in data["education"]:
            pdf.set_font(font, 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, edu["degree"], 0, 1)
            
            pdf.set_font(font, 'I', 10)
            pdf.set_text_color(80, 80, 80)
            school_date = f"{edu['school']} | {edu['graduation_year']}"
            pdf.cell(0, 6, school_date, 0, 1)
            
            if "gpa" in edu and edu["gpa"]:
                pdf.set_font(font, '', 10)
                pdf.cell(0, 5, f"GPA: {edu['gpa']}", 0, 1)
            
            pdf.ln(3)
    
    # Projects
    if "projects" in data and data["projects"]:
        pdf.set_font(font, 'B', 14)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "PROJECTS", 0, 1)
        pdf.line(70, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(5)
        
        for project in data["projects"]:
            pdf.set_font(font, 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, project["name"], 0, 1)
            
            pdf.set_font(font, '', 10)
            for bullet in project["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(3)
    
    # Sidebar content
    pdf.set_xy(15, 20)
    pdf.set_font(font, 'B', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 10, "CONTACT", 0, 1, 'L')
    
    pdf.set_font(font, '', 8)
    pdf.set_text_color(255, 255, 255)
    
    # Email
    pdf.set_xy(15, 35)
    pdf.cell(30, 5, "Email:", 0, 1, 'L')
    pdf.set_xy(15, 40)
    pdf.cell(30, 5, data["email"], 0, 1, 'L')
    
    # Phone
    pdf.set_xy(15, 50)
    pdf.cell(30, 5, "Phone:", 0, 1, 'L')
    pdf.set_xy(15, 55)
    pdf.cell(30, 5, data["phone"], 0, 1, 'L')
    
    # Website if available
    if "website" in data and data["website"]:
        pdf.set_xy(15, 65)
        pdf.cell(30, 5, "Website:", 0, 1, 'L')
        pdf.set_xy(15, 70)
        pdf.cell(30, 5, data["website"], 0, 1, 'L')
    
    # Address if available
    if "address" in data and data["address"]:
        pdf.set_xy(15, 80)
        pdf.cell(30, 5, "Address:", 0, 1, 'L')
        pdf.set_xy(15, 85)
        pdf.multi_cell(30, 5, data["address"])
    
    # Skills
    if "skills" in data and data["skills"]:
        pdf.set_xy(15, 100)
        pdf.set_font(font, 'B', 14)
        pdf.cell(30, 10, "SKILLS", 0, 1, 'L')
        
        pdf.set_font(font, '', 8)
        y_pos = 115
        for skill in data["skills"]:
            pdf.set_xy(15, y_pos)
            pdf.cell(30, 5, skill, 0, 1, 'L')
            y_pos += 7
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def create_minimal_layout(data: Dict[str, Any], accent_color: Tuple[int, int, int], font: str) -> bytes:
    """Creates a minimal, clean layout resume"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(left=20, top=20, right=20)
    
    # Set colors
    r, g, b = accent_color
    
    # Header with name
    pdf.set_font(font, 'B', 24)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 15, data["name"], 0, 1, 'C')
    
    # Contact info in a single line
    pdf.set_font(font, '', 10)
    pdf.set_text_color(80, 80, 80)
    contact_parts = [data["email"], data["phone"]]
    if "website" in data and data["website"]:
        contact_parts.append(data["website"])
    contact_info = " | ".join(contact_parts)
    pdf.cell(0, 5, contact_info, 0, 1, 'C')
    
    if "address" in data and data["address"]:
        pdf.cell(0, 5, data["address"], 0, 1, 'C')
    
    pdf.ln(10)
    
    # Summary/Objective
    if "summary" in data and data["summary"]:
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "SUMMARY", 0, 1)
        
        pdf.set_font(font, '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, data["summary"])
        pdf.ln(5)
    
    # Experience
    if "experience" in data and data["experience"]:
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "EXPERIENCE", 0, 1)
        
        for job in data["experience"]:
            # Two-column layout for job header
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(100, 6, job["title"], 0, 0)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, f"{job['start_date']} - {job['end_date']}", 0, 1, 'R')
            
            pdf.set_font(font, 'I', 10)
            pdf.cell(0, 6, job["company"], 0, 1)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(0, 0, 0)
            for bullet in job["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(3)
    
    # Education
    if "education" in data and data["education"]:
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "EDUCATION", 0, 1)
        
        for edu in data["education"]:
            # Two-column layout for education header
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(100, 6, edu["degree"], 0, 0)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(0, 6, edu["graduation_year"], 0, 1, 'R')
            
            pdf.set_font(font, 'I', 10)
            pdf.cell(0, 6, edu["school"], 0, 1)
            
            if "gpa" in edu and edu["gpa"]:
                pdf.set_font(font, '', 10)
                pdf.cell(0, 5, f"GPA: {edu['gpa']}", 0, 1)
            
            pdf.ln(3)
    
    # Skills in a clean, minimal format
    if "skills" in data and data["skills"]:
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "SKILLS", 0, 1)
        
        pdf.set_font(font, '', 10)
        pdf.set_text_color(0, 0, 0)
        
        # Create a grid of skills
        skills = data["skills"]
        col_width = 95
        x_pos = pdf.get_x()
        y_pos = pdf.get_y()
        
        for i, skill in enumerate(skills):
            if i % 2 == 0:
                pdf.set_xy(x_pos, y_pos)
                pdf.cell(col_width, 5, f"- {skill}", 0, 0)  # Using hyphen instead of bullet point
            else:
                pdf.set_xy(x_pos + col_width, y_pos)
                pdf.cell(col_width, 5, f"- {skill}", 0, 1)  # Using hyphen instead of bullet point
                y_pos = pdf.get_y()
        
        # If odd number of skills, add a line break
        if len(skills) % 2 != 0:
            pdf.ln()
        
        pdf.ln(5)
    
    # Projects
    if "projects" in data and data["projects"]:
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(r, g, b)
        pdf.cell(0, 10, "PROJECTS", 0, 1)
        
        for project in data["projects"]:
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, project["name"], 0, 1)
            
            pdf.set_font(font, '', 10)
            for bullet in project["description"]:
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.multi_cell(0, 5, bullet)
            
            pdf.ln(3)
    
    # Footer
    pdf.set_y(-15)
    pdf.set_font(font, 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')}", 0, 0, 'C')
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def create_creative_layout(data: Dict[str, Any], accent_color: Tuple[int, int, int], font: str) -> bytes:
    """Creates a creative layout resume with unique design elements"""
    pdf = FPDF()
    pdf.add_page()
    
    # Set colors
    r, g, b = accent_color
    
    # Create header bar
    pdf.set_fill_color(r, g, b)
    pdf.rect(0, 0, 210, 40, 'F')
    
    # Name and title in header
    pdf.set_font(font, 'B', 24)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 15)
    pdf.cell(180, 10, data["name"], 0, 1, 'C')
    
    if "title" in data and data["title"]:
        pdf.set_font(font, 'I', 14)
        pdf.set_xy(15, 25)
        pdf.cell(180, 10, data["title"], 0, 1, 'C')
    
    # Contact info in a creative box
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(15, 45, 180, 20, 'F')
    
    pdf.set_font(font, '', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(20, 50)
    
    contact_parts = []
    contact_parts.append(f"Email: {data['email']}")
    contact_parts.append(f"Phone: {data['phone']}")
    if "website" in data and data["website"]:
        contact_parts.append(f"Web: {data['website']}")
    if "address" in data and data["address"]:
        contact_parts.append(f"Address: {data['address']}")
    
    contact_info = " | ".join(contact_parts)
    pdf.cell(170, 10, contact_info, 0, 1, 'C')
    
    # Main content area
    y_pos = 70
    
    # Summary/Objective with creative heading
    if "summary" in data and data["summary"]:
        # Section heading with accent color
        pdf.set_fill_color(r, g, b)
        pdf.rect(15, y_pos, 180, 8, 'F')
        
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(20, y_pos)
        pdf.cell(170, 8, "PROFESSIONAL SUMMARY", 0, 1)
        
        y_pos += 10
        
        pdf.set_font(font, '', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(15, y_pos)
        pdf.multi_cell(180, 5, data["summary"])
        
        y_pos = pdf.get_y() + 5
    
    # Skills with creative visualization
    if "skills" in data and data["skills"]:
        # Section heading with accent color
        pdf.set_fill_color(r, g, b)
        pdf.rect(15, y_pos, 180, 8, 'F')
        
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(20, y_pos)
        pdf.cell(170, 8, "SKILLS", 0, 1)
        
        y_pos += 10
        
        # Create a grid of skills with small accent boxes
        skills = data["skills"]
        col_width = 85
        x_margin = 15
        
        for i, skill in enumerate(skills):
            if i % 2 == 0:
                x_pos = x_margin
            else:
                x_pos = x_margin + col_width + 10
            
            # Small accent box
            pdf.set_fill_color(r, g, b)
            pdf.rect(x_pos, y_pos, 4, 4, 'F')
            
            # Skill text - ensure it's encoded properly
            pdf.set_font(font, '', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(x_pos + 6, y_pos - 1)
            pdf.cell(col_width, 6, skill, 0, 0)
            
            if i % 2 == 1 or i == len(skills) - 1:
                y_pos += 8
        
        y_pos += 5
    
    # Experience with creative timeline
    if "experience" in data and data["experience"]:
        # Section heading with accent color
        pdf.set_fill_color(r, g, b)
        pdf.rect(15, y_pos, 180, 8, 'F')
        
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(20, y_pos)
        pdf.cell(170, 8, "PROFESSIONAL EXPERIENCE", 0, 1)
        
        y_pos += 10
        
        for job in data["experience"]:
            # Timeline dot
            pdf.set_fill_color(r, g, b)
            pdf.circle(20, y_pos + 3, 3, 'F')
            
            # Job title and date
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(r, g, b)
            pdf.set_xy(30, y_pos)
            pdf.cell(100, 6, job["title"], 0, 0)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_xy(130, y_pos)
            pdf.cell(65, 6, f"{job['start_date']} - {job['end_date']}", 0, 1, 'R')
            
            y_pos += 6
            
            # Company
            pdf.set_font(font, 'I', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(30, y_pos)
            pdf.cell(170, 6, job["company"], 0, 1)
            
            y_pos += 8
            
            # Description bullets
            pdf.set_font(font, '', 10)
            for bullet in job["description"]:
                pdf.set_xy(30, y_pos)
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.set_xy(35, y_pos)
                pdf.multi_cell(160, 5, bullet)
                y_pos = pdf.get_y() + 2
            
            y_pos += 3
            
            # Timeline vertical line
            if job != data["experience"][-1]:  # Not the last job
                pdf.set_draw_color(r, g, b)
                pdf.set_line_width(0.5)
                pdf.line(20, y_pos - 15, 20, y_pos + 5)
    
    # Check if we need a new page for education and projects
    if y_pos > 240:
        pdf.add_page()
        y_pos = 15
    
    # Education with creative elements
    if "education" in data and data["education"]:
        # Section heading with accent color
        pdf.set_fill_color(r, g, b)
        pdf.rect(15, y_pos, 180, 8, 'F')
        
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(20, y_pos)
        pdf.cell(170, 8, "EDUCATION", 0, 1)
        
        y_pos += 10
        
        for edu in data["education"]:
            # School icon
            pdf.set_fill_color(r, g, b)
            pdf.circle(20, y_pos + 3, 3, 'F')
            
            # Degree and year
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(r, g, b)
            pdf.set_xy(30, y_pos)
            pdf.cell(100, 6, edu["degree"], 0, 0)
            
            pdf.set_font(font, '', 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_xy(130, y_pos)
            pdf.cell(65, 6, edu["graduation_year"], 0, 1, 'R')
            
            y_pos += 6
            
            # School name
            pdf.set_font(font, 'I', 10)
            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(30, y_pos)
            pdf.cell(170, 6, edu["school"], 0, 1)
            
            y_pos += 6
            
            # GPA if available
            if "gpa" in edu and edu["gpa"]:
                pdf.set_font(font, '', 10)
                pdf.set_xy(30, y_pos)
                pdf.cell(170, 5, f"GPA: {edu['gpa']}", 0, 1)
                y_pos += 5
            
            y_pos += 5
    
    # Projects with creative elements
    if "projects" in data and data["projects"]:
        # Check if we need a new page
        if y_pos > 240:
            pdf.add_page()
            y_pos = 15
        
        # Section heading with accent color
        pdf.set_fill_color(r, g, b)
        pdf.rect(15, y_pos, 180, 8, 'F')
        
        pdf.set_font(font, 'B', 12)
        pdf.set_text_color(255, 255, 255)
        pdf.set_xy(20, y_pos)
        pdf.cell(170, 8, "PROJECTS", 0, 1)
        
        y_pos += 10
        
        for project in data["projects"]:
            # Project icon
            pdf.set_fill_color(r, g, b)
            pdf.rect(17, y_pos, 6, 6, 'F')
            
            # Project name
            pdf.set_font(font, 'B', 11)
            pdf.set_text_color(r, g, b)
            pdf.set_xy(30, y_pos)
            pdf.cell(170, 6, project["name"], 0, 1)
            
            y_pos += 8
            
            # Description bullets
            pdf.set_font(font, '', 10)
            pdf.set_text_color(0, 0, 0)
            for bullet in project["description"]:
                pdf.set_xy(30, y_pos)
                pdf.cell(5, 5, "-", 0, 0)  # Using hyphen instead of bullet point
                pdf.set_xy(35, y_pos)
                pdf.multi_cell(160, 5, bullet)
                y_pos = pdf.get_y() + 2
            
            y_pos += 3
    
    # Footer with date and page number
    pdf.set_y(-15)
    pdf.set_font(font, 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')} | Page {pdf.page_no()}", 0, 0, 'C')
    
    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin-1')


def show_resume_generator():
    """
    Displays the resume generator interface.
    """
    st.markdown("## 📄 Resume Generator")
    st.markdown("Create a professional resume with a clean layout.")
    
    # Create tabs for input and preview
    input_tab, preview_tab = st.tabs(["📝 Resume Information", "👁️ Preview & Download"])
    
    with input_tab:
        # Personal Information
        st.markdown("### 👤 Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", placeholder="John Doe", key="name")
            email = st.text_input("Email*", placeholder="john.doe@example.com", key="email")
        
        with col2:
            phone = st.text_input("Phone*", placeholder="(123) 456-7890", key="phone")
            website = st.text_input("Website", placeholder="www.johndoe.com", key="website")
        
        address = st.text_input("Address", placeholder="City, State, Country", key="address")
        title = st.text_input("Professional Title", placeholder="Software Engineer", key="title")
        
        # Summary
        st.markdown("### 📝 Professional Summary")
        summary = st.text_area(
            "Summary", 
            placeholder="Experienced software engineer with 5+ years of experience in web development...",
            height=100,
            key="summary"
        )
        
        # Skills
        st.markdown("### 🛠️ Skills")
        skills_input = st.text_area(
            "Skills (one per line)",
            placeholder="Python\nJavaScript\nReact\nSQL\nDocker",
            height=100,
            key="skills"
        )
        
        # Experience
        st.markdown("### 💼 Professional Experience")
        
        experience_count = st.number_input("Number of experiences", min_value=0, max_value=10, value=1, key="exp_count")
        experiences = []
        
        for i in range(experience_count):
            st.markdown(f"#### Experience {i+1}")
            exp_col1, exp_col2 = st.columns(2)
            
            with exp_col1:
                job_title = st.text_input(f"Job Title {i+1}*", placeholder="Software Engineer", key=f"job_title_{i}")
                company = st.text_input(f"Company {i+1}*", placeholder="ABC Tech Inc.", key=f"company_{i}")
            
            with exp_col2:
                start_date = st.text_input(f"Start Date {i+1}*", placeholder="Jan 2020", key=f"start_date_{i}")
                end_date = st.text_input(f"End Date {i+1}*", placeholder="Present", key=f"end_date_{i}")
            
            job_description = st.text_area(
                f"Description {i+1}* (one bullet point per line)",
                placeholder="Developed and maintained web applications using React\nImplemented RESTful APIs using Node.js\nImproved application performance by 30%",
                height=100,
                key=f"job_desc_{i}"
            )
            
            if job_title and company and start_date and end_date and job_description:
                experiences.append({
                    "title": job_title,
                    "company": company,
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": [line.strip() for line in job_description.split('\n') if line.strip()]
                })
        
        # Education
        st.markdown("### 🎓 Education")
        
        education_count = st.number_input("Number of education entries", min_value=0, max_value=5, value=1, key="edu_count")
        education = []
        
        for i in range(education_count):
            st.markdown(f"#### Education {i+1}")
            edu_col1, edu_col2 = st.columns(2)
            
            with edu_col1:
                degree = st.text_input(f"Degree {i+1}*", placeholder="Bachelor of Science in Computer Science", key=f"degree_{i}")
                school = st.text_input(f"School {i+1}*", placeholder="University of Technology", key=f"school_{i}")
            
            with edu_col2:
                graduation_year = st.text_input(f"Graduation Year {i+1}*", placeholder="2019", key=f"grad_year_{i}")
                gpa = st.text_input(f"GPA {i+1}", placeholder="3.8/4.0", key=f"gpa_{i}")
            
            if degree and school and graduation_year:
                education.append({
                    "degree": degree,
                    "school": school,
                    "graduation_year": graduation_year,
                    "gpa": gpa
                })
        
        # Projects
        st.markdown("### 🚀 Projects")
        
        project_count = st.number_input("Number of projects", min_value=0, max_value=5, value=1, key="proj_count")
        projects = []
        
        for i in range(project_count):
            st.markdown(f"#### Project {i+1}")
            
            project_name = st.text_input(f"Project Name {i+1}*", placeholder="E-commerce Website", key=f"project_name_{i}")
            
            project_description = st.text_area(
                f"Description {i+1}* (one bullet point per line)",
                placeholder="Developed a full-stack e-commerce website using MERN stack\nImplemented secure payment processing with Stripe\nDeployed on AWS with CI/CD pipeline",
                height=100,
                key=f"project_desc_{i}"
            )
            
            if project_name and project_description:
                projects.append({
                    "name": project_name,
                    "description": [line.strip() for line in project_description.split('\n') if line.strip()]
                })
        
        # Generate button
        if st.button("Generate Resume Preview", use_container_width=True, type="primary"):
            # Validate required fields
            if not name or not email or not phone:
                st.error("Please fill in all required fields (marked with *).")
            else:
                # Store data in session state for the preview tab
                st.session_state.resume_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "website": website,
                    "address": address,
                    "title": title,
                    "summary": summary,
                    "skills": [skill.strip() for skill in skills_input.split('\n') if skill.strip()],
                    "experience": experiences,
                    "education": education,
                    "projects": projects,
                    "generated": True
                }
                # Switch to preview tab
                st.info("Resume preview generated! Click on the 'Preview & Download' tab to view and download.")
    
    # Preview tab
    with preview_tab:
        if "resume_data" in st.session_state and st.session_state.resume_data.get("generated", False):
            data = st.session_state.resume_data
            
            # Display preview
            st.markdown("### 📋 Resume Preview")
            
            # Name and title
            st.markdown(f"<h1 style='text-align: center; margin-bottom: 0;'>{data['name']}</h1>", unsafe_allow_html=True)
            if data["title"]:
                st.markdown(f"<h3 style='text-align: center; color: #666; margin-top: 0;'>{data['title']}</h3>", unsafe_allow_html=True)
            
            # Contact info
            contact_parts = []
            contact_parts.append(f"📧 {data['email']}")
            contact_parts.append(f"📱 {data['phone']}")
            if data["website"]:
                contact_parts.append(f"🌐 {data['website']}")
            if data["address"]:
                contact_parts.append(f"📍 {data['address']}")
            
            st.markdown(f"<p style='text-align: center;'>{' | '.join(contact_parts)}</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Summary
            if data["summary"]:
                st.markdown("### 📝 Professional Summary")
                st.markdown(data["summary"])
                st.markdown("---")
            
            # Skills
            if data["skills"]:
                st.markdown("### 🛠️ Skills")
                skills_html = ""
                for skill in data["skills"]:
                    skills_html += f"<span style='background-color: #f0f0f0; padding: 3px 8px; margin: 2px; border-radius: 10px; display: inline-block;'>{skill}</span> "
                st.markdown(f"<p>{skills_html}</p>", unsafe_allow_html=True)
                st.markdown("---")
            
            # Experience
            if data["experience"]:
                st.markdown("### 💼 Professional Experience")
                for job in data["experience"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{job['title']} at {job['company']}**")
                    with col2:
                        st.markdown(f"*{job['start_date']} - {job['end_date']}*")
                    
                    for bullet in job["description"]:
                        st.markdown(f"- {bullet}")
                    st.markdown("")
                st.markdown("---")
            
            # Education
            if data["education"]:
                st.markdown("### 🎓 Education")
                for edu in data["education"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{edu['degree']}**")
                        st.markdown(f"*{edu['school']}*")
                    with col2:
                        st.markdown(f"*{edu['graduation_year']}*")
                    
                    if edu["gpa"]:
                        st.markdown(f"GPA: {edu['gpa']}")
                    st.markdown("")
                st.markdown("---")
            
            # Projects
            if data["projects"]:
                st.markdown("### 🚀 Projects")
                for project in data["projects"]:
                    st.markdown(f"**{project['name']}**")
                    for bullet in project["description"]:
                        st.markdown(f"- {bullet}")
                    st.markdown("")
            
            # Generate PDF for download
            try:
                # Import io module for BytesIO
                import io
                
                # Create a BytesIO buffer to receive PDF data
                buffer = io.BytesIO()
                
                # Create a simple PDF directly
                pdf = FPDF()
                pdf.add_page()
                
                # Header with name
                pdf.set_font("Helvetica", 'B', 18)
                pdf.cell(0, 10, data["name"].upper(), 0, 1, 'C')
                
                # Title if available
                if data["title"]:
                    pdf.set_font("Helvetica", 'I', 12)
                    pdf.cell(0, 6, data["title"], 0, 1, 'C')
                
                # Contact info
                pdf.set_font("Helvetica", '', 10)
                contact_info = f"{data['email']} | {data['phone']}"
                if data["website"]:
                    contact_info += f" | {data['website']}"
                pdf.cell(0, 5, contact_info, 0, 1, 'C')
                
                if data["address"]:
                    pdf.cell(0, 5, data["address"], 0, 1, 'C')
                
                pdf.ln(5)
                
                # Summary
                if data["summary"]:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(0, 10, "PROFESSIONAL SUMMARY", 0, 1)
                    pdf.set_font("Helvetica", '', 10)
                    pdf.multi_cell(0, 5, data["summary"])
                    pdf.ln(5)
                
                # Skills
                if data["skills"]:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(0, 10, "SKILLS", 0, 1)
                    pdf.set_font("Helvetica", '', 10)
                    skills_text = ", ".join(data["skills"])
                    pdf.multi_cell(0, 5, skills_text)
                    pdf.ln(5)
                
                # Experience
                if data["experience"]:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(0, 10, "PROFESSIONAL EXPERIENCE", 0, 1)
                    
                    for job in data["experience"]:
                        pdf.set_font("Helvetica", 'B', 11)
                        pdf.cell(0, 6, job["title"], 0, 1)
                        
                        pdf.set_font("Helvetica", 'I', 10)
                        company_date = f"{job['company']} | {job['start_date']} - {job['end_date']}"
                        pdf.cell(0, 6, company_date, 0, 1)
                        
                        pdf.set_font("Helvetica", '', 10)
                        for bullet in job["description"]:
                            pdf.cell(5, 5, "-", 0, 0)
                            pdf.multi_cell(0, 5, bullet)
                        
                        pdf.ln(3)
                
                # Education
                if data["education"]:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(0, 10, "EDUCATION", 0, 1)
                    
                    for edu in data["education"]:
                        pdf.set_font("Helvetica", 'B', 11)
                        pdf.cell(0, 6, edu["degree"], 0, 1)
                        
                        pdf.set_font("Helvetica", 'I', 10)
                        school_date = f"{edu['school']} | {edu['graduation_year']}"
                        pdf.cell(0, 6, school_date, 0, 1)
                        
                        if edu["gpa"]:
                            pdf.set_font("Helvetica", '', 10)
                            pdf.cell(0, 5, f"GPA: {edu['gpa']}", 0, 1)
                        
                        pdf.ln(3)
                
                # Projects
                if data["projects"]:
                    pdf.set_font("Helvetica", 'B', 12)
                    pdf.cell(0, 10, "PROJECTS", 0, 1)
                    
                    for project in data["projects"]:
                        pdf.set_font("Helvetica", 'B', 11)
                        pdf.cell(0, 6, project["name"], 0, 1)
                        
                        pdf.set_font("Helvetica", '', 10)
                        for bullet in project["description"]:
                            pdf.cell(5, 5, "-", 0, 0)
                            pdf.multi_cell(0, 5, bullet)
                        
                        pdf.ln(3)
                
                # Footer
                pdf.set_y(-15)
                pdf.set_font("Helvetica", 'I', 8)
                pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d')}", 0, 0, 'C')
                
                # Write PDF to buffer
                pdf_string = pdf.output(dest='S')
                if isinstance(pdf_string, str):
                    buffer.write(pdf_string.encode('latin-1'))
                else:
                    buffer.write(pdf_string)
                
                # Get PDF bytes from buffer
                buffer.seek(0)
                pdf_bytes = buffer.getvalue()
                
                # Provide download button
                st.download_button(
                    label="📥 Download Resume PDF",
                    data=pdf_bytes,
                    file_name=f"{data['name'].replace(' ', '_')}_Resume_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        else:
            st.info("Fill out the resume information in the 'Resume Information' tab and click 'Generate Resume Preview' to see your resume here.")