set -eu

## Setup vCenter Server 8.0 env.
mkdir -p /var/lib/sso/webapps/ROOT/WEB-INF/views
cp /app/unpentry.jsp.80 /var/lib/sso/webapps/ROOT/WEB-INF/views/unpentry.jsp
mkdir -p /usr/sbin/
touch /usr/sbin/vpxd

## Run main.py.
export VMWARE_USERNAME='administrator@vsphere.local'
export VMWARE_PASSWORD='Password123!Password123!'
python3 /main.py
python3 /main.py # Run twice to ensure the program runs correctly even if executed multiple times.

main_py_status=$?
if [ $main_py_status -ne 0 ]; then
    echo "⚠️ Test FAILURE [vCenter Server 8.0]: main.py exited with code $main_py_status"
    exit 1
fi

## Check answer file.
checksum_file=$(sha256sum /var/lib/sso/webapps/ROOT/WEB-INF/views/unpentry.jsp | awk '{print $1}')
checksum_answer=$(sha256sum /app/unpentry.jsp.80.answer | awk '{print $1}')
if [ "$checksum_file" = "$checksum_answer" ]; then
    echo "✅ Test SUCCESS [vCenter Server 8.0]: Checksums match."
    exit 0
else
    echo "⚠️ Test FAILURE [vCenter Server 8.0]: Checksums do not match."
    echo checksum_file = $checksum_file
    echo checksum_answer = $checksum_answer
    head /var/lib/sso/webapps/ROOT/WEB-INF/views/unpentry.jsp /app/unpentry.jsp.80.answer
    exit 1
fi