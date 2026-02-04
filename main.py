#!/usr/bin/env python3
import os
import sys
import subprocess

JSP_VCSA_PATH_70 = "/usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views/unpentry.jsp"
JSP_VCSA_PATH_80 = "/var/lib/sso/webapps/ROOT/WEB-INF/views/unpentry.jsp"
JAR_VCSA_PATH_90 = "/usr/lib/vmware-sso/vmware-sts/web/lib/libvmidentity-sts-server.jar"

JSP_OPS_90 = "/usr/lib/vmware-vcops/tomcat-web-app/webapps/ui/pages/login.jsp"

def setup_logger(enable_debug: bool) -> None:
    global logger
    from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO, WARN, ERROR

    class EmojiFormatter(Formatter):
        _FMT = "%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(emoji_level)s]: %(message)s"
        _EMOJIS = {
            DEBUG: "⚽ DEBUG",
            INFO: "✅ INFO",
            WARN: "⚠️ WARN",
            ERROR: "🚨 ERROR",
        }

        def __init__(self):
            super().__init__(fmt=self._FMT)

        def formatTime(self, record, datefmt=None):
            from datetime import datetime, timedelta, timezone
            ct = datetime.fromtimestamp(record.created)
            s = ct.isoformat(timespec="milliseconds")
            return s

        def format(self, record):
            emoji_level = self._EMOJIS.get(record.levelno, "UNINITIALIZED")
            setattr(record, 'emoji_level', emoji_level)

            return super().format(record)

    handler = StreamHandler()
    handler.setFormatter(EmojiFormatter())
    logger = getLogger(__name__)
    logger.addHandler(handler)

    if enable_debug:
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)



"""
    Runs shell script in Bash.
"""
def bash(script_str = ""):
    try:
        result = subprocess.run(
            ['bash'],
            input=script_str,
            text=True,
            capture_output=True
        )
        if len(result.stderr) > 0:
            raise Exception("Stderr is not empty.")
        if result.returncode != 0:
            raise Exception(f"Shell script exited with non-zero rc ({result.returncode}).")
    except Exception as e:
        print(f"Shell script exited with non-zero code: {e}")
        print("StdOut:")
        print(result.stdout)
        print("StdErr:")
        print(result.stderr)
        sys.exit(1)


def restart_sts_on_vc():
    script_str = f"""
    set -eu
    if command -v vmon-cli &> /dev/null; then
        echo "Restarting sts service..."
        vmon-cli -r sts
    else
        echo "vmon-cli command not found. Skipping sts restart."
    fi
    """
    bash(script_str)

def modify_vcsa_jsp_70(vmware_username: str, vmware_password: str):
    script_str = f"""
    set -eu
    cp {JSP_VCSA_PATH_70} /tmp/jsp-`date +%s `.txt
    if grep -qF 'placeholder="${{username_placeholder}}" value="' {JSP_VCSA_PATH_70}; then
        echo Username in {JSP_VCSA_PATH_70} has already been modified.
        exit 0
    fi
    if grep -qF 'placeholder="${{password_label}}" value="' {JSP_VCSA_PATH_70}; then
        echo Password in {JSP_VCSA_PATH_70} has already been modified.
        exit 0
    fi
    sed -i 's|placeholder="${{username_placeholder}}"|placeholder="${{username_placeholder}}" value="{vmware_username}"|g' {JSP_VCSA_PATH_70}
    sed -i 's|placeholder="${{password_label}}"|placeholder="${{password_label}}" value="{vmware_password}"|g' {JSP_VCSA_PATH_70}
    """
    bash(script_str)


def modify_vcsa_jsp_80(vmware_username: str, vmware_password: str):
    script_str = f"""
    set -eu
    cp {JSP_VCSA_PATH_80} /tmp/jsp-`date +%s `.txt
    if grep -qF 'placeholder="${{username_placeholder}}" value="' {JSP_VCSA_PATH_80}; then
        echo Username in {JSP_VCSA_PATH_80} has already been modified.
        exit 0
    fi
    if grep -qF 'placeholder="${{password_label}}" value="' {JSP_VCSA_PATH_80}; then
        echo Password in {JSP_VCSA_PATH_80} has already been modified.
        exit 0
    fi
    sed -i 's|placeholder="${{username_placeholder}}"|placeholder="${{username_placeholder}}" value="{vmware_username}"|g' {JSP_VCSA_PATH_80}
    sed -i 's|placeholder="${{password_label}}"|placeholder="${{password_label}}" value="{vmware_password}"|g' {JSP_VCSA_PATH_80}
    """
    bash(script_str)


def modify_vcsa_jar_90(vmware_username: str, vmware_password: str):
    work_dir = "/var/tmp/workdir_script"
    backup_dir = "/var/tmp"

    # Expand .jar file under work_dir.
    bash(f"""
        set -eu

        # 1. Create a backup at `backup_dir.`
        cp -p "{JAR_VCSA_PATH_90}" "{backup_dir}"

        # 2. Create a working directory at `work_dir.`
        rm -rf "{work_dir}"
        mkdir -p "{work_dir}"

        # 3. unzip .jar file at `work_dir.`
        unzip -q "{JAR_VCSA_PATH_90}" -d "{work_dir}"
    """)

    # Read all content from unpentry.jsp.
    with open(f"{work_dir}/WEB-INF/views/unpentry.jsp", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fill_script=f"""
        <script type="text/javascript">
            document.addEventListener('DOMContentLoaded', function() {{
                document.getElementById('username').value = "{vmware_username}";
                document.getElementById('password').value = "{vmware_password}";
                console.info("[vmware-ui-login-filler] Filled login form.");
            }});
        </script>
        """.replace('\n', '').replace('\r', '').replace('    ', '')
    
    # Append scripts before </body> tag.
    new_lines = []
    added_script = False
    for line in lines:
        if '</body>' in line and not added_script:
            new_lines.append(fill_script)
            new_lines.append('\n')
            added_script = True
        if 'vmware-ui-login-filler' in line:
            logger.warning(f"The .jsp file has been already modified. Removing an old line...")
            continue
        new_lines.append(line)
    
    with open(f"{work_dir}/WEB-INF/views/unpentry.jsp", 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    # Expand .jar file under work_dir.
    bash(f"""
        set -eu
        
        # 5. Generate a new .jar file.
        pushd "{work_dir}"
        zip -qr libvmidentity-sts-server.jar ./*
        popd

        # 6. Move .jar file to original location.
        TARGET_JAR="{work_dir}/libvmidentity-sts-server.jar"
        cp -p "$TARGET_JAR" "{JAR_VCSA_PATH_90}"

        rm -rf "{work_dir}"
    """)
    


def modify_vcsa(vmware_username: str, vmware_password: str):
    if os.path.exists(JSP_VCSA_PATH_70):
        modify_vcsa_jsp_70(vmware_username, vmware_password)
    elif os.path.exists(JSP_VCSA_PATH_80):
        modify_vcsa_jsp_80(vmware_username, vmware_password)
    elif os.path.exists(JAR_VCSA_PATH_90):
        modify_vcsa_jar_90(vmware_username, vmware_password)
    else:
        print("JSP file not found. Skipping auto fill login form step.")

def modify_operations():
    ops_admin_username = os.environ.get('OPS_ADMIN_USERNAME', '')
    ops_admin_password = os.environ.get('OPS_ADMIN_PASSWORD', '')
    script_str = f"""
    set -eu
    JSP_OPS_90="{JSP_OPS_90}"
    cp {JSP_OPS_90} /tmp/jsp-`date +%s `.txt
    sed -i '/var userNameField = new Ext.form.TextField/ a\\value: "{ops_admin_username}",' $JSP_OPS_90
    sed -i '/var passwordField = new Ext.form.TextField/ a\\value: "{ops_admin_password}",' $JSP_OPS_90
    """
    bash(script_str)

"""
    Determine appliance type.
    Possible outputs are: ["vcsa", "nsx", "sddc", "operations", "fleet"]
"""
def get_appliance_type():
    if os.path.exists("/usr/sbin/vpxd"):
        return "vcsa"
    if os.path.exists("/etc/init.d/vmware-vcops"):
        return "operations"
    
    print("Unknown appliance type.")
    sys.exit(1)

def main():
    if ("-h" in sys.argv) or ("--help" in sys.argv):
        print("Usage:")
        print("    export VMWARE_USERNAME='administrator@vsphere.local'")
        print("    export VMWARE_PASSWORD='password123'")
        print("    python main.py")
        sys.exit(0)

    appliance_type = get_appliance_type()
    logger.info(f"Product: {appliance_type}")
    
    vmware_username = os.environ.get('VMWARE_USERNAME', '')
    vmware_password = os.environ.get('VMWARE_PASSWORD', '')


    if appliance_type == "vcsa":
        modify_vcsa(vmware_username, vmware_password)
        logger.info(f"Restarting sts service...")
        restart_sts_on_vc()
    elif appliance_type == "operations":
        modify_operations()

    logger.info(f"Done.")

if __name__ == '__main__':
    setup_logger(False)
    main()
