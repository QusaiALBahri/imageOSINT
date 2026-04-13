"""Gradio frontend application that uses FastAPI backend"""

import gradio as gr
import requests
import logging
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Global state
class AppState:
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None


def login_user(email: str, password: str) -> tuple:
    """Login user and get access token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            AppState.access_token = data["access_token"]
            AppState.user_id = data["user_id"]
            return "✓ Login successful", email
        else:
            return "✗ Login failed", ""
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return f"✗ Error: {str(e)}", ""


def register_user(email: str, username: str, password: str) -> str:
    """Register new user account"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"email": email, "username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            AppState.access_token = data["access_token"]
            AppState.user_id = data["user_id"]
            return "✓ Registration successful"
        else:
            error = response.json().get("detail", "Registration failed")
            return f"✗ {error}"
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return f"✗ Error: {str(e)}"


def submit_analysis(image_file, analysis_types: str) -> str:
    """Submit image for analysis"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    if not image_file:
        return "✗ Please upload an image"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        with open(image_file.name, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BACKEND_URL}/api/analyze",
                files=files,
                params={"analysis_types": analysis_types},
                headers=headers,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            AppState.job_id = data["job_id"]
            return f"✓ Analysis submitted\nJob ID: {data['job_id']}"
        else:
            return f"✗ Failed to submit analysis: {response.json()}"
    
    except Exception as e:
        logger.error(f"Analysis submission error: {str(e)}")
        return f"✗ Error: {str(e)}"


def get_analysis_status(job_id: str) -> str:
    """Get analysis job status"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        response = requests.get(
            f"{BACKEND_URL}/api/analyze/{job_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            status_text = f"""
Job ID: {data['job_id']}
Status: {data['status']}
Progress: {data['progress']}%
Filename: {data['filename']}

            """
            
            if data["status"] == "completed":
                status_text += "✓ Completed!"
            elif data["status"] == "failed":
                status_text += f"✗ Error: {data.get('error', 'Unknown error')}"
            else:
                status_text += f"⏳ Processing... {data['progress']}%"
            
            return status_text
        else:
            return f"✗ Job not found"
    
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return f"✗ Error: {str(e)}"


def get_analysis_results(job_id: str) -> str:
    """Get full analysis results"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        response = requests.get(
            f"{BACKEND_URL}/api/analyze/{job_id}/results",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        else:
            return f"✗ Could not retrieve results"
    
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return f"✗ Error: {str(e)}"


def reverse_search(image_file, engines: str) -> str:
    """Perform reverse image search"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    if not image_file:
        return "✗ Please upload an image"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        with open(image_file.name, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BACKEND_URL}/api/search/reverse",
                files=files,
                params={"engines": engines},
                headers=headers,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        else:
            return f"✗ Search failed"
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"✗ Error: {str(e)}"


def analyze_location(latitude: float, longitude: float) -> str:
    """Analyze location"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        response = requests.post(
            f"{BACKEND_URL}/api/location/analyze",
            params={"latitude": latitude, "longitude": longitude},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        else:
            return f"✗ Analysis failed"
    
    except Exception as e:
        logger.error(f"Location analysis error: {str(e)}")
        return f"✗ Error: {str(e)}"


def get_user_stats() -> str:
    """Get user statistics"""
    if not AppState.access_token:
        return "✗ Please login first"
    
    try:
        headers = {"Authorization": f"Bearer {AppState.access_token}"}
        
        response = requests.get(
            f"{BACKEND_URL}/api/stats",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2)
        else:
            return f"✗ Could not retrieve stats"
    
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return f"✗ Error: {str(e)}"


def create_interface() -> gr.Blocks:
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="OSINT Image Tool - Backend Edition",
        theme=gr.themes.Soft()
    ) as demo:
        
        # Header
        with gr.Row():
            gr.HTML("""
                <div style="text-align: center; padding: 20px;">
                    <h1>🔍 OSINT Image Search & Maps Scraper</h1>
                    <p>Powered by FastAPI Backend + Celery Workers + PostgreSQL</p>
                </div>
            """)
        
        # Authentication Tab
        with gr.Tabs():
            with gr.TabItem("🔐 Authentication"):
                gr.Markdown("### Login or Register")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**Login**")
                        email = gr.Textbox(label="Email")
                        password = gr.Textbox(label="Password", type="password")
                        login_btn = gr.Button("Login", variant="primary")
                        login_output = gr.Textbox(label="Status")
                        
                        login_btn.click(
                            fn=login_user,
                            inputs=[email, password],
                            outputs=[login_output, email]
                        )
                    
                    with gr.Column():
                        gr.Markdown("**Register**")
                        reg_email = gr.Textbox(label="Email")
                        reg_username = gr.Textbox(label="Username")
                        reg_password = gr.Textbox(label="Password", type="password")
                        register_btn = gr.Button("Register", variant="primary")
                        reg_output = gr.Textbox(label="Status")
                        
                        register_btn.click(
                            fn=register_user,
                            inputs=[reg_email, reg_username, reg_password],
                            outputs=reg_output
                        )
            
            # Analysis Tab
            with gr.TabItem("📊 Submit Analysis"):
                gr.Markdown("### Submit Image for Analysis")
                
                image_file = gr.File(label="Upload Image", file_count="single")
                analysis_types = gr.Checkboxgroup(
                    choices=["metadata", "search", "location", "maps"],
                    value=["metadata"],
                    label="Analysis Types"
                )
                submit_btn = gr.Button("Submit Analysis", variant="primary")
                submit_output = gr.Textbox(label="Result")
                
                submit_btn.click(
                    fn=submit_analysis,
                    inputs=[image_file, analysis_types],
                    outputs=submit_output
                )
            
            # Job Status Tab
            with gr.TabItem("💼 Job Status"):
                job_id_input = gr.Textbox(label="Job ID")
                status_btn = gr.Button("Check Status")
                status_output = gr.Textbox(label="Status (Auto-refresh every 5s)")
                
                status_btn.click(
                    fn=get_analysis_status,
                    inputs=job_id_input,
                    outputs=status_output
                )
            
            # Results Tab
            with gr.TabItem("📈 Get Results"):
                results_job_id = gr.Textbox(label="Job ID")
                results_btn = gr.Button("Get Results")
                results_output = gr.JSON(label="Results")
                
                results_btn.click(
                    fn=get_analysis_results,
                    inputs=results_job_id,
                    outputs=results_output
                )
            
            # Reverse Search Tab
            with gr.TabItem("🔎 Reverse Image Search"):
                search_image = gr.File(label="Upload Image", file_count="single")
                search_engines = gr.Checkboxgroup(
                    choices=["google", "bing", "yandex"],
                    value=["google"],
                    label="Search Engines"
                )
                search_btn = gr.Button("Search")
                search_output = gr.JSON(label="Results")
                
                search_btn.click(
                    fn=reverse_search,
                    inputs=[search_image, search_engines],
                    outputs=search_output
                )
            
            # Location Tab
            with gr.TabItem("📍 Location Analysis"):
                latitude = gr.Number(label="Latitude")
                longitude = gr.Number(label="Longitude")
                location_btn = gr.Button("Analyze Location")
                location_output = gr.JSON(label="Location Data")
                
                location_btn.click(
                    fn=analyze_location,
                    inputs=[latitude, longitude],
                    outputs=location_output
                )
            
            # Stats Tab
            with gr.TabItem("📊 User Statistics"):
                stats_btn = gr.Button("Get Statistics")
                stats_output = gr.JSON(label="Statistics")
                
                stats_btn.click(
                    fn=get_user_stats,
                    inputs=[],
                    outputs=stats_output
                )
            
            # Documentation
            with gr.TabItem("📚 Documentation"):
                gr.Markdown("""
                ## Backend Architecture
                
                This version uses:
                - **FastAPI** backend at `http://localhost:8000`
                - **PostgreSQL** or **SQLite** database
                - **Redis** caching layer
                - **Celery** worker pool for async tasks
                
                ### Workflow
                
                1. **Register/Login** - Create account and get JWT token
                2. **Submit Analysis** - Upload image for processing
                3. **Check Status** - Monitor job progress in real-time
                4. **Retrieve Results** - Get comprehensive analysis results
                
                ### Features
                
                ✓ User authentication with JWT tokens
                ✓ Async job processing with Celery
                ✓ Result caching with Redis
                ✓ Database persistence
                ✓ Multi-engine reverse image search
                ✓ Location analysis and Maps scraping
                ✓ User statistics and history
                
                ### API Endpoints
                
                - `POST /api/auth/register` - Register
                - `POST /api/auth/login` - Login
                - `POST /api/analyze` - Submit analysis
                - `GET /api/analyze/{job_id}` - Check status
                - `GET /api/analyze/{job_id}/results` - Get results
                - `POST /api/search/reverse` - Reverse search
                - `POST /api/location/analyze` - Location analysis
                - `GET /api/stats` - User statistics
                """)
    
    return demo


if __name__ == "__main__":
    logger.info("Starting OSINT Tool with Backend")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )
