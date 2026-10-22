from pathlib import Path
import time
from dataclasses import dataclass, field
from flask import current_app
import pandas as pd

from src.app.services.retriever import Retriever

@dataclass
class PipelineResult:
    report: str
    retrieved_cases: list[dict] = field(default_factory=list)
    inference_time_ms: int = 0
    confidence_score: float | None = None

def analyze_image(image_path: Path, question: str, top_k: int, strategy: str = "image_only") -> PipelineResult:
    start = time.perf_counter()
    
    registry = current_app.extensions["model_registry"]

    image_embedding = registry.encoder.encode_image(image_path)
    images_index_path = current_app.config.get("IMAGES_INDEX_PATH")
    dicom_ids_path = current_app.config.get("DICOM_IDS_PATH")

    retriever = Retriever(index_path=images_index_path, k=top_k, ids_path=dicom_ids_path)

    results = retriever.retrieve(embedding=image_embedding)

    context = None #todo

    report = registry.generator.generate(
        image_path,
        retrieved_context=context,
    )

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return PipelineResult(
        report=report,
        retrieved_cases=results,
        inference_time_ms=elapsed_ms,
        confidence_score=0.5
    )