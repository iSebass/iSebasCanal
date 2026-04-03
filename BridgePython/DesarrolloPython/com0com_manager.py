import subprocess
import os
import re
import ctypes
import winreg

class Com0ComManager:
    SETUP_PATH = r"C:\Program Files (x86)\com0com\setupc.exe"

    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _run_command(self, cmd_args):
        if not os.path.exists(self.SETUP_PATH):
            return False, f"com0com no encontrado en {self.SETUP_PATH}"
        
        try:
            setup_dir = os.path.dirname(self.SETUP_PATH)
            process = subprocess.run([self.SETUP_PATH] + cmd_args, 
                                   cwd=setup_dir,
                                   capture_output=True, text=True, check=False)
            
            output = (process.stdout or "") + (process.stderr or "")
            
            # com0com setupc can return 0 but show "Error" in text
            if process.returncode != 0 or "Error" in output:
                return False, output.strip()
            
            return True, output.strip()
        except Exception as e:
            return False, str(e)

    def list_pairs(self):
        pairs = []
        try:
            success, output = self._run_command(["list"])
            if not success or not output.strip():
                return []
                
            port_map = {}
            for line in output.split('\n'):
                line = line.strip()
                if not line: continue
                
                parts = line.split(' ')
                if not parts: continue
                
                name_part = parts[0]
                is_A = name_part.startswith("CNCA")
                is_B = name_part.startswith("CNCB")
                
                if is_A or is_B:
                    try:
                        idx = int(name_part[4:])
                    except: 
                        continue
                        
                    port_name_match = re.search(r"PortName=([^,\s]+)", line)
                    if port_name_match:
                        if idx not in port_map: port_map[idx] = {}
                        if is_A:
                            port_map[idx]['A'] = port_name_match.group(1).strip()
                        else:
                            port_map[idx]['B'] = port_name_match.group(1).strip()

            for idx in sorted(port_map.keys()):
                if 'A' in port_map[idx] and 'B' in port_map[idx]:
                    pairs.append((idx, port_map[idx]['A'], port_map[idx]['B']))
            return pairs
        except Exception:
            return []

    def create_pair(self, port_a, port_b):
        # Format: install PortName=COM10 PortName=COM11
        cmd = ["install", f"PortName={port_a}", f"PortName={port_b}"]
        success, output = self._run_command(cmd)
        return success, output

    def remove_pair(self, index=0):
        # Format: remove 0 (remove first pair found)
        # Note: 'remove' in com0com setupc usually takes an index. 
        # Typically the first available is 0.
        success, output = self._run_command(["remove", str(index)])
        return success, output

if __name__ == "__main__":
    manager = Com0ComManager()
    print(f"Es Admin: {manager.is_admin()}")
    print(f"Pares actuales: {manager.list_pairs()}")
