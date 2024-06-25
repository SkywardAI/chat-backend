# coding=utf-8
# Copyright [2024] [SkywardAI]
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from kimchima.pkg import (
    ModelFactory,
    TokenizerFactory,
    EmbeddingsFactory,
    PipelinesFactory,
    CrossEncoderFactory,
    Devices
)
from kimchima.utils import (
    Downloader
)

from src.config.settings.const import DEFAULT_ENCODER, DEFAULT_MODEL,DEFAULT_TEXT_MODEL, DEFAUTL_SUMMERIZE_MODEL,CROSS_ENDOCDER,DEFAULT_MODEL_PATH

class ModelPipeline:
    r"""
    ModelPipeline class:
    - to compute embeddings by using the encoder model
    - to generate an answer by using the transformers pipeline.
    """

    async def init(self, model_name=DEFAULT_MODEL,model_text=DEFAULT_TEXT_MODEL,model_sum=DEFAUTL_SUMMERIZE_MODEL, encoder_name=DEFAULT_ENCODER) -> None:
        #TODO Logger system
        self.pipe_con = self.initialize_pip_con(model_name)
        self.pipe_sum = self.initialize_pip_sum(model_sum)
        self.pipe_text = self.initialize_pip_text(model_text)
        self.encoder_model, self.encoder_tokenizer = self.initialize_encoder(encoder_name)
        self.model_name = model_name
        self.cross_encoder= CrossEncoderFactory(CROSS_ENDOCDER)
        # self.initialize_encoder(DEFAULT_ENCODER)

    def encode_string(self, data):
        embeddings=EmbeddingsFactory.get_text_embeddings(
            model=self.encoder_model,
            tokenizer=self.encoder_tokenizer,
            prompt=data,
            device=Devices.get_device().value,
            max_length=512,
        )

        return embeddings
    

    def initialize_encoder(self, encoder_name):
        model_path = self._check_and_download_model(encoder_name)
        encoder_model=ModelFactory.auto_model(pretrained_model_name_or_path=model_path)
        tokenizer=TokenizerFactory.auto_tokenizer(pretrained_model_name_or_path=model_path)
        return encoder_model, tokenizer

    def initialize_pip_text(self, model_name):
        model_path = self._check_and_download_model(model_name)
        tokenizer=TokenizerFactory.auto_tokenizer(pretrained_model_name_or_path=model_path)
        pip = PipelinesFactory.text_generation(model=model_path,
                                               tokenizer=tokenizer,
                                               device_map='auto')
        return pip

    def initialize_pip_con(self, model_name):
        model_path = self._check_and_download_model(model_name)
        tokenizer=TokenizerFactory.auto_tokenizer(pretrained_model_name_or_path=model_path)
        pip = PipelinesFactory.customized_pipe(model=model_path,
                                               tokenizer=tokenizer,
                                               device_map='auto',
                                               task="conversational")
        return pip

    def initialize_pip_sum(self, model_name):
        model_path = self._check_and_download_model(model_name)
        tokenizer=TokenizerFactory.auto_tokenizer(pretrained_model_name_or_path=model_path)
        pip = PipelinesFactory.customized_pipe(model=model_path,
                                               tokenizer=tokenizer,
                                               device_map='auto',
                                               task="summarization")
        return pip

    def generate_answer(self, con, prompt=None):
        r"""
        Generate answer by generate message from converations and vector result
        then summerize the response
        """
        response = self.pipe_con(con.conversation, max_length=128, min_length=8, top_p=0.9, do_sample=True)
        response.messages[-1]["content"] = prompt + response.messages[-1]["content"]
        max_length = len(response.messages[-1]["content"])
        input = response.messages[-1]["content"]
        response = self.pipe_text(input, max_length=max_length, num_return_sequences=1)
        answer = self._remove_special_chars(response[0].get('generated_text'))
        # response = self.pipe_sum(response.messages[-1]["content"], min_length=5, max_length=max_length)
        # answer = response[0].get('summary_text')
        con.set_last_answer(answer)
        # TODO logger
        return answer
    def _check_and_download_model(self, model_name):
        r"""
        Check the model exists or not, if not download the model
        """
        model_path = DEFAULT_MODEL_PATH + model_name
        if os.path.exists(model_path):
            return model_path
        else:
            Downloader.auto_downloader(model_name=model_name, folder_name=model_path)
            return model_path

    def _remove_special_chars(self, text):
        return text.replace("|im_end|", "").replace("|im_start|", "").replace("|im_start|", "")


ai_model: ModelPipeline = ModelPipeline()
