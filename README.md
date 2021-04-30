# Steps:
1. Download trial NSO [Devnet Download](https://developer.cisco.com/fileMedia/download/da6e8ed4-0b65-357a-9cf3-c1b3357a2ad4/)
   `bash nso-5.3.linux.x86_64.signed.bin`
   
2. After connecting to Devnet sandbox VPN, ssh to Dev Server
   `ssh developer@10.10.20.50` password: `C1sco12345`

3. Clone the project
   `git clone --recurse-submodules https://github.com/wholechainsawit/devnet-gitlab-nso-cml-ci.git`

4. Copy the trial NSO from Step 1 to the Dev Server
   `scp nso-5.3.linux.x86_64.installer.bin developer@10.10.20.50:/home/developer/devnet-gitlab-nso-cml-ci/setup/nso-docker/nso-install-files`

5. Run setup script
   `cd /home/developer/devnet-gitlab-nso-cml-ci/setup`
   `sh set-env.sh`

6. Create a project in Gitlab
   [Instructions](https://developer.cisco.com/learning/lab/nso-cicd/step/4)
   1. create nso_cicd project in Gitlab
   2. `git config --global user.name "name"`
      `git config --global user.email "my@email"`
   3. 
   ```
   cd existing_repo
   git remote rename origin old-origin
   git remote add origin http://10.10.20.50/root/nso_cicd.git
   git push -u origin --all
   ```
   credential: `root/C1sco12345`





# Reference:
[Devnet Learning lab - NSO in a CI/CD Pipeline](https://developer.cisco.com/learning/lab/nso-cicd/step/1)

### Clone repo
For gitlab setup: `git clone https://github.com/CiscoDevNet/nso_cicd_setup nso_cicd_setup`
For nso-docker: `https://gitlab.com/nso-developer/nso-docker.git`

### Devnet Sandbox dev info
Dev Server: developer@10.10.20.50 /C1sco12345
CML: https://10.10.20.161  developer/C1sco12345
