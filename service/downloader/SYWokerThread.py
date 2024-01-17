import threading
import time
import numpy as np
    
class CSYThreadWorker (threading.Thread):
    def __init__(self, threadID, name, paramObj):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.paramObj = paramObj
        self.runThread = 1
        self.task_queue = None;
    def run(self):
        print("开始执行任务")        
        while self.runThread == 1:            
            iconData = self.getNextData()
            if None == iconData:
                time.sleep(3)
                continue;                
            try:

                iconData["fun"](iconData["param"]); 
            except Exception as e:
                iconData["fun"](iconData["param"]); 
                print("---CSYThreadWorker work_fun ---e = ", e,  e.__traceback__.tb_frame,e.__traceback__.tb_lineno)         

    def getNextData(self):
        # 获取锁，用于线程同步
        if None == self.task_queue:
            return None        
        
        self.task_queue["lock"].acquire();
        if len(self.task_queue["task_list"]) <= 0:
            self.task_queue["lock"].release()
            return None
            
        iconData = self.task_queue["task_list"][0]
        del self.task_queue["task_list"][0]
       
        # 释放锁，开启下一个线程
        self.task_queue["lock"].release()
        
        return iconData   
               
    def stop_thread(self):
        self.runThread = 0
        self.join();       
        


    
class CVMThreadWorkMgr():   
    obj_picker = None 
    def __init__(self):
        self.worker = [];   
        self.worker_count = 1; 
        self.task_queue = None  
        
    def put_request(self, fun, param):
        self.init_worker()        
        data = {
            "fun":fun,
            "param":param,
        }
        self.task_queue["lock"].acquire();
        self.task_queue["task_list"].append(data);
        self.task_queue["lock"].release()
        return True;
    def task_list_size(self):
        if None == self.task_queue:
            return 0;
        self.task_queue["lock"].acquire();
        size = len(self.task_queue["task_list"]);
        self.task_queue["lock"].release()
        return size;    
    def init_worker(self):
        if len(self.worker) > 0:
            return self.worker
        self.task_queue = {
            "lock":threading.Lock(),
            "task_list":[]
        }
        for i in range(self.worker_count):
            obj = CSYThreadWorker(100, "ThreadWorker", self)
            obj.task_queue = self.task_queue;
            obj.start()
            self.worker.append(obj)

        return self.worker; 
    
def instance():
    if None == CVMThreadWorkMgr.obj_picker:
        CVMThreadWorkMgr.obj_picker = CVMThreadWorkMgr();   

    return CVMThreadWorkMgr.obj_picker
