import threading
import time
import json
from core.db import db_manager

class DAGEngine:
    def __init__(self):
        self.running_tasks = {}

    def execute_workflow(self, workflow_name, nodes, callback=None):
        """
        Executes a sequence of security tools. 
        nodes: list of dicts with {'id': str, 'tool': str, 'target': str}
        """
        thread = threading.Thread(target=self._run_job, args=(workflow_name, nodes, callback))
        thread.start()
        return thread

    def _run_job(self, workflow_name, nodes, callback):
        log_msg = f"[*] Starting Workflow: {workflow_name}"
        if callback: callback(log_msg)
        
        db_manager.log_action("Workflow Started", workflow_name)
        
        for node in nodes:
            node_id = node['id']
            tool = node['tool']
            target = node['target']
            
            msg = f"[RUNNING] Step {node_id}: {tool} on {target}"
            if callback: callback(msg)
            
            # Simulate tool execution logic
            time.sleep(2) 
            
            status = "SUCCESS"
            if "fail" in target.lower(): # Simulation of a failure point
                status = "FAILED"
                err = f"[ERROR] {tool} failed. Stopping DAG orchestration."
                if callback: callback(err)
                break
                
            res_msg = f"[DONE] {node_id} complete."
            if callback: callback(res_msg)
            
        final_msg = "[+] Workflow Finished."
        if callback: callback(final_msg)
        db_manager.log_action("Workflow Finished", workflow_name)

dag_engine = DAGEngine()
