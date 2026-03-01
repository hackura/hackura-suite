from core.wrapper import ToolWrapper
import xml.etree.ElementTree as ET

class NmapWrapper(ToolWrapper):
    def __init__(self, windows_path=None):
        super().__init__("nmap", windows_path)

    def scan(self, target, arguments="-F"):
        """Performs a scan and returns the results."""
        # Force XML output for easier parsing
        all_args = arguments.split() + ["-oX", "-", target]
        result = self.run(all_args)
        
        if result["success"]:
            return self._parse_xml(result["stdout"])
        return result

    def _parse_xml(self, xml_string):
        """Basic XML parser for nmap results."""
        try:
            root = ET.fromstring(xml_string)
            hosts = []
            for host in root.findall('host'):
                addr = host.find('address').attrib['addr']
                status = host.find('status').attrib['state']
                ports = []
                for port in host.findall('.//port'):
                    p_id = port.attrib['portid']
                    p_proto = port.attrib['protocol']
                    p_state = port.find('state').attrib['state']
                    ports.append({"id": p_id, "protocol": p_proto, "state": p_state})
                hosts.append({"address": addr, "status": status, "ports": ports})
            return {"success": True, "hosts": hosts}
        except Exception as e:
            return {"success": False, "error": f"Failed to parse XML: {str(e)}"}
