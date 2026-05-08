# some important notes to point out:   

- [fixed] only udp and arp packets are being captured and displayed, other protocol packets arent (tcp, icmp, http/s maybe?, dns)/ improper capturing #critical/ most important issue to fix
  
possible causes (may be correct and may be not, just some guesses):

### first, a file named "packet_capturer_Version2.py" that works correctly and captures all packets, including tcp, udp, arp, icmp, etc. was created as a separate script to test the packet capturing logic and ensure that it is working properly. This file uses a simple sniff approach without any complex filtering or interface mapping, which may be why it captures all packets correctly.
### use this file as a reference to compare with the capture logic in "templates/app.py" and identify any differences or issues that may be causing the problem with missing packets. as for the possible causes its as follows:

* using elif (?) instead of if statements in the packet processing code, which may cause some packets to be skipped if they match multiple conditions (e.g. a packet that is both UDP and ARP may only be processed as UDP and not ARP, or vice versa)
* the packet filtering logic may be incorrect or too restrictive, maybe it did capture some tcp packets but filtered as udp or arp, or maybe it is only capturing packets that are strictly udp or arp and missing packets that have other protocols encapsulated within them (e.g. tcp packets that are encapsulated within udp packets)
* the code in packet proccessing could be correct but there may be an issue with how the packets are being captured or read from the network interface, which could result in some packets being missed or not processed correctly (e.g. if the capture library is not configured to capture all packets or if there is an issue with the network interface itself)
* the interface could be the issue, (lines 321-377): The get_scapy_interface_for_name() function maps "Wi-Fi" → Scapy's NPF device identifier, but may resolve to the wrong interface
* sniff parameters?, (lines 640-647): Uses stop_filter=lambda x: not is_capturing without a count - could prevent packets from being delivered properly
* environmental routing/firewall issue? if the computer running the capture has some routing or firewall rules that are preventing certain types of packets from being captured or processed correctly, this could also result in missing packets in the stats. #unlikely since packet_capturer_Version2.py isnt effected, but still worth checking if other solutions dont work.
* if so, would wireshark show the same issue? if wireshark also shows missing packets, then it is likely an environmental issue with the network configuration or firewall rules. if wireshark captures all packets correctly, then it is more likely an issue with the code in templates/app.py that needs to be addressed. (but wireshark does work correctly, so it is more likely an issue with the code in templates/app.py that needs to be addressed) #important step for troubleshooting and identifying the root cause of the issue with missing packets.
* since packet_capturer_Version2.py and wireshark botth capture all packets correctly. copilot analysis could be wrong with the issue being environmental/ firewall related since both app.py and packet_capturer_Version2.py both using scapy on the same wi-fi interface, it caught a key difference is that version2 accepts a filter paramter (which the note says works with filter="ip") while app.py has no filter and in concluded that the issues is likely as follows:
    * windows npacp requiers explixit BPF filters to reliably deliver certain packet types
    * version2 works because it can accept filer="ip" from the command line
    * app.py fails because its not using the proper filter
* after copilot tested with multiple approuches (changing timeouts, filters, sniff parameters) the application is consistanly captures arp but never captures tcp/icmp/dns from the test traffic and it indicated that:
    * sniff () is working correctly - arp packets proven consistantly captured
    * interface mapping is correct - captures from the right interface
    * protocol detecton logic is correct - verifired in the previous analysis
* what copilot also summarized is that the packet capture application is funcionally working but with a specific limitation, but what it said what works as follows:
    * flask API endpoints functioning correctly
    * interface detection and mapping working correctly
    * arp packet capture consistant
    * protocol detection logic verfied correct for all types
    * threading & daemon architecture operational
    * network adapter responding to ARP requests
* npcap is the issue? if npcap has some limitations it is possible that npcap itself is the issue
* more than one sniff call sites? there may have more than one sniff(), and the one actually running does NOT use the filter. #important note for troubleshooting and finding a solution for the issue with missing packets on windows.
  
* important note for this issue:-
the platform can work perfectly fine on linux, and it can normally capture tcp, icmp and http/s, meaning its very much likely the BPF filter that needs proper configuring (this took some time to discover because the platform wasnt tested on linux untill later on)
    * even after configuring the BPF filter, it still resists capturing tcp, icmp and http/s packets, which may indicate that there is an issue with how the filter is being applied or with the capture library itself on windows (e.g. npcap) and it may require further investigation or testing to determine the root cause of the issue and find a solution for it. #important note for troubleshooting and finding a solution for the issue with missing packets on windows.
    * while it still works perfectly fine on linux because it uses libpcap which handles the BPF filters in its own way and may not have the same limitations as npcap on windows, which is why it is able to capture all packets correctly without needing any special configuration for the BPF filters. #important note for troubleshooting and finding a solution for the issue with missing packets on windows.
    * so that may lead to the conclusion that app.py has the filter but still fails, and this strongly suggests that the fliter is either overridden, conditionally empty, or passed incorrectly (eg. none, wrong variable, wrong scope). theres a chance that all of the three are correct #important note for troubleshooting and finding a solution for the issue with missing packets on windows.
    * this strongly suggests that it is a Windows-specific Npcap behavior: without a BPF filter string, Npcap's driver may silently drop IP-layer unicast traffic when in certain capture modes, while ARP (being a broadcast/layer-2 protocol) slips through anyway. This would explain why ARP packets are captured but TCP/ICMP/DNS are not, and why the issue does not occur on Linux with libpcap. #important note for troubleshooting and finding a solution for the issue with missing packets on windows.

* BPF filter:-
    * originaly there was no filter and the platform captured only arp and udp
    * applying the filter as "ip or arp" or "only ip" resulted in the same way as not having the filter in the beginning
    * having the filter bracket empty resaulted with only arp being captured
    * having the fliter as "None" reasulted in this error message:- ```[DEBUG] Sniff iteration exception: Cannot set filter: can't parse filter expression: syntax error``` becasue "None" was being converted to the string "None" and passed to the BPF parser
    * applying it as None (without quotes) resulted in no packets being captured at all

some possible solutions? (could not be correct, just some guesses):
* Align templates/app.py's capture logic with packet_capturer_Version2.py:
    * Use the same simple sniff approach without stop_filter
    * Or use direct Scapy interface names instead of friendly name mapping
* copilot concluded that the solution isnt to debug network routing, but to add a configurable BPF filter parameter to app.py and use filter="ip or arp" to capture all protocol types just like version2 does
* if npcap is the issue would installing winpcap and make the project work with it instead solve it?
* is it possible to configure npcap' BPF filter to match how lipcap handles it on linux, or is it a fundamental limitation of npcap on windows that cannot be overcome with configuration? #important question for finding a solution for the issue with missing packets on windows.
* or maybe configure npcap to match how it works for version2, since version2 works correctly on windows, it may be possible to configure npcap in a similar way to how it is configured for version2 to achieve the same results and capture all packets correctly. #important question for finding a solution for the issue with missing packets on windows.
* more accurately, the filter is probably not applied properly at the capture level where npcap expects it, and the filter string is not actually reaching sniff() the same way as version2, which is why it is not capturing all packets correctly. #important note for troubleshooting and finding a solution for the issue with missing packets on windows.
- [fixed] protocols arent correctly classified. after fixing the capture issue, it was found out that the protocol classification logic was also flawed and needed to be fixed to correctly classify packets based on their actual protocol types rather than just relying on the presence of certain layers or fields in the packet structure. #critical/ important issue to fix after the capture issue is resolved, since even if all packets are captured correctly, if they are not classified correctly then the stats and information displayed to the user will be inaccurate and misleading, which can affect the overall user experience and the usefulness of the platform for analyzing network traffic.
- [fixed] once going to the broswer after starting app.py, this message is contuined to be printed in the powershell: 
    ```INFO:werkzeug:127.0.0.1 - - [22/Apr/2026 17:53:59] "GET /api/stats HTTP/1.1" 200 -``` which can be annoying, but it is just the flask server logging the request to the /api/stats endpoint, which is expected behavior when the browser makes a request to that endpoint to fetch the stats data. (can it be disabled? maybe, but it is not a critical issue and can be ignored for now) #ingnorable/ minor issue

### in line 34, right after the logging configuration, these were the lines that were added to disable the werkzeug logging, and heres how it works:
* logging.getLogger('werkzeug') gets the werkzeug logger (flask' internal HTTP request logger)
* .setLevel(logging.WARNING) sets the logging level to WARNING, which means:
    * info level messages are suppressed (these are the HTTP request logs)
    * warning level messages are shown (only critical issues)
    * error level messages are shown (error details)
and by chaning the logging level to WARNING, we're essentially saying: "Only show me werkzeug messages if they're warnings or errors, not informational messages. This keeps the console clean while still showing important error information if something goes wrong with Flask.

- [fixed] it can be easy to mix up which URL to use when accessing the web interface, and it is needed to update "how_to_run.md" to make it more clear when to use each URL #medium issue/ not so critical but can cause confusion for users, so it should be clarified in the instructions.
- [fixed] the "how_to_run.md" file should also be updated to include instructions on how to access the web interface from another computer on the same network, as well as troubleshooting tips for common issues that may arise when trying to access the web interface. #not too minor issue/ can be easily fixed by adding a section in the instructions for troubleshooting and accessing from other devices, which can improve the user experience and make it easier for users to get started with the project.
- [fixed] local host IP addresses change depending on the computer (?) if published and used by other users/ other computers, if so, it should be noted in the instructions that the user should check the output of the Flask server to see which URL to use when accessing the web interface, as it may differ based on the network configuration of the computer running the server. #medium issue/ not so critical but can cause confusion for users, so it should be clarified in the instructions. 

# complete summary of the issue:-
the platform was only capturing arp and udp packets on windows, missing other protocols like tcp, icmp, dns, etc. meanwhile packet_capturer_Version2.py captured all packets correctly using the same scapy library on the same network interface

### but none of the above solutions worked, but later on it was discovered that the core issue was in the BPF filter configuration for npcap on windows. and below is why none of them was the acutal cause:-

- **first cause**, the code used elif instead of if, which might skip packets matching multiple conditions
    * arp packets dont have an ip layer, wich is why it was processed correctly
    * protocol detection logic was logically sound, a packet cant have both aro and tcp simultaneously
    * it was then verified that the logic was correct examining acutal packet structure
- **second cause**, get_scapy_interface_for_name() was maping "Wi-Fi" to the wrong scapy interface identifier (the NPF deivce GUID)
    * after some debugging the mapping logic, it was verified to be correct
    * when testing version2 with explicit interface name, it also struggled
    * but when version2 used iface=None (default), it worked perfectly
    * this indicated the problem wasnt which interface was selected, but HOW it was being used
- **third cause**, timeout=5 or stop_filter=lambda x: not is_capturing parameters were preventing packets from being delivered properly
    * after testing with different combinations (changing timeout value, modifying the sniff loop structire, adjusting threading behavior) this wasnt in issue at all
    * if the issue was with the sniff parameters, all packets would be missing, but arp was being captured
    * the timeout mechanism was necessary to allow stopping the capture when is_capturing = False
- **fourth cause**, environmental routing/firewall rules were preventing certain packets from being captured
    * wireshark was capturing all packets correctly as well as version2, which indicated the issue was not with the network configuration or firewall rules
    * if it was an environmental issue, both of them would fail
- **fifth cause**, even when the correct interface was being selected, maybe the actual capture was happening on a different interface
    * after adding extensive debug output to track which interface was being used, it was verified that this wasnt an issue either
    * the debug logs showed the correct interface was being passed
    * even if the wrong interface was being used, no packets would arrive at all since arp was alerady being captured
- **sixth cause**, bpf_filter variable might be empty, none, or malformed
    * as the notes mentioned the different testing of the filter parameter, none of them worked as expected
    * empty string and valid BPF filters both resulted in arp-only capture
    * this was confusing because the filter string itself wasnt the problem
    * but it suggested that something deeper about HOW the filter was being passed to scapy

## the actual root cause was windows/ npcap BPF driver behavior:-
when investigating why even correct BPF filters wasnt helping, it was found out that it is a windows-soecific npcap driver limitation since it was working fine on linux
- when filter is being passed as an empty string '', npcap applies a default or internal filter that silently drops IP-layer unicast traffic
- arp packets slipped through because they are broadcast/ layer-2 protocol, which is different from linux libpcap

## but why the fix was counterintuitive:-
the solution wasnt to specifiy a better filter, but not to pass the filter parameter at all. when the filter parameter is completely onmitted from the sniff() call:
- scapy/ npcap doesnt apply any BPF filter whatsoever
- npcap captures all packets at the driver level without filtering
- all protocol packets arrive at the fallback function
- the packets are then correctly classified by the application layer

## secondary fix: interface selection:-
once the filter issue was resolved, it was then discovered that the manual interface mapping was also problomatic
- this mattered because scapy' auto-selection iface=None is more reliable on windows
- it automatically picks the most appropriate active interface
- manual mapping added unnecessary complexity and potential failure points
- combined with the filter fix, this ensured packets were captured from the right interface

### TL;DR, it was a two-part solution, first part was to fix conditional filter parameter, second part was fixing auto-selected interface

## final notes, why this finally worked:-
- no default filter applied - npcap captures everything
- scapy auto-selection - most reliable interface detection on windows
- conditional filter passing - users can apply filters if needed, but its not forced
- protocol detection logic - now receives all packet types and correctly classifies them

# as for the second major issue:-
protocols arent properly calssified, while the capturing itself works fine (verified by the saved pcap files and wireshark analysis) for example tcp was being classified as http/s, and so on. leter on some testing was made to verify the protocol classification:- 

### linux:-
**test 1** in the browser it did caught 2 tcp packets, but the saved pcap file in wireshark showed 59, the browser caught 94 udp but the pcap showed 100, browser caught 8 dns just as the pcap, browser caught 0 icmp just as the pcap, browser caught 24 arp just as the pcap, browser caught 57 http but the pcap showed none

**test 2** browser caught 2 tcp but in the pcap it showed 75, browser caught 95 udp but the pcap showed 108, browser caught 16 dns just as the pcap, browser caught 0 icmp just as the pcap, browser caught 17 aro but the pcap showed 16, browser caught 73 http but hte pcap showed only 2

**test 3** browser caught 2 tcp but pcap showed 48, browser caught 104 udp but pcap showed 116, browser caught 10 dns just as the pcap, browser caught 16 icmp just as the pcap, browser caught 28 but pcap showed 25, browser caught 53 http but pcap showed 2
### since macOS uses the same logic as linux, i'd assume the result would be the same as linux

### windows:-
**test 1** browser caught 2 tcp but pcap showed 182, browser caught 147 udp but pcap showed 148, browser caught 3 dns just as the pcap, browser caught 0 icmp just as the pcap, browser caught 20 arp but pcap showed 19, browser caught 187 http but pcap showed 0

**test 2** browser caught 2 tcp but pcap showed 699, browser caught 48 udp but pcap showed 59, browser caught 0 dns just as the pcap, browser caught 0 icmp just as the pcap, browser caught 18 arp just as the pcap, browser caught 697 http but browser showed 0

**test 3** browser caught 0 tcp but pcap showed 181, browser caught 51 but pcap showed 62, browser caught 11 dns just as the pcap, browser caught 16 icmp just as the pcap, browser caught 16 arp but pcap hsowed 14, browser caught 184 http but pcap showed 0

## in conclusion:- since testing on both linux and windows, it isnt a platform specific issue just as the capturing issue on windows. all packets are correctly captured but not displayed correctly (e.g tcp is displayed as http since http is barely present in the pcap and not tcp) 

- this is becasue the function process_packet() classifies based only on the port numbers, and since tcp and http/s uses the same port number (80/443) without verifying the actual packets payload, the tcp packets gets classified as http/s
- same logic applies to udp and dns, since both ports uses port 53, all dns packets gets classified as udp
- the solution was to implement a more robust protocol classification logic that examines the actual packet payload and structure rather than just relying on port numbers, this can be done by checking for specific protocol signatures in the packet payload or by using more advanced packet parsing techniques to accurately identify the protocol type. 
