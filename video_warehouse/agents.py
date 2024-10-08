# Copyright 2024 Google, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Copyright 2024 Google, LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, List, Optional
import vertexai
from vertexai.generative_models import HarmCategory, HarmBlockThreshold, GenerativeModel, GenerationConfig, Tool, grounding
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
import vertexai.generative_models

from video_warehouse.domain import Config
from video_warehouse.utils import fix_output

default_instructions = 'Answer all questions as an expert retailer and merchandiser.'

fact_json_config = GenerationConfig(temperature=0.2, candidate_count=1, top_k=40, top_p=0.6, max_output_tokens=8192, response_mime_type="application/json")
creative_json_config = GenerationConfig(temperature=0.9, candidate_count=1, top_k=40, top_p=0.92, max_output_tokens=8192, response_mime_type="application/json")
critic_json_config = GenerationConfig(temperature=0.0, candidate_count=1, top_k=30, top_p=0.6, max_output_tokens=8192, response_mime_type="application/json")

fact_text_config = GenerationConfig(temperature=0.2, candidate_count=1, top_k=40, top_p=0.6, max_output_tokens=8192, response_mime_type="text/plain")
creative_text_config = GenerationConfig(temperature=0.9, candidate_count=1, top_k=40, top_p=0.92, max_output_tokens=8192, response_mime_type="text/plain")
critic_text_config = GenerationConfig(temperature=0.0, candidate_count=1, top_k=30, top_p=0.6, max_output_tokens=8192, response_mime_type="text/plain")

video_text_config = GenerationConfig(temperature=0.8, candidate_count=1, top_k=40, top_p=0.6, max_output_tokens=2048, response_mime_type="text/plain")

google_grounding = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

def InitializeVertex(config: Config) -> None:
    vertexai.init(project=config.application.project_id, location=config.application.location)
    

def SafetySettings() -> Dict[HarmCategory, HarmBlockThreshold]:
    return {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
    }


def VisionModel(generation_config: GenerationConfig, instruction: str = default_instructions, enable_grounding: bool = False) -> GenerativeModel:
    return vertexai.generative_models.GenerativeModel(
               
                model_name="gemini-pro-vision",
                generation_config=generation_config if generation_config else fact_text_config,
                tools=[google_grounding] if (enable_grounding) else [],
                safety_settings=SafetySettings())


def ProModel(generation_config: GenerationConfig, instruction: str = default_instructions, enable_grounding: bool = False) -> GenerativeModel:
    return  vertexai.generative_models.GenerativeModel(
                model_name="gemini-1.5-pro",
                system_instruction=instruction,
                generation_config=generation_config if generation_config else fact_json_config,
                tools=[google_grounding] if (enable_grounding) else [],
                safety_settings=SafetySettings())



def FlashModel(generation_config: GenerationConfig, instruction: str = default_instructions) -> GenerativeModel:
    return vertexai.generative_models.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=instruction,
            generation_config=generation_config if generation_config else fact_json_config,
            safety_settings=SafetySettings())

def getProJSON(prompt: str, instruction: str = default_instructions, enable_grounding: bool = False) -> str:
    agent = ProModel(instruction=instruction, enable_grounding=enable_grounding, generation_config=fact_json_config)
    resp = agent.generate_content(prompt)
    return fix_output(resp.text)


def getProText(prompt: str, instruction: str = default_instructions, enable_grounding: bool = False) -> str:
    agent = ProModel(instruction=instruction, enable_grounding=enable_grounding, generation_config=fact_text_config)
    resp = agent.generate_content(prompt)
    return fix_output(resp.text)


def getFlashJSON(prompt: str, instruction: str = default_instructions) -> str:
    agent = FlashModel(instruction=instruction, generation_config=fact_json_config)
    resp = agent.generate_content(prompt)
    return fix_output(resp.text)


def EmbeddingModel(config: Config):
    return TextEmbeddingModel.from_pretrained(config.vertex.text_embedding_model)


def getEmbeddings(config: Config, text: List[str]) -> List[float]:
    model = EmbeddingModel(config)
    kwargs = dict(output_dimensionality=config.vertex.text_embedding_length)
    results = model.get_embeddings([TextEmbeddingInput(" ".join(text), "RETRIEVAL_DOCUMENT")], **kwargs)
    return results[0].values