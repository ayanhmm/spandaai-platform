from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
import random
import os
from typing import List

from spanda_domains.services.EdTech.microservices.qa_generation.spanda_types import QueryRequest, QuestionRequest
from spanda_domains.services.EdTech.microservices.qa_generation.rag_configs import RagConfigForGeneration, RagConfigForIngestion, credentials_default, credentials_ingest
from spanda_domains.services.EdTech.microservices.qa_generation.utils import process_context, generate_essay_questions, generate_fill_blank_questions, generate_multiple_choice_questions, generate_short_answer_questions, generate_true_false_questions, distractor_generation_agent, correct_statement_agent, tag_spanda_question
from spanda_domains.services.EdTech.shared.platform_client.rag_client import send_file_to_verba
from spanda_domains.services.EdTech.shared.config.rag_types import QueryPayload

app = FastAPI()
MAX_FILE_SIZE = 10000 * 1024 * 1024

VERBA_URL = os.getenv("VERBA_URL", "http://localhost:8000")  # Default if not set
VERBA_API_ENDPOINT = f"{VERBA_URL}/api/import_file"



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("Content-Length")
    if content_length and int(content_length) > MAX_FILE_SIZE:
        return JSONResponse(
            content={"error": "File size exceeds the allowed limit (100 MB)."},
            status_code=413,
        )

    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    return {"message": "Hello! This is the advanced question/answer generation microservice! Running successfully!"}


@app.post("/api/questions_generation")
async def spanda_questions_generation(query_request: QueryRequest):

    try:
        context_payload = QueryPayload(
            query=query_request.topic,
            RAG=RagConfigForGeneration["rag_config"],
            labels=[],
            documentFilter=[],
            credentials=credentials_default["credentials"]
        )
        context_result = await process_context(jsonable_encoder(context_payload), query_request.context)
        if query_request.type_of_question.lower() == "multiple choice questions":
            generated_questions = await generate_multiple_choice_questions(
                query_request,
                context_result["filtered_context"]
            )
        elif query_request.type_of_question.lower() == "true/false":
            generated_questions = await generate_true_false_questions(
                query_request,
                context_result["filtered_context"]
            )
        elif query_request.type_of_question.lower() == "fill in the blanks":
            generated_questions = await generate_fill_blank_questions(
                query_request,
                context_result["filtered_context"]
            )
        elif query_request.type_of_question.lower() == "short answer":
            generated_questions = await generate_short_answer_questions(
                query_request,
                context_result["filtered_context"]
            )
        elif query_request.type_of_question.lower() == "essay":
            generated_questions = await generate_essay_questions(
                query_request,
                context_result["filtered_context"]
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported question type: {query_request.type_of_question}")

        response_preamble = "There is no specific information provided about this topic, but I can answer with my intrinsic knowledge as follows: " \
            if not context_result["filtered_context"].strip() else ""

        return {
            "preamble": response_preamble,
            "questions": generated_questions["questions"],
            "metadata": generated_questions["metadata"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/answers_generation")
async def spanda_answers_generation(question_request: QuestionRequest):
    final_questions = []
    try:
        context_payload = QueryPayload(
            query=question_request.question,
            RAG=RagConfigForGeneration["rag_config"],
            labels=[],
            documentFilter=[],
            credentials=credentials_default["credentials"]
        )

        context_result = await process_context(jsonable_encoder(context_payload), question_request.context)
        if question_request.type_of_question.lower() == "multiple choice questions":
            correct_answer_result = await correct_statement_agent(
                question_request.type_of_question, question_request.question, question_request.context
            )
            correct_answer = correct_answer_result.get('answer', '').strip()
            if not correct_answer:
                raise ValueError(f"Invalid correct answer: {correct_answer_result}")

            distractors = []
            current_context = context_result or ""
            for _ in range(question_request.no_of_options - 1):
                distractor_result = await distractor_generation_agent(
                    question_request.question,
                    correct_answer,
                    current_context,
                    existing_distractors=distractors
                )
                new_distractor = distractor_result.get('answer', '').strip()
                if not new_distractor:
                    raise ValueError(f"Invalid distractor: {distractor_result}")
                distractors.append(new_distractor)
            all_options = [correct_answer] + distractors
            random.shuffle(all_options)

            tagged_question = tag_spanda_question(
                question_request.question, correct_answer, "multiple choice questions", all_options
            )
            final_questions.append(tagged_question)

        else:
            key_points_result = await correct_statement_agent(
                question_request.type_of_question, question_request.question, context_result["filtered_context"]
            )
            key_points = key_points_result.get('answer', '').strip()
            if not key_points:
                raise ValueError(f"Invalid key points: {key_points_result}")

            tagged_question = tag_spanda_question(
                question_request.question,
                key_points,
                question_request.type_of_question
            )

            final_questions.append(tagged_question)

        return {
            "questions": final_questions,
            "metadata": {
                "total_questions": len(final_questions)
            }
        }

    except Exception as e:
        return {
            "error": str(e)
        }

@app.post("/api/ingest_files/")
async def ingest_files(
    courseid: str = Form(...),
    files: List[UploadFile] = File(...),
):
    """
    Endpoint to ingest multiple files and send them to Verba API.
    """
    credentials = credentials_ingest["credentials"]

    rag_config = RagConfigForIngestion["rag_config"]

    results = []
    for file in files:
        try:
            file_bytes = await file.read()

            if len(file_bytes) > MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": "File size exceeds the allowed limit (100 MB).",
                })
                continue

            # Send file to Verba API
            result = await send_file_to_verba(
                file_bytes, file.filename, credentials, rag_config, labels=[courseid]
            )
            results.append(result)
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "error": str(e)})

    return {"results": results}

# Main function to start the FastAPI server
def main():
    uvicorn.run(app, host="0.0.0.0", port=9004)


if __name__ == "__main__":
    main()
