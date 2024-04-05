# Ravi Patel

from dataclasses import dataclass
import datetime
from typing import Dict, List
from hashlib import sha256


@dataclass
class Policy:
    policy_type: str = None
    policy_id: str = None
    applied: str = None
    settings_hash: str = None
    assigned_date: str = None
    applied_date: str = None
    rule_groups: List = None


@dataclass
class Model:
    """Model
    Dataclass for host data
    """

    agent_info: Dict = None
    bios_info: str = None
    data_source: str = None
    external_ip: str = None
    first_seen: str = None
    raw_payloads: List = None
    group_info: List = None
    hardware_info: Dict = None
    host_name: str = None
    identifier: str = None
    instance_id: str = None
    internal_ip: str = None
    last_seen: str = None
    mac_address: str = None
    modified_timestamp: str = None
    open_ports: List = None
    os_version: str = None
    platform: str = None
    policies: List[Policy] = None
    software_info: Dict = None
    source_specific: Dict = None
    status: str = None
    system_manufacturer: str = None
    system_product_name: str = None
    tags: List = None
    version: str = None
    volunerabilties: Dict = None
    ingest_timestamp: str = datetime.datetime.utcnow().isoformat()
    recent_raw_hash: str = None

    @staticmethod
    def from_crowdstrike(payload: List) -> List:
        """Create Model instances from CrowdStrike payload"""
        models = []
        for host_payload in payload["body"]:
            model = Model()
            model.data_source = "crowdstrike"
            model.identifier = host_payload.get("_id")
            model.bios_info = (
                host_payload.get("bios_manufacturer", "")
                + " "
                + host_payload.get("bios_version", "")
            )
            model.host_name = host_payload.get("hostname")
            model.first_seen = host_payload.get("first_seen")
            model.last_seen = host_payload.get("last_seen")
            model.internal_ip = host_payload.get("local_ip")
            model.external_ip = host_payload.get("external_ip")
            model.os_version = host_payload.get("os_version")
            model.mac_address = host_payload.get("mac_address")
            model.platform = host_payload.get("platform_name")
            model.status = host_payload.get("status")
            model.modified_timestamp = host_payload["modified_timestamp"]["$date"]
            model.tags = host_payload.get("tags")
            model.system_manufacturer = host_payload.get("system_manufacturer")
            model.system_product_name = host_payload.get("system_product_name")
            model.policies = []
            for policy_type in host_payload["device_policies"]:
                policy = host_payload["device_policies"][policy_type]
                model.policies.append(
                    Policy(
                        policy_type=policy.get("policy_type"),
                        policy_id=policy.get("policy_id"),
                        applied=policy.get("applied"),
                        settings_hash=policy.get("settings_hash"),
                        assigned_date=policy.get("assigned_date"),
                        rule_groups=policy.get(
                            "rule_groups", []
                        ),
                    )
                )
            model.group_info = host_payload.get("groups", [])
            model.tags = host_payload.get("tags")
            model.raw_payloads = [host_payload]
            model.recent_raw_hash = sha256(str(host_payload).encode()).hexdigest()
            models.append(model)
        return models

    @staticmethod
    def from_qualys(payload: List) -> List:
        """Create Model instances from Qualys payload"""
        models = []
        for host_payload in payload["body"]:
            model = Model()
            model.data_source = "qualys"
            model.identifier = host_payload.get("id")
            model.host_name = host_payload.get("dnsHostName")
            model.bios_info = host_payload.get("biosDescription")
            model.internal_ip = host_payload.get("dnsHostName")
            model.external_ip = host_payload.get("address")
            model.os_version = host_payload.get("os")
            model.modified_timestamp = host_payload.get("modified")
            model.tags = host_payload.get("tags")
            model.system_manufacturer = host_payload.get("manufacturer")
            model.system_product_name = host_payload.get("model")
            model.agent_info = host_payload.get("agentInfo")
            model.volunerabilties = host_payload.get("vuln")
            model.last_seen = host_payload["lastVulnScan"]["$date"]
            # There are many other fields here to clean and add
            model.raw_payloads = [host_payload]
            model.recent_raw_hash = sha256(str(host_payload).encode()).hexdigest()
            models.append(model)
        return models
