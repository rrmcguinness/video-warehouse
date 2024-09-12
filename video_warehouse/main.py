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

from functools import partial
from multiprocessing import Pool
import traceback

import vertexai
from vertexai.generative_models import GenerativeModel, Image, Content, Part, Tool, FunctionDeclaration, GenerationConfig, ChatSession
from video_warehouse.agents import VisionModel, getEmbeddings,video_text_config
from video_warehouse.domain import Config

def answer_question(question, config, vision_model, video_part) -> None:
    ans = vision_model.generate_content(contents=[question, video_part])
    print("#"*80)
    print(f"Question: {question}")
    print(f"Answer:\n{ans.text}")
    print(f"\nEmbeddings:\n{getEmbeddings(config=config, text=ans.text)}")


def main():
    config = Config(file_name="env.toml")
    
    vertexai.init(project=config.application.project_id, location=config.application.location)
    
    try:
        
        # Set the video URL
        video_file = "gs://cloud-samples-data/video/chicago.mp4"
        
        # Load the vision model
        vision = VisionModel(video_text_config, "You're a professional critic capable of answering questions about movies")
        
        # Create a Part (used for Gemini multi modal arguments) to hold the video
        video_part = Part.from_uri(video_file, mime_type="video/mp4")
        
        # Create a partial, this is a fancy way to create to create a method point for the Pool object
        handler = partial(answer_question, config=config, vision_model=vision, video_part=video_part)
        
        # List all of the questions
        questions = ["Write a creative summary the video that captures the storyline",
                     "List the characters in the movie",
                     'Transcribe the content in this movie and in a separate section and text displayed']
        
        # Execute them in parallel to get a faster response time per video, just note this is the devisor for quota / time
        pool = Pool(config.processor.thread_pool_size)
        pool.map(handler, questions)
        
    except Exception as e:
        print(traceback.format_exc())
    
    