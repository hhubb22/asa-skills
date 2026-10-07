import importlib.util
import json
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import library
import check_docs
import prepare_eval

spec = importlib.util.spec_from_file_location("collector", ROOT / "skills/skill-doctor/scripts/collect_sessions.py")
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class TemporaryCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, content):
        path = self.base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def clone(self):
        target = self.base / "source"
        shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__", ".local", ".git"))
        return target


class LibraryTests(TemporaryCase):
    def test_all_skills_validate(self):
        errors, stats = library.check(ROOT)
        self.assertEqual(errors, [])
        self.assertEqual(stats["skills"], len(library.skill_names()))
        self.assertLessEqual(max(stats["skill_lines"].values()), 120)

    def test_standard_frontmatter(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            meta = library.read_meta(path)
            self.assertEqual(meta["name"], path.parent.name)
            self.assertEqual(meta["license"], "MIT")
            self.assertNotIn("disable-model-invocation", meta)

    def test_each_skill_has_local_dependencies(self):
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            copied = self.base / path.parent.name
            shutil.copytree(path.parent, copied)
            for md in copied.rglob("*.md"):
                for link in library.LINK_RE.findall(md.read_text(encoding="utf-8")):
                    if ":" in link or link.startswith("#"):
                        continue
                    target = (md.parent / link.split("#", 1)[0]).resolve()
                    self.assertTrue(target.exists(), (md, link))
                    self.assertTrue(target.is_relative_to(copied.resolve()))

    def test_shared_files_are_exact(self):
        for path, content in library.generated_files(ROOT).items():
            self.assertEqual(path.read_bytes(), content)

    def test_missing_local_reference_is_detected(self):
        clone = self.clone()
        (clone / "skills/research/references/evidence.md").unlink()
        errors, _ = library.check(clone)
        self.assertTrue(any("Broken relative link" in x for x in errors))

    def test_shared_drift_is_detected(self):
        clone = self.clone()
        p = clone / "skills/work/references/operating-contract.md"
        p.write_text("drift", encoding="utf-8")
        errors, _ = library.check(clone)
        self.assertTrue(any("Generated file drift" in x for x in errors))

    def test_bad_frontmatter_rejected(self):
        p = self.write("SKILL.md", "---\nname: test\nname: test\n---\n")
        with self.assertRaises(ValueError):
            library.read_meta(p)

    def test_source_identifiers_are_blob_hashes(self):
        lock = json.loads((ROOT / "upstream.lock.json").read_text())
        self.assertLessEqual(set(lock["skills"]), set(library.skill_names()))
        for entries in lock["skills"].values():
            for item in entries:
                self.assertRegex(item["git_blob_sha"], r"^[0-9a-f]{40}$")
                self.assertIn("/git/blobs/", item["content_url"])

    def test_stale_lock_entry_is_detected(self):
        clone = self.clone()
        shutil.rmtree(clone / "skills/wait-what")
        errors, stats = library.check(clone)
        self.assertEqual(stats["skills"], len(library.skill_names()) - 1)
        self.assertTrue(any("no longer exists: wait-what" in x for x in errors))

    def test_new_skill_without_lock_entry_is_accepted(self):
        clone = self.clone()
        skill = clone / "skills/new-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text('---\nname: new-skill\ndescription: "本地新增。"\nlicense: MIT\n---\n\n# New\n', encoding="utf-8")
        for path, data in library.generated_files(clone).items():
            if path.is_relative_to(skill):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        errors, stats = library.check(clone)
        self.assertEqual(errors, [])
        self.assertEqual(stats["skills"], len(library.skill_names()) + 1)
        self.assertIn("# Sources", (skill / "SOURCES.md").read_text(encoding="utf-8"))


class CollectorTests(TemporaryCase):
    def records(self, data, fmt="auto", budget=10000):
        raw = "\n".join(json.dumps(x) for x in data).encode()
        return collector.normalize(raw, fmt, ".jsonl", budget)

    def test_generic_visible_records(self):
        entries, stats = self.records([{"role": "user", "content": "question"}, {"role": "assistant", "content": "answer"}])
        self.assertEqual([x["text"] for x in entries], ["question", "answer"])
        self.assertEqual(stats["skipped_records"], 0)

    def test_pi_messages_and_tools(self):
        rows = [{"type": "message", "message": {"role": "assistant", "content": [{"type": "toolCall", "name": "read", "arguments": {"path": "x"}}]}},
                {"type": "message", "message": {"role": "toolResult", "content": [{"type": "text", "text": "output"}]}}]
        entries, _ = self.records(rows, "pi")
        self.assertIn("TOOL read", entries[0]["text"])
        self.assertEqual(entries[1]["text"], "output")

    def test_claude_message_with_nested_secret(self):
        rows = [{"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "request", "input": {"headers": {"Authorization": "private-value"}}}]}}]
        entries, _ = self.records(rows, "claude")
        self.assertNotIn("private-value", entries[0]["text"])

    def test_codex_visible_messages_skip_hidden_and_duplicates(self):
        rows = [{"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "analysis", "content": [{"type": "output_text", "text": "hidden sentinel"}]}},
                {"type": "response_item", "payload": {"type": "message", "role": "assistant", "channel": "final", "content": [{"type": "output_text", "text": "visible answer"}]}},
                {"type": "event_msg", "payload": {"type": "agent_message", "message": "visible answer"}},
                {"type": "response_item", "payload": {"type": "reasoning", "summary": "hidden sentinel"}}]
        entries, stats = self.records(rows, "codex")
        self.assertEqual([x["text"] for x in entries], ["visible answer"])
        self.assertEqual(stats["skipped_records"], 3)

    def test_codex_event_only_export(self):
        entries, _ = self.records([{"type": "event_msg", "payload": {"type": "user_message", "message": "hello"}}], "codex")
        self.assertEqual(entries[0]["text"], "hello")

    def test_unknown_records_are_counted(self):
        _, stats = self.records([{"type": "future-format", "payload": "unknown"}, {"role": "user", "content": "visible"}])
        self.assertEqual(stats["skipped_records"], 1)

    def test_hidden_blocks_not_extracted(self):
        value = [{"type": "thinking", "thinking": "not visible"}, {"type": "text", "text": "visible"}]
        self.assertEqual(collector.visible_content(value), "visible")

    def test_common_credentials_redacted(self):
        text = 'api_key="secret-a"\npassword=secret-b\nAuthorization: Bearer secret-c\nCookie: sid=secret-d\nhttps://user:secret-e@example.test\nsk-abcdefghijklmnop\n'
        result = collector.redact(text)
        for value in ["secret-a", "secret-b", "secret-c", "secret-d", "secret-e", "sk-abcdefghijklmnop"]:
            self.assertNotIn(value, result)

    def test_pem_redaction_retains_line_count(self):
        text = '-----BEGIN RSA PRIVATE KEY-----\nprivate-material\n-----END RSA PRIVATE KEY-----'
        result = collector.redact(text)
        self.assertNotIn("private-material", result)
        self.assertEqual(result.count("\n"), text.count("\n"))

    def test_truncation_is_reported(self):
        entries, stats = self.records([{"role": "user", "content": "x" * 20}], budget=5)
        self.assertEqual(entries[0]["text"], "xxxxx")
        self.assertTrue(entries[0]["truncated"])
        self.assertEqual(stats["omitted_characters"], 15)

    def test_collect_private_permissions_and_no_raw_copy(self):
        source = self.write("input.txt", "api_key=secret-a\nvisible")
        out = self.base / "report"
        result = collector.collect([source], out)
        self.assertFalse(result["network_used"])
        self.assertFalse(result["model_evaluation_performed"])
        self.assertNotIn("secret-a", (out / "session-001.md").read_text())
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((out / "session-001.md").stat().st_mode), 0o600)
        self.assertEqual(len(list(out.iterdir())), 2)

    def test_existing_output_is_preserved(self):
        source = self.write("input.txt", "visible")
        self.write("report/keep.txt", "original")
        with self.assertRaisesRegex(ValueError, "already exist"):
            collector.collect([source], self.base / "report")
        self.assertEqual((self.base / "report/keep.txt").read_text(), "original")

    def test_malformed_jsonl_does_not_create_output(self):
        source = self.write("bad.jsonl", '{"broken":')
        with self.assertRaisesRegex(ValueError, "Invalid JSONL"):
            collector.collect([source], self.base / "report")
        self.assertFalse((self.base / "report").exists())

    def test_unknown_only_export_fails_honestly(self):
        source = self.write("unknown.jsonl", '{"type":"new-unknown"}\n')
        with self.assertRaisesRegex(ValueError, "No supported"):
            collector.collect([source], self.base / "report")

    def test_symlink_and_directory_inputs_rejected(self):
        source = self.write("input.txt", "visible")
        alias = self.base / "alias.txt"
        alias.symlink_to(source)
        for path in [alias, self.base]:
            with self.assertRaises(ValueError):
                collector.collect([path], self.base / "report")

    def test_fifo_input_does_not_block(self):
        import os
        fifo = self.base / "pipe"
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            collector.collect([fifo], self.base / "report")

    def test_size_and_duplicate_limits(self):
        source = self.write("input.txt", "123456")
        with self.assertRaises(ValueError):
            collector.collect([source], self.base / "report", max_bytes=2)
        with self.assertRaises(ValueError):
            collector.collect([source, source], self.base / "report")
        self.assertFalse((self.base / "report").exists())

    def test_collector_has_no_network_or_process_import(self):
        import ast
        source = ROOT / "skills/skill-doctor/scripts/collect_sessions.py"
        imports = []
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append((node.module or "").split(".")[0])
        self.assertFalse(set(imports) & {"requests", "urllib", "http", "socket", "subprocess"})


class DocumentTests(unittest.TestCase):
    def test_example_pair_passes_structural_check(self):
        product = (ROOT / "skills/write-product-spec/references/example-product.md").read_text()
        tech = (ROOT / "skills/write-tech-spec/references/example-tech.md").read_text()
        self.assertEqual(check_docs.validate(product, "product")[0], [])
        self.assertEqual(check_docs.validate(tech, "tech", product)[0], [])

    def test_duplicate_requirements_fail(self):
        text = 'Status: draft\n## Summary\nx\n## Behavior\n- R-01: a\n- R-01: b\n'
        self.assertIn("Duplicate requirement identifiers", check_docs.validate(text, "product")[0])

    def test_unknown_requirement_fails(self):
        tech = 'Status: draft\n## Context\nx\n## Proposed changes\nx\n## Testing and validation\nR-99\n'
        errors, _ = check_docs.validate(tech, "tech", "- R-01: known")
        self.assertIn("Unknown requirement: R-99", errors)

    def test_missing_source_does_not_claim_validated_references(self):
        tech = 'Status: draft\n## Context\nx\n## Proposed changes\nx\n## Testing and validation\nR-01\n'
        errors, warnings = check_docs.validate(tech, "tech")
        self.assertEqual(errors, [])
        self.assertTrue(any("not resolved" in warning for warning in warnings))


class EvaluationTests(TemporaryCase):
    def test_cases_are_unique_and_split(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        self.assertEqual(len(cases), 48)
        self.assertEqual(len({x["id"] for x in cases}), 48)
        self.assertEqual(sum(x["split"] == "holdout" for x in cases), 16)

    def test_trigger_queries_cover_known_skills(self):
        data = json.loads((ROOT / "evals/triggers.json").read_text())["skills"]
        self.assertLessEqual(set(data), set(library.skill_names()))
        queries = []
        for name, item in data.items():
            self.assertGreaterEqual(len(item["should_trigger"]), 5, name)
            self.assertGreaterEqual(len(item["should_not_trigger"]), 5, name)
            queries += item["should_trigger"] + item["should_not_trigger"]
        self.assertEqual(len(queries), len(set(queries)))

    def test_preparation_has_no_model_results(self):
        out = self.base / "eval"
        result = prepare_eval.prepare(out, case_id="D04-implement")
        self.assertEqual(result["model_runs_performed"], 0)
        self.assertTrue((out / "D04-implement/workspace/policy_view.py").exists())
        task = (out / "D04-implement/task.md").read_text()
        self.assertNotIn('"forbidden"', task)
        self.assertNotIn('"expected"', task)
        evaluator = json.loads((out / "D04-implement/evaluator.json").read_text())
        self.assertEqual(evaluator["status"], "not_run")
        self.assertFalse((out / "D04-implement/workspace/evaluator.json").exists())

    def test_existing_evaluation_is_not_overwritten(self):
        out = self.base / "eval"
        out.mkdir()
        with self.assertRaises(ValueError):
            prepare_eval.prepare(out)

    def test_no_matching_case_is_an_error(self):
        with self.assertRaises(ValueError):
            prepare_eval.prepare(self.base / "eval", case_id="missing")


if __name__ == "__main__":
    unittest.main()
