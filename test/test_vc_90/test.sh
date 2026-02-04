set -eu

## Setup vCenter Server 9.0 env.
mkdir -p /usr/lib/vmware-sso/vmware-sts/web/lib/
cp /app/libvmidentity-sts-server.jar.90 /usr/lib/vmware-sso/vmware-sts/web/lib/libvmidentity-sts-server.jar
mkdir -p /usr/sbin/
touch /usr/sbin/vpxd

## Run main.py.
export VMWARE_USERNAME='administrator@vsphere.local'
export VMWARE_PASSWORD='Password123!Password123!'
python3 /main.py
python3 /main.py # Run twice to ensure the program runs correctly even if executed multiple times.

main_py_status=$?
if [ $main_py_status -ne 0 ]; then
    echo "⚠️ Test FAILURE [vCenter Server 9.0]: main.py exited with code $main_py_status"
    exit 1
fi

## Check answer file.
WORKDIR="/var/tmp"
mkdir $WORKDIR/test
pushd $WORKDIR/test > /dev/null
unzip -q /usr/lib/vmware-sso/vmware-sts/web/lib/libvmidentity-sts-server.jar
popd > /dev/null
checksum_test=$(sha256sum $WORKDIR/test/WEB-INF/views/unpentry.jsp | awk '{print $1}')

checksum_answer=$(sha256sum /app/jar.90.answer | awk '{print $1}')

if [ "$checksum_test" = "$checksum_answer" ]; then
    echo "✅ Test SUCCESS [vCenter Server 9.0]: Checksums match."
    exit 0
else
    echo "⚠️ Test FAILURE [vCenter Server 9.0]: Checksums do not match."
    echo checksum_test = $checksum_test
    echo checksum_answer = $checksum_answer
    head $WORKDIR/test/WEB-INF/views/unpentry.jsp $WORKDIR/answer/WEB-INF/views/unpentry.jsp
    exit 1
fi