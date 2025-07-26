import sys
import traceback
from logger.custom_logger import CustomLogger

log = CustomLogger().get_logger(__file__)
class CustomDocumentException(Exception):
    """Custom Exception for Document Portal"""
    def __init__(self, error_message: str, error_details: sys):
        _,_,exe_tb = error_details.exc_info() 
        
        self.file_name = exe_tb.tb_frame.f_code.co_filename
        self.lineno = exe_tb.tb_lineno
        self.error_message = str(error_message)
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
        
    def __str__(self):
        return f"""Error occured in [{self.file_name}] at line [{self.lineno}]
            Message: {self.error_message}
            Traceback: {self.traceback_str}"""
    
if __name__ == "__main__":
    try:
        # simulating an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exec = CustomDocumentException(e, sys)
        log.error(app_exec)
        raise app_exec