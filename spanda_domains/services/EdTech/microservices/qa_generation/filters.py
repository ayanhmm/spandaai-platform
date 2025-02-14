import os
from dotenv import load_dotenv

from spanda_domains.services.EdTech.shared.config.model_configs import ModelType
from spanda_domains.services.EdTech.shared.platform_client.service_client import invoke_llm

# Load environment variables from .env file
load_dotenv()

verba_url = os.getenv("VERBA_URL")

async def response_relevance_filter(query: str, response: str) -> str:
    evaluate_system_prompt = """You are given a query and a response. Determine if the response is relevant, irrelevant, or highly irrelevant to the query. Only respond with "Relevant", "Irrelevant", or "Highly Irrelevant"."""

    evaluate_user_prompt = f"""
        Query: {query}

        Content: {response}
    """
    
    is_response_relevant_dict = await invoke_llm(
        system_prompt=evaluate_system_prompt,
        user_prompt=evaluate_user_prompt,
        model_type= ModelType.ANALYSIS
    )
    is_response_relevant = is_response_relevant_dict["answer"]
    if is_response_relevant.lower() == 'highly irrelevant':
        return "Given that the answer that I am able to retrieve with the information I have seems to be highly irrelevant to the query, I abstain from providing a response. I am sorry for not being helpful." # Returns an empty coroutine
    elif is_response_relevant.lower() == 'irrelevant':
        return "The answer I am able to retrieve with the information I have seems to be irrelevant to the query. Nevertheless, I will provide you with the response in the hope that it will be valuable. Apologies in advance if it turns out to be of no value: " + response
    return response


async def context_relevance_filter(query: str, context: str) -> str:
    evaluate_system_prompt = (
        """You are an AI responsible for assessing whether the provided content is relevant to a specific query. Carefully analyze the content and determine if it directly addresses or provides pertinent information related to the query. Only respond with "YES" if the content is relevant, or "NO" if it is not. Do not provide any explanations, scores, or additional text—just a single word: "YES" or "NO"."""
    )
    evaluate_user_prompt = (
        f"""
        Content: {context}

        Query: {query}

        You are an AI responsible for assessing whether the provided content is able to answer the query. Carefully analyze the content and determine if it directly addresses or provides pertinent information related to the query. Only respond with "YES" if the content is relevant, or "NO" if it is not. Do not provide any explanations, scores, or additional text—just a single word: "YES" or "NO".
        """
    )

    is_context_relevant_dict = await invoke_llm(
        system_prompt=evaluate_system_prompt,
        user_prompt=evaluate_user_prompt,
        model_type= ModelType.ANALYSIS
    )
    is_context_relevant = is_context_relevant_dict["answer"]
    if is_context_relevant.lower() == 'no':
        return " "  # Returns an empty coroutine
    return context