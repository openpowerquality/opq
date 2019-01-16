import ctypes
import fcntl
import socket
import struct
import time
import libnl.handlers
from libnl.attr import nla_parse, nla_parse_nested, nla_put, nla_put_nested, nla_put_u32
from libnl.genl.ctrl import genl_ctrl_resolve, genl_ctrl_resolve_grp
from libnl.genl.genl import genl_connect, genlmsg_attrdata, genlmsg_attrlen, genlmsg_put
from libnl.linux_private.genetlink import genlmsghdr
from libnl.linux_private.netlink import NLM_F_DUMP
from libnl.msg import nlmsg_alloc, nlmsg_data, nlmsg_hdr
from libnl.nl import nl_recvmsgs, nl_send_auto
from libnl.nl80211 import nl80211
from libnl.nl80211.helpers import parse_bss
from libnl.nl80211.iw_scan import bss_policy
from libnl.socket_ import nl_socket_add_membership, nl_socket_alloc, nl_socket_drop_membership


def do_scan_trigger(sk, if_index, driver_id, mcid):
    """Issue a scan request to the kernel and wait for it to reply with a signal.

    This function issues NL80211_CMD_TRIGGER_SCAN which requires root privileges.

    The way NL80211 works is first you issue NL80211_CMD_TRIGGER_SCAN and wait for the kernel to signal that the scan is
    done. When that signal occurs, data is not yet available. The signal tells us if the scan was aborted or if it was
    successful (if new scan results are waiting). This function handles that simple signal.

    May exit the program (sys.exit()) if a fatal error occurs.

    Positional arguments:
    sk -- nl_sock class instance (from nl_socket_alloc()).
    if_index -- interface index (integer).
    driver_id -- nl80211 driver ID from genl_ctrl_resolve() (integer).
    mcid -- nl80211 scanning group ID from genl_ctrl_resolve_grp() (integer).

    Returns:
    0 on success or a negative error code.
    """
    # First get the "scan" membership group ID and join the socket to the group.
    ret = nl_socket_add_membership(sk, mcid)  # Listen for results of scan requests (aborted or new results).
    if ret < 0:
        return ret

    # Build the message to be sent to the kernel.
    msg = nlmsg_alloc()
    genlmsg_put(msg, 0, 0, driver_id, 0, 0, nl80211.NL80211_CMD_TRIGGER_SCAN, 0)  # Setup which command to run.
    nla_put_u32(msg, nl80211.NL80211_ATTR_IFINDEX, if_index)  # Setup which interface to use.
    ssids_to_scan = nlmsg_alloc()
    nla_put(ssids_to_scan, 1, 0, b'')  # Scan all SSIDs.
    nla_put_nested(msg, nl80211.NL80211_ATTR_SCAN_SSIDS, ssids_to_scan)  # Setup what kind of scan to perform.

    # Setup the callbacks to be used for triggering the scan only.
    err = ctypes.c_int(1)  # Used as a mutable integer to be updated by the callback function. Signals end of messages.
    results = ctypes.c_int(-1)  # Signals if the scan was successful (new results) or aborted, or not started.
    cb = libnl.handlers.nl_cb_alloc(libnl.handlers.NL_CB_DEFAULT)
    libnl.handlers.nl_cb_set(cb, libnl.handlers.NL_CB_VALID, libnl.handlers.NL_CB_CUSTOM, callback_trigger, results)
    libnl.handlers.nl_cb_err(cb, libnl.handlers.NL_CB_CUSTOM, error_handler, err)
    libnl.handlers.nl_cb_set(cb, libnl.handlers.NL_CB_ACK, libnl.handlers.NL_CB_CUSTOM, ack_handler, err)
    libnl.handlers.nl_cb_set(cb, libnl.handlers.NL_CB_SEQ_CHECK, libnl.handlers.NL_CB_CUSTOM,
                             lambda *_: libnl.handlers.NL_OK, None)  # Ignore sequence checking.

    # Now we send the message to the kernel, and retrieve the acknowledgement. The kernel takes a few seconds to finish
    # scanning for access points.
    ret = nl_send_auto(sk, msg)
    if ret < 0:
        return ret
    while err.value > 0:
        ret = nl_recvmsgs(sk, cb)
        if ret < 0:
            return ret
    if err.value < 0:
        raise RuntimeError("Unknown Error")

    # Block until the kernel is done scanning or aborted the scan.
    while results.value < 0:
        ret = nl_recvmsgs(sk, cb)
        if ret < 0:
            return ret
    if results.value > 0:
        raise RuntimeError('The kernel aborted the scan.')

    # Done, cleaning up.
    return nl_socket_drop_membership(sk, mcid)  # No longer need to receive multicast messages.


def error_handler(_, err, arg):
    """Update the mutable integer `arg` with the error code."""
    arg.value = err.error
    return libnl.handlers.NL_STOP


def ack_handler(_, arg):
    """Update the mutable integer `arg` with 0 as an acknowledgement."""
    arg.value = 0
    return libnl.handlers.NL_STOP

def callback_trigger(msg, arg):
    """Called when the kernel is done scanning. Only signals if it was successful or if it failed. No other data.

    Positional arguments:
    msg -- nl_msg class instance containing the data sent by the kernel.
    arg -- mutable integer (ctypes.c_int()) to update with results.

    Returns:
    An integer, value of NL_SKIP. It tells libnl to stop calling other callbacks for this message and proceed with
    processing the next kernel message.
    """
    gnlh = genlmsghdr(nlmsg_data(nlmsg_hdr(msg)))
    if gnlh.cmd == nl80211.NL80211_CMD_SCAN_ABORTED:
        arg.value = 1  # The scan was aborted for some reason.
    elif gnlh.cmd == nl80211.NL80211_CMD_NEW_SCAN_RESULTS:
        arg.value = 0  # The scan completed successfully. `callback_dump` will collect the results later.
    return libnl.handlers.NL_SKIP

def callback_dump(msg, results):
    """Here is where SSIDs and their data is decoded from the binary data sent by the kernel.

    This function is called once per SSID. Everything in `msg` pertains to just one SSID.

    Positional arguments:
    msg -- nl_msg class instance containing the data sent by the kernel.
    results -- dictionary to populate with parsed data.
    """
    bss = dict()  # To be filled by nla_parse_nested().

    # First we must parse incoming data into manageable chunks and check for errors.
    gnlh = genlmsghdr(nlmsg_data(nlmsg_hdr(msg)))
    tb = dict((i, None) for i in range(nl80211.NL80211_ATTR_MAX + 1))
    nla_parse(tb, nl80211.NL80211_ATTR_MAX, genlmsg_attrdata(gnlh, 0), genlmsg_attrlen(gnlh, 0), None)
    if not tb[nl80211.NL80211_ATTR_BSS]:
        print('WARNING: BSS info missing for an access point.')
        return libnl.handlers.NL_SKIP
    if nla_parse_nested(bss, nl80211.NL80211_BSS_MAX, tb[nl80211.NL80211_ATTR_BSS], bss_policy):
        print('WARNING: Failed to parse nested attributes for an access point!')
        return libnl.handlers.NL_SKIP
    if not bss[nl80211.NL80211_BSS_BSSID]:
        print('WARNING: No BSSID detected for an access point!')
        return libnl.handlers.NL_SKIP
    if not bss[nl80211.NL80211_BSS_INFORMATION_ELEMENTS]:
        print('WARNING: No additional information available for an access point!')
        return libnl.handlers.NL_SKIP

    # Further parse and then store. Overwrite existing data for BSSID if scan is run multiple times.
    bss_parsed = parse_bss(bss)
    results[bss_parsed['bssid']] = bss_parsed
    return libnl.handlers.NL_SKIP



def do_scan_results(sk, if_index, driver_id, results):
    """Retrieve the results of a successful scan (SSIDs and data about them).

    This function does not require root privileges. It eventually calls a callback that actually decodes data about
    SSIDs but this function kicks that off.

    May exit the program (sys.exit()) if a fatal error occurs.

    Positional arguments:
    sk -- nl_sock class instance (from nl_socket_alloc()).
    if_index -- interface index (integer).
    driver_id -- nl80211 driver ID from genl_ctrl_resolve() (integer).
    results -- dictionary to populate with results. Keys are BSSIDs (MAC addresses) and values are dicts of data.

    Returns:
    0 on success or a negative error code.
    """
    msg = nlmsg_alloc()
    genlmsg_put(msg, 0, 0, driver_id, 0, NLM_F_DUMP, nl80211.NL80211_CMD_GET_SCAN, 0)
    nla_put_u32(msg, nl80211.NL80211_ATTR_IFINDEX, if_index)
    cb = libnl.handlers.nl_cb_alloc(libnl.handlers.NL_CB_DEFAULT)
    libnl.handlers.nl_cb_set(cb, libnl.handlers.NL_CB_VALID, libnl.handlers.NL_CB_CUSTOM, callback_dump, results)
    ret = nl_send_auto(sk, msg)
    if ret >= 0:
        try:
            ret = nl_recvmsgs(sk, cb)
        except NotImplementedError:
            pass
    return ret


def scan_for_wifi_networks(interface):
    def db_to_percent(db):
        return 2.0 * (db + 100)

    pack = struct.pack('16sI', interface, 0)
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        info = struct.unpack('16sI', fcntl.ioctl(sk.fileno(), 0x8933, pack))
    except OSError:
        raise RuntimeError('Wireless interface {0} does not exist.'.format(interface))
    finally:
        sk.close()
    if_index = int(info[1])

    # Next open a socket to the kernel and bind to it. Same one used for sending and receiving.
    sk = nl_socket_alloc()  # Creates an `nl_sock` instance.
    if not genl_connect(sk) == 0: # Create file descriptor and bind socket.
        raise RuntimeError('Could not communicate with kernel via nl80211')
    driver_id = genl_ctrl_resolve( sk, b'nl80211')
    mcid = genl_ctrl_resolve_grp(sk, b'nl80211', b'scan')

    results = dict()
    for i in range(2, -1, -1):  # Three tries on errors.
        ret = do_scan_trigger(sk, if_index, driver_id, mcid)
        if ret < 0:
            #timeout
            time.sleep(5)
            continue
        ret = do_scan_results( sk, if_index, driver_id, results)
        if ret < 0:
            time.sleep(5)
            continue
        break
    if not results:
        return {}

    ap_list = []
    for _, f in results.items():
        ssid = str(f['information_elements']['SSID']).encode("ascii", "ignore")
        if len(ssid) == 0:
            continue
        if u"\x00".encode("ascii", "ignore") in ssid:
            continue
        print (ssid, len(ssid))
        # pp.pprint(f['information_elements'])
        security = 0
        if 'RSN' in f['information_elements']:
            security = 1
        signal_strength = db_to_percent(f['signal'])
        if signal_strength <= 25:
            continue
        network_tuple = [ssid, security, signal_strength]
        ap_list.append(network_tuple)
    return ap_list


if __name__=='__main__':
    result = scan_for_wifi_networks("wlp2s0")
    print(result)
