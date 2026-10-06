from pathlib import Path
import time
from dataclasses import dataclass, field

@dataclass
class PipelineResult:
    report: str
    retrieved_cases: list[dict] = field(default_factory=list)
    inference_time_ms: int = 0
    confidence_score: float | None = None

def analyze_image(image_path: Path, question: str, top_k: int, strategy: str = "image_only") -> PipelineResult:
    #todo - now sample output
    start = time.perf_counter()
    report = (
        "Findings: "
        "\n\n"
        "Impression: "
    )

    retrieved = [
        {"case_id": "1", "score": 0.5, "path": "data/1.jpg"},
        {"case_id": "2", "score": 0.5, "path": "data/2.jpg"},
        {"case_id": "3", "score": 0.5, "path": "data/3.jpg"},
    ]

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return PipelineResult(
        report=report,
        retrieved_cases=retrieved[:top_k],
        inference_time_ms=elapsed_ms,
        confidence_score=0.5,
    )