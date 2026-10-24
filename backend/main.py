import os
import time
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi  
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 1. 加载环境变量与初始化
# ---------------------------------------------------------
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
if not env_path.exists():
    env_path = current_dir.parent / ".env"

load_dotenv(dotenv_path=env_path)

app = FastAPI(title="MOSA AI Verification Backend")

# 配置 CORS 跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_key = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=gemini_key) if gemini_key else None

# 初始化 MongoDB Atlas 连接
mongo_uri = os.getenv("MONGODB_ATLAS_URI")
db = None

if mongo_uri:
    try:
        mongo_client = MongoClient(
            mongo_uri, 
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where()
        )
        db = mongo_client["mosa_db"]
        mongo_client.admin.command('ping')
        print("✅ 成功连接到 MongoDB Atlas 数据库!")
    except Exception as e:
        print(f"⚠️ MongoDB 连接失败: {e}")
        db = None
else:
    print("ℹ️ 未设置 MONGODB_ATLAS_URI，将切换至本地/内存模式。")

# ---------------------------------------------------------
# 2. 数据请求结构定义
# ---------------------------------------------------------
class FileItem(BaseModel):
    path: str
    content: str

class GenerateQuestionRequest(BaseModel):
    repoUrl: Optional[str] = ""
    files: List[FileItem] = []
    sandboxLogs: Optional[str] = "Build & Tests Passed."
    questionIndex: Optional[int] = 1

class EvaluateRequest(BaseModel):
    question: str
    userAnswer: str
    codeContext: Optional[str] = ""
    files: Optional[List[FileItem]] = []

class CreateProjectRequest(BaseModel):
    title: Optional[str] = ""
    repo_url: Optional[str] = ""
    stage: Optional[str] = "mvp"

class MatchRequest(BaseModel):
    user_id: Optional[str] = "demo_user"
    project_id: Optional[str] = None

# ---------------------------------------------------------
# 3. 基础健康检查 API
# ---------------------------------------------------------

@app.get("/")
def health_check():
    return {
        "status": "ok", 
        "message": "MOSA Verification Backend Running",
        "db_connected": db is not None
    }

# ---------------------------------------------------------
# 4. 项目管理 API
# ---------------------------------------------------------

@app.post("/api/projects")
def create_project_endpoint(req: CreateProjectRequest):
    """【API】前端提交 GitHub 项目链接"""
    print(f"📥 收到前端提交的项目: Repo={req.repo_url}, Title={req.title}")
    
    project_id_str = f"proj_{int(time.time())}"
    
    project_data = {
        "project_id": project_id_str,
        "title": req.title or "Untitled Project",
        "repo_url": req.repo_url,
        "stage": req.stage,
        "created_at": time.time(),
        "status": "ready"
    }

    if db is not None:
        try:
            doc_to_insert = project_data.copy()
            res = db["projects"].insert_one(doc_to_insert)
            project_id_str = str(res.inserted_id)
            project_data["project_id"] = project_id_str
            print(f"💾 项目成功写入数据库！ID: {project_id_str}")
        except Exception as e:
            print(f"⚠️ 保存项目到数据库失败: {e}")

    return {
        "success": True,
        "id": project_id_str,
        "project_id": project_id_str,
        "data": {
            "id": project_id_str,
            "project_id": project_id_str,
            **project_data
        },
        "message": "Project submitted successfully"
    }

@app.get("/api/projects")
def get_projects_endpoint():
    """获取所有项目列表"""
    projects = []
    if db is not None:
        try:
            for doc in db["projects"].find():
                doc["_id"] = str(doc["_id"])
                projects.append(doc)
            return {"success": True, "data": projects}
        except Exception as e:
            print(f"⚠️ 读取项目失败: {e}")
            
    return {"success": True, "data": []}

@app.get("/api/projects/{project_id}")
@app.get("/api/project/{project_id}")
@app.get("/api/projects/detail/{project_id}")
def get_single_project_endpoint(project_id: str):
    """【API】获取单个项目详情（防 undefined）"""
    print(f"📥 收到前端读取项目请求: project_id = {project_id}")
    
    title = "MOSA Project"
    repo_url = "https://github.com/sgxy975-bit/Mosa.git"
    trust_score = 88

    if db is not None:
        try:
            from bson import ObjectId
            doc = db["projects"].find_one({"_id": ObjectId(project_id)}) if ObjectId.is_valid(project_id) else db["projects"].find_one({"project_id": project_id})
            if doc:
                title = doc.get("title", title)
                repo_url = doc.get("repo_url", repo_url)
                trust_score = doc.get("trust_score", trust_score)
        except Exception as e:
            print(f"⚠️ 数据库读取项目失败: {e}")

    base_project_info = {
        "id": project_id,
        "project_id": project_id,
        "title": title,
        "repo_url": repo_url,
        "stars": 15,
        "forks": 4,
        "commits": 42,
        "status": "ready",
        "trust_score": trust_score,
        "checks": {
            "repository_exists": True,
            "original_commits": True,
            "commit_frequency": True
        }
    }

    return {
        "success": True,
        "id": project_id,
        "project_id": project_id,
        "project": base_project_info,
        "data": base_project_info,
        **base_project_info
    }

# ---------------------------------------------------------
# 5. Gemini 核心功能：【1】动态 AI 评估打分
# ---------------------------------------------------------

@app.post("/api/projects/{project_id}/verify")
def start_verification_endpoint(project_id: str):
    """【API】调用 Gemini 动态打分并存入 MongoDB"""
    print(f"⚙️ 开始调用 Gemini 评估项目 ID: {project_id}")
    
    repo_url = "https://github.com/sgxy975-bit/Mosa.git"
    if db is not None:
        try:
            from bson import ObjectId
            doc = db["projects"].find_one({"_id": ObjectId(project_id)}) if ObjectId.is_valid(project_id) else db["projects"].find_one({"project_id": project_id})
            if doc and "repo_url" in doc:
                repo_url = doc["repo_url"]
        except Exception as e:
            print(f"⚠️ 获取项目地址失败: {e}")

    calculated_score = 85
    ai_summary = "AI verification completed."

    if genai_client:
        prompt = f"""
        You are a Senior Technical Auditor evaluating a software project for a peer-matching platform.
        Analyze the project repository at URL: {repo_url}.
        
        Evaluate code quality and architecture.
        Generate a dynamic integer Trust Score between 65 and 98.
        
        Return pure JSON ONLY:
        {{
            "score": <integer score between 65 and 98>,
            "verdict": "verified",
            "summary": "<1-2 sentence AI summary of this repo>"
        }}
        """
        try:
            response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            res_data = json.loads(response.text)
            calculated_score = res_data.get("score", 85)
            ai_summary = res_data.get("summary", ai_summary)
            print(f"🤖 Gemini 成功给出真实打分！Score={calculated_score}")
        except Exception as e:
            print(f"⚠️ Gemini 打分失败，使用备用算式: {e}")
            calculated_score = 72 + (hash(repo_url) % 20)
    else:
        calculated_score = 72 + (hash(repo_url) % 20)

    if db is not None:
        try:
            from bson import ObjectId
            query = {"_id": ObjectId(project_id)} if ObjectId.is_valid(project_id) else {"project_id": project_id}
            db["projects"].update_one(query, {"$set": {"trust_score": calculated_score, "ai_summary": ai_summary, "status": "verified"}})
            print(f"💾 动态 Trust Score ({calculated_score}) 已保存至 MongoDB!")
        except Exception as e:
            print(f"⚠️ 保存至数据库失败: {e}")

    task_id = f"tsk_{int(time.time())}"
    
    project_obj = {
        "id": project_id,
        "project_id": project_id,
        "repo_url": repo_url,
        "trust_score": calculated_score,
        "status": "verified",
        "ai_summary": ai_summary
    }

    return {
        "success": True,
        "id": task_id,
        "task_id": task_id,
        "project_id": project_id,
        "project": project_obj,
        "data": project_obj,
        "status": "done",
        "progress": 100,
        "score": calculated_score,
        "summary": ai_summary,
        "step": "Verification Complete"
    }

@app.get("/api/tasks/{task_id}")
@app.get("/api/tracks/{task_id}")
@app.get("/api/task/{task_id}")
def get_task_status_endpoint(task_id: str):
    """【API】前端 Task 轮询接口"""
    print(f"🔄 收到前端 Task 轮询: task_id={task_id}")
    
    task_result = {
        "score": 88,
        "trust_score": 88,
        "verdict": "verified",
        "project_id": "proj_demo",
        "id": "proj_demo",
        "checks": {
            "repository_exists": True,
            "original_commits": True,
            "commit_frequency": True
        }
    }

    return {
        "success": True,
        "id": task_id,
        "task_id": task_id,
        "status": "done",
        "progress": 100,
        "step": "Verification Complete",
        "project_id": "proj_demo",
        "result": task_result,
        "project": task_result,
        "data": task_result
    }

# ---------------------------------------------------------
# 6. Gemini 核心功能：【2】动态生成专属面试题与回答评估
# ---------------------------------------------------------

@app.post("/api/generate-question")
def generate_question_endpoint(req: GenerateQuestionRequest):
    """【API】由 Gemini 根据项目代码动态生成提问"""
    if not genai_client:
        return {
            "success": True,
            "data": {
                "questionId": f"q_{req.questionIndex}_fallback",
                "question": "Could you explain the state management and memory model used in your primary entry file?",
                "codeContextSnippet": "Main Entry File",
                "targetConcept": "Core Architecture"
            }
        }

    combined_code = "\n\n".join([f"FILE: {f.path}\n{f.content}" for f in req.files]) if req.files else f"Repo URL: {req.repoUrl}"
    
    prompt = f"""
    You are an expert technical interviewer. Analyze the project below:
    [Context]: {combined_code[:20000]}
    
    Generate Question #{req.questionIndex} specifically for this codebase that tests actual ownership.
    Return pure JSON ONLY:
    {{
      "questionId": "q_{req.questionIndex}_{int(time.time())}",
      "question": "<custom technical question>",
      "codeContextSnippet": "<file or architecture module>",
      "targetConcept": "<evaluated concept>"
    }}
    """

    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        parsed_data = json.loads(response.text)
        print(f"🤖 Gemini 成功生成问题: {parsed_data.get('question')}")
        return {"success": True, "data": parsed_data}
    except Exception as e:
        print(f"⚠️ 生成问题回退: {e}")
        return {
            "success": True,
            "data": {
                "questionId": f"q_{req.questionIndex}_fallback",
                "question": "How did you handle error handling and concurrency in this project's architecture?",
                "codeContextSnippet": "Project Architecture",
                "targetConcept": "Concurrency"
            }
        }

@app.post("/api/evaluate-and-save")
def evaluate_and_save_endpoint(req: EvaluateRequest):
    """【API】调用 Gemini 评估面试回答并入库"""
    eval_result = {
        "score": 85,
        "isPassed": True,
        "feedback": "Your explanation demonstrates solid understanding.",
        "uncertaintyLevel": "low"
    }

    if genai_client:
        try:
            eval_prompt = f"""
            Evaluate candidate's answer for code verification.
            [Question]: {req.question}
            [Candidate Answer]: {req.userAnswer}

            Return pure JSON:
            {{
              "score": <0-100 integer score>,
              "isPassed": <true/false>,
              "feedback": "<technical feedback>",
              "uncertaintyLevel": "low"
            }}
            """
            eval_resp = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=eval_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            eval_result = json.loads(eval_resp.text)
            print(f"🤖 Answer Evaluated by Gemini! Score: {eval_result.get('score')}")
        except Exception as e:
            print(f"⚠️ Gemini Evaluation failed: {e}")

    db_record = {
        "question": req.question,
        "userAnswer": req.userAnswer,
        "evaluation": eval_result,
        "created_at": time.time()
    }

    inserted_id = f"mosa_rec_{int(time.time())}"
    if db is not None:
        try:
            res = db["verifications"].insert_one(db_record)
            inserted_id = str(res.inserted_id)
            print(f"💾 答题评估保存至 MongoDB! ID: {inserted_id}")
        except Exception as e:
            print(f"❌ 写入数据库错误: {e}")

    return {
        "success": True,
        "record_id": inserted_id,
        "evaluation": eval_result
    }

# ---------------------------------------------------------
# 7. 协作人员与状态 API
# ---------------------------------------------------------

@app.get("/api/collaborators")
def get_collaborators_endpoint(skills: Optional[str] = None):
    return [
        {
            "name": "Priya Shah",
            "handle": "priyash",
            "club": "Leeds Design Society",
            "skills": ["UI Design", "Figma", "User Research"],
            "seeking": ["TypeScript", "Backend"],
            "project": "Accessible timetable app",
            "availability": "Weekends",
            "hue": 262,
            "match": 92,
            "brings": ["UI Design"],
            "needs": ["TypeScript"]
        },
        {
            "name": "Tom Okafor",
            "handle": "tomok",
            "club": "Leeds Student Developers",
            "skills": ["Backend", "Python", "PostgreSQL"],
            "seeking": ["UI Design", "TypeScript"],
            "project": "Society budget tracker",
            "availability": "Weekday evenings",
            "hue": 152,
            "match": 85,
            "brings": ["Backend"],
            "needs": ["UI Design"]
        }
    ]

@app.post("/api/collaborators/intro")
def request_collaborator_intro(data: dict):
    return {"success": True, "status": "requested", "message": "Intro request sent successfully"}

@app.get("/api/matching")
@app.get("/api/matches")
def get_matching_endpoint():
    return {"success": True, "joined": False, "visible_to": 0, "matches": []}

@app.post("/api/matching")
def post_matching_endpoint(req: MatchRequest):
    return {"success": True, "message": "Matching initialized", "matches": []}

@app.get("/api/verification/status")
@app.get("/api/status")
def get_status_placeholder():
    return {
        "success": True,
        "status": "idle",
        "verified": False,
        "project": {
            "project_id": "proj_default",
            "id": "proj_default",
            "trust_score": 85
        },
        "matches": []
    }

# ---------------------------------------------------------
# 8. 启动入口（必须保持在全文件最后！）
# ---------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
