# Extract ssh-agent environment variables from ssh-agent output
#
# Source: https://github.com/haarcuba/ssh-agent-setup
# 
# MIT License
# 
# Copyright (c) 2019 Yoav Kleinberger
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

_OUTPUT_PATTERN = re.compile(r'SSH_AUTH_SOCK=(?P<SSH_AUTH_SOCK>[^;]+).*SSH_AGENT_PID=(?P<SSH_AGENT_PID>\d+)', re.MULTILINE | re.DOTALL)

def parse(output):
    match = _OUTPUT_PATTERN.search(output)
    if match is None:
        raise Exception('Could not parse ssh-agent output. It was: {output}'.format(output))
    return match.groupdict()
