# vmware-ui-login-filler
This script edits unpentry.jsp to have the SSO administrator’s ID and password pre-filled on the vSphere Client login screen.

# Usage
```
export VMWARE_USERNAME='administrator@vsphere.local'
export VMWARE_PASSWORD='MyPassword'
python main.py
```

# Running Tests
```
git clone https://github.com/ushiba0/vmware-ui-login-filler.git
cd test
bash run_test.sh
```

# Importana Notes
- **This script significantly increases security risks.**  
  By embedding administrator credentials directly into the login page, it exposes sensitive information that could be exploited by unauthorized users or malware.

- **This tool is not officially supported or endorsed by VMware.**  
  It is strongly advised **not to use this script in any production environment** where security and stability are critical.

- **Use at your own risk.**  
  The author and contributors assume no responsibility for any damage, data loss, or security breaches resulting from the use of this script.
