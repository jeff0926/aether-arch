"""Style Registry: maps (ComponentKind, provider) -> mxGraph style string.

The PDF specifies that high-fidelity draw.io diagrams require precise style
strings (shape, fillColor, strokeColor). Missing these makes icons collapse or
render glyphs incorrectly. This registry is the single source of truth.
"""

from __future__ import annotations

from aether.schemas.architecture import ComponentKind

# AWS palette (aws4 stencil).  Format: fully-qualified mxgraph style.
_AWS: dict[ComponentKind, str] = {
    ComponentKind.LAMBDA: "shape=mxgraph.aws4.lambda;fillColor=#ED7100;strokeColor=#ffffff;",
    ComponentKind.COMPUTE: "shape=mxgraph.aws4.ec2;fillColor=#ED7100;strokeColor=#ffffff;",
    ComponentKind.CONTAINER: "shape=mxgraph.aws4.fargate;fillColor=#ED7100;strokeColor=#ffffff;",
    ComponentKind.KUBERNETES: "shape=mxgraph.aws4.elastic_kubernetes_service;fillColor=#ED7100;strokeColor=#ffffff;",
    ComponentKind.DATABASE_SQL: "shape=mxgraph.aws4.rds;fillColor=#2E27AD;strokeColor=#ffffff;",
    ComponentKind.DATABASE_NOSQL: "shape=mxgraph.aws4.dynamodb;fillColor=#2E27AD;strokeColor=#ffffff;",
    ComponentKind.OBJECT_STORE: "shape=mxgraph.aws4.s3;fillColor=#7AA116;strokeColor=#ffffff;",
    ComponentKind.CACHE: "shape=mxgraph.aws4.elasticache;fillColor=#2E27AD;strokeColor=#ffffff;",
    ComponentKind.DATA_WAREHOUSE: "shape=mxgraph.aws4.redshift;fillColor=#2E27AD;strokeColor=#ffffff;",
    ComponentKind.LOAD_BALANCER: "shape=mxgraph.aws4.elastic_load_balancing;fillColor=#8C4FFF;strokeColor=#ffffff;",
    ComponentKind.CDN: "shape=mxgraph.aws4.cloudfront;fillColor=#8C4FFF;strokeColor=#ffffff;",
    ComponentKind.API_GATEWAY: "shape=mxgraph.aws4.api_gateway;fillColor=#8C4FFF;strokeColor=#ffffff;",
    ComponentKind.DNS: "shape=mxgraph.aws4.route_53;fillColor=#8C4FFF;strokeColor=#ffffff;",
    ComponentKind.QUEUE: "shape=mxgraph.aws4.simple_queue_service;fillColor=#E7157B;strokeColor=#ffffff;",
    ComponentKind.STREAM: "shape=mxgraph.aws4.kinesis;fillColor=#E7157B;strokeColor=#ffffff;",
    ComponentKind.WAF: "shape=mxgraph.aws4.waf;fillColor=#DD344C;strokeColor=#ffffff;",
    ComponentKind.IAM: "shape=mxgraph.aws4.identity_and_access_management;fillColor=#DD344C;strokeColor=#ffffff;",
    ComponentKind.SECRETS: "shape=mxgraph.aws4.secrets_manager;fillColor=#DD344C;strokeColor=#ffffff;",
    ComponentKind.LOGGING: "shape=mxgraph.aws4.cloudwatch;fillColor=#E7157B;strokeColor=#ffffff;",
    ComponentKind.MONITORING: "shape=mxgraph.aws4.cloudwatch;fillColor=#E7157B;strokeColor=#ffffff;",
    ComponentKind.TRACING: "shape=mxgraph.aws4.x_ray;fillColor=#E7157B;strokeColor=#ffffff;",
    ComponentKind.CLIENT: "shape=mxgraph.aws4.client;fillColor=#232F3E;strokeColor=#ffffff;",
    ComponentKind.EXTERNAL: "shape=mxgraph.aws4.internet;fillColor=#232F3E;strokeColor=#ffffff;",
}

# GCP palette (gcp2 stencil).
_GCP: dict[ComponentKind, str] = {
    ComponentKind.LAMBDA: "shape=mxgraph.gcp2.cloud_functions;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.COMPUTE: "shape=mxgraph.gcp2.compute_engine;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.CONTAINER: "shape=mxgraph.gcp2.cloud_run;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.KUBERNETES: "shape=mxgraph.gcp2.kubernetes_engine;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.DATABASE_SQL: "shape=mxgraph.gcp2.cloud_sql;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.DATABASE_NOSQL: "shape=mxgraph.gcp2.cloud_firestore;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.OBJECT_STORE: "shape=mxgraph.gcp2.cloud_storage;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.CACHE: "shape=mxgraph.gcp2.memorystore;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.DATA_WAREHOUSE: "shape=mxgraph.gcp2.bigquery;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.LOAD_BALANCER: "shape=mxgraph.gcp2.cloud_load_balancing;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.CDN: "shape=mxgraph.gcp2.cloud_cdn;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.API_GATEWAY: "shape=mxgraph.gcp2.apigee_api_platform;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.DNS: "shape=mxgraph.gcp2.cloud_dns;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.QUEUE: "shape=mxgraph.gcp2.cloud_tasks;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.STREAM: "shape=mxgraph.gcp2.cloud_pubsub;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.WAF: "shape=mxgraph.gcp2.cloud_armor;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.IAM: "shape=mxgraph.gcp2.cloud_iam;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.SECRETS: "shape=mxgraph.gcp2.secret_manager;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.LOGGING: "shape=mxgraph.gcp2.cloud_logging;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.MONITORING: "shape=mxgraph.gcp2.cloud_monitoring;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.TRACING: "shape=mxgraph.gcp2.cloud_trace;fillColor=#4285F4;strokeColor=#ffffff;",
    ComponentKind.CLIENT: "shape=mxgraph.gcp2.client;fillColor=#9AA0A6;strokeColor=#ffffff;",
    ComponentKind.EXTERNAL: "shape=mxgraph.gcp2.external_user;fillColor=#9AA0A6;strokeColor=#ffffff;",
}

# Azure palette (mscae stencil).
_AZURE: dict[ComponentKind, str] = {
    ComponentKind.LAMBDA: "shape=mxgraph.azure2.functions;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.COMPUTE: "shape=mxgraph.azure2.virtual_machine;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.CONTAINER: "shape=mxgraph.azure2.container_instances;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.KUBERNETES: "shape=mxgraph.azure2.kubernetes_services;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.DATABASE_SQL: "shape=mxgraph.azure2.sql_database;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.DATABASE_NOSQL: "shape=mxgraph.azure2.cosmos_db;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.OBJECT_STORE: "shape=mxgraph.azure2.storage_accounts;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.CACHE: "shape=mxgraph.azure2.cache_redis;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.DATA_WAREHOUSE: "shape=mxgraph.azure2.synapse_analytics;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.LOAD_BALANCER: "shape=mxgraph.azure2.load_balancer;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.CDN: "shape=mxgraph.azure2.cdn_profiles;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.API_GATEWAY: "shape=mxgraph.azure2.api_management;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.DNS: "shape=mxgraph.azure2.dns_zones;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.QUEUE: "shape=mxgraph.azure2.queue_storage;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.STREAM: "shape=mxgraph.azure2.event_hubs;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.WAF: "shape=mxgraph.azure2.application_gateway;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.IAM: "shape=mxgraph.azure2.active_directory;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.SECRETS: "shape=mxgraph.azure2.key_vaults;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.LOGGING: "shape=mxgraph.azure2.log_analytics_workspaces;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.MONITORING: "shape=mxgraph.azure2.monitor;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.TRACING: "shape=mxgraph.azure2.application_insights;fillColor=#0078D4;strokeColor=#ffffff;",
    ComponentKind.CLIENT: "shape=mxgraph.azure2.client;fillColor=#737373;strokeColor=#ffffff;",
    ComponentKind.EXTERNAL: "shape=mxgraph.azure2.internet;fillColor=#737373;strokeColor=#ffffff;",
}

# Generic fallback: simple coloured boxes that always render even if the
# stencil library is missing.
_GENERIC: dict[ComponentKind, str] = {
    kind: f"rounded=1;whiteSpace=wrap;html=1;fillColor=#E1E5EB;strokeColor=#5F6B7C;fontColor=#172B4D;"
    for kind in ComponentKind
}

_TABLES: dict[str, dict[ComponentKind, str]] = {
    "aws": _AWS,
    "gcp": _GCP,
    "azure": _AZURE,
    "generic": _GENERIC,
}


def style_for(kind: ComponentKind, provider: str = "aws") -> str:
    """Return the mxGraph style string for a given component on a given cloud.

    Falls back to the generic palette when a provider-specific entry is missing,
    guaranteeing the diagram always renders something visible.
    """
    table = _TABLES.get(provider, _GENERIC)
    return table.get(kind) or _GENERIC[kind]


def edge_style(style: str = "solid") -> str:
    """mxGraph style for connections."""
    base = (
        "endArrow=classic;html=1;rounded=0;"
        "strokeColor=#5F6B7C;strokeWidth=2;fontColor=#172B4D;"
    )
    if style == "dashed":
        base += "dashed=1;"
    return base
