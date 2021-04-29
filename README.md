# Clone repo with submodule
`git clone --recurse-submodules https://github.com/wholechainsawit/devnet-gitlab-nso-cml-ci.git`

# Clone repo
For gitlab setup: `git clone https://github.com/CiscoDevNet/nso_cicd_setup nso_cicd_setup`
For nso-docker: `https://gitlab.com/nso-developer/nso-docker.git`

# Devnet Sandbox dev info
Dev Server: developer@10.10.20.50 /C1sco12345
CML: https://10.10.20.161  developer/C1sco12345

# pip install
pip3 install virl2_client


# link iOS ned
ln -s ln -s /opt/ncs/current/packages/neds/cisco-ios-cli-3.8 /nso/run/packages/cisco-ios-cli-3.8 

# load authgroup
ncs_load -lm auth_groups.xml -u admin

# Setup Gitlab-CE
echo "Spinning up GitLab-CE"
cwd=$(pwd)
cd gitlab
make
cd ${cwd}

