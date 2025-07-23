set -eu

## Setup vCenter Server 7.0 env.
mkdir -p /usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views
cp /app/unpentry.jsp.70 /usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views/unpentry.jsp
mkdir -p /usr/sbin/
touch /usr/sbin/vpxd

## Run main.py.
SSO_USERNAME='administrator@vsphere.local' \
SSO_PASSWORD='Password123!Password123!' \
python3 /app/main.py

main_py_status=$?
if [ $main_py_status -ne 0 ]; then
    echo "Test FAILURE [vCenter Server 7.0]: main.py exited with code $main_py_status"
    exit 1
fi

## Check answer file.
checksum_file=$(sha256sum /usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views/unpentry.jsp | awk '{print $1}')
checksum_answer=$(sha256sum /app/unpentry.jsp.70.answer | awk '{print $1}')
if [ "$checksum_file" = "$checksum_answer" ]; then
    echo "Test SUCCESS [vCenter Server 7.0]: Checksums match."
    exit 0
else
    echo "Test FAILURE [vCenter Server 7.0]: Checksums do not match."
    echo checksum_file = $checksum_file
    echo checksum_answer = $checksum_answer
    head /usr/lib/vmware-sso/vmware-sts/webapps/ROOT/WEB-INF/views/unpentry.jsp /app/unpentry.jsp.70.answer
    exit 1
fi