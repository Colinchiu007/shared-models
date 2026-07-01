#!/usr/bin/env python3
"""Generate TypeScript type declarations from shared-models JSON Schema.

Reads .schemas/ directory output from export_schemas.py and produces:
  types/index.ts          -- Barrell export of all types
  types/{module}.ts       -- Per-module type declarations

Usage:
    python scripts/generate_types.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

SCHEMAS_DIR = Path(".schemas")
TYPES_DIR = Path("types")


def _to_ts_type(schema: dict[str, Any], definitions: dict[str, Any]) -> str:
    """Convert a JSON Schema property to a TypeScript type string."""
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return name if name in definitions else name

    if "anyOf" in schema:
        types = [_to_ts_type(s, definitions) for s in schema["anyOf"]]
        non_null = [t for t in types if t != "null"]
        result = " | ".join(non_null)
        if "null" in types:
            result = f"{result} | null"
        return result

    if "allOf" in schema:
        types = [_to_ts_type(s, definitions) for s in schema["allOf"]]
        return " & ".join(types)

    if "oneOf" in schema:
        types = [_to_ts_type(s, definitions) for s in schema["oneOf"]]
        return " | ".join(types)

    if "enum" in schema:
        vals = ", ".join(json.dumps(v) for v in schema["enum"])
        return f"({vals})"

    if "type" not in schema:
        return "unknown"

    t = schema["type"]
    if t == "string":
        return "string"
    if t in ("integer", "number"):
        return "number"
    if t == "boolean":
        return "boolean"
    if t == "array":
        items = schema.get("items", {})
        return f"Array<{_to_ts_type(items, definitions)}>"
    if t == "object":
        additional = schema.get("additionalProperties", {})
        if additional and isinstance(additional, dict) and additional != {}:
            val_type = _to_ts_type(additional, definitions)
            return f"Record<string, {val_type}>"
        return "Record<string, unknown>"
    return "unknown"


def generate_module_types(module_name: str, group_schemas: list[tuple[str, dict]]) -> str:
    """Generate TypeScript declarations for one module's models."""
    lines: list[str] = []
    lines.append(f"// Module: {module_name} -- Auto-generated from shared-models")
    lines.append("")

    # Track all written type names across ALL models in this module to avoid duplicates
    written: set[str] = set()

    for model_name, schema in group_schemas:
        definitions = schema.get("$defs", {})

        all_interfaces: dict[str, dict] = {}
        all_interfaces[model_name] = schema
        for def_name, def_schema in definitions.items():
            if def_name not in all_interfaces:
                all_interfaces[def_name] = def_schema

        for name, s in all_interfaces.items():
            if name in written:
                continue
            written.add(name)

            props = s.get("properties", {})
            required = set(s.get("required", []))

            if not props:
                if "enum" in s:
                    vals = ", ".join(json.dumps(v) for v in s["enum"])
                    lines.append(f"export type {name} = {vals};")
                elif s.get("type") in ("string", "number", "boolean", "integer"):
                    lines.append(f"export type {name} = {_to_ts_type(s, definitions)};")
                else:
                    lines.append(f"export interface {name} {{}}")
                lines.append("")
                continue

            lines.append(f"export interface {name} {{")
            for prop_name, prop_schema in props.items():
                ts_type = _to_ts_type(prop_schema, definitions)
                optional = "" if prop_name in required else "?"
                if "description" in prop_schema:
                    desc = prop_schema["description"]
                    lines.append(f"  /** {desc} */")
                lines.append(f"  {prop_name}{optional}: {ts_type};")
            lines.append("}")
            lines.append("")

    return "\n".join(lines)


def generate_index(models_map: dict[str, list[tuple[str, dict]]]) -> str:
    """Generate barrel export index.ts."""
    lines = [
        "// shared-models TypeScript declarations -- Auto-generated",
        "// Source: Python Pydantic v2 models -> JSON Schema -> TypeScript",
        "",
    ]
    for module_name in sorted(models_map.keys()):
        lines.append(f"export * from './{module_name}';")
    lines.append("")
    return "\n".join(lines)


def collect_schemas() -> dict[str, list[tuple[str, dict]]]:
    """Walk .schemas/ directory and collect all schemas grouped by module."""
    result: dict[str, list[tuple[str, dict]]] = {}
    if not SCHEMAS_DIR.exists():
        print("ERROR: .schemas/ not found. Run `python scripts/export_schemas.py` first.")
        sys.exit(1)

    for group_dir in sorted(SCHEMAS_DIR.iterdir()):
        if not group_dir.is_dir():
            continue
        module_name = group_dir.name
        schemas: list[tuple[str, dict]] = []
        for schema_file in sorted(group_dir.glob("*.json")):
            model_name = schema_file.stem
            schema = json.loads(schema_file.read_text())
            schemas.append((model_name, schema))
        if schemas:
            result[module_name] = schemas

    return result


def main():
    print("[shared-models] Generating TypeScript declarations...")

    models_map = collect_schemas()
    TYPES_DIR.mkdir(parents=True, exist_ok=True)

    for module_name, schemas in sorted(models_map.items()):
        ts_content = generate_module_types(module_name, schemas)
        target = TYPES_DIR / f"{module_name}.ts"
        target.write_text(ts_content, encoding="utf-8")
        print(f"  OK  types/{module_name}.ts  ({len(schemas)} models)")

    index_content = generate_index(models_map)
    (TYPES_DIR / "index.ts").write_text(index_content, encoding="utf-8")
    print(f"  OK  types/index.ts")

    total = sum(len(s) for s in models_map.values())
    print(f"\nDone. Generated {total} TypeScript types across {len(models_map)} modules.")


if __name__ == "__main__":
    main()
