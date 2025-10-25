# TODO Synthetic data generator using OSS or Frontier models
# TODO Build synthetic data layout
# TODO Create data generator prompt
# TODO Create UI for output display

# Generate random data given a particular specification and output it to csv, json, or a sqlite db file.

import atexit
import csv
import logging
import logging.handlers
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.conversations import Conversation
from openai.types.responses import Response, ResponseInputParam


def setup_logging() -> logging.Logger:
    """ Initalize logger in the console and .log file. """
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    _log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if not logger.handlers:
        _log_file_handler = logging.handlers.TimedRotatingFileHandler(
        '.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
        )
        _log_file_handler.setLevel(logging.DEBUG)
        _log_file_handler.setFormatter(_log_formatter)
        logger.addHandler(_log_file_handler)

        _log_console_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        _log_console_handler.setLevel(logging.INFO)
        _log_console_handler.setFormatter(_log_formatter)
        logger.addHandler(_log_console_handler)

        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.INFO)
    return logger

logger: logging.Logger = setup_logging()

SERVER_STARTTIME: datetime = datetime.now(datetime.utc)
load_dotenv()
client= OpenAI()

MODEL: str = "gpt-4.1-nano"
SYSTEMPROMPT: str = "Generate a random set of data based on the user-defined specifications. Provide 20-40 individual datapoints in a csv format (do not include the header)"

def write_output(filename: str, headers: list, data: dict) -> int:
    with open(f'${filename}.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    return len(data)

# Build prompts# Build prompts
def new_chat() -> str:
    """ Create a new conversation to keep track of inputs & responses.

    Returns:
        The unique ID for this session.
    """
    _conversation: Conversation = client.conversations.create(
        items=[{'type': 'message', 'role': 'system', 'content': SYSTEMPROMPT}]
    )
    logger.info(f'Conversation created successfully. {_conversation}')
    return _conversation.id

# TODO Ensure end_chat is called to close the 
def end_chat(conversation: str) -> None:
    """ Deletes the current conversation by ID number.

    Args:
        conversation: The unique ID for the conversation session.
    """
    client.conversations.delete(conversation)
    logger.debug(f'Conversation {conversation} deleted successfully.')

def chat (message: str, conv_id: str) -> str:
    _input: ResponseInputParam = [{'role': 'system', 'content': SYSTEMPROMPT}, {'role': 'user', 'content': message}]
    _response: Response = client.responses.create(
        conversation = conv_id,
        model = MODEL,
        input = _input
    )

    if _response.output_text:
        return _response.output_text

# def cleanup() -> None:
#     """
#     Helper function to end the conversation session and ensure everything is properly closed out.
#     """
#     if 'conversation_id' in st.session_state and st.session_state.conversation_id:
#         try:
#             end_chat(st.session_state.conversation_id)
#             logger.info(f'Cleaned up conversation: {st.session_state.conversation_id}')
#         except Exception as e:
#             logger.error(f'Error during cleanup: {e}')

# atexit.register(cleanup)