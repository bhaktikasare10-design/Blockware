// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// =====================================================
//  BlockWare — FirmwareRegistry.sol
//  Team     : Circuit Wizards — VESIT TE D14B 2025-26
//  Mentor   : Mrs. Arti Sawant
//  Tool     : Remix IDE Desktop
//  Network  : Ganache (HTTP://127.0.0.1:7545)
// =====================================================
//  DEPLOY STEPS:
//  1. Open Remix IDE Desktop
//  2. Paste this code in new file FirmwareRegistry.sol
//  3. Compile (Solidity 0.8.19+)
//  4. Open Ganache → Quickstart
//  5. Deploy tab → Custom External Http Provider
//     → http://127.0.0.1:7545 → OK
//  6. UNCHECK "Verify Contract on Explorers"
//  7. Click Deploy
//  8. Copy CONTRACT ADDRESS from bottom
//     Paste in broker.py and gateway main.py
// =====================================================

contract FirmwareRegistry {

    struct FirmwareRecord {
        string  version;
        string  firmwareHash;
        string  downloadURL;
        string  deviceType;
        string  signature;
        address uploadedBy;
        uint256 timestamp;
        bool    isActive;
    }

    struct DeviceLog {
        string  deviceId;
        string  firmwareVersion;
        bool    updateSuccess;
        uint256 timestamp;
    }

    address public owner;
    mapping(address => bool)           public authorizedUploaders;
    mapping(bytes32 => FirmwareRecord) public firmwares;
    bytes32[]                          public firmwareIds;
    mapping(string => bytes32)         public latestFirmware;
    DeviceLog[]                        public deviceLogs;

    event FirmwareRegistered(bytes32 indexed id, string version, string deviceType);
    event DeviceUpdateLogged(string deviceId, string version, bool success);
    event UploaderAuthorized(address uploader);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(
            authorizedUploaders[msg.sender] || msg.sender == owner,
            "Not authorized"
        );
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedUploaders[msg.sender] = true;
    }

    // Called by Pi 3B broker.py
    function registerFirmware(
        string memory _version,
        string memory _hash,
        string memory _url,
        string memory _deviceType,
        string memory _signature
    ) external onlyAuthorized returns (bytes32 firmwareId) {
        firmwareId = keccak256(
            abi.encodePacked(_hash, _deviceType, block.timestamp, msg.sender)
        );
        require(bytes(firmwares[firmwareId].version).length == 0, "Already registered");
        firmwares[firmwareId] = FirmwareRecord({
            version:      _version,
            firmwareHash: _hash,
            downloadURL:  _url,
            deviceType:   _deviceType,
            signature:    _signature,
            uploadedBy:   msg.sender,
            timestamp:    block.timestamp,
            isActive:     true
        });
        firmwareIds.push(firmwareId);
        latestFirmware[_deviceType] = firmwareId;
        emit FirmwareRegistered(firmwareId, _version, _deviceType);
        return firmwareId;
    }

    // Called by Pi Zero gateway main.py
    function getLatestFirmware(string memory _deviceType)
        external view
        returns (
            string memory version,
            string memory firmwareHash,
            string memory downloadURL,
            string memory signature,
            bool isActive,
            bytes32 firmwareId
        )
    {
        firmwareId = latestFirmware[_deviceType];
        FirmwareRecord memory fw = firmwares[firmwareId];
        return (fw.version, fw.firmwareHash, fw.downloadURL,
                fw.signature, fw.isActive, firmwareId);
    }

    // Called by Pi Zero to verify hash
    function verifyFirmwareHash(bytes32 _firmwareId, string memory _hash)
        external view returns (bool)
    {
        FirmwareRecord memory fw = firmwares[_firmwareId];
        return fw.isActive &&
               keccak256(bytes(fw.firmwareHash)) == keccak256(bytes(_hash));
    }

    // Called by Pi Zero after OTA
    function logDeviceUpdate(
        string memory _deviceId,
        string memory _firmwareVersion,
        bool _success
    ) external {
        deviceLogs.push(DeviceLog({
            deviceId:        _deviceId,
            firmwareVersion: _firmwareVersion,
            updateSuccess:   _success,
            timestamp:       block.timestamp
        }));
        emit DeviceUpdateLogged(_deviceId, _firmwareVersion, _success);
    }

    function authorizeUploader(address _uploader) external onlyOwner {
        authorizedUploaders[_uploader] = true;
        emit UploaderAuthorized(_uploader);
    }

    function getFirmwareCount() external view returns (uint256) {
        return firmwareIds.length;
    }

    function getLogCount() external view returns (uint256) {
        return deviceLogs.length;
    }

    function getDeviceLog(uint256 _index)
        external view
        returns (string memory, string memory, bool, uint256)
    {
        require(_index < deviceLogs.length, "Out of bounds");
        DeviceLog memory l = deviceLogs[_index];
        return (l.deviceId, l.firmwareVersion, l.updateSuccess, l.timestamp);
    }

    function deactivateFirmware(bytes32 _firmwareId) external onlyAuthorized {
        firmwares[_firmwareId].isActive = false;
    }
}
