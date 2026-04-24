## some important notes to point out:   

- only udp and arp packets are being captured and displayed, other protocol packets arent (tcp, icmp, http/s maybe?, dns)/ improper capturing #critical/ most important issue to fix
possible causes (may be correct and may be not, just some guesses):
** first, a file named "packet_capturer_Version2.py" that works correctly and captures all packets, including tcp, udp, arp, icmp, etc. was created as a separate script to test the packet capturing logic and ensure that it is working properly. This file uses a simple sniff approach without any complex filtering or interface mapping, which may be why it captures all packets correctly.
** use this file as a reference to compare with the capture logic in "templates/app.py" and identify any differences or issues that may be causing the problem with missing packets. as for the possible causes its as follows:
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

some possible solutions? (could not be correct, just some guesses):
* Align templates/app.py's capture logic with packet_capturer_Version2.py:
    * Use the same simple sniff approach without stop_filter
    * Or use direct Scapy interface names instead of friendly name mapping
* copilot concluded that the solution isnt to debug network routing, but to add a configurable BPF filter parameter to app.py and use filter="ip or arp" to capture all protocol types just like version2 does
* if npcap is the issue would installing winpcap and make the project work with it instead solve it?
- once going to the broswer after starting app.py, this message is contuined to be printed in the powershell: 
    ```INFO:werkzeug:127.0.0.1 - - [22/Apr/2026 17:53:59] "GET /api/stats HTTP/1.1" 200 -``` which can be annoying, but it is just the flask server logging the request to the /api/stats endpoint, which is expected behavior when the browser makes a request to that endpoint to fetch the stats data. (can it be disabled? maybe, but it is not a critical issue and can be ignored for now) #ingnorable/ minor issue
- it can be easy to mix up which URL to use when accessing the web interface, and it is needed to update "how_to_run.md" to make it more clear when to use each URL #medium issue/ not so critical but can cause confusion for users, so it should be clarified in the instructions.
- the "how_to_run.md" file should also be updated to include instructions on how to access the web interface from another computer on the same network, as well as troubleshooting tips for common issues that may arise when trying to access the web interface. #not too minor issue/ can be easily fixed by adding a section in the instructions for troubleshooting and accessing from other devices, which can improve the user experience and make it easier for users to get started with the project.
- local host IP addresses change depending on the computer (?) if published and used by other users/ other computers, if so, it should be noted in the instructions that the user should check the output of the Flask server to see which URL to use when accessing the web interface, as it may differ based on the network configuration of the computer running the server. #medium issue/ not so critical but can cause confusion for users, so it should be clarified in the instructions.
