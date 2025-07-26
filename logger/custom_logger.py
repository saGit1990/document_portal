import logging
import sys
import os
from datetime import datetime

class CustomLogger:
    def __init__(self, log_dir='logs'):
        self.logs_dir=os.path.join(os.getcwd(),log_dir) # log_dir not defined
        os.makedirs(self.logs_dir, exist_ok=True)
        
        LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        LOG_FILE_PATH=os.path.join(self.logs_dir, LOG_FILE)
        
        logging.basicConfig(
                filename=LOG_FILE_PATH,
                format="[ %(asctime)s ] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s]",
                level=logging.INFO,
            )
    
    def get_logger(self, name= __file__): # __file__ dunder variable
        return logging.getLogger(os.path.basename(name)) 
    
if __name__=="__main__":
    logger = CustomLogger()
    logger.get_logger(__file__)
    logging.info("The logger is initialized")