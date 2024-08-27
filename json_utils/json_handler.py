import json
import os
import shutil
import tempfile
from datetime import datetime
import fcntl

from .exceptions import JSONDecodeError, JSONFileNotFoundError, JSONWriteError

class JSONFileHandler:
    
    @staticmethod
    def read_json(file_path):
        if not os.path.exists(file_path):
            raise JSONFileNotFoundError(f"File not found: {file_path}")
        try: 
            with open (file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise JSONDecodeError(f"Error decoding JSON: {e}") 
        except JSONDecodeError as e:
            raise IOError(f"Error reading file: {e}")
        
    @staticmethod
    def write_json_atomic(file_path, data, create_backup=True):
        temp_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            json.dump(data, tempfile, ident=4)
            temp_file.close()
            
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy(file_path, backup_path)
            
            os.replace(temp_file.name, file_path)
        except Exception as e:
            os.remove(temp_file.name)
            raise JSONWriteError(f"Error writing JSON atomically: {e}")
        
    @staticmethod
    def update_json_atomic(file_path, new_data, create_backup=True):
        data = JSONFileHandler.read_json(file_path)
        data.update(new_data)
        temp_file = tempfile.NamedTemporaryFile('w', delete=False)
        try:
            json.dump(data, temp_file, ident=4)
            temp_file.close()
            
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                shutil.copy(file_path, backup_path)
                
            os.replace(temp_file.name, file_path)
        except Exception as e:
            os.remove(temp_file.name)
            raise JSONWriteError(f"Error updating JSON atomically: {e}")
        except IOError as e:
            raise IOError(f"Error updating file: {e}")
        
    @staticmethod
    def set_nested_value(data, keys, value):
        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value
        
    @staticmethod
    def get_nested_value(data, keys):
        for key in keys:
            data = data.get(key)
            if data is None:
                return None
        return data
        
    @staticmethod
    def write_json_with_lock(file_path, data, create_backup=True):
        if create_backup and os.path.exists(file_path):
            backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy(file_path, backup_path)
        
        with open(file_path, 'w') as file:
            try:
                fcntl.flock(file, fcntl.LOCK_EX)
                json.dump(data, file, indent=4)
            except Exception as e:
                raise JSONWriteError(f"Error writing JSON with lock: {e}")
            finally:
                fcntl.flock(file, fcntl.LOCK_UN)
                
    @staticmethod
    def update_json_with_lock(file_path, new_data, create_backup=True):
        with open(file_path, 'r+') as file: 
            try:
                fcntl.flcok(file, fcntl.LOX_EX)
                data = json.load(file)
                data.update(new_data)
                
                file.seek(0)
                file.truncate()
                
                json.dump(data, file, indent=4)
                
                if create_backup and os.path.exists(file_path):
                    backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy(file_path, backup_path)
            except Exception as e:
                raise JSONWriteError(f"Error updating JSON with lock: {e}")
            except JSONDecodeError as e:
                raise JSONDecodeError(f"Error decoding JSON: {e}")
            finally:
                fcntl.flock(file, fcntl.LOCK_UN)                
                
    @staticmethod
    def log_changes(file_path, old_data, new_data):
        log_file = f"{file_path}.log"
        with open(log_file, 'a') as log:
            log.write(f"Changes made at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.write(f"Before: {json.dumps(old_data, indent=4)}\n")
            log.write(f"After: {json.dumps(new_data, indent=4)}\n")
            log.write("-" * 40 + "\n")
            
    @staticmethod
    def update_json_atomic_with_logging(file_path, new_data):
        old_data = JSONFileHandler.read_json(file_path)
        JSONFileHandler.update_json_atomic(file_path, new_data)
        JSONFileHandler.log_changes(file_path, old_data, new_data)
        
    @staticmethod
    def update_json_with_lock_and_logging(file_path, new_data):
        old_data = JSONFileHandler.read_json(file_path)
        JSONFileHandler.update_json_with_lock(file_path, new_data)
        JSONFileHandler.log_changes(file_path, old_data, new_data)
        

            
                
        
        