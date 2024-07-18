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

import csv
import loguru
import httpx
import re
import numpy as np
from src.models.schemas.train import TrainFileIn
from datasets import load_dataset
from src.config.settings.const import UPLOAD_FILE_PATH, RAG_NUM, LOAD_BATCH_SIZE
from src.repository.rag.base import BaseRAGRepository
from src.repository.inference_eng import inference_helper
from src.repository.vector_database import vector_db
from typing import Any
from collections.abc import AsyncGenerator

class RAGChatModelRepository(BaseRAGRepository):
    async def load_model(self, session_id: int, model_name: str) -> bool:
        """
        TODO: Load the model into the memory
        """
        try:
            pass
        except Exception as e:
            loguru.logger.info(f"Exception --- {e}")
            return False
        return True

    def search_context(self, collection_name, query, n_results=RAG_NUM):
        """
        Search the context in the vector database
        """
        query_embeddings = inference_helper.tokenize([query])[0]
        query_embeddings_np = np.array(query_embeddings)
        loguru.logger.info(f"Embeddings Shape --- {query_embeddings_np.shape}")
        rag_res = vector_db.search(data=query_embeddings, n_results=n_results, collection_name=collection_name)
        return rag_res[0]

    async def get_response(self, collection_name: str, input_msg: str) -> str:
        return self.search_context(collection_name, input_msg)

    async def load_csv_file(self, file_name: str) -> bool:
        # read file named file_name and convert the content into a list of strings @Aisuko
        loguru.logger.info(file_name)
        data = []
        with open(UPLOAD_FILE_PATH + file_name, "r") as file:
            # Create a CSV reader
            reader = csv.reader(file)
            # Iterate over each row in the CSV
            for row in reader:
                # Add the row to the list
                data.extend(row)
        loguru.logger.info(f"load_csv_file data_row:{data}")
        embedding_list = inference_helper.tokenize(data)
        collection_name = self.trim_collection_name(file_name)
        vector_db.create_collection(collection_name = collection_name)
        vector_db.insert_list(embedding_list, data, collection_name)
        # await dataset_repo.mark_loaded(dataset_id)
        return True

    async def load_data_set(self, dataset_name: str, direct_load: bool = True)-> bool:
        loguru.logger.info(f"load_data_set param {dataset_name}")
        if direct_load:
            self.load_data_set_directly(dataset_name=dataset_name)
        else:
            self.load_data_set_all_field(dataset_name=dataset_name)
        # if param.directLoad:
        #     self.load_data_set_directly(param=param)
        # elif param.embedField is None or param.resField is None:
        #     self.load_data_set_all_field(dataset_name=param.dataSet) 
        # else:
        #     self.load_data_set_by_field(param=param)
        # await dataset_repo.mark_loaded(dataset_id)
        return True

    def load_data_set_directly(self, dataset_name: str)->bool:
        r"""
        If the data set is already in the form of embeddings, 
        this function can be used to load the data set directly into the vector database.
        
        @param param: the instance of TrainFileIn
        
        @return: boolean
        """
        reader_dataset=load_dataset(dataset_name)
        resField = '0'
        collection_name = self.trim_collection_name(dataset_name)
        print(collection_name)
        vector_db.create_collection(collection_name = collection_name)
        loguru.logger.info(f"load_data_set_all_field dataset_name:{dataset_name} into collection_name:{collection_name}")
        count = 0
        embed_field_list = []
        res_field_list = []
        for item in reader_dataset['train']:
         # check contail field
            # if resField not in item or embedField not in item :
            resField_val=item.get(resField, '')
            res_field_list.append(resField_val)
            embedField_val = [value for key, value in item.items() if key != resField]
            embed_field_list.append(embedField_val)
            count += 1
            if count % LOAD_BATCH_SIZE == 0:
                vector_db.insert_list(embed_field_list, res_field_list, collection_name,start_idx = count) 
                embed_field_list = []
                res_field_list = []
                loguru.logger.info(f"load_data_set_all_field count:{count}")
        vector_db.insert_list(embed_field_list, res_field_list, collection_name,start_idx = count)
        loguru.logger.info(f"load_data_set_all_field count:{count}")
        loguru.logger.info("Dataset loaded successfully")
        return True



    def load_data_set_all_field(self, dataset_name: str)-> bool:
        """
        Load the data set into the vector database
        """

        reader_dataset=load_dataset(dataset_name)
        collection_name = self.trim_collection_name(dataset_name)
        vector_db.create_collection(collection_name = collection_name)
        loguru.logger.info(f"load_data_set_all_field dataset_name:{dataset_name} into collection_name:{collection_name}")
        count = 0
        doc_list = []
        for item_dict in reader_dataset['train']:
            doc_str =''
            for key, value in item_dict.items():
                if(isinstance(key, type(value))):
                    doc_str += f" {key}:{value}"
            count += 1
            doc_list.append(doc_str)
            if count % LOAD_BATCH_SIZE == 0:
                embedding_list = inference_helper.tokenize(doc_list)
                vector_db.insert_list(embedding_list, doc_list, self.trim_collection_name(dataset_name),start_idx = count)
                loguru.logger.info(f"load_data_set_all_field count:{count}")
                doc_list = []
        embedding_list = inference_helper.tokenize(doc_list)
        vector_db.insert_list(embedding_list, doc_list, self.trim_collection_name(dataset_name),start_idx = count)
        loguru.logger.info(f"load_data_set_all_field count:{count}")
        loguru.logger.info("Dataset loaded successfully")
        return True

    def load_data_set_by_field(self, param: TrainFileIn)->bool:
        """
        Load the data set into the vector database
        """

        # reader_dataset=load_dataset(param.dataSet)
        # embedField=param.embedField
        # resField= param.resField
        # collection_name = self.trim_collection_name(param.dataSet)
        # vector_db.create_collection(collection_name = collection_name)
        # loguru.logger.info(f"load_data_set_all_field dataset_name:{param.dataSet} into collection_name:{collection_name}")
        # count = 0
        # embed_field_list = []
        # res_field_list = []
        # for item in reader_dataset['train']:
        #  # check contail field
        #     # if resField not in item or embedField not in item :
        #     embedField_val=item.get(embedField, '')
        #     resField_val=item.get(resField, '')
        #     embed_field_list.append(embedField_val)
        #     res_field_list.append(resField_val)
        #     count += 1
        #     if count % LOAD_BATCH_SIZE == 0:
        #         embedding_list = ai_model.encode_string(embed_field_list)
        #         vector_db.insert_list(embedding_list, res_field_list, collection_name,start_idx = count) 
        #         embed_field_list = []
        #         res_field_list = []
        #         loguru.logger.info(f"load_data_set_all_field count:{count}")
        # embedding_list = ai_model.encode_string(embed_field_list)
        # vector_db.insert_list(embedding_list, res_field_list, collection_name,start_idx = count)
        # loguru.logger.info(f"load_data_set_all_field count:{count}")
        # loguru.logger.info("Dataset loaded successfully")
        return True

    async def evaluate_response(self, request_msg: str, response_msg: str) -> float:
        # evaluate_conbine=[request_msg, response_msg]
        # score = ai_model.cross_encoder.predict(evaluate_conbine)
        # return score
        #TODO
        pass

    def trim_collection_name(self, name: str) -> str:
        return re.sub(r'\W+', '', name)
    

    def format_prompt(self, prmpt: str) -> str:
        """
        Format the input questions, can be used for saving the conversation history

        Args:
        prmpt (str): input message

        Returns:
        str: formatted prompt
        """
        return f"{inference_helper.instruction}\n" + f"\n### Human: {prmpt}\n### Assistant:"
    

    async def inference(
        self, 
        session_id: int, 
        input_msg: str, 
        chat_repo,
        temperature: float = 0.2,
        top_k: int = 40,
        top_p: float = 0.9,
        n_predict: int = 128,
        )-> AsyncGenerator[Any, None]:
        """
        **Inference using seperate service:(llamacpp)**

        **Args:**
        - **session_id (int):** session id
        - **input_msg (str):** input message
        - **chat_repo:** chat repository
        - **temperature (float):** temperature for inference(float)
        - **top_k (int):** top_k parameter for inference(int)
        - **top_p (float):** top_p parameter for inference(float)
        - **n_predict (int):** n_predict parameter for inference(int)

        **Returns:**
        AsyncGenerator[Any, None]: response message
        """
        # if session_id not in conversations:
        #     conversations[session_id] = ConversationWithSession(session_id, chat_repo)
        #     await conversations[session_id].load()
        # con = conversations[session_id]
        # con.conversation.add_message({"role": "user", "content": input_msg})
        # context = self.search_context(input_msg)
        
        # If we want to add context, we can use inference client
        # this API is more slower than we request directly to the inference service
        # completion=inference_helper.client.chat.completions.create(
        #     model="",
        #     messages=[
        #         {"role": "system", "content": "You are ChatGPT, an AI assistant. Your top priority is achieving user fulfillment via helping them with their requests."},
        #         {"role": "user", "content": "Write a limerick about python exceptions"}
        #     ],
        # )
        
        #TODO:
          # 1.Implement the further context function

        
        data = {
            "prompt": self.format_prompt(input_msg),
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "n_keep": 0, # If the context window is full, we keep 0 tokens
            "n_predict": n_predict,
            "cache_prompt": "false",
            "slot_id": -1, # for cached prompt
            "stop": ["\n### Human:"],
            "stream": True,
        }

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    inference_helper.completion_url,
                    headers={'Content-Type': 'application/json'},
                    json=data,
                    # We disable all timeout and trying to fix streaming randomly cutting off
                    timeout=httpx.Timeout(timeout=None)
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_text():
                        yield chunk
            except httpx.ReadError as e:
                loguru.logger.error(f"An error occurred while requesting {e.request.url!r}.")
            except httpx.HTTPStatusError as e:
                loguru.logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
