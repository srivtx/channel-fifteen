# 12 · Glossary and credits

## Glossary

| Term | Meaning |
|---|---|
| **A2DP** | Advanced Audio Distribution Profile: stereo music over Bluetooth Classic. |
| **ACK** | Acknowledgement: a message saying "I got yours". |
| **ACL** | Asynchronous connection-less link: Bluetooth Classic's data link. |
| **ADC / DAC** | Analogue-to-digital / digital-to-analogue converter. |
| **AFH** | Adaptive frequency hopping: dropping bad channels from the hop list. |
| **ANC** | Active noise cancelling. |
| **AVRCP** | Remote-control profile: play, pause, volume. |
| **BD_ADDR** | A Bluetooth device's 48-bit address. |
| **Big- / little-endian** | Most- / least-significant byte first. |
| **Bit mask** | A byte whose individual bits carry separate meanings. |
| **BLE** | Bluetooth Low Energy. |
| **Byte stuffing** | Escaping marker bytes that appear inside a frame's body. |
| **Capabilities** | Earshot's description of what a model can do. |
| **Central / peripheral** | The device that runs a piconet's clock, and the ones that follow it. |
| **CID** | L2CAP channel identifier. |
| **Codec** | Audio compressor and decompressor: SBC, AAC, LDAC, LHDC. |
| **CRC** | Cyclic redundancy check: the remainder of a polynomial division, used to detect errors. |
| **DLCI** | RFCOMM's channel address inside a session. |
| **Driver** | In Earshot, one brand family's protocol implementation. |
| **DSP** | Digital signal processor: the maths engine for audio. |
| **EDR** | Enhanced Data Rate: Bluetooth's 2–3 Mbit/s modes. |
| **Event** | In Earshot, a brand-neutral fact reported by a driver. |
| **FCS** | Frame check sequence: a frame's checksum. |
| **Firmware** | The software running inside the buds. |
| **Flash** | Memory that keeps its contents without power; where settings live. |
| **Frame** | One complete message on the wire, with its markers and lengths. |
| **GATT** | BLE's attribute protocol, the alternative to RFCOMM on many newer devices. |
| **GFSK** | Gaussian frequency-shift keying, Bluetooth's basic modulation. |
| **Hall sensor** | A chip that senses a magnetic field: lid open or closed. |
| **HCI** | Host Controller Interface, between the OS and the Bluetooth chip. |
| **Hex** | Base 16; two digits per byte. |
| **HFP** | Hands-Free Profile, for calls. |
| **Intent** | In Earshot, a brand-neutral request like "set ANC deep". |
| **IOBluetooth** | Apple's Bluetooth Classic framework for macOS. |
| **ISM band** | Licence-free radio spectrum, including 2.4 GHz. |
| **L2CAP** | Logical channels and segmentation over an ACL link. |
| **LEB128** | Variable-length integer encoding, 7 bits per byte. |
| **LMP** | Link Manager Protocol, between two Bluetooth chips. |
| **Multipoint** | Connected to two devices at once ("dual device"). |
| **Nyquist** | Sample at more than twice the highest frequency you want to keep. |
| **OPO** | Our name for the realme / OPPO / OnePlus control protocol. |
| **Optimistic UI** | Showing a change before it's confirmed, rolling back on failure. |
| **Payload** | The part of a message that carries the content, after the headers. |
| **Piconet** | One central and up to seven active peripherals. |
| **PMIC** | Power-management IC. |
| **Pogo pins** | Spring-loaded contacts for charging. |
| **Profile** | A standard use of the stack (A2DP, HFP…); in Earshot, also a brand's matching rules. |
| **Push** | A message the device sends without being asked. |
| **RFCOMM** | Serial-port emulation over L2CAP; up to 30 channels. |
| **SDP** | Service Discovery Protocol: a device's table of contents. |
| **Seq** | Sequence number. |
| **SoC** | System-on-chip: radio, CPU, DSP and memory on one die. |
| **SPP** | Serial Port Profile. |
| **Supersede key** | Earshot's "which setting" key, so only the newest request per setting is sent. |
| **TCC** | macOS privacy permissions (Transparency, Consent and Control). |
| **TWS** | True wireless stereo: two independent buds. |
| **UUID** | A 128-bit identifier; Bluetooth's short 16-bit ones expand from a base UUID. |
| **Whitening** | Scrambling bits before transmission to avoid long runs. |

## Where to go next

- **Read Earshot's code:** start at `Sources/EarshotCore/Driver.swift`, then `OPO/OPODriver.swift`, then `Sources/Earshot/BudsLink.swift`.
- **Run the tests:** `./scripts/test.sh`.
- **Own beta buds?** Settings → Report → Save, then open a *Buds report* issue on github.com/srivtx/earshot.
- **Rebuild this manual's artwork:**
  - `tools/earbud_blender.py` and `tools/parts_blender.py` (in Blender);
  - `python3 tools/build_figures.py`.

## Credits

![Thank you](../figures/43-back-cover.svg)

- **Gadgetbridge:** the open Android project whose protocol work made the OPO, Sony, Nothing and soundcore drivers possible.
- **GalaxyBudsClient:** Samsung's message layouts and captured status frames.
- **The OnePlus Buds write-up** by Aasheesh: proof that the OPO family could be spoken to from a computer.
- **The realme Buds Air 7,** which patiently answered every question.

Earshot and this manual were made by srivtx with Claude.
