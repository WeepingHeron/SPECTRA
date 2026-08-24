#!/usr/bin/env python3
"""Collect a non-secret, H05-scoped GCP resource and log inventory."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def run_json(command: list[str]) -> Any:
    completed = subprocess.run([*command, "--format=json"], check=True, text=True, capture_output=True)
    return json.loads(completed.stdout)


def unauthenticated_status(url: str) -> int:
    completed = subprocess.run(
        [
            "curl", "--silent", "--show-error", "--output", "/dev/null",
            "--write-out", "%{http_code}", "--max-time", "15", url + "/healthz",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return int(completed.stdout)


def h04_bindings(policy: dict[str, Any]) -> list[dict[str, Any]]:
    selected = []
    for binding in policy.get("bindings", []):
        members = [member for member in binding.get("members", []) if "spectra-h04" in member]
        if members:
            selected.append({"role": binding.get("role"), "members": sorted(members)})
    return sorted(selected, key=lambda item: (item["role"] or "", item["members"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="iceu-686")
    parser.add_argument("--region", default="asia-northeast3")
    parser.add_argument("--bucket", default="spectra-h04-iceu-686")
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    runs = json.loads(args.runs.read_text(encoding="utf-8"))
    correlations = [case["correlation_id"] for case in runs["cases"]]

    services = []
    service_iam = {}
    for role in ("mission", "parts", "assurance"):
        name = f"spectra-h04-{role}"
        raw = run_json([
            "gcloud", "run", "services", "describe", name,
            "--project", args.project, "--region", args.region,
        ])
        template = raw["spec"]["template"]
        url = raw["status"]["url"]
        policy = run_json([
            "gcloud", "run", "services", "get-iam-policy", name,
            "--project", args.project, "--region", args.region,
        ])
        public_members = sorted({
            member
            for binding in policy.get("bindings", [])
            for member in binding.get("members", [])
            if member in {"allUsers", "allAuthenticatedUsers"}
        })
        services.append({
            "name": raw["metadata"]["name"],
            "region": raw["metadata"]["labels"]["cloud.googleapis.com/location"],
            "latest_ready_revision": raw["status"]["latestReadyRevisionName"],
            "url": url,
            "runtime_service_account": template["spec"]["serviceAccountName"],
            "role": role,
            "ingress": raw["metadata"].get("annotations", {}).get("run.googleapis.com/ingress", "all"),
            "public_iam_members": public_members,
            "unauthenticated_healthz_http_status": unauthenticated_status(url),
        })
        service_iam[name] = h04_bindings(policy)

    workflow = run_json([
        "gcloud", "workflows", "describe", "spectra-h04-e2e",
        "--project", args.project, "--location", args.region,
    ])
    bucket = run_json([
        "gcloud", "storage", "buckets", "describe", f"gs://{args.bucket}",
        "--project", args.project,
    ])
    bucket_policy = run_json([
        "gcloud", "storage", "buckets", "get-iam-policy", f"gs://{args.bucket}",
    ])
    project_policy = run_json([
        "gcloud", "projects", "get-iam-policy", args.project,
    ])
    service_accounts = run_json([
        "gcloud", "iam", "service-accounts", "list", "--project", args.project,
        "--filter", "email:spectra-h04",
    ])
    image = run_json([
        "gcloud", "artifacts", "docker", "images", "describe",
        f"{args.region}-docker.pkg.dev/{args.project}/spectra-h04/agents:h05",
        "--project", args.project,
    ])

    log_filter = (
        'resource.type="cloud_run_revision" AND '
        'jsonPayload.message="spectra_h05_agent_result" AND ('
        + " OR ".join(f'jsonPayload.correlation_id="{value}"' for value in correlations)
        + ")"
    )
    raw_logs = run_json([
        "gcloud", "logging", "read", log_filter,
        "--project", args.project, "--freshness=2h", "--limit=30",
    ])
    logs = []
    for entry in raw_logs:
        payload = entry.get("jsonPayload", {})
        resource_labels = entry.get("resource", {}).get("labels", {})
        logs.append({
            "timestamp": entry.get("timestamp"),
            "insert_id": entry.get("insertId"),
            "service_name": resource_labels.get("service_name"),
            "revision_name": resource_labels.get("revision_name"),
            "run_id": payload.get("run_id"),
            "correlation_id": payload.get("correlation_id"),
            "agent": payload.get("agent"),
            "processing_status": payload.get("processing_status"),
            "assurance_decision": payload.get("assurance_decision"),
            "stable_codes": payload.get("stable_codes"),
            "body_hash_verified": payload.get("body_hash_verified"),
            "core_run_id": payload.get("core_run_id"),
            "latency_ms": payload.get("latency_ms"),
        })

    evidence = {
        "schema_version": "1.0.0",
        "project_id": args.project,
        "region": args.region,
        "services": sorted(services, key=lambda item: item["name"]),
        "workflow": {
            "name": workflow["name"],
            "revision_id": workflow["revisionId"],
            "state": workflow["state"],
            "service_account": workflow["serviceAccount"],
            "call_log_level": workflow["callLogLevel"],
            "deployment_bound_agent_urls": workflow.get("userEnvVars", {}),
        },
        "bucket": {
            "name": bucket["name"],
            "location": bucket["location"],
            "public_access_prevention": bucket["public_access_prevention"],
            "uniform_bucket_level_access": bucket["uniform_bucket_level_access"],
            "soft_delete_policy": bucket.get("soft_delete_policy"),
            "versioning_enabled": bucket.get("versioning_enabled", False),
            "lifecycle_config": bucket.get("lifecycle_config"),
        },
        "artifact_image": {
            "fully_qualified_digest": image["image_summary"]["fully_qualified_digest"],
            "digest": image["image_summary"]["digest"],
        },
        "service_accounts": sorted(
            {account["email"] for account in service_accounts if "spectra-h04" in account.get("email", "")}
        ),
        "iam": {
            "cloud_run": service_iam,
            "bucket": h04_bindings(bucket_policy),
            "project": h04_bindings(project_policy),
        },
        "cloud_run_structured_logs": sorted(
            logs, key=lambda item: (item["correlation_id"] or "", item["agent"] or "")
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "services": len(evidence["services"]),
        "service_accounts": len(evidence["service_accounts"]),
        "structured_logs": len(evidence["cloud_run_structured_logs"]),
        "workflow_revision": evidence["workflow"]["revision_id"],
        "unauthenticated_statuses": [item["unauthenticated_healthz_http_status"] for item in evidence["services"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
