# Uploaded file path
UPLOAD_FILE_PATH = "./uploaded_files/"
MAX_SQL_LENGTH = 200

DEFAULT_COLLECTION = "default_collection"
DEFAULT_DIM = 384
CHAT_COMTEXT = "Melbourne is the capital city of the Australian state of Victoria.It is known for its diverse and vibrant cultural scene.The city is famous for its coffee culture, with numerous cafes scattered throughout.Melbourne is home to iconic landmarks like the Royal Exhibition Building and Flinders Street Station.The Yarra River runs through the heart of the city, providing a picturesque setting.The Melbourne Cricket Ground (MCG) is a historic sports venue and a key part of the city's identity.The city hosts various events, including the Australian Open, Melbourne Fashion Week, and the Melbourne International Comedy Festival.Melbourne's street art scene is renowned, with vibrant murals adorning many laneways.The Queen Victoria Market is a popular spot for fresh produce, local crafts, and diverse international cuisines.Melbourne is often considered one of the most livable cities globally, offering a high quality of life."
# DEFAULT MODELS
DEFAULT_ENCODER = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENDOCDER = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
DEFAULT_MODEL = "microsoft/GODEL-v1_1-base-seq2seq"
DEFAULT_TEXT_MODEL = "openai-community/gpt2"
DEFAUTL_SUMMERIZE_MODEL="Falconsai/text_summarization"
DEFAULT_MODEL_PATH = "/models/"
# CONVERSATION
CONVERSATION_INACTIVE_SEC= 300
RAG_NUM = 5

#DATASET LOADBATCH
LOAD_BATCH_SIZE = 100

# SAMPLE_CONTEXT
SAMPLE_CONTEXT = [
    "Melbourne is the capital city of the Australian state of Victoria.",
    "It is known for its diverse and vibrant cultural scene.",
    "The city is famous for its coffee culture, with numerous cafes scattered throughout.",
    "Melbourne is home to iconic landmarks like the Royal Exhibition Building and Flinders Street Station.",
    "The Yarra River runs through the heart of the city, providing a picturesque setting.",
    "The Melbourne Cricket Ground (MCG) is a historic sports venue and a key part of the city's identity.",
    "The city hosts various events, including the Australian Open, Melbourne Fashion Week, and the Melbourne International Comedy Festival.",
    "Melbourne's street art scene is renowned, with vibrant murals adorning many laneways.",
    "The Queen Victoria Market is a popular spot for fresh produce, local crafts, and diverse international cuisines.",
    "Melbourne is often considered one of the most livable cities globally, offering a high quality of life."
]
