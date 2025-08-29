from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yaml
import random
from typing import Dict, Any, List
from datetime import datetime
import os

app = FastAPI(
    title="EchoRAG Capsule Judgment API",
    description="REST API for capsule judgment processing and feedback generation",
    version="1.0.0",
)

FEEDBACK_DIR = "./feedback"
CAPSULE_DIR = "./capsules"
os.makedirs(FEEDBACK_DIR, exist_ok=True)


class CapsuleRequest(BaseModel):
    capsule: Dict[str, Any]
    flow: Dict[str, Any]


class CapsuleSubmission(BaseModel):
    id: str
    topic: str
    content: str
    tags: List[str] = []


class JudgmentFeedback(BaseModel):
    capsule_id: str
    judgment: str
    reason: str
    confidence: float = 0.8


@app.get("/")
async def root():
    return {"message": "🧠 EchoRAG Judgment API - Ready for capsule processing"}


@app.post("/run_capsule_flow")
async def run_capsule_flow(data: CapsuleRequest):
    """Run capsule through judgment flow"""
    capsule = data.capsule
    flow = data.flow

    if not capsule or not flow:
        raise HTTPException(status_code=400, detail="Capsule or flow missing.")

    # Simulate judgment process
    result = []
    judgment_stages = flow.get(
        "judgment_loop",
        [
            {"stage": "initial_analysis", "description": "Primary ethical assessment"},
            {"stage": "signature_matching", "description": "Echo signature alignment"},
            {
                "stage": "quantum_collapse",
                "description": "Final judgment determination",
            },
        ],
    )

    for step in judgment_stages:
        # Simulate EchoJudgmentSystem quantum collapse
        decision = random.choice(
            [
                "✅ accept - resonance achieved",
                "⚠️ defer - requires further analysis",
                "❌ reject - ethical constraints violated",
            ]
        )

        result.append(
            {
                "stage": step.get("stage", "unknown"),
                "description": step.get("description", "Processing step"),
                "decision": decision,
                "timestamp": datetime.now().isoformat(),
            }
        )

    return {
        "capsule_topic": capsule.get("topic", "N/A"),
        "capsule_id": capsule.get("id", "unknown"),
        "result": result,
        "meta": {
            "processed_at": datetime.now().isoformat(),
            "api_version": "1.0.0",
            "echo_system": "EchoJudgmentSystem_v10",
        },
    }


@app.post("/get_feedback")
async def get_feedback(results: List[Dict[str, Any]]):
    """Generate feedback from judgment results"""
    feedback = []

    for r in results:
        decision = r.get("decision", "unknown")
        stage = r.get("stage", "unknown")

        # Generate contextual feedback
        if "defer" in decision:
            note = f"{stage} requires meta-cognitive reflection and additional signature input"
        elif "reject" in decision:
            note = f"{stage} identified ethical boundary violations - requires doctrine review"
        elif "accept" in decision:
            note = f"{stage} achieved successful resonance - quantum collapse completed"
        else:
            note = f"{stage} processed with standard EchoRAG protocol"

        feedback.append(
            {
                "stage": stage,
                "decision": decision,
                "note": note,
                "learning_weight": random.uniform(0.1, 1.0),
            }
        )

    return {
        "feedback": feedback,
        "meta": {
            "feedback_generated_at": datetime.now().isoformat(),
            "total_stages": len(feedback),
        },
    }


@app.post("/submit_capsule")
async def submit_capsule(capsule: CapsuleSubmission):
    """Submit new capsule to the system"""
    capsule_data = {
        "id": capsule.id,
        "topic": capsule.topic,
        "content": capsule.content,
        "tags": capsule.tags,
        "submitted_at": datetime.now().isoformat(),
        "source": "external_api",
        "status": "pending_judgment",
    }

    filename = os.path.join(CAPSULE_DIR, f"{capsule.id}.yaml")
    os.makedirs(CAPSULE_DIR, exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(capsule_data, f, allow_unicode=True)

    return {"message": f"✅ Capsule received: {capsule.id}", "file": filename}


@app.post("/record_judgment")
async def record_judgment(feedback: JudgmentFeedback):
    """Record judgment feedback in the system"""
    feedback_data = {
        "capsule_id": feedback.capsule_id,
        "judgment": feedback.judgment,
        "reason": feedback.reason,
        "confidence": feedback.confidence,
        "timestamp": datetime.now().isoformat(),
        "source": "api_submission",
    }

    filename = os.path.join(
        FEEDBACK_DIR,
        f"{feedback.capsule_id}_api_feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml",
    )

    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(feedback_data, f, allow_unicode=True)

    return {"message": "✅ Judgment recorded", "file": filename}


@app.get("/capsule_stats")
async def get_capsule_stats():
    """Get statistics about processed capsules"""

    # Count feedback files
    feedback_count = 0
    if os.path.exists(FEEDBACK_DIR):
        feedback_count = len(
            [f for f in os.listdir(FEEDBACK_DIR) if f.endswith(".yaml")]
        )

    # Count capsule files
    capsule_count = 0
    if os.path.exists(CAPSULE_DIR):
        capsule_count = len([f for f in os.listdir(CAPSULE_DIR) if f.endswith(".yaml")])

    return {
        "total_capsules": capsule_count,
        "total_judgments": feedback_count,
        "system_status": "operational",
        "api_version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting EchoRAG API Server...")
    uvicorn.run(app, host="0.0.0.0", port=7860)
