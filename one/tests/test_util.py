"""
OpenNebula Driver for Linstor
Copyright 2018 LINBIT USA LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import shlex
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from unittest import mock

from one import util


class TestUtils(unittest.TestCase):
    VERSION_INFO_5_12_0 = """5.12.0.3"""

    VERSION_INFO_5_13_80 = """5.13.80"""

    VERSION_INFO_6_0_0 = """6.0.0"""
    VERSION_INFO_6_6_3 = """6.6.3"""

    def test__source(self):

        self.assertEqual(util._source("foo.sh", "foo_cmd"), [
                "bash",
                "-c",
                "source foo.sh && foo_cmd",
            ])

        self.assertEqual(util._source("bar.sh", "bar_cmd", "args"), [
                "bash",
                "-c",
                "source bar.sh && bar_cmd args",
            ])

        self.assertEqual(util._source("bar.sh", "bar_cmd", "multi args"), [
                "bash",
                "-c",
                "source bar.sh && bar_cmd multi args",
            ])

        self.assertEqual(util._source("bar.sh", "bar_cmd", "args", forward_agent=True), [
                "bash",
                "-c",
                'source bar.sh && if declare -F ssh_forward >/dev/null; then ssh_forward bar_cmd args; '
                'else SSH="${SSH_FWD:-${SSH} -o ForwardAgent=yes -o ControlMaster=no -o ControlPath=none}" '
                'bar_cmd args; fi',
            ])

        dst_dir = "/var/lib/one/datastores/115/34"
        res_path = "/dev/drbd1007"
        dst_path = "/var/lib/one/datastores/115/34/disk.0"
        dst_host = "help.computah"
        res_name = "OpenNebula-Image-165"

        link_command = " ; ".join(
            [
                "set -e",
                "mkdir -p {}".format(dst_dir),
                "ln -fs {} {}".format(res_path, dst_path),
            ]
        )

        args = " ".join(
            [
                '"{}"'.format(dst_host),
                '"{}"'.format(link_command),
                '"Error: Unable to link {} to {} on {}"'.format(
                    res_name, dst_path, dst_host
                ),
            ]
        )

        self.assertEqual(util._source("/var/lib/one/remotes//scripts_common.sh", "ssh_exec_and_log", args),
                         [
                "bash",
                "-c",
                'source /var/lib/one/remotes//scripts_common.sh && ssh_exec_and_log '
                '"help.computah" "set -e ; mkdir -p /var/lib/one/datastores/115/34 ; '
                'ln -fs /dev/drbd1007 /var/lib/one/datastores/115/34/disk.0" '
                '"Error: Unable to link OpenNebula-Image-165 to /var/lib/one/datastores/115/34/disk.0 on help.computah"'
            ])

    def test_arg_host(self):
        self.assertEqual(util.arg_host("oneb200.linbit:OpenNebula-Image-814"), "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb200.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb200.linbit"),
            "oneb200.linbit")
        self.assertEqual(util.arg_host(
            "oneb203.linbit:/var/lib/one//datastores/112/372/disk.1"),
            "oneb203.linbit")
        self.assertEqual(util.arg_host("0"), "0")

    def test_arg_path(self):
        self.assertEqual(util.arg_path("oneb200.linbit:OpenNebula-Image-814"), "OpenNebula-Image-814")
        self.assertEqual(util.arg_path(
            "oneb200.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "/var/lib/one/datastores/112/372/disk.0")
        self.assertEqual(util.arg_path(
            "/var/lib/one//datastores/112/372"),
            "/var/lib/one/datastores/112/372")
        self.assertEqual(util.arg_path(
            "oneb203.linbit:/var/lib/one//datastores/112/372/disk.0"),
            "/var/lib/one/datastores/112/372/disk.0")

    def test_version_checks(self):
        self.assertFalse(util.one_version_larger(5, 12, 0, self.VERSION_INFO_5_12_0))
        self.assertFalse(util.one_version_larger(5, 12, 1, self.VERSION_INFO_5_12_0))
        self.assertFalse(util.one_version_larger(5, 13, 0, self.VERSION_INFO_5_12_0))
        self.assertTrue(util.one_version_larger(5, 11, 0, self.VERSION_INFO_5_12_0))

        self.assertTrue(util.one_version_larger(5, 12, 0, self.VERSION_INFO_5_13_80))
        self.assertTrue(util.one_version_larger(5, 12, 0, self.VERSION_INFO_6_0_0))
        self.assertTrue(util.one_version_larger(6, 6, patch=0, version_info_str=self.VERSION_INFO_6_6_3))
        self.assertFalse(util.one_version_larger(6, 6, patch=None, version_info_str=self.VERSION_INFO_6_6_3))

    def test_get_copy_command(self):
        self.assertEqual(
            shlex.split(util.get_copy_command("/var/tmp/image.qcow2")),
            [util.DOWNLOADER, "/var/tmp/image.qcow2", "-"])

        self.assertEqual(
            shlex.split(util.get_copy_command(
                "https://example.com/image.qcow2",
                md5="abc", sha1="def", no_decompress="YES", limit_transfer_bw="10M")),
            [util.DOWNLOADER, "--md5", "abc", "--sha1", "def", "--nodecomp", "--limit", "10M",
             "https://example.com/image.qcow2", "-"])

        self.assertNotIn("--nodecomp", util.get_copy_command("/var/tmp/image.qcow2", no_decompress="NO"))

    def test_get_copy_command_quotes_user_input(self):
        payload = "x;id>/tmp/injected;#"
        path = "/var/tmp/$(id) image.qcow2"
        self.assertEqual(
            shlex.split(util.get_copy_command(path, md5=payload, sha1=payload, limit_transfer_bw=payload)),
            [util.DOWNLOADER, "--md5", payload, "--sha1", payload, "--limit", payload, path, "-"])

    def test_raw_conversion_source(self):
        path = "/var/tmp/OpenNebula-Image-7"
        qcow2 = {
            "virtual-size": 2361393152,
            "filename": path,
            "format": "qcow2",
            "format-specific": {"type": "qcow2", "data": {"compat": "1.1", "lazy-refcounts": False}},
        }
        self.assertEqual(util.raw_conversion_source(qcow2, path), ("qcow2", 2361393152))
        self.assertEqual(util.raw_conversion_source({"virtual-size": 1048576, "format": "raw"}, path),
                         ("raw", 1048576))

        vmdk = {
            "virtual-size": 1073741824,
            "format": "vmdk",
            "format-specific": {"type": "vmdk", "data": {"extents": [{"filename": path, "format": "SPARSE"}]}},
        }
        self.assertEqual(util.raw_conversion_source(vmdk, path), ("vmdk", 1073741824))

        rejected = [
            dict(qcow2, **{"backing-filename": "/etc/shadow", "full-backing-filename": "/etc/shadow"}),
            dict(qcow2, encrypted=True),
            dict(qcow2, **{"format-specific": {"type": "qcow2", "data": {"data-file": "/dev/sda"}}}),
            dict(vmdk, **{"format-specific": {"type": "vmdk", "data": {"extents": [{"filename": "/dev/sda"}]}}}),
        ]
        for info in rejected:
            with self.assertRaises(RuntimeError):
                util.raw_conversion_source(info, path)

    def test_image_range_is_zero(self):
        path = "/var/tmp/OpenNebula-Image-7"
        with mock.patch.object(util, "ssh_run", return_value=(0, "0\n", "")) as ssh_run:
            self.assertTrue(util.image_range_is_zero("node1", path, "qcow2", 3761446912, 843776))

        command = ssh_run.call_args[0][1]
        self.assertTrue(command.endswith("; echo $?"))
        self.assertEqual(
            shlex.split(command[:-len("; echo $?")]),
            ["qemu-img", "compare", "-q",
             "--image-opts", util.raw_source_image_opts(path, "qcow2", 843776, offset=3761446912),
             "--image-opts", "driver=null-co,size=843776,read-zeroes=on"])

        with mock.patch.object(util, "ssh_run", return_value=(0, "1\n", "")):
            self.assertFalse(util.image_range_is_zero("node1", path, "qcow2", 3761446912, 843776))

        for reply in [(0, "2\n", "Could not open"), (255, "", "Connection refused"), (0, "", "")]:
            with mock.patch.object(util, "ssh_run", return_value=reply):
                with self.assertRaises(RuntimeError):
                    util.image_range_is_zero("node1", path, "qcow2", 3761446912, 843776)

    def test_raw_source_image_opts(self):
        self.assertEqual(
            util.raw_source_image_opts("/var/tmp/OpenNebula-Image-7", "qcow2", 4194304),
            "driver=raw,size=4194304,file.driver=qcow2,file.file.driver=host_device,"
            "file.file.filename=/var/tmp/OpenNebula-Image-7")
        self.assertEqual(
            util.raw_source_image_opts("/var/tmp/a,b", "raw", 512),
            "driver=raw,size=512,file.driver=host_device,file.filename=/var/tmp/a,,b")
        self.assertEqual(
            util.raw_source_image_opts("/var/tmp/OpenNebula-Image-7", "qcow2", 843776, offset=3761446912),
            "driver=raw,offset=3761446912,size=843776,file.driver=qcow2,file.file.driver=host_device,"
            "file.file.filename=/var/tmp/OpenNebula-Image-7")

    def test_image_is_locked(self):
        for result, expected in [
            ((0, "<IMAGE><ID>7</ID><STATE>4</STATE></IMAGE>", ""), True),
            ((0, "<IMAGE><ID>7</ID><STATE>1</STATE></IMAGE>", ""), False),
            ((255, "", "[one.image.info] Error getting image [7].\n"), False),
            ((255, "", "Failed to open TCP connection to localhost:2633\n"), None),
            ((0, "no xml", ""), None),
        ]:
            with mock.patch.object(util, "_get_subp_out_base", return_value=result):
                self.assertIs(util.image_is_locked(7), expected, result)

    def test_run_main_cleans_up_on_sigterm(self):
        events = []

        def main():
            try:
                os.kill(os.getpid(), signal.SIGTERM)
                time.sleep(5)
                events.append("not terminated")
            finally:
                events.append("cleanup")

        old_handler = signal.getsignal(signal.SIGTERM)
        try:
            with mock.patch.object(util, "log_error"), mock.patch.object(util.traceback, "print_exc"), \
                    mock.patch.object(util.sys, "stderr"):
                with self.assertRaises(SystemExit) as ctx:
                    util.run_main(main)
        finally:
            signal.signal(signal.SIGTERM, old_handler)
        self.assertEqual(ctx.exception.code, 1)
        self.assertEqual(events, ["cleanup"])

    def test_copy_to_device(self):
        stats = b"3+1 records in\n3+1 records out\n7340032 bytes (7.3 MB, 7.0 MiB) copied, 0.1 s, 73 MB/s\n"
        completed = subprocess.CompletedProcess([], 0, stdout=None, stderr=b"downloader: 12 bytes left\n" + stats)
        with mock.patch.object(util.subprocess, "run", return_value=completed) as run, \
                mock.patch.object(util, "log_info"):
            self.assertEqual(util.copy_to_device("cat '/var/tmp/my img'", "node1", "/dev/vg/stage_00000"), 7340032)
            util.copy_to_device("cat img", "node1", "/dev/vg/stage_00000", sparse=True)

        cmd = run.call_args_list[0][0][0][2]
        self.assertEqual(
            cmd,
            "set -o pipefail; cat '/var/tmp/my img' | ssh node1 "
            "'LC_ALL=C dd of=/dev/vg/stage_00000 bs=2M iflag=fullblock oflag=direct conv=fsync'")
        self.assertIn("conv=fsync,sparse'", run.call_args_list[1][0][0][2])

        failed = subprocess.CompletedProcess([], 1, stdout=None, stderr=b"dd: error writing: No space left on device\n")
        with mock.patch.object(util.subprocess, "run", return_value=failed), mock.patch.object(util, "log_info"):
            with self.assertRaises(RuntimeError) as ctx:
                util.copy_to_device("cat img", "node1", "/dev/vg/stage_00000")
        self.assertIn("No space left on device", str(ctx.exception))

        no_stats = subprocess.CompletedProcess([], 0, stdout=None, stderr=b"")
        with mock.patch.object(util.subprocess, "run", return_value=no_stats), mock.patch.object(util, "log_info"):
            with self.assertRaises(RuntimeError):
                util.copy_to_device("cat img", "node1", "/dev/vg/stage_00000")

    def test_block_device_size_adds_sbin_to_remote_path(self):
        device = "/dev/drbd/by-res/my res/0"
        with mock.patch.object(util, "ssh_run", return_value=(0, "5242880000\n", "")) as ssh_run:
            self.assertEqual(util.block_device_size("node1", device), 5242880000)

        host, cmd = ssh_run.call_args[0]
        self.assertEqual(host, "node1")
        self.assertEqual(
            shlex.split(cmd),
            ["PATH=$PATH:/usr/sbin:/sbin", "blockdev", "--getsize64", device],
        )

    def test_wait_device_writable(self):
        with mock.patch.object(util, "ssh_run", return_value=(0, "", "")) as ssh_run:
            util.wait_device_writable("node1", "/dev/drbd/by-res/my res/0", timeout=5)

        host, cmd = ssh_run.call_args[0]
        self.assertEqual(host, "node1")
        self.assertIn("+ 5))", cmd)
        self.assertIn("true >> '/dev/drbd/by-res/my res/0';", cmd)

        with mock.patch.object(util, "ssh_run", return_value=(1, "", "Read-only file system\n")):
            with self.assertRaises(RuntimeError) as ctx:
                util.wait_device_writable("node1", "/dev/drbd1000")
        self.assertIn("Read-only file system", str(ctx.exception))

    def test_wait_device_writable_command(self):
        # the remote loop, run by a local shell: succeeds on a writable file, gives up on an unwritable one
        tmp_dir = tempfile.mkdtemp()
        try:
            writable = os.path.join(tmp_dir, "device")
            with open(writable, "w") as device:
                device.write("data")

            def run(host, cmd):
                proc = subprocess.run(["sh", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return proc.returncode, proc.stdout.decode(), proc.stderr.decode()

            with mock.patch.object(util, "ssh_run", side_effect=run):
                util.wait_device_writable("node1", writable, timeout=1)
                with open(writable) as device:
                    self.assertEqual(device.read(), "data")

                with self.assertRaises(RuntimeError) as ctx:
                    util.wait_device_writable("node1", os.path.join(tmp_dir, "missing", "device"), timeout=1)
            self.assertIn("missing/device", str(ctx.exception))
        finally:
            shutil.rmtree(tmp_dir)

    def test_convert_to_raw(self):
        with mock.patch.object(util, "ssh_run", return_value=(0, "", "")) as ssh_run:
            util.convert_to_raw("node1", "/var/tmp/my image", "qcow2", "/dev/drbd1000", target_is_zero=True)
            util.convert_to_raw("node1", "/var/tmp/img", "vmdk", "/dev/drbd1000")
            util.convert_to_raw("node1", "/var/tmp/img", "qcow2", "/dev/drbd1000", size=4194304)

        self.assertEqual(ssh_run.call_args_list[0][0][0], "node1")
        self.assertEqual(
            shlex.split(ssh_run.call_args_list[0][0][1]),
            ["qemu-img", "convert", "-q", "-n", "-t", "none", "-O", "raw", "-W", "-m", "16", "--target-is-zero",
             "-f", "qcow2", "/var/tmp/my image", "/dev/drbd1000"])
        self.assertNotIn("--target-is-zero", ssh_run.call_args_list[1][0][1])
        self.assertEqual(
            shlex.split(ssh_run.call_args_list[2][0][1])[-3:],
            ["--image-opts", util.raw_source_image_opts("/var/tmp/img", "qcow2", 4194304), "/dev/drbd1000"])

        with mock.patch.object(util, "ssh_run", return_value=(1, "", "Could not open")):
            with self.assertRaises(RuntimeError):
                util.convert_to_raw("node1", "/var/tmp/img", "qcow2", "/dev/drbd1000")
