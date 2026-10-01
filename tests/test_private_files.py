"""Private-file regressions; run natively on Windows for ACL evidence.

Only synthetic fixtures beneath this test directory are mutated. No users,
accounts, global settings, external services or live workers are changed.
"""

import ctypes
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest import mock

try:
    from tests.test_lifecycle import AI_HUMAN as PRIVATE
except ModuleNotFoundError as exc:
    if exc.name not in {"tests", "tests.test_lifecycle"}:
        raise
    # unittest discover -s tests places that directory directly on sys.path.
    from test_lifecycle import AI_HUMAN as PRIVATE


class _PrivateFileFixture:
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="private-probe-", dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_private(self, path, content=b"synthetic private payload\n"):
        with os.fdopen(PRIVATE.open_private_exclusive(path), "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())

class PrivateFileTests(_PrivateFileFixture, unittest.TestCase):
    def test_exclusive_create_preserves_existing_bytes(self):
        path = self.root / "existing.stage"
        self.write_private(path, b"original")
        with self.assertRaises(FileExistsError):
            PRIVATE.open_private_exclusive(path)
        self.assertEqual(path.read_bytes(), b"original")
        PRIVATE.require_private_file(path)

    @unittest.skipIf(os.name == "nt", "POSIX mode contract")
    def test_posix_mode_and_tampering_without_windows_calls(self):
        path = self.root / "posix.stage"
        with mock.patch.object(PRIVATE, "_windows_private_api", side_effect=AssertionError("Windows call")):
            self.write_private(path)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            PRIVATE.require_private_file(path)
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "0600"):
                PRIVATE.require_private_file(path)

    @unittest.skipIf(os.name == "nt", "POSIX link fixture")
    def test_posix_preexisting_symlink_and_hardlink_refused(self):
        target = self.root / "target"
        self.write_private(target)
        link = self.root / "reserved"
        link.symlink_to(target)
        with self.assertRaises(FileExistsError):
            PRIVATE.open_private_exclusive(link)
        with self.assertRaises(ValueError):
            PRIVATE.require_private_file(link)
        link.unlink()
        os.link(target, link)
        with self.assertRaises(ValueError):
            PRIVATE.require_private_file(link)


@unittest.skipUnless(os.name == "nt", "Requires native Windows; a skip is NOT ACL evidence")
class NativeWindowsPrivateFileTests(_PrivateFileFixture, unittest.TestCase):
    def powershell(self, path, program):
        env = dict(os.environ, AIH_PRIVATE_PROBE_PATH=str(path))
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
             "$ErrorActionPreference = 'Stop'; " + program],
            capture_output=True, text=True, check=False, env=env, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout.strip() else None

    def acl(self, path):
        # Independent .NET/PowerShell readback, not the production verifier.
        return self.powershell(path, r"""
        $a = Get-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH
        $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $owner = $a.GetOwner([System.Security.Principal.SecurityIdentifier]).Value
        $rules = @($a.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier]) |
            ForEach-Object { [ordered]@{
                principal = $(if ($_.IdentityReference.Value -eq $sid) { '<CURRENT_USER>' }
                              else { $_.IdentityReference.Value })
                rights = [int]$_.FileSystemRights
                type = $_.AccessControlType.ToString()
                inherited = $_.IsInherited
                inheritance = [int]$_.InheritanceFlags
                propagation = [int]$_.PropagationFlags
            } })
        [ordered]@{ owner_is_current = ($owner -eq $sid)
                    protected = $a.AreAccessRulesProtected
                    rules = $rules } | ConvertTo-Json -Depth 5 -Compress
        """)

    def broad_parent(self):
        self.powershell(self.root, r"""
        $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
        $world = [System.Security.Principal.SecurityIdentifier]::new('S-1-1-0')
        $a = [System.Security.AccessControl.DirectorySecurity]::new()
        $a.SetOwner($sid)
        $a.SetAccessRuleProtection($true, $false)
        $a.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new(
            $sid, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'))
        $a.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new(
            $world, 'ReadAndExecute', 'ContainerInherit,ObjectInherit', 'None', 'Allow'))
        Set-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH -AclObject $a
        """)

    def assert_private_acl(self, path):
        observed = self.acl(path)
        self.assertEqual(observed, {
            "owner_is_current": True, "protected": True,
            "rules": [{"principal": "<CURRENT_USER>", "rights": 0x001F01FF,
                       "type": "Allow", "inherited": False,
                       "inheritance": 0, "propagation": 0}],
        })
        return observed

    def test_broad_parent_independent_acl_and_rename_readback(self):
        self.broad_parent()
        reference = self.root / "ordinary-reference"
        reference.write_bytes(b"synthetic public control")
        self.assertTrue(any(rule["principal"] == "S-1-1-0" and rule["inherited"]
                            for rule in self.acl(reference)["rules"]))
        stage = self.root / ".store.json.h53-stage"
        self.write_private(stage)
        before = self.assert_private_acl(stage)
        PRIVATE.require_private_file(stage)
        target = self.root / "store.json"
        os.replace(stage, target)
        after = self.assert_private_acl(target)
        PRIVATE.require_private_file(target)
        self.assertEqual(target.read_bytes(), b"synthetic private payload\n")
        print("WINDOWS_PRIVATE_ACL_EVIDENCE " + json.dumps({
            "fixture": "synthetic-broad-parent", "stage": before, "target": after,
        }, sort_keys=True))

    def test_explicit_broad_acl_tampering_is_refused_without_repair(self):
        stage = self.root / ".store.json.h53-stage"
        self.write_private(stage)
        self.powershell(stage, r"""
        $a = Get-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH
        $world = [System.Security.Principal.SecurityIdentifier]::new('S-1-1-0')
        $a.AddAccessRule([System.Security.AccessControl.FileSystemAccessRule]::new(
            $world, 'Read', 'Allow'))
        Set-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH -AclObject $a
        """)
        before = self.acl(stage)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            PRIVATE.require_private_file(stage)
        self.assertEqual(self.acl(stage), before)
        self.assertEqual(stage.read_bytes(), b"synthetic private payload\n")

    def test_inheritance_tampering_is_refused(self):
        self.broad_parent()
        stage = self.root / ".store.json.h53-stage"
        self.write_private(stage)
        self.powershell(stage, r"""
        $a = Get-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH
        $a.SetAccessRuleProtection($false, $true)
        Set-Acl -LiteralPath $env:AIH_PRIVATE_PROBE_PATH -AclObject $a
        """)
        with self.assertRaisesRegex(ValueError, "protected"):
            PRIVATE.require_private_file(stage)

    def test_security_readback_failure_precedes_payload_and_closes_handle(self):
        api = PRIVATE._windows_private_api()
        stage = self.root / ".store.json.h53-stage"
        with mock.patch.object(api, "verify_handle", side_effect=OSError("synthetic query failure")):
            with self.assertRaisesRegex(OSError, "synthetic query failure"):
                self.write_private(stage)
        self.assertEqual(stage.read_bytes(), b"")
        PRIVATE.require_private_file(stage)  # No leaked exclusive handle.
        stage.unlink()  # Test fixture only, proving the native handle was closed.

    def test_crt_conversion_failure_leaves_only_empty_private_stage(self):
        api = PRIVATE._windows_private_api()
        stage = self.root / ".store.json.h53-stage"
        with mock.patch.object(api.msvcrt, "open_osfhandle", side_effect=OSError("synthetic conversion failure")):
            with self.assertRaisesRegex(OSError, "synthetic conversion failure"):
                self.write_private(stage)
        self.assertEqual(stage.read_bytes(), b"")
        self.assert_private_acl(stage)
        stage.unlink()

    def test_windows_kernel_accesscheck_has_positive_and_negative_controls(self):
        self.broad_parent()
        reference = self.root / "ordinary-reference"
        reference.write_bytes(b"synthetic public control")
        stage = self.root / ".store.json.h53-stage"
        self.write_private(stage)
        self.assertEqual(accesscheck_read(reference), (True, True))
        self.assertEqual(accesscheck_read(stage), (True, False))


def accesscheck_read(path):
    """Actual queried descriptor + native AccessCheck; no account/host mutations.

    Return (current user may read, Everyone-restricted current token may read).
    This is effective-access evidence, not a separate-human-account login test.
    """
    from ctypes import wintypes as w
    c = ctypes
    advapi = c.WinDLL("advapi32", use_last_error=True)
    kernel = c.WinDLL("kernel32", use_last_error=True)
    P, PP, D = c.c_void_p, c.POINTER(c.c_void_p), w.DWORD

    class SID_AND_ATTRIBUTES(c.Structure):
        _fields_ = [("sid", P), ("attributes", D)]

    class GENERIC_MAPPING(c.Structure):
        _fields_ = [("read", D), ("write", D), ("execute", D), ("all", D)]

    def bind(dll, name, result, arguments):
        f = getattr(dll, name)
        f.restype, f.argtypes = result, arguments
        return f

    get_sd = bind(advapi, "GetNamedSecurityInfoW", D,
                  [w.LPWSTR, c.c_int, D, PP, PP, PP, PP, PP])
    process = bind(kernel, "GetCurrentProcess", w.HANDLE, [])
    open_token = bind(advapi, "OpenProcessToken", w.BOOL, [w.HANDLE, D, PP])
    duplicate = bind(advapi, "DuplicateToken", w.BOOL, [w.HANDLE, c.c_int, PP])
    restrict = bind(advapi, "CreateRestrictedToken", w.BOOL,
                    [w.HANDLE, D, D, P, D, P, D, P, PP])
    make_sid = bind(advapi, "ConvertStringSidToSidW", w.BOOL, [w.LPCWSTR, PP])
    access = bind(advapi, "AccessCheck", w.BOOL,
                  [P, w.HANDLE, D, c.POINTER(GENERIC_MAPPING), P,
                   c.POINTER(D), c.POINTER(D), c.POINTER(w.BOOL)])
    free = bind(kernel, "LocalFree", P, [P])
    close = bind(kernel, "CloseHandle", w.BOOL, [w.HANDLE])

    def check(result):
        if not result:
            raise c.WinError(c.get_last_error())

    descriptor, world = P(), P()
    token, impersonation, restricted = P(), P(), P()
    try:
        # OWNER | GROUP | DACL: AccessCheck requires owner and group in the descriptor.
        error = get_sd(str(path), 1, 7, None, None, None, None, c.byref(descriptor))
        if error:
            raise c.WinError(error)
        check(open_token(process(), 0x000A, c.byref(token)))  # QUERY | DUPLICATE
        check(duplicate(token, 2, c.byref(impersonation)))
        check(make_sid("S-1-1-0", c.byref(world)))
        restriction = SID_AND_ATTRIBUTES(world, 0)
        check(restrict(impersonation, 1, 0, None, 0, None, 1,
                       c.byref(restriction), c.byref(restricted)))
        mapping = GENERIC_MAPPING(0x120089, 0x120116, 0x1200A0, 0x1F01FF)
        results = []
        for candidate in (impersonation, restricted):
            privileges = c.create_string_buffer(4096)
            length, granted, allowed = D(c.sizeof(privileges)), D(), w.BOOL()
            check(access(descriptor, candidate, 0x0001, c.byref(mapping), privileges,
                         c.byref(length), c.byref(granted), c.byref(allowed)))
            results.append(bool(allowed.value))  # FILE_READ_DATA, not API success.
        return tuple(results)
    finally:
        for handle in (restricted, impersonation, token):
            if handle.value:
                close(handle)
        if world.value:
            free(world)
        if descriptor.value:
            free(descriptor)


if __name__ == "__main__":
    unittest.main(verbosity=2)
