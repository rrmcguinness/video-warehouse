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

import logging
from pathlib import Path
import tomllib
from typing import Dict
from video_warehouse.utils import get_env_file_name

logger = logging.getLogger(__name__)

class TomlClass:
    def __init__(self, d: Dict[str, any] = None):
        if d is not None:
            for k, v in d.items():
                logger.debug("creating value for property: %s", k)
                setattr(self, k, v)
                
    def updateValues(self, d: Dict[str, any] = None):
        if d is not None:
            for k, v in d.items():
                logger.debug("overriding value for property: %s", k)
                setattr(self, k, v)
 
 
class ApplicationConfig(TomlClass):
    project_id: str
    location: str     
    
    
class VertexConfig(TomlClass):
    max_token_output: int
    text_embedding_length: int
    text_embedding_model: str
    
    
class ProcessorConfig(TomlClass):
    thread_pool_size: int
    file_name: str             
               
                
class Config:
    application: ApplicationConfig
    vertex: VertexConfig
    processor: ProcessorConfig

    def __init__(self, file_name: str):
        env_fil_name = get_env_file_name(file_name)
        files = [file_name, env_fil_name]
        for file in files:
            if file is not None and (Path(file)).is_file():
                with open(file, "rb") as f:
                    print("Loading configuration from file: ", file_name)
                    data = tomllib.load(f)
                    if file == file_name:
                        setattr(self, "application", ApplicationConfig(data.get("application")))
                        setattr(self, "vertex", VertexConfig(data.get("vertex")))
                        setattr(self, "processor", ProcessorConfig(data.get("processor")))

                    elif file == env_fil_name:
                        self.application.updateValues(data.get("application"))
                        self.vertex.updateValues(data.get("vertex"))
                        self.vertex.updateValues(data.get("processor"))