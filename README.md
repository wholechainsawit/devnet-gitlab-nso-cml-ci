# Steps:
1. Reserve an instance of the [Devnet CML Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/45100600-b413-4471-b28e-b014eb824555?diagramType=Topology)

2. Download trial NSO from [Devnet Download](https://developer.cisco.com/fileMedia/download/da6e8ed4-0b65-357a-9cf3-c1b3357a2ad4/) and get the `nso-5.3.linux.x86_64.installer.bin` by 
   ```
   bash nso-5.3.linux.x86_64.signed.bin
   ```
   
3. After connecting to Devnet sandbox VPN, ssh to Dev Server
   ```
   ssh developer@10.10.20.50 
   ```
   password: C1sco12345

3. Clone this project
   ```
   git clone --recurse-submodules https://github.com/wholechainsawit/devnet-gitlab-nso-cml-ci.git
   ```

4. Copy the trial NSO from Step 2 to the Dev Server
   ```
   scp nso-5.3.linux.x86_64.installer.bin developer@10.10.20.50:/home/developer/devnet-gitlab-nso-cml-ci/setup/nso-docker/nso-install-files
   ```

5. Run setup script
   ```
   cd /home/developer/devnet-gitlab-nso-cml-ci/setup
   sh set-env.sh
   ```

6. Setup a new project in Gitlab
   1. Create a new project, nso_cicd, on Gitlab [Instructions](https://developer.cisco.com/learning/lab/nso-cicd/step/4)
   2. Add this project to the Gitlab
   ```
   cd devnet-gitlab-nso-cml-ci
   git remote add gitlab http://10.10.20.50/root/nso_cicd.git
   git push -u gitlab --all
   ```
   credential: `root/C1sco12345`


# Reference:
[Devnet Learning lab - NSO in a CI/CD Pipeline](https://developer.cisco.com/learning/lab/nso-cicd/step/1)

### Devnet Sandbox devices info
```
Dev Server: developer@10.10.20.50 developer/C1sco12345
CML: https://10.10.20.161  developer/C1sco12345
```
