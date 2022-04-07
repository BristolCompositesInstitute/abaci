import os
import subprocess
import cPickle as pkl
from tempfile import gettempdir
from redist import parse_agent_variables

ssh_agent_cache_file = os.path.join(gettempdir(),'abaci-ssh-agent-cache')

def setup_ssh_agent():
    """ Top-level wrapper to setup a persistent ssh-agent for abaci
    
        Agent details are cached to file to allow reusing the same ssh-agent
        per session

    """
    agent_data = get_existing_agent()

    if not agent_data:

        agent_data = start_ssh_agent()

    set_envvars(agent_data)

    if not is_identity_added():
        subprocess.check_call(['ssh-add'])


def is_identity_added():
    """Check if the default ssh identity has been added to the ssh-agent"""

    devnull = open(os.devnull,'w')

    cmd = ['ssh-add', '-l']
                
    stat =  subprocess.call(cmd,stdout=devnull,stderr=devnull)
    
    return stat == 0


def start_ssh_agent():
    """Start a new ssh-agent and return the agent_data struct"""

    global ssh_agent_cache_file

    p = subprocess.Popen(['ssh-agent', '-s'], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()

    agent_data = parse_agent_variables.parse(stdout)
    
    with open(ssh_agent_cache_file,'w') as f:
        pkl.dump(agent_data,f,)

    return agent_data


def set_envvars(agent_data):
    """Setup environment variables from agent_data struct"""

    os.environ['SSH_AUTH_SOCK'] = agent_data['SSH_AUTH_SOCK']
    os.environ['SSH_AGENT_PID'] = agent_data['SSH_AGENT_PID']


def get_existing_agent():
    """Check the cache file to see if an ssh-agent has already been started for this session"""

    global ssh_agent_cache_file

    pid = os.getenv('SSH_AGENT_PID')
    sock = os.getenv('SSH_AUTH_SOCK')

    if pid and sock and check_agent(pid):

        # Use ssh-agent from parent environment
        return {'SSH_AGENT_PID': os.getenv('SSH_AGENT_PID'),
                    'SSH_AUTH_SOCK': os.getenv('SSH_AUTH_SOCK')}

    elif os.path.exists(ssh_agent_cache_file):

        with open(ssh_agent_cache_file,'r') as f:
            agent_data = pkl.load(f)
        
        if check_agent(agent_data['SSH_AGENT_PID']):

            # Use ssh-agent from cache file
            return agent_data

    # No existing ssh-agent found
    return None


def check_agent(pid):
    """Check if PID corresponds to existing ssh-agent instance"""
    
    if os.name == 'nt':

        cmd = ['tasklist', '/fi', 'pid eq {pid}'.format(pid=pid)]

    else:

        cmd = ['ps', '-p', '{pid}'.format(pid=pid)]

    try:

        output = subprocess.check_output(cmd).strip()

    except:

        output = ''

    return 'ssh-agent' in output


