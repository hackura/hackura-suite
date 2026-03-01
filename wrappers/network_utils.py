from core.wrapper import ToolWrapper
import sys
import re

class PingWrapper(ToolWrapper):
    def __init__(self):
        # cross-platform ping command
        tool = "ping"
        super().__init__(tool)

    def scan(self, target):
        count_arg = "-n" if sys.platform == "win32" else "-c"
        result = self.run([count_arg, "4", target])
        if result["success"]:
            # Basic parsing to see if host is alive
            alive = "received" in result["stdout"].lower() or "reply from" in result["stdout"].lower()
            return {"success": True, "alive": alive, "raw": result["stdout"]}
        return result

class WhoisWrapper(ToolWrapper):
    def __init__(self):
        super().__init__("whois")

    def scan(self, target):
        # Simple domain regex
        if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", target):
            return {"success": False, "error": "Invalid domain for WHOIS"}
        
        result = self.run([target])
        if result["success"]:
            return {"success": True, "data": result["stdout"]}
        return result

class DNSWrapper(ToolWrapper):
    def __init__(self):
        # Use dig on linux, nslookup on windows as fallback
        tool = "dig" if sys.platform != "win32" else "nslookup"
        super().__init__(tool)

    def scan(self, target):
        args = [target, "ANY"] if self.tool_name == "dig" else [target]
        result = self.run(args)
        if result["success"]:
            return {"success": True, "data": result["stdout"]}
        return result
