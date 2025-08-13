#!/usr/bin/env python3
import os
import sys
import subprocess

JSP_VCSA_PATH_70 = "/usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views/unpentry.jsp"
JSP_VCSA_PATH_80 = "/var/lib/sso/webapps/ROOT/WEB-INF/views/unpentry.jsp"
JAR_VCSA_PATH_90 = "/usr/lib/vmware-sso/vmware-sts/web/lib/libvmidentity-sts-server.jar"

JSP_OPS_90 = "/usr/lib/vmware-vcops/tomcat-web-app/webapps/ui/pages/login.jsp"

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
        print(f"Failed to update {JSP_VCSA_PATH_70}: {e}")
        print("StdOut:")
        print(result.stdout)
        print("StdErr:")
        print(result.stderr)
        sys.exit(1)


def modify_vcsa_jsp_70():
    sso_username = os.environ.get('SSO_USERNAME', '')
    sso_password = os.environ.get('SSO_PASSWORD', '')
    script_str = f"""
    set -eu
    cp {JSP_VCSA_PATH_70} /tmp/jsp-`date +%s `.txt
    sed -i 's|placeholder="${{username_placeholder}}"|placeholder="${{username_placeholder}}" value="{sso_username}"|g' {JSP_VCSA_PATH_70}
    sed -i 's|placeholder="${{password_label}}"|placeholder="${{password_label}}" value="{sso_password}"|g' {JSP_VCSA_PATH_70}
    """
    bash(script_str)


def modify_vcsa_jsp_80():
    sso_username = os.environ.get('SSO_USERNAME', '')
    sso_password = os.environ.get('SSO_PASSWORD', '')
    script_str = f"""
    set -eu
    cp {JSP_VCSA_PATH_80} /tmp/jsp-`date +%s `.txt
    sed -i 's|placeholder="${{username_placeholder}}"|placeholder="${{username_placeholder}}" value="{sso_username}"|g' {JSP_VCSA_PATH_80}
    sed -i 's|placeholder="${{password_label}}"|placeholder="${{password_label}}" value="{sso_password}"|g' {JSP_VCSA_PATH_80}
    """
    bash(script_str)


def modify_vcsa_jar_90():
    sso_username = os.environ.get('SSO_USERNAME', '')
    sso_password = os.environ.get('SSO_PASSWORD', '')
    work_dir = "/var/tmp/workdir_script"
    backup_dir = "/var/tmp"
    script_str = f"""
    set -eu

    # 1. バックアップ作成
    cp -p "{JAR_VCSA_PATH_90}" "{backup_dir}"

    # 2. 作業ディレクトリ準備
    rm -rf "{work_dir}"
    mkdir -p "{work_dir}"

    # 3. JAR展開 (unzip)
    unzip -q "{JAR_VCSA_PATH_90}" -d "{work_dir}"

    # 4. sed コマンド実行対象ファイルパス設定
    JSP_PATH="{work_dir}/WEB-INF/views/unpentry.jsp"
    sed -i 's|placeholder="${{username_placeholder}}"|placeholder="${{username_placeholder}}" value="{sso_username}"|g' "$JSP_PATH"
    sed -i 's|placeholder="${{password_label}}"|placeholder="${{password_label}}" value="{sso_password}"g' "$JSP_PATH"

    # 5. JAR 再生成 (zip)
    pushd "{work_dir}"
    zip -qr libvmidentity-sts-server.jar ./*
    popd

    # 6. 元の場所に配置（上書き）
    TARGET_JAR="{work_dir}/libvmidentity-sts-server.jar"
    cp -p "$TARGET_JAR" "{JAR_VCSA_PATH_90}"

    rm -rf "{work_dir}"
    """
    bash(script_str)


def modify_vcsa():
    if os.path.exists(JSP_VCSA_PATH_70):
        modify_vcsa_jsp_70()
    elif os.path.exists(JSP_VCSA_PATH_80):
        modify_vcsa_jsp_80()
    elif os.path.exists(JAR_VCSA_PATH_90):
        modify_vcsa_jar_90()
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
    appliance_type = get_appliance_type()

    if appliance_type == "vcsa":
        modify_vcsa()
    elif appliance_type == "operations":
        modify_operations()


if __name__ == '__main__':
   main()
