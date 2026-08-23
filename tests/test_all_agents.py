#!/usr/bin/env python3
import json
import os
import subprocess
import unittest

BIN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "agent-guard")

class TestAgentSecurityGate(unittest.TestCase):

    def run_guard(self, payload_dict):
        res = subprocess.run(
            [BIN_PATH, "eval"],
            input=json.dumps(payload_dict),
            text=True,
            capture_output=True
        )
        self.assertEqual(res.returncode, 0, f"agent-guard exited with code {res.returncode}: {res.stderr}")
        return json.loads(res.stdout)

    def test_antigravity_format(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "mktemp -d", "Cwd": "/tmp"}
            },
            "workspacePaths": ["/tmp"]
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "allow")

    def test_copilot_format_allowed(self):
        payload = {
            "tool_name": "bash",
            "tool_input": {"command": "docker ps"},
            "cwd": "/Users/nils/Developer/project"
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "allow")

    def test_copilot_format_ask(self):
        payload = {
            "tool_name": "bash",
            "tool_input": {"command": "docker run -d redis"},
            "cwd": "/Users/nils/Developer/project"
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "ask_user")

    def test_opencode_format(self):
        payload = {
            "tool": "bash",
            "args": {"command": "pytest tests/"},
            "cwd": "/Users/nils/Developer/project"
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "allow")

    def test_cline_format(self):
        payload = {
            "tool": "execute_command",
            "args": {"command": "git push origin main"},
            "cwd": "/Users/nils/Developer/project"
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "ask")

    def test_continue_format(self):
        payload = {
            "name": "run_terminal_command",
            "arguments": {"command": "mktemp -d"}
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "allow")

    def test_deletion_in_temp_allowed(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -rf /tmp/test_dir", "Cwd": "/Users/nils/Developer/project"}
            },
            "workspacePaths": ["/Users/nils/Developer/project"]
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "allow")

    def test_deletion_in_cwd_prompt(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm main.py", "Cwd": "/Users/nils/Developer/project"}
            },
            "workspacePaths": ["/Users/nils/Developer/project"]
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "force_ask")

    def test_deletion_outside_denied(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -rf /Users/other/docs", "Cwd": "/Users/nils/Developer/project"}
            },
            "workspacePaths": ["/Users/nils/Developer/project"]
        }
        resp = self.run_guard(payload)
        self.assertEqual(resp["decision"], "deny")

if __name__ == "__main__":
    unittest.main()
